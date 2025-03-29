from typing import Any, Type, get_origin, get_args
from dataclasses import fields, is_dataclass

from debin.primitives.numerical import *
from debin.primitives.string import *
from debin.protocol import DebinInstance




def calc_primitive_type_size(field_type: Type[Any]) -> int:
    """Get the size of a primitive field type."""
    """if is_dataclass(field_type):
        return calc_dataclass_size(field_type)"""

    if isinstance(field_type, type) and issubclass(field_type, BasePrimitiveType):
        return field_type.byte_size()

    if field_type is nullstr:
        return 1  # Size is dynamic, but we know the null terminator is 1 byte

    if get_origin(field_type) is list:
        element_type = get_args(field_type)[0]
        if isinstance(element_type, type) and issubclass(element_type, BasePrimitiveType):
            return element_type.byte_size()
        raise TypeError(f"Unsupported list element type: {element_type}")

    raise TypeError(f"Unsupported field type: {field_type}")


def calc_dataclass_size(instance: DebinInstance) -> int:
    """Calculate the total size of a dataclass instance based on its fields and metadata."""

    print(f"Calculating size for {instance.__class__.__name__}")
    total_size = 0

    for field in fields(instance):
        field_type = field.type
        field_size = 0

        align_before = field.metadata.get("align_before", None)
        if align_before:
            align_mask = align_before - 1
            total_size = (total_size + align_mask) & ~align_mask




        if get_origin(field_type) is list:  # If it's a list
            element_type = get_args(field_type)[0]
            values = getattr(instance, field.name, [])

            if element_type is nullstr:
                # Sum the actual lengths of strings plus their null terminators
                field_size = sum(len(str(value)) for value in values)
                print(f"    String list '{field.name}' contains {len(values)} strings, total size: {field_size}")
                total_size+= field_size

            if is_dataclass(element_type):
                # Sum up the size of each nested dataclass instance
                field_size = sum(calc_dataclass_size(item) for item in values)
                total_size+= field_size
            else:
                field_size = len(values) * calc_primitive_type_size(element_type)
                print(f"    Primitive list '{field.name}' contains {len(values)} elements of size {calc_primitive_type_size(element_type)}, total: {field_size}")
                total_size+= field_size

        elif is_dataclass(field_type):  # If it's a nested dataclass
            nested_instance = getattr(instance, field.name, None)
            if nested_instance is not None:
                field_size = calc_dataclass_size(nested_instance)
                total_size+= field_size
        else:  # Normal primitive type
            field_size = calc_primitive_type_size(field_type)
            total_size+= field_size
            print(f"  Field {field.name}: {field_size} bytes (at offset {total_size})")




        if 'pad_after' in field.metadata:
            total_size += field.metadata['pad_after']

        align_after = field.metadata.get("align_after", None)
        if align_after:
            align_mask = align_after - 1
            total_size = (total_size + align_mask) & ~align_mask

    print(f"Total size for {instance.__class__.__name__}: {total_size}")
    return total_size
