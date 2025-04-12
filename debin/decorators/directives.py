from typing import Any, Tuple, get_origin, get_args
from dataclasses import Field, is_dataclass
from debin.core.binary_parser import BinaryParser
from debin.core.io import SeekFrom, SeekSpec
from debin.utils.state import This
from debin.utils.endian import read_from_endian
from debin.utils.size import calc_dataclass_size



def default_dir(field: Field, buffer: bytearray, offset: int, default_endian: str, parser):
    pass

def calc_dir(field: Field, buffer: bytearray, offset: int, default_endian: str, this: This):
    expression = field.metadata.get('calc')

    if expression is None:
        raise ValueError('The "calc" directive requires an expression to evaluate.')

    context = vars(this)

    value = eval(expression, {}, context)


    setattr(this, field.name, value)

    return value, offset

def if_dir(field: Field, buffer: bytearray, offset: int, parser: BinaryParser, this: This) -> tuple[Any, int]:
    condition = field.metadata.get('if')
    if condition is None:
        raise ValueError('The "if" directive requires a condition to evaluate.')

    # Evaluate condition
    if callable(condition):
        should_parse = condition(this)
    else:
        context = vars(this)
        should_parse = bool(eval(condition, {}, context))

    if not should_parse:
        return None, offset  # Skip parsing if condition fails

    field_type = field.type


    if get_origin(field_type) is list:
        element_type = get_args(field_type)[0]
        count = field.metadata.get("count", 1)
        
        
        # Resolve count
        if isinstance(count, str):
            count = getattr(this, count, 1)
        elif callable(count):
            count = count(this)


        values = [] * count
        for _ in range(count):
            if is_dataclass(element_type):
                endian = field.metadata.get("endian", parser.endian)
                parsed = read_from_endian(element_type, endian, buffer, offset)
                offset += calc_dataclass_size(parsed)
            else:
                parsed, offset = parser.parse(buffer, offset, element_type)
            values.append(parsed)

        return values, offset

    # Handle non-list types
    return parser.parse(buffer, offset, field_type)

def map_dir(field: Field, buffer: bytearray, offset: int, default_endian: str, parser: BinaryParser, this: This):
    """
    Apply a transformation function to the parsed value.
    """

    if field.metadata.get("ignore", False):
        setattr(this, field.name, None)  # Placeholder to avoid NoneType issues
        return None, offset

    value, offset = parser.parse(buffer, offset, field.type)


    map_func = field.metadata.get('map')
    if map_func:
        value = map_func(value)


    setattr(this, field.name, value)

    return value, offset


def pad_before_dir(field, buffer, offset, default_endian):
    """Skip a specified number of bytes before reading the field."""
    pad_bytes = field.metadata.get('pad_before', 0)
    return None, offset + pad_bytes

def pad_after_dir(field, buffer, offset, default_endian):
    """Skip a specified number of bytes after reading the field."""
    pad_bytes = field.metadata.get('pad_after', 0)
    return None, offset + pad_bytes

def align_before_dir(field, buffer, offset, default_endian):
    """Align the offset to a specified boundary before reading the field."""
    alignment = field.metadata.get('align_before', 1)
    padding = (alignment - (offset % alignment)) % alignment
    return None, offset + padding

def align_after_dir(field, buffer, offset, default_endian):
    """Align the offset to a specified boundary after reading the field."""
    alignment = field.metadata.get('align_after', 1)
    padding = (alignment - (offset % alignment)) % alignment
    return None, offset + padding



def seek_dir(field: Field, buffer: bytearray, offset: int, default_endian: str, 
             parser: BinaryParser, this: This) -> Tuple[Any, int]:
    """Seek to a specific position before reading the field and parse it."""
    seek_spec = field.metadata.get('seek')
    seek_before = field.metadata.get('seek_before')
    
    # Determine new offset
    new_offset = offset
    if seek_spec is not None:
        if isinstance(seek_spec, str):
            new_offset = getattr(this, seek_spec)
        else:
            new_offset = seek_spec
    elif seek_before is not None:
        if isinstance(seek_before, int):
            new_offset = seek_before
        elif isinstance(seek_before, tuple) and len(seek_before) == 2:
            origin, rel_offset = seek_before
            if origin == SeekFrom.START:
                new_offset = rel_offset
            elif origin == SeekFrom.CURRENT:
                new_offset = offset + rel_offset
            elif origin == SeekFrom.END:
                new_offset = len(buffer) + rel_offset
            else:
                raise ValueError(f"Invalid seek origin: {origin}")
        elif isinstance(seek_before, str):
            new_offset = getattr(this, seek_before)
        elif callable(seek_before):
            new_offset = seek_before(buffer, offset)
        else:
            raise ValueError(f"Invalid seek_before specification: {seek_before}")
    
    
    # Now parse the field at the new offset
    field_type = field.type
    if get_origin(field_type) is list:
        element_type = get_args(field_type)[0]
        count = field.metadata.get("count", 1)
        
        if isinstance(count, str):
            count = getattr(this.obj, count, 1)
        elif callable(count):
            count = count(this.obj)
        
        values = []
        for _ in range(count):
            parsed, new_offset = parser.parse(buffer, new_offset, element_type)
            values.append(parsed)
        
        return values, new_offset
    else:
        parsed, new_offset = parser.parse(buffer, new_offset, field_type)
        return parsed, new_offset


def ignore_dir():
    """Ignore the field and do not parse it."""
    pass


def parse_with_dir(field: Field, buffer: bytearray, offset: int, default_endian: str, parser: BinaryParser, this: This):
    """
    Use a custom parsing function to parse the field.
    The function should be passed the buffer, offset, and parser, and should return the parsed value and the new offset.
    """
    parse_func = field.metadata.get('parse_with')

    if parse_func is None:
        raise ValueError(f"The 'parse_with' directive requires a custom parsing function for field '{field.name}'.")

    field_type = field.type

    if get_origin(field_type) is list:
        element_type = get_args(field_type)[0]  # Get the type of elements in the list
    else:
        raise TypeError(f"The 'parse_with' directive can only be used with List fields, not {field_type}.")


    value, new_offset = parse_func(buffer, offset, parser, element_type)


    return value, new_offset


# Register metadata directives
METADATA_DIRECTIVES = {
    'pad_before': pad_before_dir,
    'pad_after': pad_after_dir,
    'align_before': align_before_dir,
    'align_after': align_after_dir,
    'ignore': ignore_dir,
    'parse_with': parse_with_dir,
}
