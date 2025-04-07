from typing import Any, Type, get_origin, get_args
from dataclasses import fields, is_dataclass


from debin.primitives.numerical import *
from debin.primitives.string import *
from debin.protocol import DebinInstance
from debin.utils.enum import is_debin_enum
from functools import lru_cache






@lru_cache(maxsize=256)
def calc_primitive_type_size(field_type: Type[Any]) -> int:
    """Calculate the size of a primitive type"""
    if field_type is uint8: return 1
    if field_type is uint16: return 2
    if field_type is uint32: return 4
    if field_type is uint64: return 8
    if field_type is nullstr: return 1
    

    if isinstance(field_type, type) and issubclass(field_type, BasePrimitiveType):
        return field_type.byte_size()


    if get_origin(field_type) is list:
        element_type = get_args(field_type)[0]
        if isinstance(element_type, type) and issubclass(element_type, BasePrimitiveType):
            return element_type.byte_size()
        raise TypeError(f"Unsupported list element type: {element_type}")

    raise TypeError(f"Unsupported field type: {field_type}")

def calc_dataclass_size(instance: DebinInstance) -> int:
    """Calculate the total size of a dataclass instance based on its fields and metadata."""

    #print(f"Calculating size for {instance.__class__.__name__}")
    total_size = 0

    for field in fields(instance):
        field_type = field.type
        field_size = 0

        align_before = field.metadata.get("align_before", None)
        if align_before:
            align_mask = align_before - 1
            total_size = (total_size + align_mask) & ~align_mask


    
        if is_debin_enum(field_type):
            repr_type = field_type._debin_repr
            field_size = calc_primitive_type_size(repr_type)
            total_size += field_size

        if get_origin(field_type) is list:  # If it's a list
            element_type = get_args(field_type)[0]
            values = getattr(instance, field.name, ())

            if element_type is nullstr:
                field_size = sum(map(len, map(str, values)))
                total_size += field_size

            if is_dataclass(element_type):
                field_size = sum(calc_dataclass_size(item) for item in values)
                total_size += field_size
            else:
                field_size = len(values) * calc_primitive_type_size(element_type)
                total_size += field_size

        elif is_dataclass(field_type):  # If it's a nested dataclass
            nested_instance = getattr(instance, field.name, None)
            if nested_instance is not None:
                field_size = calc_dataclass_size(nested_instance)
                total_size += field_size

        else:  # Normal primitive type
            field_size = calc_primitive_type_size(field_type)
            total_size += field_size
          


        if 'pad_after' in field.metadata:
            total_size += field.metadata['pad_after']

        align_after = field.metadata.get("align_after", None)
        if align_after:
            align_mask = align_after - 1
            total_size = (total_size + align_mask) & ~align_mask

    return total_size
