#! Helper functions for reading and writing data.
from typing import List, Type
from dataclasses import is_dataclass

from debin.core.binary_parser import BinaryParser
from debin.utils.size import calc_dataclass_size
from debin.utils.endian import read_from_endian
from debin.protocol import DebinInstance, T




def until_eof(buffer: bytes, offset: int, parser: BinaryParser, cls: Type[T]) -> tuple[List[DebinInstance], int]:
    """
    Custom parser function that reads data until the end of the buffer.
    It parses each chunk dynamically based on its own size.
    """
    values: List[DebinInstance] = []
    cur_offset = offset


    while cur_offset < len(buffer):
        if is_dataclass(cls):
            parsed = read_from_endian(cls, parser.endian, buffer, cur_offset)
            
            if parsed is None:
                break

            values.append(parsed)
            cur_offset += calc_dataclass_size(parsed)

    return values, cur_offset
