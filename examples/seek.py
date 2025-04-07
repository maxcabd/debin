from typing import List
from debin import *



@debin
class FileHeader:
    file_size: int32
    data_start: int32
    
    # Seek to data_start position before reading payload
    payload: List[uint8] = field(metadata={"seek": 'data_start', "count": 8})
    
    # Seek to 4 bytes before end to read checksum
    checksum: int32 = field(metadata={
        "seek_before": (SeekFrom.END, -4)
    })

def main():
    buffer = bytearray([
        0x00, 0x00, 0x00, 0x20,
      
        0x00, 0x00, 0x00, 0x10,
       
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
       
        0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
     
        0xFF, 0xEE, 0xDD, 0xCC
    ])

    header = FileHeader().read_be(buffer)
    
    print(header) # FileHeader(file_size=32, data_start=16, payload=[1, 2, 3, 4, 5, 6, 7, 8], checksum=-1122868)
    
    

if __name__ == "__main__":
    main()