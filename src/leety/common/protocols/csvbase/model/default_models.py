from typing import Any, Optional, Type, get_origin, get_type_hints

from leety.common.protocols.csvbase.model.field_model import Field, FieldModel
from leety.common.utils.type_utils import get_attributes_of_type


class SearchableField[valueType: Any](Field[valueType]):
    pass

class IdField[idType: Optional[str | int]](SearchableField[idType]):
    def __init__(self, default: idType | None = None, frozen: bool = False, id: str = "", value_type_hint: type[idType] | None = None):
        super().__init__(default, id, frozen, value_type_hint=value_type_hint)

class IndexableFieldModel[idType: str | int](FieldModel):
    id: IdField[Optional[idType]]
    _searchables: tuple[str, ...]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        id_fields = get_attributes_of_type(cls, IdField)
        if len(id_fields) > 1:
            raise Exception(f"ERROR in {cls.__name__}: {IndexableFieldModel.__name__}s should contain only one {IdField.__name__}")

        cls._setup_searchables()

    @classmethod
    def _setup_searchables(cls):
        searchable_fields = get_attributes_of_type(cls, SearchableField)
        cls._searchables = tuple(searchable_fields)


    # @classmethod
    # def main_id(cls) -> IdField[Optional[idType]]:
    #     return cls.id # type: ignore


    @classmethod
    def searchable_fields(cls) -> tuple[str, ...]:
        return cls._searchables