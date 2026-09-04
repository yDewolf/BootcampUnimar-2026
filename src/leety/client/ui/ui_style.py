import tkinter as tk
from tkinter import ttk

COLOR_BG = "#F8FCFF"
COLOR_PRIMARY = "#1B57BF"
COLOR_WHITE = "#F8FCFF"
def apply_global_styles(root: tk.Tk):

    root.configure(bg=COLOR_BG)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".", background=COLOR_BG)
    style.configure("TFrame", background=COLOR_BG)
    style.configure("TLabel", background=COLOR_BG, foreground="#000000")
    style.configure("TButton", background="#E0E0E0", foreground="#000000", padding=(6, 2))

    style.configure("Navbar.TFrame", background=COLOR_PRIMARY)
    style.configure(
        "Navbar.TLabel", 
        background=COLOR_PRIMARY, 
        foreground=COLOR_WHITE,
        font=("Helvetica", 12, "bold")
    )
    style.configure(
        "Navbar.TButton", 
        background=COLOR_PRIMARY, 
        foreground=COLOR_WHITE,
        bordercolor=COLOR_PRIMARY,
        lightcolor=COLOR_PRIMARY,
        darkcolor=COLOR_PRIMARY
    )

    style.map(
        "Navbar.TButton",
        background=[("active", "#144498")],
        foreground=[("active", COLOR_WHITE)]
    )
