from typing import get_origin, get_args
from dataclasses import Field
from debin.core.binary_parser import BinaryParser
from debin.utils.state import This

def default_dir(field: Field, buffer: bytearray, offset: int, default_endian: str, parser):
    pass

def calc_dir(field: Field, buffer: bytearray, offset: int, default_endian: str, this):
    expression = field.metadata.get('calc')

    if expression is None:
        raise ValueError('The "calc" directive requires an expression to evaluate.')

    context = vars(this)

    value = eval(expression, {}, context)


    setattr(this, field.name, value)

    return value, offset

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

    # Start the buffer at the current offset
    #buffer = buffer[offset:]
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
