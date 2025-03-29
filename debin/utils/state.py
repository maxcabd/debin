from dataclasses import is_dataclass
from typing import ClassVar, Dict, Protocol, Any, runtime_checkable

@runtime_checkable
class DataclassInstance(Protocol):
    """Dataclass interface for static type checking"""
    __dataclass_fields__: ClassVar[Dict[str, Any]] 

class This:
    """Proxy object for accessing the current struct's fields dynamically, including nested fields."""
    def __init__(self, instance):
        self._instance = instance

    def __getattr__(self, name):
        # Split the attribute path (e.g., "header.count" -> ["header", "count"])
        parts = name.split(".")
        value = self._instance


        for part in parts:
            value = getattr(value, part)

        # If the value is a nested dataclass, wrap it in a `This` object
        if is_dataclass(value):
            return This(value)

        return value



