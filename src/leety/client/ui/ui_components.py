from tkinter import ttk
import tkinter as tk


def default_title(parent: tk.Misc, text: str, bold: bool = False, **kwargs) -> ttk.Label:
    return ttk.Label(parent, text=text, font=("TkDefaultFont", 13, "bold" if bold else ""), **kwargs)

def default_text(parent: tk.Misc, text: str, **kwargs) -> ttk.Label:
    return ttk.Label(parent, text=text, font=("TkDefaultFont", 11), **kwargs)

