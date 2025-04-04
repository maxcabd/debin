from typing import List
from dataclasses import dataclass, field
from debin import *

# Simple test buffer: [condition_flag, element_count, value1, value2, ...]
test_buffer = bytearray([
    1,       # condition_flag (True)
    3,      # element_count
    10, 20, 30,  # list values
    4 # int
   
])

@debin
class Nest:
    var: uint8

@debin
class TestStruct:
    condition_flag: uint8
    element_count: uint8  # Placed after to test forward reference
    numbers: List[Nest] = field(
        metadata={
            "if": lambda self: self.condition_flag == 1,
            "count": "element_count" 
        }
    )
    var: uint8
    

def test_if_dir_with_list():
    parsed = TestStruct().read_le(test_buffer)
    print(f"Full parse result: {parsed}")
    
    print(f"Parsed value: {parsed.numbers}")  # Should be [10, 20, 30]
   
    
    # Full parse test
    

if __name__ == "__main__":
    test_if_dir_with_list()