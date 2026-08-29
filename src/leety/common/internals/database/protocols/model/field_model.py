# Estarei tentando não usar pydantic então vou tentar implementar algumas coisas que são bem úteis da biblioteca manualmente
from typing import Any, Optional, Type, dataclass_transform, get_args, get_origin, get_type_hints, overload
from leety.common.internals.database.protocols.model.field_exceptions import FieldMissingValue
from leety.common.internals.database.protocols.type_protocols import TableProtocol
from leety.common.utils.type_utils import get_attributes_of_type, is_type_optional
# TODO: talvez implementa relacionamentos para evitar que dados relacionados em tabelas diferentes fiquem dessincronizados
# a minha ideia é tentar linkar as tabelas usando um LinkField, que recebe o field que ele está linkado
# dessa forma você teria que fazer algo tipo: 
# class Model(FieldModel):
#   link_field = LinkField(target_field=TargetModel.field)
# 
# assim o python automaticamente registraria a dependencia de um modelo sobre o outro
# já que ele depende de importar a classe alvo do modelo alvo, aí eu só teria que registrar a ordem de compilação das classes
# para reutilizar depois como uma lista de dependência e carregar os dados salvos na ordem certa

class Field[valueType: Any]:
    _field_id: str

    # Field Modifiers:
    _is_required: Optional[bool] = None
    _is_unique: bool = False
    _is_frozen: bool = False

    _default_value: Optional[valueType]
    _type_hint: Type[valueType]

    def __init__(
        self, 
        default: Optional[valueType] = None, 
        id: str = "", 
        frozen: bool = False,
        unique: bool = False,
        value_type_hint: Optional[Type[valueType]] = None
    ):
        self._default_value = default
        self._is_frozen = frozen
        self._is_unique = unique
        self._field_id = id
        if value_type_hint:
            self._type_hint = value_type_hint
            self._bake_is_required()

    def __set_name__(self, owner: type, name: str):
        if not self._field_id:
            self._field_id = name

    # Acesso via classe: FieldModel.model. -> Field[valueType]
    @overload
    def __get__(self, instance: None, owner: type) -> "Field[valueType]": ...

    # Acesso via instância: model_instance.model. -> valueType
    @overload
    def __get__(self, instance: Any, owner: type) -> valueType: ...

    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        
        if not hasattr(instance, "_data"):
            instance._data = {}
        
        return instance._data.get(self._field_id, self.default_value)

    # Exemplo: field_model.model. = value
    # ao invés de fazer a variável field ser = a value isso aqui faz field.value = value
    def __set__(self, instance: Any, new_value: Optional[valueType]) -> None:
        if not hasattr(instance, "_data"):
            instance._data = {}

        if self._is_frozen and self._field_id in instance._data:
            raise AttributeError(f"{Field} {self._field_id} is imutable and can't be modified")

        if self._is_unique and hasattr(instance, "_table_ref"):
            table: TableProtocol = instance._table_ref
            old_value = instance._data.get(self._field_id)
            # TODO: talvez pensar em uma forma melhor de fazer isso aqui
            table._swap_unique_value(self._field_id, old_value, new_value)
        
        instance._data[self._field_id] = new_value

    def validate(self, value: Optional[valueType]) -> bool:
        if self.is_required and value is None:
            raise FieldMissingValue(self)

        return True

    @property
    def id(self):
        return self._field_id

    @property
    def default_value(self):
        return self._default_value

    @property
    def frozen(self) -> bool:
        return self._is_frozen

    @property
    def unique(self) -> bool:
        return self._is_unique

    @property
    def is_required(self) -> bool:
        if self._is_required is None and self._type_hint:
            self._bake_is_required()
        
        return self._is_required or False

    def _bake_is_required(self):
        is_optional = is_type_optional(self._type_hint)
        self._is_required = not is_optional


@dataclass_transform(field_specifiers=(Field,), kw_only_default=True)
class FieldModel:
    _table_ref: Optional[TableProtocol]

    _header_keys: tuple[str, ...]
    _unique_fields: tuple[str, ...]
    _data: dict[str, Any] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._bake_header_keys()
        cls._setup_field_descriptors()

    def __init__(self, **kwargs):
        self._data = {}
        self._set_from_dict(kwargs)
        self.validate()

    def validate(self):
        for field_name in self.header_keys():
            field_obj: Field = getattr(self.__class__, field_name)
            
            value = getattr(self, field_name)
            field_obj.validate(value)

    
    def _set_from_dict(self, data_dict: dict[str, Any]):
        for key in self.header_keys():
            val = data_dict.get(key)
            setattr(self, key, val)
        

    @classmethod
    def header_keys(cls) -> tuple[str, ...]:
        return cls._header_keys

    @classmethod
    def _bake_header_keys(cls) -> tuple[str, ...]:
        cls._header_keys = get_attributes_of_type(cls, Field)
        return cls._header_keys

    @classmethod
    def _setup_field_descriptors(cls):
        hints = cls._get_type_hints()
        unique_fields: list[str] = []
        for field_name in cls.header_keys():
            field_instance: Optional[Field[Any]] = getattr(cls, field_name, None)

            hint = hints[field_name]
            origin = get_origin(hint) or hint
            args = get_args(hint)
            value_type = args[0] if args else type[Any]
            # if len(args) > 1: #TODO WARNING: avisar que provavelmente tem algo de errado com o field e ele provavelmente não vai ser interpretado corretamente
            if field_instance == None:
                if not issubclass(origin, Field): continue

                field_instance = hint(id=field_name, value_type_hint=value_type)
                setattr(cls, field_name, field_instance)

            if field_instance:
                field_instance._type_hint = value_type
                if field_instance._is_unique:
                    unique_fields.append(field_name)

        cls._unique_fields = tuple(unique_fields)

    @classmethod
    def _get_type_hints(cls):
        return get_type_hints(cls)

    def to_csv_str(self, include_header: bool = False) -> str:
        field_values: list[Field] = [
            getattr(self, key) for key in self.header_keys()
        ]
        value_str = ",".join([str(value) for value in field_values])
        if not include_header:
            return value_str
        
        header_str = ",".join(self.header_keys())
        return header_str + "\n" + value_str
        

    def __str__(self):
        return self.to_csv_str(include_header=True)
