from typing import TypeVar, Generic, Protocol, runtime_checkable

T = TypeVar("T", int, float)

@runtime_checkable
class PrimitiveType(Protocol[T]):
    """A protocol defining a primitive numerical type with a byte size method."""

    value: T

    def __add__(self, other: object) -> "PrimitiveType[T]": ...
    def __sub__(self, other: object) -> "PrimitiveType[T]": ...
    def __mul__(self, other: object) -> "PrimitiveType[T]": ...
    def __truediv__(self, other: object) -> "PrimitiveType[T]": ...
    def __int__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...

    @classmethod
    def byte_size(cls) -> int:
        """Return the size of this type in bytes."""
        ...


class BasePrimitiveType(Generic[T]):
    def __init__(self, value: T = 0):
        self.value: T = value

    def __add__(self, other: object) -> "BasePrimitiveType[T]":
        return self.__class__(self.value + self._get_value(other))

    def __sub__(self, other: object) -> "BasePrimitiveType[T]":
        return self.__class__(self.value - self._get_value(other))

    def __mul__(self, other: object) -> "BasePrimitiveType[T]":
        return self.__class__(self.value * self._get_value(other))
    
    def __truediv__(self, other: object) -> "BasePrimitiveType[T]":
        result = self.value / self._get_value(other)
      
        if isinstance(self.value, int):
            result = int(result)
        return self.__class__(result)

    def __int__(self) -> int:
        return int(self.value)

    def __eq__(self, other: object) -> bool:
        return self.value == self._get_value(other)

    def __hash__(self) -> int:
        return hash(self.value)

    def _get_value(self, other: object) -> T:
        if isinstance(other, BasePrimitiveType):
            return other.value
        elif isinstance(other, (int, float)):
            return int(other)
        else:
            raise TypeError(f"Unsupported operand type(s) for '{self.__class__.__name__}' and '{type(other).__name__}'")

    @classmethod
    def byte_size(cls) -> int:
        """Return byte size for different primitive types."""
        size_map = {
            "uint8": 1, "int8": 1,
            "uint16": 2, "int16": 2,
            "uint32": 4, "int32": 4,
            "uint64": 8, "int64": 8,
            "float16": 2, "float32": 4, "float64": 8
        }
        return size_map.get(cls.__name__, 4)  # Default to 4 bytes if unknown

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


# --- Concrete Primitive Types ---
class uint8(BasePrimitiveType[int]): pass
class int8(BasePrimitiveType[int]): pass
class uint16(BasePrimitiveType[int]): pass
class int16(BasePrimitiveType[int]): pass
class uint32(BasePrimitiveType[int]): pass
class int32(BasePrimitiveType[int]): pass
class uint64(BasePrimitiveType[int]): pass
class int64(BasePrimitiveType[int]): pass
class float16(BasePrimitiveType[float]): pass
class float32(BasePrimitiveType[float]): pass
class float64(BasePrimitiveType[float]): pass