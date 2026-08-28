import tkinter as tk

from leety.client.ui.screens.register_screen import RegisterScreen

# nome provisório btw
APP_NAME = "Leety"
DEFAULT_SIZE = (640, 480)

class MainScreen(tk.Frame):
    def __int__(self, parent):
        super().__init__(parent)
        label = tk.Label(self, text="Main Screen")


class AppRoot(tk.Tk):
    root_container: tk.Frame
    _test_counter: int = 0
    _frames: dict[str, tk.Frame]
    _frame_order: list[tk.Frame]

    def __init__(self, frames: dict[str, type[tk.Frame]], default_frame: str):
        super().__init__()
        self.title(APP_NAME)
        self.geometry(f"{DEFAULT_SIZE[0]}x{DEFAULT_SIZE[1]}")
        self.minsize(DEFAULT_SIZE[0] // 2, DEFAULT_SIZE[1] // 2)

        self.root_container = tk.Frame(self)
        self.root_container.pack(fill="both", expand=True)

        self._setup_frames(frames, default_frame)
        self._setup_widgets()

        self.change_to_screen(default_frame)

    def _setup_frames(self, frames: dict[str, type[tk.Frame]], default_frame: str):
        self._frames = {}
        for name, frame_cls in frames.items():
            frame = frame_cls(self.root_container)
            self._frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self._frame_order = [self._frames[default_frame]]

    def open_window(self):
        self.mainloop()

    def _setup_widgets(self):
        pass
        # button = ttk.Button(self._root, text="Registrar conta", command=)


    def change_to_screen(self, target_screen: str):
        screen = self._frames.get(target_screen)
        if screen: 
            screen.tkraise()
    

app = AppRoot({
    "main": MainScreen,
    "register": RegisterScreen
}, "main")
app.open_window()