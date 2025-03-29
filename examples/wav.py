from typing import List

from debin import debin
from dataclasses import dataclass, field
from debin.primitives.numerical import uint8, uint16, uint32
from debin.primitives.string import nullstr

@debin(magic="RIFF")
class RiffHeader:
    chunk_size: uint32
    format: List[uint8] = field(metadata={"count": 4})

@debin(magic="fmt ")
class FMTChunk:
    sub_chunk_size: uint32
    audio_format: uint16
    num_channels: uint16
    sample_rate: uint32
    byte_rate: uint32
    block_align: uint16
    bits_per_sample: uint16

@debin(magic="data")
class DataChunk:
    sub_chunk_size: uint32
    samples: List[uint8] = field(metadata={"count": "sub_chunk_size"})


@debin
class WAVFile:
    riff: RiffHeader
    fmt: FMTChunk
    #data: DataChunk

    #total_samples: int = field(metadata={"ignore": True, "calc": "data.subchunk_size // fmt.block_align"})


# 🚀 Usage Example
def main():
    with open("4.wav", "rb") as f:
        buffer = bytearray(f.read())

    wav = WAVFile().read_le(buffer)

    print(f"Format: {wav.fmt.audio_format}")
    print(f"Channels: {wav.fmt.num_channels}")
    print(f"Sample Rate: {wav.fmt.sample_rate}")
    print(f"Bits per Sample: {wav.fmt.bits_per_sample}")
    #print(f"Total Samples: {wav.total_samples}")

if __name__ == "__main__":
    main()
