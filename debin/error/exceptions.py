# src/error/exceptions.py

class BinaryParsingError(Exception):
    """Base class for all binary parsing errors."""
    pass

class InvalidBufferError(BinaryParsingError):
    """Raised when the buffer is invalid or insufficient for parsing."""
    def __init__(self, message="Invalid or insufficient buffer for parsing"):
        super().__init__(message)

class UnsupportedTypeError(BinaryParsingError):
    """Raised when an unsupported field type is encountered."""
    def __init__(self, field_type, message="Unsupported field type"):
        super().__init__(f"{message}: {field_type}")

class ValidationError(BinaryParsingError):
    """Raised when a field fails validation."""
    def __init__(self, field_name, message="Field validation failed"):
        super().__init__(f"{message}: {field_name}")

class AlignmentError(BinaryParsingError):
    """Raised when alignment requirements are not met."""
    def __init__(self, alignment, message="Alignment requirements not met"):
        super().__init__(f"{message}: alignment={alignment}")

class MagicError(BinaryParsingError):
    """Raised when the magic bytes do not match."""
    def __init__(self, expected, actual, message="Magic bytes do not match"):
        super().__init__(f"{message}: expected={expected}, actual={actual}")
