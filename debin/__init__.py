# debin/__init__.py

# Expose helpers, types, and utility functions directly
from .helpers import *  # Exposes helpers
from .protocol import *  # Exposes protocol-related components
from .core import *  # Exposes core components like BinaryParser and StructReader, and IO
from .decorators import *  # Exposes all decorators and meta
from .primitives import *  # Exposes all primitives (numerical and string types)
from .utils import *  # Exposes utilities like endian, size, and state
from .error import *  # Exposes exceptions and error handling


from dataclasses import field  # Expose field from dataclasses





# Define what gets imported with `from debin import *`
__all__ = [
    "debin",
    "uint64",
    "uint32",
    "uint16",
    "uint8",
    "int64",
    "int32",
    "int16",
    "int8",
    "float64",
    "float32",
    "float16",
    "nullstr",
    "field",
    "BinaryParser",
    "SeekFrom"
]