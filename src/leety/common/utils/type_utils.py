from typing import Type, Union, get_args, get_origin


def is_type_optional(type_hint: Type) -> bool:
    if get_origin(type_hint) is Union:
        return type(None) in get_args(type_hint)
    
    return False
