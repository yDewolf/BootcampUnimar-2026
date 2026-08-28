from typing import Type, Union, get_args, get_origin, get_type_hints


def is_type_optional(type_hint: Type) -> bool:
    if get_origin(type_hint) is Union:
        return type(None) in get_args(type_hint)
    
    return False

def get_attributes_of_type(cls: type, target_types: tuple[type] | type) -> tuple[str, ...]:
    hints = get_type_hints(cls)
    attributes: list[str] = []
    for key, type_hint in hints.items():
        origin = get_origin(type_hint) or type_hint
        if issubclass(origin, target_types):
            attributes.append(key)

    return tuple(attributes)
