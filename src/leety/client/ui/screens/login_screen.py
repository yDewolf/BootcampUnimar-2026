from tkinter import messagebox, ttk
import tkinter as tk

from leety.client.app_protocol import AppProtocol
from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.components.login_components import login_form

# ok, eu sei que isso aqui é a mesma tela do cadastro só que com algumas coisinhas
# a menos, mas faz parte né kkkkkk
# não dá pra fazer tudo perfeito as vezes
class LoginScreen(MFrame[AppProtocol]):
    def __init__(self, parent: tk.Misc, controller: AppProtocol):
        super().__init__(parent, controller)
        self._setup_widgets()

    def _setup_widgets(self):
        self.grid()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        
        self.root = ttk.Frame(self, padding=10)
        self.root.grid(column=0, row=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)

        login_form(
            self.root, self.controller, self._go_to_register, self._handle_login,
            "Não tem uma conta? Cadastre-se", "Entrar", "Login"
        )

    def _handle_login(self, username: str, password: str, remember_me: bool):
        user_data = self.controller.log_in(username, password, remember_me)
        if not user_data:
            raise Exception(f"Não foi possível logar como {username}")

        self._go_to_index()
        messagebox.showinfo("Sucesso", f"Logado como {username}")

    def _go_to_register(self):
        self.controller.change_to_screen(ScreenNames.REGISTER.value)

    def _go_to_index(self):
        self.controller.change_to_screen(ScreenNames.MAIN.value)
    