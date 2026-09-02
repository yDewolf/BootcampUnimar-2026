from typing import Optional
from pathlib import Path
import json

from leety.common.internals.database.database_file import DBFileManager
from leety.client.data.client_cfg import ClientConfig
from leety.client.controllers.screen_manager import ScreenManager
from leety.common.database.models.user_model import UserModel
from leety.server.server import Server

class AppProtocol(ScreenManager):
    _default_solution_path: Path
    _cfg_path: Path

    _logged_user: Optional[UserModel] = None
    _cfg: ClientConfig
    _connected_server: Server

    @property
    def solutions_path(self) -> Path: return self._default_solution_path

    @property
    def server(self) -> Server: return self._connected_server

    @property
    def logged_user(self): return self._logged_user

    def log_in(self, username: str, password: str, remember_user: bool = False) -> Optional[UserModel]:
        self._logged_user = self.server.log_as_user(username, password)

        if remember_user and self._logged_user:
            self._update_login_cfg(username, password)
        
        return self._logged_user

    def log_out(self):
        self._logged_user = None
        self._update_login_cfg(None, None)

    def _update_login_cfg(self, username: Optional[str], password: Optional[str]):
        self._cfg.logged_username = username
        self._cfg.logged_password = password
        self._save_cfg()

    def _save_cfg(self):
        data = self._cfg.get_data(raw=True)
        self._cfg_path.write_text(json.dumps(data), encoding="utf-8")

    def _load_cfg(self):
        if not self._cfg_path.exists():
            return
        
        data = json.loads(self._cfg_path.read_text(encoding="utf-8"))
        parsed_data = DBFileManager._parse_row_data(ClientConfig, data)
        self._cfg._set_from_dict(parsed_data)
