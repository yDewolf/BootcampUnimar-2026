
from typing import dataclass_transform

from leety.common.protocols.csvbase.csv_table import IndexableTable, Table

@dataclass_transform(field_specifiers=(Table, IndexableTable,))
class Database:
    # Armazena todas as tabelas etc eu acho
    # TODO: Implementar algo para ler os atributos que são tabelas
    pass

