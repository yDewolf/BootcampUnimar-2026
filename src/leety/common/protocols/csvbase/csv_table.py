from types import get_original_bases
from typing import get_args, get_origin

from leety.common.protocols.field.field_model import FieldModel


class Table[model: FieldModel]:
    _rows: list[model]
    _model_cls: type[FieldModel]

    def __init__(self):
        self._rows = []

    @property
    def rows(self) -> list[model]:
        return self._rows

    # Isso aqui é necessário para caso for usar algo tipo:
    # class UserTable(Table[UserModel]): ...
    # assim ele vai atribuir o _model_cls para UserModel
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for base in get_original_bases(cls):
            origin = get_origin(base)
            if issubclass(origin, Table):
                args = get_args(base)
                if args and isinstance(args[0], type) and issubclass(args[0], FieldModel):
                    cls._model_cls = args[0]
                    break

    # Esse pedaço aqui é para criar uma classe anônima quando usar algo do tipo:
    # user_table = Table[UserModel]()
    # aí a classe criada vai ser Table_UserModel e terá o _model_cls = UserModel
    def __class_getitem__(cls, model_cls: type[FieldModel]):
        if not isinstance(model_cls, type) or not issubclass(model_cls, FieldModel):
            raise TypeError(f"Generic type for 'model' should inherit {FieldModel.__class__}")

        subclass = type(
            f"Table_{model_cls.__name__}",
            (cls,),
            {"_model_cls": model_cls}
        )
        return subclass

    @classmethod
    def get_headers(cls) -> tuple[str, ...]:
        return cls._model_cls.header_keys()

    def add_row(self, row: model) -> None:
        if not isinstance(row, self._model_cls):
            raise TypeError(f"Row should be of type: {self._model_cls.__name__}")
    
        self._rows.append(row)


class TableIndexer:
    pass
