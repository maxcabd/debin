from enum import Enum, auto
from typing import Union, Tuple, Callable

class SeekFrom(Enum):
    START = 0    # Seek from start of buffer
    CURRENT = 1  # Seek from current position
    END = 2      # Seek from end of buffer



# Type alias for seek specifications
SeekSpec = Union[
    int,                           # Absolute position
    Tuple[SeekFrom, int],          # (Origin, offset)
    str,                           # Field name reference
    Callable[[bytearray, int], int] # Callable that computes offset
]
