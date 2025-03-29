from typing import Optional, Type, cast
from debin.protocol import DebinInstance, T


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
    instance = cast(DebinInstance, cls()) 

    match convert_endian_str(endian):
        case ">":
            parsed = instance.read_be(buffer, offset)
            return parsed
        case "<":
            parsed = instance.read_le(buffer, offset)
            return parsed
        case _:
            parsed = instance.read(buffer, offset)
            return parsed
    
    