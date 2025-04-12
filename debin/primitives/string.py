from typing import Tuple


class nullstr:
    """Represents a null-terminated ASCII string."""

    @classmethod
    def read(cls, buffer: bytearray, offset: int) -> Tuple[str, int]:
        """Read a null-terminated string from the buffer."""
        string_bytes = bytearray()
        while buffer[offset] != 0:  # Read until null terminator
            string_bytes.append(buffer[offset])
            offset += 1
        offset += 1
        return string_bytes.decode("ascii"), offset

    @classmethod
    def write(cls, buffer: bytearray, offset: int, value: str) -> int:
        """Write a null-terminated string to the buffer."""
        string_bytes = value.encode("ascii") + b"\x00"  # Encode string and add null terminator
        buffer[offset:offset + len(string_bytes)] = string_bytes
        return offset + len(string_bytes)

    @classmethod
    def byte_size(cls) -> int:
        """Return the size of the null-terminated string (variable length)."""
        return 1  # The null terminator is 1 byte, but we calculate length dynamically when reading

class nullwidestr:
    """Represents a null-terminated wide string (UTF-16)."""

    @classmethod
    def read(cls, buffer: bytearray, offset: int, endian: str = "<") -> Tuple[str, int]:
        """
        Read a null-terminated wide string from the buffer.
        :param endian: Byte order for UTF-16 ("<" for little-endian, ">" for big-endian).
        """
        string_bytes = bytearray()


        while True:
            # Read 2 bytes (UTF-16 character)
            char_bytes = buffer[offset:offset + 2]
            if char_bytes == b"\x00\x00":  # Null terminator (2 bytes)
                break
            string_bytes.extend(char_bytes)
            offset += 2

        offset += 2  # Skip the null terminator (2 bytes)
        return string_bytes.decode(f"utf-16-{endian}"), offset

    @classmethod
    def write(cls, buffer: bytearray, offset: int, value: str) -> int:
        """Write a null-terminated wide string to the buffer."""
        string_bytes = value.encode("utf-16") + b"\x00\x00"  # Encode string and add null terminator (2 bytes)
        
        buffer[offset:offset + len(string_bytes)] = string_bytes
        return offset + len(string_bytes)
