from typing import List

from debin import uint8, uint16, uint32
from debin import *
from debin.helpers import until_eof

@debin(magic="RIFF")
class RiffHeader:
    chunk_size: uint32
    format: List[uint8] = field(metadata={"count": 4})

@debin
class ChunkHeader:
    chunk_id: List[uint8] = field(metadata={"count": 4})
    chunk_size: uint32

@debin(magic="fmt ")
class FmtChunk:
    chunk_header: ChunkHeader
    audio_format: uint16
    num_channels: uint16
    sample_rate: uint32
    byte_rate: uint32
    block_align: uint16
    bits_per_sample: uint16
    extra_params: List[uint8] = field(
        metadata={
            "if": lambda self: self.chunk_header.chunk_size > 16,
            "count": "chunk_header.chunk_size - 16"
        }
    )
@debin(magic="data")
class DataChunk:
    chunk_header: ChunkHeader
    samples: List[uint8] = field(metadata={"count": "chunk_header.chunk_size"})



@debin
class WAVFile:
    riff: RiffHeader
    fmt: FmtChunk
    data: DataChunk

    total_samples: int = field(metadata={"ignore": True, "calc": "data.subchunk_size // fmt.block_align"})


def main():
    with open("sample.wav", "rb") as f:
        buffer = bytearray(f.read())

    wav = WAVFile().read_be(buffer)

  

if __name__ == "__main__":
    main()
