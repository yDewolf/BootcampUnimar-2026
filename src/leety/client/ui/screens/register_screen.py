from tkinter import ttk
import tkinter as tk

from leety.client.app_protocol import AppProtocol
from leety.client.ui.abstract_screen import MFrame

class RegisterScreen(MFrame):
    def __init__(self, parent: tk.Misc, controller: AppProtocol):
        super().__init__(parent, controller)
        self._setup_widgets()

    def _setup_widgets(self):
        ttk.Label(self, text="Username:").grid(column=0, row=0, sticky="w")
        ttk.Entry(self).grid(column=1, row=0)

        password: str = ""
        ttk.Label(self, text="Password:").grid(column=0, row=1, sticky="w")
        ttk.Entry(self, textvariable=password).grid(column=1, row=0)
        ttk.Button(self, text="OK").grid(column=1, row=1, sticky="e")
