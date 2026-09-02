from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from leety.client.app_protocol import AppProtocol, ClientConfig
from leety.client.ui.abstract_screen import MFrame
from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.screens.exercise_screen import ExerciseScreen
from leety.client.ui.screens.login_screen import LoginScreen
from leety.client.ui.screens.register_screen import RegisterScreen
from leety.client.ui.screens.main_screen import MainScreen
from leety.server.server import Server

# nome provisório btw
APP_NAME = "Leety"
DEFAULT_SIZE = (640, 480)
DEFAULT_SOLUTION_PATH = Path(__file__).resolve().parent.parent.parent.parent / "solutions"

INTERNAL_SERVER = Server()
DEFAULT_CFG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "client_cfg.json" # ProjectFolder/client_cfg.json
class AppRoot(tk.Tk, AppProtocol):
    def __init__(self, frames: dict[ScreenNames, type[MFrame]], default_frame: str, cfg_path: Path = DEFAULT_CFG_PATH):
        self._default_solution_path = DEFAULT_SOLUTION_PATH
        self._default_solution_path.mkdir(exist_ok=True)
        self._connected_server = INTERNAL_SERVER
        self._cfg = ClientConfig()
        self._cfg_path = cfg_path
        self._load_cfg()
        super().__init__()
        self._setup_root()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._setup_frames(frames, default_frame)
        self._auto_login()

        self.change_to_screen(default_frame)


    def _setup_root(self):
        self.title(APP_NAME)
        self.geometry(f"{DEFAULT_SIZE[0]}x{DEFAULT_SIZE[1]}")
        self.minsize(DEFAULT_SIZE[0] // 2, DEFAULT_SIZE[1] // 2)

        self.root_container = tk.Frame(self)
        self.root_container.pack(fill="both", expand=True)
        self.root_container.grid_rowconfigure(0, weight=1)
        self.root_container.grid_columnconfigure(0, weight=1)

    def _auto_login(self):
        if not self._cfg.logged_username or not self._cfg.logged_password:
            return
        
        user = self.log_in(self._cfg.logged_username, self._cfg.logged_password)
        if not user:
            return
        keep_session = messagebox.askyesno("Login Automático", f"Quer continuar como {user.username}?")
        if keep_session:
            return
        
        self.log_out()


    def open_window(self):
        self.mainloop()

    def on_closing(self):
        self._save_cfg()
        self.destroy()

app = AppRoot({
    ScreenNames.MAIN: MainScreen,
    ScreenNames.REGISTER: RegisterScreen,
    ScreenNames.LOGIN: LoginScreen,
    ScreenNames.EXERCISE: ExerciseScreen
}, "main")
app.open_window()