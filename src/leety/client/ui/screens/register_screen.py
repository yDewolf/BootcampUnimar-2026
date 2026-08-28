from tkinter import ttk
import tkinter as tk

class RegisterScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_widgets()

    def _setup_widgets(self):
        ttk.Label(self, text="Name:").grid(column=0, row=0, sticky="w")
        ttk.Entry(self).grid(column=1, row=0)
        ttk.Button(self, text="OK").grid(column=1, row=1, sticky="e")
