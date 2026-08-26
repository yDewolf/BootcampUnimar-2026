
from leety.common.database.csvbase import Database
from leety.common.protocols.csvbase.csv_table import IndexableTable
from leety.common.protocols.csvbase.model.default_models import IndexableFieldModel
from leety.common.protocols.csvbase.model.field_model import Field, FieldModel


class UserModel(IndexableFieldModel):
    username: Field[str]


class MyDatabase(Database):
    user_table: IndexableTable[UserModel]

