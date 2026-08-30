
from typing import Optional

from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.user_model import UserModel


class UserController:
    database: LeetyDatabase

    def __init__(self, database: LeetyDatabase) -> None:
        self.database = database


    def register_user(self, user_data: UserModel):
        if user_data.is_admin:
            # simplesmente porque eu quis assim
            raise Exception("Admins must be inserted directly to the database")

        if not self.is_username_unique(user_data.username):
            raise Exception(f"Username '{user_data.username}' is already in use")
        
        self.database.users.add_row(user_data)
        return True

    def delete_user(self, user_id: int, password: str) -> bool:
        user_data = self.get_user(user_id)
        if not user_data: return False
        if user_data.password != password: return False

        self.database.users.remove_row_id(user_id)
        return True

    def admin_delete_user(self, user_id: int, admin_id: int, admin_password: str) -> bool:
        user_data = self.get_user(user_id)
        if not user_data: return False

        admin_data = self.get_user(admin_id)
        if not admin_data: return False
        if not admin_data.is_admin: return False

        if admin_data.password != admin_password: return False
        self.database.users.remove_row_id(user_id)
        return True


    def is_username_unique(self, username: str) -> bool:
        return len(self.database.users.match_searchable_field({
            UserModel.username: username
        }) or []) > 0


    def get_user(self, user_id: int) -> Optional[UserModel]:
        return self.database.users.get_by_id(user_id)

    def user_exists(self, user_id: int) -> bool:
        return self.get_user(user_id) != None

    def is_admin(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        
        return user.is_admin
