import tkinter as tk
from tkinter import ttk

from leety.client.app_protocol import AppProtocol
from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.abstract_screen import MFrame

class MainScreen(MFrame[AppProtocol]):
    search_var: tk.StringVar

    auth_button: ttk.Button

    def __init__(self, parent: tk.Misc, controller: AppProtocol):
        super().__init__(parent, controller)
        self.search_var = tk.StringVar()
        self._setup_widgets()

    def _setup_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=0) # navbar
        self.rowconfigure(2, weight=1) # conteúdo
        self.setup_navbar()

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        content_frame = ttk.Frame(self, padding=20)
        content_frame.grid(row=2, column=0, sticky="nsew")
        
        placeholder = ttk.Label(content_frame, text="Placeholder for exercise list")
        placeholder.pack(anchor="n", expand=True)

    # TODO: separar isso aqui em um componente
    def setup_navbar(self):
        navbar = ttk.Frame(self, padding=(10, 5))
        navbar.grid(row=0, column=0, sticky="ew")

        navbar.columnconfigure(0, weight=0) # 'logo' da plataforam
        navbar.columnconfigure(1, weight=1) # barra de pesquisa
        navbar.columnconfigure(2, weight=0) # perfil

        brand_label = ttk.Label(navbar, text="leety")
        brand_label.grid(row=0, column=0, padx=(0, 15), sticky="w")

        search_entry = ttk.Entry(navbar, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew", padx=10)
        search_entry.insert(0, "Pesquise exercícios aqui !!")
        
        self.auth_button = ttk.Button(navbar)
        self.auth_button.grid(row=0, column=2, padx=(15, 0), sticky="e")

    def refresh_auth_button(self):
        if self.controller.logged_user:
            self.auth_button.config(
                text=self.controller.logged_user.username,
                command=self._go_to_profile
            )
            return
        
        self.auth_button.config(
            text="Login",
            command=self._go_to_login
        )

    def tkraise(self, *args, **kwargs):
        self.refresh_auth_button()
        super().tkraise(*args, **kwargs)
    

    def _go_to_profile(self):
        self.controller.change_to_screen(target_screen=ScreenNames.PROFILE.value)

    def _go_to_login(self):
        self.controller.change_to_screen(target_screen=ScreenNames.LOGIN.value)

    def goto_register(self):
        self.controller.change_to_screen(target_screen=ScreenNames.REGISTER.value)
