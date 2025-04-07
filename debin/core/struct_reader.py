
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
    """Optimized helper function to read a field from the buffer and update the offset."""
    
   
    if field.metadata.get("ignore", False):
        object.__setattr__(self, field.name, None)
        return offset

    # Create `this` context object once
    this = This(self)
    field_type = field.type
    field_metadata = field.metadata
    field_name = field.name


    # Handle the seek directive first
    if 'seek' in field.metadata or 'seek_before' in field.metadata:
        value, offset = seek_dir(field, buffer, offset, parser.endian, parser, this)
        object.__setattr__(self, field_name, value)
        return offset

    # Handle directives in order of likely frequency
    if 'if' in field_metadata:
        value, offset = if_dir(field, buffer, offset, parser, this)
        if value is not object():  # Only set attribute if not our sentinel
            object.__setattr__(self, field_name, value)
        return offset

    if "map" in field_metadata:
        _, offset = map_dir(field, buffer, offset, parser.endian, parser, this)
        return offset

   
    if "calc" in field_metadata:
        return offset

   
    field_endian = convert_endian_str(field_metadata.get("endian", parser.endian))
    cur_offset = offset

    # Handle enums
    if is_debin_enum(field_type):
        repr_type = field_type._debin_repr
        if repr_type is None:
            raise ValueError(f"Enum {field_type.__name__} has None as representation type")
            
        value, offset = parser.parse(buffer, offset, repr_type)
        
       
        flag_value = field_type(0)
        for flag in field_type:
            if flag.value & value:
                flag_value |= flag
      
        object.__setattr__(self, field_name, flag_value)
        return offset

    # Handle parse_with directive
    if "parse_with" in field_metadata:
        value, offset = parse_with_dir(field, buffer, offset, field_endian, parser, this)
        object.__setattr__(self, field_name, value)
        return offset

    # Handle lists
    if get_origin(field_type) is list:
        elem_type = get_args(field_type)[0]
        count = field_metadata.get("count", 1)
        
       
        if isinstance(count, str):
            count = getattr(this, count, 1)
        elif callable(count):
            count = count(this)

        # Pre-allocate list
        values = [None] * count
        
       
        if not is_dataclass(elem_type):
            for i in range(count):
                parsed, offset = parser.parse(buffer, offset, elem_type)
                values[i] = parsed
        else:
            endian = field_endian if "endian" in field_metadata else getattr(elem_type, "_endianness", parser.endian)
            for i in range(count):
                parsed = read_from_endian(elem_type, endian, buffer, offset)
                offset += calc_dataclass_size(parsed)
                values[i] = parsed

        object.__setattr__(self, field_name, values)
        return offset

    # Handle dataclasses
    if is_dataclass(field_type):
        endian = field_endian if "endian" in field_metadata else getattr(field_type, "_endianness", parser.endian)
        parsed = read_from_endian(field_type, endian, buffer, offset)
        object.__setattr__(self, field_name, parsed)

        # Handle magic field if present
        if field_type in debin_metadata and "magic" in debin_metadata[field_type]:
            magic = field_type.__dict__.get("magic").default
            offset += len(magic)

        offset += calc_dataclass_size(parsed)
        return offset

    # Default case for primitives
    parsed, offset = parser.parse(buffer, offset, field_type)
    object.__setattr__(self, field_name, parsed)

    # Debug output
    if field_metadata.get("dbg", False):
        print(f"[offset 0x{cur_offset:02x}] {field_name} = {parsed}")

    return offset