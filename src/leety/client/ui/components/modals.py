import tkinter as tk

from leety.client.ui.ui_style import COLOR_BG

class CenterableModal(tk.Toplevel):
    def __init__(self, parent: tk.Misc, geometry: str):
        super().__init__(parent, bg=COLOR_BG)
        self.geometry(geometry)
        top_window = parent.winfo_toplevel()
        self.transient(top_window)
        self.grab_set()

        self._center_on_parent(top_window)

    def _center_on_parent(self, top_window: tk.Misc):
        self.update_idletasks()
        p_x, p_y = top_window.winfo_x(), top_window.winfo_y()
        p_w, p_h = top_window.winfo_width(), top_window.winfo_height()
        w, h = self.winfo_width(), self.winfo_height()

        c_x = p_x + (p_w // 2) - (w // 2)
        c_y = p_y + (p_h // 2) - (h // 2)
        self.geometry(f"+{c_x}+{c_y}")
