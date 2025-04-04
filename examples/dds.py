from typing import List, Optional
from enum import IntFlag
from debin import *


@debin(repr=uint32)
class DDSPixelFormatFlags(IntFlag):
    DDPF_ALPHAPIXELS = 0x1
    DDPF_ALPHA = 0x2
    DDPF_FOURCC = 0x4
    DDPF_RGB = 0x40
    DDPF_YUV = 0x200
    DDPF_LUMINANCE = 0x20000


@debin(repr=uint32)
class DDSHeaderFlags(IntFlag):
    DDSD_CAPS = 0x1
    DDSD_HEIGHT = 0x2
    DDSD_WIDTH = 0x4
    DDSD_PITCH = 0x8
    DDSD_PIXELFORMAT = 0x1000
    DDSD_MIPMAPCOUNT = 0x20000
    DDSD_LINEARSIZE = 0x80000
    DDSD_DEPTH = 0x800000


@debin(repr=uint32)
class DDSSurfaceFlags(IntFlag):
    DDSCAPS_COMPLEX = 0x8
    DDSCAPS_MIPMAP = 0x400000
    DDSCAPS_TEXTURE = 0x1000


@debin(repr=uint32)
class DDSCubeMapFlags(IntFlag):
    DDSCAPS2_CUBEMAP = 0x200
    DDSCAPS2_CUBEMAP_POSITIVEX = 0x400
    DDSCAPS2_CUBEMAP_NEGATIVEX = 0x800
    DDSCAPS2_CUBEMAP_POSITIVEY = 0x1000
    DDSCAPS2_CUBEMAP_NEGATIVEY = 0x2000
    DDSCAPS2_CUBEMAP_POSITIVEZ = 0x4000
    DDSCAPS2_CUBEMAP_NEGATIVEZ = 0x8000
    DDSCAPS2_VOLUME = 0x200000


@debin
class DDSPixelFormat:
    size: uint32
    flags: DDSPixelFormatFlags
    four_cc: List[uint8] =  field(metadata={"count": 4})
    rgb_bit_count: uint32
    r_bit_mask: uint32
    g_bit_mask: uint32
    b_bit_mask: uint32
    a_bit_mask: uint32

@debin(endian="little")
class DDSHeader:
    size: uint32
    flags: DDSHeaderFlags
    height: uint32
    width: uint32
    pitch_or_linear_size: uint32
    depth: uint32
    mipmap_count: uint32
    reserved1: List[uint32] = field(metadata={"count": 11})
    pixel_format: DDSPixelFormat
    caps: DDSSurfaceFlags
    caps2: DDSCubeMapFlags
    caps3: uint32
    caps4: uint32
    reserved2: uint32

@debin
class DDSHeaderDX10:
    dxgi_format: uint32
    resource_dimension: uint32
    misc_flag: uint32
    array_size: uint32
    misc_flags2: uint32

@debin(magic="DDS ")
class DDSFile:
    header: DDSHeader
    dx10_header: DDSHeaderDX10 = field(metadata={
        "if": lambda self: self.header.pixel_format.four_cc == b"DX10"
    })
    texture_data: List[uint8] = field(metadata={"count": lambda self: self.header.pitch_or_linear_size})


def main():
    with open("sample.dds", "rb") as file:
        buffer = file.read()

    
    dds = DDSFile().read_le(buffer)


if __name__ == "__main__":
    main()