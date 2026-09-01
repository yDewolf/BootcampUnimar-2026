import tkinter as tk

from leety.client.ui.screens.index import ScreenNames

class ScreenManager:
    root_container: tk.Frame

    _frames: dict[str, tk.Frame]
    _frame_order: list[tk.Frame]
    _current_frame_idx: int

    def __init__(self, frames: dict[ScreenNames, type[MFrame]], default_frame: str) -> None:
        super().__init__()
        self._setup_frames(frames, default_frame)

    def _setup_frames(self, frames: dict[ScreenNames, type[MFrame]], default_frame: str):
        self._frames = {}
        for name, frame_cls in frames.items():
            frame = frame_cls(self.root_container, controller=self) # type: ignore
            self._frames[name.value] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self._current_frame_idx = 0
        self._frame_order = [self._frames[default_frame]]

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


class MFrame(tk.Frame):
    controller: ScreenManager
    def __init__(self, parent: tk.Misc, controller: ScreenManager):
        super().__init__(parent)
        self.controller = controller