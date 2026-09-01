import tkinter as tk
from tkinter import ttk

from leety.client.ui.screens.index import ScreenNames
from leety.client.ui.screens.abstract_screen import MFrame, ScreenManager

class MainScreen(MFrame):
    def __init__(self, parent: tk.Misc, controller: ScreenManager):
        super().__init__(parent, controller)
        label = tk.Label(self, text="Tela Inicial")
        label.pack(padx=20, pady=20)

        ttk.Button(self, text="Registrar conta", command=self.goto_register).pack()

    def goto_register(self):
        self.controller.change_to_screen(target_screen=ScreenNames.REGISTER.value)