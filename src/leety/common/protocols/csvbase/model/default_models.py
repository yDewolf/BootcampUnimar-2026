from typing import Optional, Type, get_origin, get_type_hints

from leety.common.protocols.csvbase.model.field_model import Field, FieldModel

class IdField[idType: Optional[str | int]](Field[idType]):
    def __init__(self, default: idType | None = None, frozen: bool = False, id: str = "", value_type_hint: type[idType] | None = None):
        super().__init__(default, id, frozen, value_type_hint=value_type_hint)

class IndexableFieldModel[idType: str | int](FieldModel):
    id: IdField[Optional[idType]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        hints = get_type_hints(cls)
        id_fields: list[str] = []
        for key in cls.header_keys():
            hint = hints[key]
            origin = get_origin(hint) or hint
            if issubclass(origin, IdField):
                id_fields.append(key)

        if len(id_fields) > 1:
            raise Exception(f"ERROR in {cls.__name__}: {IndexableFieldModel.__name__}s should contain only one {IdField.__name__}")
