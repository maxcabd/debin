from dataclasses import Field, dataclass, fields, field
from typing import Any, Type, Optional
from enum import IntEnum, IntFlag

from debin.error.exceptions import MagicError

from debin.primitives.numerical import *
from debin.primitives.string import *

from debin.utils.size import *
from debin.utils.endian import convert_endian_str

from debin.core.binary_parser import BinaryParser


from debin.decorators.meta import debin_metadata
from debin.decorators.directives import *


def debin(*args, endian: Optional[str] = "little", magic: Optional[str] = None, repr: Optional[Type] = None):
    """Decorator to add read and write methods to a dataclass"""
    def decorator(cls) -> Type:
        
        cls = dataclass(init=False)(cls)

        cls._endianness = endian
        cls._debin_repr = repr
        cls.read = _create_read_method(cls, convert_endian_str(endian), magic)
        cls.read_le = _create_read_method(cls, "<", magic)  # Little-endian
        cls.read_be = _create_read_method(cls, ">", magic)  # Big-endian

        
        debin_metadata[cls] = set()

        if magic is not None:
            setattr(cls, "magic", field(default=magic, metadata={"ignore": True}))
            debin_metadata[cls].add("magic")

        return cls

    # If no arguments are provided, return the decorator directly
    if not args:
        return decorator
    # If arguments are provided, apply the decorator to the first argument
    return decorator(args[0])

def _create_read_method(cls, default_endian: str, magic: Optional[str]) -> Any:
    """Create a method to read binary data in the specified endian format."""

    # Set the endian based on the read method
    cls._endianness = convert_endian_str(default_endian)


    parser = BinaryParser(cls._endianness)


    def read_method(self, buffer: bytearray, offset: int = 0) -> Any:
        from debin.core.struct_reader import read_field
        
        if magic is not None:
            magic_bytes = buffer[offset: offset + 4]
            self.magic = magic_bytes.decode("ascii")
            if self.magic != magic:
                raise MagicError(magic, self.magic)
            offset += 4  # Move the cursor
       

        for field in fields(cls):

            if "calc" in field.metadata:
                _, offset = calc_dir(field, buffer, offset, parser.endian, self)

            if "map" in field.metadata:
                _, offset = map_dir(field, buffer, offset, parser.endian, parser, self)

            if field.metadata.get("ignore", False) and "map" in field.metadata:
                setattr(self, field.name, field.metadata["map"](self))


            # Handle align_before
            if 'align_before' in field.metadata:
                _, offset = align_before_dir(field, buffer, offset, default_endian)
                parser.current_offset = offset

            # Handle pad_before
            if 'pad_before' in field.metadata:
                _, offset = pad_before_dir(field, buffer, offset, default_endian)

            # Read the field and update the offset
            offset = read_field(self, field, buffer, offset, parser)
            

            # Handle pad_after
            if 'pad_after' in field.metadata:
                _, offset = pad_after_dir(field, buffer, offset, default_endian)

            # Handle align_after
            if 'align_after' in field.metadata:
                _, offset = align_after_dir(field, buffer, offset, default_endian)
                

        for field in fields(cls):
            if field.metadata.get("ignore", False) and "map" in field.metadata:
                setattr(self, field.name, field.metadata["map"](self))

        return self

    return read_method