from typing import List

from debin import *
from enum import IntFlag, IntEnum


@debin(repr=uint8)
class Flags(IntFlag):
    FIN = 0x01    # 1
    SYN = 0x02    # 2
    RST = 0x04    # 4
    PSH = 0x08    # 8
    ACK = 0x10    # 16
    URG = 0x20    # 32
    ECE = 0x40    # 64
    CWR = 0x80    # 128

    def __str__(self):
        return self.name  # Use the auto-generated name

   



class Flag2(IntFlag):
    FIN = 0x01    # 1
    SYN = 0x02    # 2
    RST = 0x04    # 4
    PSH = 0x08    # 8
    ACK = 0x10    # 16
    URG = 0x20    # 32
    ECE = 0x40    # 64
    CWR = 0x80    # 128


@debin
class TCPHeader:
    source_port: uint16
    destination_port: uint16
    sequence_number: uint32
    acknowledgment_number: uint32
    flags: Flags = field(metadata={"repr": True})
    window_size: uint16

@debin
class TCPPacket:
    header: TCPHeader
    payload: List[uint8] = field(metadata={"count": lambda self: self.header.window_size})



def main():
    # Example TCP packet buffer
    buffer = bytearray([
        # Header (20 bytes)
        0x30, 0x39,  # Source Port (12345)
        0x1F, 0x90,  # Destination Port (8080)
        0x00, 0x00, 0x00, 0x01,  # Sequence Number (1)
        0x00, 0x00, 0x00, 0x02,  # Acknowledgment Number (2)
        0x12,  # Flags (SYN=0x02, ACK=0x10 → SYN+ACK=0x12)
        0x00, 0x08,  # Window Size (8192)

        # Payload (8 bytes)
        0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x21, 0x0A, 0x00  # "Hello!\n\0"
    ])


    packet = TCPPacket().read(buffer)
    print(packet)
   
    

if __name__ == "__main__":
    main()
