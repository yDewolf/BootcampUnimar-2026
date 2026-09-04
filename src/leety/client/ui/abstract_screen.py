from tkinter import ttk
import tkinter as tk
from typing import Protocol

class ScreenManagerProtocol(Protocol):
    root_container: tk.Frame

    def change_to_screen(self, target_screen: str): pass
    def forward(self): pass
    def back(self): pass

class MFrame[controllerType: ScreenManagerProtocol](ttk.Frame):
    controller: controllerType
    def __init__(self, parent: tk.Misc, controller: controllerType):
        super().__init__(parent)
        self.controller = controller
