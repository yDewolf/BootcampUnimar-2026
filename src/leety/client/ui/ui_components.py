from tkinter import ttk
import tkinter as tk


def default_title(parent: tk.Misc, text: str, bold: bool = False, fontsize: int = 13, **kwargs) -> ttk.Label:
    return ttk.Label(parent, text=text, font=("TkDefaultFont", fontsize, "bold" if bold else ""), **kwargs)

def default_text(parent: tk.Misc, text: str, fontsize: int = 11, **kwargs) -> ttk.Label:
    return ttk.Label(parent, text=text, font=("TkDefaultFont", fontsize), **kwargs)

