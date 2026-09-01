import tkinter as tk
from typing import Optional

from leety.client.ui.screens.abstract_screen import MFrame
from leety.client.ui.screens.index import ScreenNames
from leety.client.ui.screens.register_screen import RegisterScreen
from leety.client.ui.screens.main_screen import MainScreen
from leety.client.ui.screens.abstract_screen import ScreenManager
from leety.server.server import Server

# nome provisório btw
APP_NAME = "Leety"
DEFAULT_SIZE = (640, 480)

INTERNAL_SERVER = Server()

class AppRoot(tk.Tk, ScreenManager):
    _connected_server: Server

    @property
    def server(self) -> Server: return self._connected_server

    def __init__(self, frames: dict[ScreenNames, type[MFrame]], default_frame: str):
        self._connected_server = INTERNAL_SERVER
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{DEFAULT_SIZE[0]}x{DEFAULT_SIZE[1]}")
        self.minsize(DEFAULT_SIZE[0] // 2, DEFAULT_SIZE[1] // 2)

        self.root_container = tk.Frame(self)
        self.root_container.pack(fill="both", expand=True)
        self.root_container.grid_rowconfigure(0, weight=1)
        self.root_container.grid_columnconfigure(0, weight=1)

        self._setup_frames(frames, default_frame)
        self.change_to_screen(default_frame)

    def open_window(self):
        self.mainloop()



app = AppRoot({
    ScreenNames.MAIN: MainScreen,
    ScreenNames.REGISTER: RegisterScreen
}, "main")
app.open_window()