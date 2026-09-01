
from typing import Any, get_type_hints

from leety.common.internals.database.protocols.csv_table import IndexableTable, Table
from leety.common.utils.type_utils import get_attributes_of_type

# A classe Database é bem similar ao FieldModel, basicamente ela só descreve
# as tabelas que existem nesse "tipo" de Database e a instância armazena elas
# dentro de um dicionário para acessar os dados reais das tabelas

# @dataclass_transform(field_specifiers=(Table, IndexableTable,))
class _Database:
    _tables: dict[str, Table]
    _table_names: tuple[str, ...]
    _initialized: bool = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._bake_table_names()

    def __init__(self) -> None:
        self._tables = {}
        self._setup_tables()

        self._initialized = True

    def __setattr__(self, name: str, value: Any):
        if self._initialized and name in self._table_names:
            raise AttributeError(f"Database ({self.__class__.__name__}) was already initialized so you can't set table attributes")

        super().__setattr__(name, value)

    @classmethod
    def _bake_table_names(cls):
        cls._table_names = get_attributes_of_type(cls, Table)
        return cls._table_names

    def _setup_tables(self):
        hints = get_type_hints(self.__class__)
        for table_name in self.table_names():
            type_hint = hints[table_name]

            if issubclass(type_hint, Table): # Teoricamente aqui é 100% de certeza que já é Table, mas é bom ter mesmo assim
                table_instance = type_hint()
                
                self._tables[table_name] = table_instance
                setattr(self, table_name, table_instance)

    def get_table(self, table_name: str) -> Table:
        if table_name not in self._tables:
            raise KeyError(f"Table {table_name} couldn't be found in database {self.__class__.__name__}: {self}")

        return self._tables[table_name]

    @property
    def tables(self) -> dict[str, Table]:
        return self._tables

    @classmethod
    def table_names(cls) -> tuple[str, ...]:
        return cls._table_names


    def clear_all(self):
        for table in self._tables.values():
            table._rows.clear()
            if isinstance(table, IndexableTable):
                table._last_inserted_int_id = 0
                table._table_index.clear()
                table._searchable_index.clear()

            for key in table._unique_columns:
                table._unique_columns[key].clear()
    
    def to_dict(self) -> dict[str, list[dict]]:
        return {
            table_name: [row._data for row in table.rows]
            for table_name, table in self._tables.items()
        }
    