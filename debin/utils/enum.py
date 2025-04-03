from enum import Enum, IntEnum, IntFlag, Flag


def is_debin_enum(cls):
    """
    Similar to is_dataclass method except for Enums to check if class is an Enum
    """
    return (isinstance(cls, type) and 
           (issubclass(cls, IntEnum) or issubclass(cls, IntFlag)) and 
           hasattr(cls, '_debin_repr'))