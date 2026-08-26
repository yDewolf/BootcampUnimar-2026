# Estarei tentando não usar pydantic então vou tentar implementar algumas coisas que são bem úteis da biblioteca manualmente
from typing import Any, Optional, Type, Union, dataclass_transform, get_args, get_origin, get_type_hints
from leety.common.protocols.database_exceptions import FieldMissingValue
from leety.common.utils.type_utils import is_type_optional

class CSVField[valueType: Any]:
    _field_id: str
    _is_required: Optional[bool] = None
    _value: valueType
    _type_hint: Type[valueType]

    def __init__(self, initial_value: valueType, id: str, value_type_hint: Optional[Type[valueType]]):
        self.value = initial_value
        self._field_id = id
        if value_type_hint:
            self._type_hint = value_type_hint
            self._bake_is_required()

    def validate(self) -> bool:
        if self.is_required and self.value is None:
            raise FieldMissingValue(self)

        return True

    @property
    def id(self):
        return self._field_id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: valueType):
        self._value = new_value

    @property
    def is_required(self):
        if self._is_required is None and self._type_hint:
            self._bake_is_required()
        
        return self._is_required

    def _bake_is_required(self):
        is_optional = is_type_optional(self._type_hint)
        self._is_required = not is_optional

@dataclass_transform()
class FieldModel:
    _header_keys: Optional[list[str]] = None

    def __init__(self, **kwargs):
        self._set_from_dict(kwargs)
        self.validate()

    def validate(self):
        for field_name in self.header_keys():
            field_obj: CSVField = getattr(self, field_name)
            field_obj.validate()

    # Instancia os CSVField com base nas anotações de tipo do FieldModel 
    def _set_from_dict(self, data_dict: dict[str, Any]):
        hints = get_type_hints(self.__class__)
        for field_name, hint in hints.items():
            if field_name.startswith("_"):
                continue

            # Instanciação e atribuição dos fields no objeto dessa classe
            origin = get_origin(hint)
            if not origin is CSVField: continue
            args = get_args(hint)
            # if len(args) > 1: #TODO WARNING: avisar que provavelmente tem algo de errado com o field e ele provavelmente não vai ser interpretado corretamente
            
            field_instance = CSVField(data_dict.get(field_name), field_name, args[0])
            setattr(self, field_name, field_instance)

    @classmethod
    def header_keys(cls) -> list[str]:
        header_keys: Optional[list[str]] = cls._header_keys
        if not header_keys:
            header_keys = cls._bake_header_keys()

        return header_keys

    @classmethod
    def _bake_header_keys(cls) -> list[str]:
        hints = get_type_hints(cls)
        header_keys: list[str] = [
            key for key, type_hint in hints.items() if get_origin(type_hint) is CSVField
        ]

        cls._header_keys = header_keys
        return cls._header_keys

    def __str__(self):
        keys = self.header_keys()
        values = [
            getattr(self, key) for key in keys
        ]
        return ",".join(values)
