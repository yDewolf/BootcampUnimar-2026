
from leety.common.database.csvbase import Database
from leety.common.protocols.csvbase.csv_table import IndexableTable
from leety.common.protocols.csvbase.model.default_models import IndexableFieldModel
from leety.common.protocols.csvbase.model.field_model import Field, FieldModel


class UserModel(IndexableFieldModel[int]):
    username: Field[str] = Field(unique=True)
    password: Field[str]


class AdminModel(IndexableFieldModel[int]):
    user_id: Field[int] = Field(default=None, unique=True)

class TestDatabase(Database):
    users: IndexableTable[UserModel]
    admins: IndexableTable[AdminModel]


db = TestDatabase()

assert db.get_table("users") == db.users
assert db.get_table("admins") == db.admins

test_user = UserModel(id=None, username="testUser", password="123456")
db.users.add_row(test_user)
assert db.users._rows == [test_user]

db.admins.add_row(AdminModel(id=None, user_id=test_user.id))
assert db.admins.get_by_id(test_user.id)

db.users.remove_row_id(test_user.id)
db.admins.remove_row_id(test_user.id)

pass