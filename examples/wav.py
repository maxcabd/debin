from typing import List


from debin import *
from debin.helpers import until_eof

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
    data: DataChunk

    total_samples: int = field(metadata={"ignore": True, "calc": "data.subchunk_size // fmt.block_align"})


# 🚀 Usage Example
def main():
    with open("sample.wav", "rb") as f:
        buffer = bytearray(f.read())

    wav = WAVFile().read_le(buffer)

  

if __name__ == "__main__":
    main()
