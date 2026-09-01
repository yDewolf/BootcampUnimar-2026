import tkinter as tk
from tkinter import ttk

from leety.client.app_protocol import AppProtocol
from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.abstract_screen import MFrame

class MainScreen(MFrame[AppProtocol]):
    def __init__(self, parent: tk.Misc, controller: AppProtocol):
        super().__init__(parent, controller)
        label = tk.Label(self, text="Tela Inicial")
        label.pack(padx=20, pady=20)

        ttk.Button(self, text="Registrar conta", command=self.goto_register).pack()

    def goto_register(self):
        self.controller.change_to_screen(target_screen=ScreenNames.REGISTER.value)
