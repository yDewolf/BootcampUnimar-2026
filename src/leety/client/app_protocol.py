from typing import Optional

from leety.client.controllers.screen_manager import ScreenManager
from leety.common.database.models.user_model import UserModel
from leety.server.server import Server


class AppProtocol(ScreenManager):
    _logged_user: Optional[UserModel] = None
    _connected_server: Server
    
    @property
    def server(self) -> Server: return self._connected_server

    @property
    def logged_user(self): return self.logged_user

    def log_in(self, username: str, password: str):
        self._logged_user = self.server.log_as_user(username, password)

    def log_out(self):
        self._logged_user = None

