# Estarei tentando não usar pydantic então vou tentar implementar algumas coisas que são bem úteis da biblioteca manualmente
from typing import Any, Optional, Type, dataclass_transform, get_args, get_origin, get_type_hints
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
    _header_keys: tuple[str, ...]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._bake_header_keys()

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
        for field_name in self.header_keys():
            hint = hints.get(field_name)
            
            # Instanciação e atribuição dos fields no objeto dessa classe
            origin = get_origin(hint)
            if not origin is CSVField: continue
            args = get_args(hint)
            value_type = args[0] if args else Any
            # if len(args) > 1: #TODO WARNING: avisar que provavelmente tem algo de errado com o field e ele provavelmente não vai ser interpretado corretamente
            
            field_instance = CSVField(data_dict.get(field_name), field_name, value_type)
            setattr(self, field_name, field_instance)

    @classmethod
    def header_keys(cls) -> tuple[str, ...]:
        return cls._header_keys

    @classmethod
    def _bake_header_keys(cls) -> tuple[str, ...]:
        hints = get_type_hints(cls)
        header_keys: tuple[str, ...] = tuple([
            key for key, type_hint in hints.items() 
            if (get_origin(type_hint) is CSVField)
        ])

        cls._header_keys = header_keys
        return cls._header_keys

    def __str__(self):
        values = [
            getattr(self, key) for key in self.header_keys()
        ]
        return ",".join(values)
