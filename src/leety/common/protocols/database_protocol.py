# Estarei tentando não usar pydantic então vou tentar implementar algumas coisas que são bem úteis da biblioteca manualmente
from typing import Any, Optional

class FieldModel:
    pass

class CSVField[valueType: Any]:
    is_required: bool = False
    _value: valueType

    def __init__(self, default_value: valueType, is_required: bool = False):
        self.is_required = is_required
        self.value = default_value

    @property
    def value(self):
        return self._value

    @property.setter
    def value(self, new_value: valueType):
        self.value = new_value

# TODO
class CSVObject[data_model: FieldModel]:
    _header_keys: Optional[list[str]] = None
    _data_model: dict[str, CSVField]
    # Sobreescrever isso aqui com os fields do objeto

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        class GeneratedFields:
            pass

        cls._data_model = {}
        
        cls._Fields = cls.Fields
        cls.Fields = GeneratedFields

    def __str__(self):
        keys = self.header_keys()
        values = [
            getattr(self, key) for key in keys
        ]
        return ",".join(values)

    @classmethod

    @classmethod
    def header_keys(cls) -> list[str]:
        header_keys: Optional[list[str]] = cls._header_keys
        if not header_keys:
            header_keys = [
                key for key in cls.__dict__.keys() if not key.startswith("_")
            ]
            cls._header_keys = header_keys

        return header_keys
