import tkinter as tk
from typing import Protocol


class ScreenManager(Protocol):
    def forward(self): pass
    def back(self): pass
    def change_to_screen(self, target_screen: str): pass

class MFrame(tk.Frame):
    controller: ScreenManager
    def __init__(self, parent: tk.Misc, controller: ScreenManager):
        super().__init__(parent)
        self.controller = controller