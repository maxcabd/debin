from typing import List
from debin import *


@debin(magic="BM")
class BMPHeader:
    filesize: uint32
    reserved: uint32
    data_offset: uint32


@debin
class DIBHeader:
    header_size: uint32
    width: int32
    height: int32
    planes: uint16
    bpp: uint16
    compression: uint32
    image_size: uint32
    x_ppm: uint32
    y_ppm: uint32 
    colors_used: uint32
    important_colors: uint32


@debin
class BMPFile:
    header: BMPHeader
    dib: DIBHeader
    color_table: List[uint8] = field(metadata={
        "if": lambda self: self.dib.bpp <= 8,
        "count": lambda self: 4 * (2 ** self.dib.bpp) if self.dib.bpp <= 8 else 0
    })
    
    pixel_data: List[uint8] = field(metadata={"count": "dib.image_size"})


def main():
    with open("sample.bmp", "rb") as file:
        buffer = file.read()

    bmp = BMPFile().read_le(buffer)

    print(bmp)

    

if __name__ == "__main__":
    main()