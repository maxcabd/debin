from typing import List
from debin import *
from debin.helpers import until_with



    

@debin
class Entry:
    value: int32

@debin
class Container:
    entries: List[Entry] = field(metadata={
        "parse_with": until_with(lambda e: e.value == 0)
    })


def main():
    buffer = bytes([
    0x7b, 0x00, 0x00, 0x00,  # 123
    0xc8, 0x01, 0x00, 0x00,  # 456
    0x00, 0x00, 0x00, 0x00   # 0 (terminator)
    ])

    container = Container().read_le(buffer) 

  

if __name__ == "__main__":
    main()

