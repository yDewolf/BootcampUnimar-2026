from tkinter import messagebox, ttk
import tkinter as tk

from leety.client.app_protocol import AppProtocol
from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.abstract_screen import MFrame

class RegisterScreen(MFrame[AppProtocol]):
    username_var: tk.StringVar
    password_var: tk.StringVar
    remember_me: tk.BooleanVar

    _text_padding: int = 5
    _button_padding: int = 10
    def __init__(self, parent: tk.Misc, controller: AppProtocol):
        super().__init__(parent, controller)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_me = tk.BooleanVar()
        self._setup_widgets()

    def _setup_widgets(self):
        ttk.Label(self, text="Username:").grid(column=0, row=0, sticky="w", pady=self._text_padding)
        ttk.Entry(self, textvariable=self.username_var).grid(column=1, row=0, sticky="ew", pady=self._text_padding)

        ttk.Label(self, text="Password:").grid(column=0, row=1, sticky="w", pady=self._text_padding)
        ttk.Entry(self, textvariable=self.password_var, show="*").grid(column=1, row=1, sticky="ew", pady=self._text_padding)

        ttk.Checkbutton(self, text="Matenha-me logado", variable=self.remember_me).grid(column=0, row=2, sticky="ew", pady=self._text_padding)

        ttk.Button(self, text="Cadastrar", command=self._handle_register).grid(column=1, row=3, sticky="e", pady=self._button_padding)
        ttk.Button(self, text="Já tem conta? Login", command=self._go_to_login).grid(column=0, row=3, sticky="w", pady=self._button_padding)

    def _handle_register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Formulário Inválido", "Todos os campos devem ser preenchidos")
            return
        try:
            self.controller.server.register_user(username, password)
            user_data = self.controller.log_in(username, password, self.remember_me.get())
            if not user_data:
                raise Exception(f"Não foi possível logar como {username}")

            messagebox.showinfo("Sucesso", "Usuário cadastrado")
            self.username_var.set("")
            self.password_var.set("")
            
            self.controller.back()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no cadastro: {str(e)}")

    def _go_to_login(self):
        self.controller.change_to_screen(ScreenNames.LOGIN.value)