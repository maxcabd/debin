from typing import List
from debin import *



def bytes_to_trimmed_string(x: List[uint8]) -> str:
    """Convert a byte array to a UTF-8 string and trim trailing null bytes."""
    arr = bytearray(x)
    return arr.decode("utf-8").rstrip("\x00")

@debin
class Entry:
    raw_bytes: List[uint8] = field(metadata={"count": 8}, repr=False)  # Read exactly 8 bytes
    characode: str = field(metadata={"ignore": True, "map": lambda x: bytes_to_trimmed_string(x.raw_bytes)})

@debin
class Characode:
    entry_count: uint32
    entries: List[Entry] = field(metadata={"count": "entry_count"})

def main():
    with open("characode.binary", "rb") as f:
        buffer = f.read()

    characode = Characode().read(buffer)



if __name__ == "__main__":
    main()
