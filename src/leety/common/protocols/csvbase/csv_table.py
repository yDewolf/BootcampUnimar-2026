from types import get_original_bases
from typing import Any, Optional, TypeVar, get_args, get_origin
import uuid

from leety.common.protocols.field.default_fields import IndexableFieldModel
from leety.common.protocols.field.field_model import Field, FieldModel


class Table[model: FieldModel]:
    _rows: list[model]
    _model_cls: type[FieldModel]

    _unique_columns: dict[str, set[Any]]

    def __init__(self):
        self._rows = []
        self._unique_columns = {
            key: set() for key in self._model_cls._unique_fields
        }

    @classmethod
    def model_cls(cls) -> type[model]:
        # pylance vai ter que confiar em mim aqui
        return cls._model_cls # type: ignore

    @property
    def rows(self) -> list[model]:
        return self._rows

    # Isso aqui é necessário para caso for usar algo tipo:
    # class UserTable(Table[UserModel]): ...
    # assim ele vai atribuir o _model_cls para UserModel
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for base in get_original_bases(cls):
            origin = get_origin(base) or base
            if not issubclass(origin, Table):
                continue

            args = get_args(base)
            if args and isinstance(args[0], type) and issubclass(args[0], FieldModel):
                cls._model_cls = args[0]
                break

    # Esse pedaço aqui é para criar uma classe anônima quando usar algo do tipo:
    # user_table = Table[UserModel]()
    # aí a classe criada vai ser Table_UserModel e terá o _model_cls = UserModel
    def __class_getitem__(cls, model_cls: type[FieldModel]):
        if isinstance(model_cls, TypeVar):
            return super().__class_getitem__(model_cls)
        
        if not isinstance(model_cls, type) or not issubclass(model_cls, FieldModel):
            raise TypeError(f"Generic type for 'model' should inherit {FieldModel}")

        subclass = type(
            f"Table_{model_cls.__name__}",
            (cls,),
            {"_model_cls": model_cls}
        )
        return subclass

    @classmethod
    def get_headers(cls) -> tuple[str, ...]:
        return cls._model_cls.header_keys()

    def add_row(self, row: model, check_duplicate: bool = True) -> int:
        if not isinstance(row, self._model_cls):
            raise TypeError(f"Row should be of type: {self._model_cls.__name__}")

        if check_duplicate:
            if row in self._rows: 
                raise Exception(f"Row already exists in table {self.__class__.__name__}: {self}")

        self._validate_unique_columns(row)
        row._table_ref = self

        self._rows.append(row)
        self._update_unique_columns(row)

        return len(self._rows) - 1 # index do row que acabou de ser adicionado

    def remove_row(self, row: model):
        row._table_ref = None
        self._rows.remove(row)
        self._discard_unique_columns(row)

    def _validate_unique_columns(self, new_row: model):
        for key in self._unique_columns:
            value = getattr(new_row, key, None)
            if value == None: continue
            if value in self._unique_columns[key]:
                raise Exception(f"Value {value} already exists in unique column {key}")

    # TODO: implement proper way of updating this when rows are removed
    def _update_unique_columns(self, new_row: model):
        for key in self._unique_columns:
            value = getattr(new_row, key, None)
            if value == None: continue

            self._unique_columns[key].add(value)

    def _discard_unique_columns(self, removed_row: model):
        for key in self._unique_columns:
            value = getattr(removed_row, key, None)
            if value is not None:
                self._unique_columns[key].discard(value)

    # Chamado pelo Field quando field_model.field = <value>
    def _swap_unique_value(self, field_name: str, old_value: Any, new_value: Any):
        if new_value == old_value:
            return

        if new_value is not None and new_value in self._unique_columns[field_name]:
            raise ValueError(f"Value {new_value} already exists in unique column {field_name}")

        if old_value is not None:
            self._unique_columns[field_name].discard(old_value)
        
        if new_value is not None:
            self._unique_columns[field_name].add(new_value)


    def to_csv_str(self) -> str:
        header_str = ",".join(self.model_cls().header_keys())
        value_strings = [row.to_csv_str(include_header=False) for row in self._rows]

        return f"{header_str}\n{"\n".join(value_strings)}"

class IndexableTable[model: IndexableFieldModel](Table[model]):
    _table_index: dict[str, model]
    _last_inserted_int_id: int

    def __init__(self):
        self._table_index = {}
        self._last_inserted_int_id = 0
        super().__init__()

    def add_row(self, row: model) -> None:
        if row.id == None:
            self._auto_set_id(row)

        if str(row.id) in self._table_index:
            raise Exception(f"A row with id={row.id} already exists inside table {self.__class__.__name__}: {self}")

        last_idx = super().add_row(row)
        self._table_index[str(row.id)] = row
        self._update_last_id(row)
    
    def remove_row(self, row: model):
        row_id = str(row.id)
        if row_id in self._table_index:
            del self._table_index[row_id]

        if row in self._rows:
            super().remove_row(row)

    def remove_row_id(self, row_id: str | int):
        row = self._table_index.get(str(row_id), None)
        if row: self.remove_row(row)

    def get_by_id(self, row_id: str | int) -> Optional[model]:
        return self._table_index.get(str(row_id))


    def _update_last_id(self, row: model):
        if type(row.id) is int:
            self._last_inserted_int_id = max(row.id, self._last_inserted_int_id)

    def _auto_set_id(self, row: model):
        id_field: Field = row.__class__.id
        id_type = id_field._type_hint

        if id_type is int:
            self._auto_int_id(row)
        elif id_type is str:
            self._auto_str_id(row)
        else: 
            self._auto_int_id(row)


    def _auto_int_id(self, row: model):
        new_id = self._last_inserted_int_id + 1
        # FIXME: espero que isso aqui não cause loops muito longos
        while str(new_id) in self._table_index:
            new_id += 1

        row.id = new_id
        
    # isso aqui é meio placeholder
    def _auto_str_id(self, row: model):
        new_id = str(uuid.uuid4())
        while new_id in self._table_index:
            new_id = str(uuid.uuid4())
        
        row.id = new_id
