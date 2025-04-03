from typing import Optional, Type, cast
from dataclasses import is_dataclass
from debin.protocol import DebinInstance, T
from debin.utils.enum import is_debin_enum


def convert_endian_str(endian: Optional[str]) -> str:
    """Convert endian string to standard format."""
    if endian:
        match endian.lower():
            case "big" | ">":
                return ">"
            case "little" | "<":
                return "<"

    raise ValueError(f"Invalid endian specification: {endian}")


def read_from_endian(cls: Type[T], endian: str, buffer: bytes, offset: int) -> DebinInstance:
    # Handle enum types
    if is_debin_enum(cls):
        repr_type = cls._debin_repr
        if repr_type is None:
            raise ValueError(f"Enum {cls.__name__} has no binary representation specified")
        
        # Read the underlying value
        value, _ = repr_type.read(buffer, offset)
        instance = cast(DebinInstance, cls(value))
      
        return instance
    
    # Handle dataclasses
    if is_dataclass(cls):
        instance = cast(DebinInstance, cls())
        match convert_endian_str(endian):
            case ">":
                return instance.read_be(buffer, offset)
            case "<":
                return instance.read_le(buffer, offset)
            case _:
                return instance.read(buffer, offset)
    
    else:
        raise ValueError(f"Unsupported type: {cls.__name__}")
    
    
    