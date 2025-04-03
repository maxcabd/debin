
from typing import Any, List, get_args, get_origin
from dataclasses import Field, is_dataclass
from enum import IntEnum, IntFlag

from debin.primitives.numerical import *
from debin.core.binary_parser import BinaryParser
from debin.utils.size import *
from debin.utils.endian import convert_endian_str, read_from_endian
from debin.utils.state import This
from debin.utils.enum import is_debin_enum
from debin.decorators.directives import *
from debin.decorators.meta import debin_metadata





def read_field(self, field: Field, buffer: bytearray, offset: int, parser: BinaryParser) -> int:
    """Helper function to read a field from the buffer and update the offset."""

    # Create `this` context object for access to the current instance
    this = This(self)

    # Ignore fields marked with 'ignore'
    if field.metadata.get("ignore", False):
        setattr(self, field.name, None)
        return offset

    # Handle the `map` directive
    if "map" in field.metadata:
        _, offset = map_dir(field, buffer, offset, parser.endian, parser, this)
        return offset

    if 'if' in field.metadata:
        value, offset = if_dir(field, buffer, offset, parser, this)
        if value is not object():  # Only set attribute if not our sentinel
            setattr(self, field.name, value)
        return offset

    # Skip `calc` fields for now (handled later)
    if "calc" in field.metadata:
        return offset

    field_type = field.type
    field_endian = convert_endian_str(field.metadata.get("endian", parser.endian))
    cur_offset: int = offset  # Save for debugging

    if is_debin_enum(field_type):
        if not hasattr(field_type, '_debin_repr'):
            raise ValueError(f"Enum {field_type.__name__} missing repr - did you use @debin(repr=...)?")
        
        repr_type = field_type._debin_repr
       
        if repr_type is None:
            raise ValueError(f"Enum {field_type.__name__} has None as representation type")
            
        value, offset = parser.parse(buffer, offset, repr_type)

         # Manually decompose the value into individual flags
        flag_value = field_type(0)  # Start with empty flag
        for flag in field_type:
            if flag.value & value:
                flag_value |= flag  # Add each matching flag
      
        setattr(self, field.name, flag_value)
        return offset

    # Handle the `parse_with` directive
    if "parse_with" in field.metadata:
        value, offset = parse_with_dir(field, buffer, offset, field_endian, parser, this)
        setattr(self, field.name, value)
        return offset  # Avoid unnecessary list handling

    # Handle Lists
    if get_origin(field_type) is list:
        values: List[Any] = []
        elem_type = get_args(field_type)[0]  # Get the inner type

        # Determine count of elements
        count = field.metadata.get("count", 1)
        if isinstance(count, str):
            count = getattr(this, count, None)
        elif callable(count):
            count = count(this)

        # Read list elements
        for _ in range(count):
            if is_dataclass(elem_type):
                endian = field_endian if field.metadata.get("endian") else getattr(elem_type, "_endianness", parser.endian)
                parsed = read_from_endian(elem_type, endian, buffer, offset)
                offset += calc_dataclass_size(parsed)
            else:
                parsed, offset = parser.parse(buffer, offset, elem_type)

            values.append(parsed)

        setattr(self, field.name, values)

    # Handle Nested Dataclasses
    elif is_dataclass(field_type):
        endian = field_endian if field.metadata.get("endian") else getattr(field_type, "_endianness", parser.endian)
        parsed = read_from_endian(field_type, endian, buffer, offset)
        setattr(self, field.name, parsed)

        # Account for 'magic' field if added by decorator
        if field_type in debin_metadata and "magic" in debin_metadata[field_type]:
            offset += 4  # Assuming magic size is 4 bytes

        offset += calc_dataclass_size(parsed)

    # Handle Primitives
    else:
        parsed, offset = parser.parse(buffer, offset, field_type)
        setattr(self, field.name, parsed)

    # Debugging: Print the value if 'dbg' directive is set
    if field.metadata.get("dbg", False):
        value = getattr(self, field.name)
        print(f"[offset 0x{cur_offset:02x}] {field.name} = {value}")

    return offset