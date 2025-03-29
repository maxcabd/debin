from debin import debin
from dataclasses import dataclass, field
from typing import List
from debin.primitives.numerical import uint8, uint16, uint32

@debin(endian="big")
class OBDHeader:
    identifier: uint16
    length: uint8
    timestamp: uint32

@debin(endian="big")
class EngineData:
    rpm: uint16  # Engine RPM
    speed: uint8  # Vehicle speed
    throttle_position: uint8  # Throttle position (%)
    engine_load: uint8

@debin(endian="big")
class OBDPacket:
    header: OBDHeader
    data: EngineData


def main():
    # Example buffer
    buffer = bytearray([
        0x01, 0x02,  # Identifier
        0x08,        # Length
        0x00, 0x00, 0x00, 0x3C,  # Timestamp (aligned)
        0x0F, 0xA0,  # RPM (4000)
        0x50,        # Speed (80 km/h)
        0x64,        # Throttle position (100%)
        0x30,        # Engine load (48%)
        0x00, 0x00   # Padding
    ])

    obd_packet = OBDPacket().read(buffer)
    print(obd_packet)


if __name__ == "__main__":
    main()
