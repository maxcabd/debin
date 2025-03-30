from typing import List

from debin import *
from debin.helpers import until_eof




@debin
class XfbinChunk:
    size: uint32
    chunk_map_index: uint32

    version: uint16 = field(metadata={"pad_after": 2})

    data: List[uint8] = field(metadata={"count": "size"})



@debin
class XfbinChunkMap:
    chunk_type_index: uint32
    filepath_index: uint32
    chunk_name_index: uint32

@debin
class XfbinChunkReference:
    chunk_name_index: uint32
    chunk_map_index: uint32



@debin
class XfbinIndex:
    chunk_table_size: uint32
    min_page_size: uint32

    version: uint16
    padding: List[uint8] = field(metadata={"count": 2})

    chunk_type_count: uint32
    chunk_type_size: uint32

    filepath_count: uint32
    filepath_size: uint32

    chunk_name_count: uint32
    chunk_name_size: uint32

    chunk_map_count: uint32
    chunk_map_size: uint32

    chunk_map_indices_count: uint32
    references_count: uint32

    chunk_types: List[nullstr] = field(metadata={"count": "chunk_type_count"})
    filepaths: List[nullstr] = field(metadata={"count": "filepath_count"})
    chunk_names: List[nullstr] = field(metadata={"count": "chunk_name_count", "align_after": 4})

    chunk_maps: List[XfbinChunkMap] = field(metadata={"count": "chunk_map_count"})
    chunk_references: List[XfbinChunkReference] = field(metadata={"count": "references_count"})
    chunk_map_indices: List[uint32] = field(metadata={"count": "chunk_map_indices_count"})



@debin
class XfbinHeader:
    magic: uint32
    version: uint32
    encrypted: uint16
    padding: List[uint8] = field(metadata={"count": 6})


@debin
class XfbinFile:
    header: XfbinHeader
    index: XfbinIndex
    chunks: List[XfbinChunk] = field(metadata={"parse_with": until_eof})




def main():
    with open("sample.xfbin", "rb") as f:
        buffer = f.read()

    xfbin = XfbinFile().read_be(buffer)




if __name__ == "__main__":
    main()
