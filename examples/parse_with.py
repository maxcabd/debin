from typing import List, Type, TypeVar
from dataclasses import field, is_dataclass
from debin import debin
from debin.primitives.numerical import uint8, uint16, uint32
from debin.binary_parser import BinaryParser
from debin.helpers import until_eof
from debin.utils.size import calc_dataclass_size



@debin
class Header:
    magic: uint32
    version: uint32

@debin
class Chunk:
    size: uint32
    index: uint32
    version: uint32
    data: List[uint8] = field(metadata={"count": "size"})

@debin
class ParseWithExample:
    header: Header
    chunks: List[Chunk] = field(metadata={"parse_with": until_eof})


def main():
    buffer = bytearray([
            # Header
            0x45, 0x47, 0x48, 0x45,  # size = 4
            0x00, 0x00, 0x00, 0x99,

            # Chunk 1
            0x04, 0x00, 0x00, 0x00,  # size = 4
            0x00, 0x00, 0x00, 0x01,  # chunk_map_index = 1
            0x02, 0x00, 0x00, 0x00,                    # version = 2
            0x01, 0x02, 0x03, 0x04,  # data = [1, 2, 3, 4]

            # Chunk 2
            0x02, 0x00, 0x00, 0x00,  # size = 2
            0x03, 0x00, 0x00, 0x00,  # chunk_map_index = 3
            0x00, 0x04, 0x00, 0x00,           # version = 4
            0x05, 0x06,          # data = [5, 6]

            # Chunk 3
            0x03, 0x00, 0x00, 0x00,  # size = 2
            0x02, 0x00, 0x00, 0x00,  # chunk_map_index = 3
            0x00, 0x04, 0x00, 0x00,           # version = 4
            0x07, 0x08, 0x09           # data = [5, 6]
        ])


    example = ParseWithExample().read_le(buffer)


    print(example)





if __name__ == "__main__":
    main()
