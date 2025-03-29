import struct
from struct import unpack
from typing import Any, Type

from dataclasses import is_dataclass


from debin.error.exceptions import InvalidBufferError, UnsupportedTypeError
from debin.primitives.numerical import *
from debin.primitives.string import *
from debin.utils.size import calc_primitive_type_size

class BinaryParser:
    def __init__(self, endian: str):
        self.endian = endian
        self.current_offset = 0  # Add offset tracking

    def parse(self, buffer: bytearray, offset: int, field_type: Type) -> tuple[Any, int]:
        self.current_offset = offset  # Track the starting offset
        
        if field_type is nullstr:
            value, new_offset = self._parse_nullstring(buffer, offset)
        elif is_dataclass(field_type):
            value, new_offset = self._parse_dataclass(buffer, offset, field_type)
        else:
            value, new_offset = self._parse_numeric(buffer, offset, field_type)
        
        self.current_offset = new_offset  # Update the current offset
        return value, new_offset

    def _parse_numeric(self, buffer: bytearray, offset: int, field_type: Type) -> tuple[Any, int]:
        format_char = {
            bool: "?",
            uint8: "B",
            int8: "b",
            uint16: "H",
            int16: "h",
            uint32: "I",
            int32: "i",
            int: "i", # treat Python int as int32
            uint64: "Q",
            int64: "q",
            float16: "e",
            float32: "f",
            float: "f",
            float64: "d",
        }.get(field_type)

        if format_char is None:
            raise UnsupportedTypeError(field_type)

        size = calc_primitive_type_size(field_type)

        if offset + size > len(buffer):
            raise InvalidBufferError(f"Buffer too small to read {field_type} at offset {offset}")

        format_str = f"{self.endian}{format_char}"

        try:
            value = unpack(format_str, buffer[offset:offset+size])[0]
        except struct.error as e:
            raise InvalidBufferError(f"Failed to unpack {field_type} at offset {offset}: {e}")

        new_offset = offset + size
        self.current_offset = new_offset  # Update current offset
        return value, new_offset

    def _parse_nullstring(self, buffer: bytearray, offset: int) -> tuple[Any, int]:
        value, new_offset = nullstr.read(buffer, offset)
        self.current_offset = new_offset  # Update current offset
        return value, new_offset

    def _parse_dataclass(self, buffer: bytearray, offset: int, field_type: Type) -> tuple[Any, int]:
        instance = field_type()
        value, new_offset = instance.read(buffer, offset)
        self.current_offset = new_offset  # Update current offset
        return value, new_offset
