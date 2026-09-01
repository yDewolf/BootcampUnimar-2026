import tkinter as tk
from typing import Protocol

class ScreenManagerProtocol(Protocol):
    root_container: tk.Frame
    
    def change_to_screen(self, target_screen: str): pass
    def forward(self): pass
    def back(self): pass

class MFrame(tk.Frame):
    controller: ScreenManagerProtocol
    def __init__(self, parent: tk.Misc, controller: ScreenManagerProtocol):
        super().__init__(parent)
        self.controller = controller
