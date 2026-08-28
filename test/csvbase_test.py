
from leety.common.database.csvbase import Database
from leety.common.protocols.csvbase.csv_table import IndexableTable
from leety.common.protocols.csvbase.model.default_models import IndexableFieldModel, SearchableField
from leety.common.protocols.csvbase.model.field_model import Field, FieldModel


class UserModel(IndexableFieldModel[int]):
    username: Field[str] = Field(unique=True)
    description: SearchableField[str] = SearchableField(default=None)
    password: Field[str]


class AdminModel(IndexableFieldModel[int]):
    user_id: Field[int] = Field(default=None, unique=True)

class TestDatabase(Database):
    users: IndexableTable[UserModel]
    admins: IndexableTable[AdminModel]


db = TestDatabase()

assert db.get_table("users") == db.users
assert db.get_table("admins") == db.admins

test_user = UserModel(id=None, username="testUser", password="123456", description="hello I'm your neighbour")
db.users.add_row(test_user)
assert db.users._rows == [test_user]
assert db.users._searchable_index == {"description": {test_user.description: [test_user]}}

db.users.match_field({UserModel.description: test_user.description})
db.admins.add_row(AdminModel(id=None, user_id=test_user.id))

db.users.remove_row_id(test_user.id)
assert db.users._searchable_index == {"description": {}}

db.admins.remove_row_id(test_user.id)

pass