from tkinter import messagebox, ttk
import tkinter as tk
from typing import Callable

from leety.client.app_protocol import AppProtocol
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.ui_components import default_text, default_title


def login_form(
    root_container: ttk.Frame,
    controller: AppProtocol, 
    goto_counterpart: Callable[[], None], 
    on_form_send: Callable[[str, str, bool], None],
    counterpart_link_txt: str,
    form_send_txt: str,
    title: str
):
    password_var = tk.StringVar()
    username_var = tk.StringVar()
    remember_me_var = tk.BooleanVar()

    def _handle_form_send():
        username = password_var.get().strip()
        password = username_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Formulário Inválido", "Todos os campos devem ser preenchidos")
            return
        try:
            on_form_send(username, password, remember_me_var.get())
            password_var.set("")
            username_var.set("")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no {title}: {str(e)}")

    top_row = ttk.Frame(root_container)
    top_row.grid(column=0, row=0, sticky="ew")
    top_row.columnconfigure(0, weight=0)
    top_row.columnconfigure(1, weight=1)
    top_row.columnconfigure(2, weight=0)
    ttk.Button(top_row, text="Voltar", command=controller.back).grid(row=0, column=0, sticky="w")
    default_title(top_row, f"Leety - {title}").grid(row=0, column=1, sticky="ew")

    form_frame = ttk.Frame(root_container, padding=20, width=250)
    form_frame.grid(column=0, row=1, sticky="n")

    default_text(form_frame, text="Nome de usuário:").grid(column=0, row=0, sticky="w", pady=5)
    ttk.Entry(form_frame, textvariable=password_var).grid(column=1, row=0, sticky="ew", pady=5)

    default_text(form_frame, text="Senha:").grid(column=0, row=1, sticky="w", pady=5)
    ttk.Entry(form_frame, textvariable=username_var, show="*").grid(column=1, row=1, sticky="ew", pady=5)

    ttk.Checkbutton(form_frame, text="Matenha-me logado", variable=remember_me_var).grid(column=0, row=2, sticky="ew", pady=5)

    ttk.Button(form_frame, text=counterpart_link_txt, command=goto_counterpart).grid(column=0, row=3, sticky="w", pady=10)
    ttk.Button(form_frame, text=form_send_txt, command=_handle_form_send).grid(column=1, row=3, sticky="e", pady=10)
