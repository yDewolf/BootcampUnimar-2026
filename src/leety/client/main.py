import tkinter as tk

from leety.client.ui.screens.screen_protocols import MFrame
from leety.client.ui.screens.index import ScreenNames
from leety.client.ui.screens.register_screen import RegisterScreen
from leety.client.ui.screens.main_screen import MainScreen
from leety.client.ui.screens.screen_protocols import ScreenManager

# nome provisório btw
APP_NAME = "Leety"
DEFAULT_SIZE = (640, 480)

class AppRoot(tk.Tk, ScreenManager):
    root_container: tk.Frame
    _test_counter: int = 0
    _frames: dict[str, tk.Frame]
    _frame_order: list[tk.Frame]
    _current_frame_idx: int

    def __init__(self, frames: dict[ScreenNames, type[MFrame]], default_frame: str):
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

    def _setup_frames(self, frames: dict[ScreenNames, type[MFrame]], default_frame: str):
        self._frames = {}
        for name, frame_cls in frames.items():
            frame = frame_cls(self.root_container, controller=self) # type: ignore
            self._frames[name.value] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self._current_frame_idx = 0
        self._frame_order = [self._frames[default_frame]]

    def open_window(self):
        self.mainloop()

    def change_to_screen(self, target_screen: str):
        screen = self._frames.get(target_screen)
        if screen: screen.tkraise()

    def forward(self):
        if self._current_frame_idx + 1 >= len(self._frame_order):
            return
        
        self._current_frame_idx += 1
        frame = self._frame_order[self._current_frame_idx]
        frame.tkraise()

    def back(self):
        if self._current_frame_idx - 1 < 0:
            return
        self._current_frame_idx -= 1
        frame = self._frame_order[self._current_frame_idx]
        frame.tkraise()


app = AppRoot({
    ScreenNames.MAIN: MainScreen,
    ScreenNames.REGISTER: RegisterScreen
}, "main")
app.open_window()