from tkinter import messagebox, ttk
import tkinter as tk

from leety.client.app_protocol import AppProtocol
from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.components.login_components import login_form
from leety.client.ui.ui_components import default_text, default_title

class RegisterScreen(MFrame[AppProtocol]):
    def __init__(self, parent: tk.Misc, controller: AppProtocol):
        super().__init__(parent, controller)

        self._setup_widgets()

    def _setup_widgets(self):
        self.grid()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        
        self.root = ttk.Frame(self)
        self.root.grid(column=0, row=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)

        login_form(
            self.root, self.controller, self._go_to_login, self._handle_register,
            "Já tem uma conta? Faça login", "Cadastrar", "Cadastro"
        )

    def _handle_register(self, username: str, password: str, remember_me: bool):
        self.controller.server.register_user(username, password)
        user_data = self.controller.log_in(username, password, remember_me)
        if not user_data:
            raise Exception(f"Não foi possível logar como {username}")

        messagebox.showinfo("Sucesso", "Usuário cadastrado")
        self.controller.change_to_screen(ScreenNames.MAIN.value)

    def _go_to_login(self):
        self.controller.change_to_screen(ScreenNames.LOGIN.value)