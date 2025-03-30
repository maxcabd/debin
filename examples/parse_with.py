from typing import List


from debin import *
from debin.helpers import until_eof


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
            0x45, 0x47, 0x48, 0x45,  
            0x00, 0x00, 0x00, 0x99,

            # Chunk 1
            0x04, 0x00, 0x00, 0x00, 
            0x00, 0x00, 0x00, 0x01,  
            0x02, 0x00, 0x00, 0x00,                   
            0x01, 0x02, 0x03, 0x04, 

            # Chunk 2
            0x02, 0x00, 0x00, 0x00,  
            0x03, 0x00, 0x00, 0x00,  
            0x00, 0x04, 0x00, 0x00,          
            0x05, 0x06,         

            # Chunk 3
            0x03, 0x00, 0x00, 0x00, 
            0x02, 0x00, 0x00, 0x00, 
            0x00, 0x04, 0x00, 0x00,          
            0x07, 0x08, 0x09           
        ])


    example = ParseWithExample().read_le(buffer)


   
if __name__ == "__main__":
    main()
