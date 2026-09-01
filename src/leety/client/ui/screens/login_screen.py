from tkinter import messagebox, ttk
import tkinter as tk

from leety.client.app_protocol import AppProtocol
from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.abstract_screen import MFrame

# ok, eu sei que isso aqui é a mesma tela do cadastro só que com algumas coisinhas
# a menos, mas faz parte né kkkkkk
# não dá pra fazer tudo perfeito as vezes
class LoginScreen(MFrame[AppProtocol]):
    username_var: tk.StringVar
    password_var: tk.StringVar

    _text_padding: int = 5
    _button_padding: int = 10
    def __init__(self, parent: tk.Misc, controller: AppProtocol):
        super().__init__(parent, controller)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self._setup_widgets()

    def _setup_widgets(self):
        ttk.Label(self, text="Username:").grid(column=0, row=0, sticky="w", pady=self._text_padding)
        ttk.Entry(self, textvariable=self.username_var).grid(column=1, row=0, sticky="ew", pady=self._text_padding)

        ttk.Label(self, text="Password:").grid(column=0, row=1, sticky="w", pady=self._text_padding)
        ttk.Entry(self, textvariable=self.password_var, show="*").grid(column=1, row=1, sticky="ew", pady=self._text_padding)

        ttk.Button(self, text="Entrar", command=self._handle_register).grid(column=1, row=2, sticky="e", pady=self._button_padding)
        ttk.Button(self, text="Não tem conta? cadastre-se", command=self._go_to_register).grid(column=0, row=2, sticky="w", pady=self._button_padding)

    def _handle_register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Formulário Inválido", "Todos os campos devem ser preenchidos")
            return
        try:
            user_data = self.controller.log_in(username, password)
            if not user_data:
                raise Exception(f"Não foi possível logar como {username}")

            self.username_var.set("")
            self.password_var.set("")
            self._go_to_index()
            
            messagebox.showinfo("Sucesso", f"Logado como {username}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no login: {str(e)}")

    def _go_to_register(self):
        self.controller.change_to_screen(ScreenNames.REGISTER.value)

    def _go_to_index(self):
        self.controller.change_to_screen(ScreenNames.MAIN.value)
    