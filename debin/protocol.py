from typing import Protocol, TypeVar, Optional, ClassVar, Dict, Any, runtime_checkable


T = TypeVar('T')

@runtime_checkable
class DebinInstance(Protocol):
    """Protocol for debin classes that can be read from binary data."""
    __dataclass_fields__: ClassVar[Dict[str, Any]]  # For dataclass compatibility
    def read(self, buffer: bytes, offset: int) -> 'DebinInstance':
        ...
    
    def read_le(self, buffer: bytes, offset: int) -> 'DebinInstance':
        ...
    
    def read_be(self, buffer: bytes, offset: int) -> 'DebinInstance':
        ...