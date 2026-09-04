import tkinter as tk
from typing import Optional

from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.abstract_screen import MFrame, ScreenManagerProtocol

class ScreenManager(ScreenManagerProtocol):
    root_container: tk.Frame

    _frames: dict[str, MFrame]
    _frame_order: list[MFrame]
    _current_frame_idx: int

    _previous_frame: Optional[MFrame] = None

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
        self._frame_order = []
        self.change_to_screen(default_frame)

    def get_screen(self, target_screen: str) -> Optional[MFrame]:
        return self._frames.get(target_screen, None)

    def change_to_screen(self, target_screen: str):
        screen = self._frames.get(target_screen)
        if screen:
            if screen in self._frame_order:
                idx = self._frame_order.index(screen)
                self._frame_order = self._frame_order[:idx + 1]
                self._update_current_screen(idx)
                return

            self._frame_order = self._frame_order[:self._current_frame_idx + 1]

            idx = len(self._frame_order)
            self._frame_order.append(screen)
            self._update_current_screen(idx)

    def _update_current_screen(self, new_idx: int):
        self._previous_frame = self._frame_order[self._current_frame_idx]
        frame = self._frame_order[new_idx]
        self._current_frame_idx = new_idx
        frame.tkraise()
        

    def forward(self):
        if self._current_frame_idx + 1 >= len(self._frame_order):
            return
        
        self._update_current_screen(self._current_frame_idx + 1)

    def back(self):
        if self._current_frame_idx - 1 < 0:
            return
        
        self._update_current_screen(self._current_frame_idx - 1)