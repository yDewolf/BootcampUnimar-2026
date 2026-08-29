from types import get_original_bases
from typing import Any, Generic, Optional, Type, get_args, get_origin, get_type_hints, overload, override

from leety.common.protocols.csvbase.model.field_model import Field, FieldModel
from leety.common.utils.type_utils import get_attributes_of_type


class SearchableField[valueType: Any](Field[valueType]):
    @overload
    def __get__(self, instance: None, owner: type) -> "SearchableField[valueType]": ...

    @overload
    def __get__(self, instance: Any, owner: type) -> valueType: ...

    @override
    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

class IdField[idType: Optional[str | int]](SearchableField[idType]):
    def __init__(self, default: idType | None = None, frozen: bool = False, id: str = "", value_type_hint: type[idType] | None = None):
        super().__init__(default, id, frozen, value_type_hint=value_type_hint)

class IndexableFieldModel[idType: str | int](FieldModel):
    id: IdField[Optional[idType]]
    _searchables: tuple[str, ...] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        id_fields = get_attributes_of_type(cls, IdField)
        if len(id_fields) > 1:
            raise Exception(f"ERROR in {cls.__name__}: {IndexableFieldModel.__name__}s should contain only one {IdField.__name__}")

        cls._setup_searchables()

    @classmethod
    def _get_type_hints(cls):
        hints = super()._get_type_hints()
        bases = get_original_bases(cls)
        id_type_hint = (str | int)
        for base in bases:
            # if issubclass(base, IndexableFieldModel):
            args = get_args(base)
            if args:
                if not isinstance(args[0], type): continue
                id_type_hint = args[0]

        hints["id"] = IdField[Optional[id_type_hint]]
        return hints
        

    @classmethod
    def _setup_searchables(cls):
        searchable_fields = get_attributes_of_type(cls, SearchableField, exclude=IdField)
        cls._searchables = tuple(searchable_fields)

    @classmethod
    def searchable_fields(cls) -> tuple[str, ...]:
        return cls._searchables