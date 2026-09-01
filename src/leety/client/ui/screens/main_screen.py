import tkinter as tk
from tkinter import ttk
from typing import Callable

from leety.client.app_protocol import AppProtocol
from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.ui_components import default_text, default_title
from leety.common.database.models.exercise_model import ExerciseDifficulty, ExerciseModel

DEFAULT_DIFF_COLUMNS = 3
class MainScreen(MFrame[AppProtocol]):
    search_var: tk.StringVar
    content_frame: ttk.Frame

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
        
        self.content_frame = ttk.Frame(self, padding=20)
        self.content_frame.grid(row=2, column=0, sticky="nsew")

    # TODO: separar isso aqui em um componente
    def setup_navbar(self):
        navbar = ttk.Frame(self, padding=(10, 5))
        navbar.grid(row=0, column=0, sticky="ew")

        navbar.columnconfigure(0, weight=0) # 'logo' da plataforam
        navbar.columnconfigure(1, weight=1) # barra de pesquisa
        navbar.columnconfigure(2, weight=0) # perfil

        brand_label = default_title(navbar, text="leety")
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
        self.show_difficulties_grid()
        super().tkraise(*args, **kwargs)


    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()


    def show_difficulties_grid(self):
        self._clear_content()

        info_container = ttk.Frame(self.content_frame)
        title_label = default_title(info_container, "Selecione uma dificuldade")
        title_label.pack(anchor="w")
        subtitle_label = default_text(info_container, f"Exercícios indexados: {len(self.controller.server.get_all_exercises())}")
        subtitle_label.pack(anchor="w")
        info_container.pack(anchor="w", pady=(0, 10))

        grid_container = ttk.Frame(self.content_frame)
        grid_container.pack(fill="both", expand=True)

        try:
            difficulties = self.controller.server.get_difficulties()
        except Exception as e:
            default_text(grid_container, text=f"Erro ao carregar dificuldades: {e}").pack()
            return

        cols = DEFAULT_DIFF_COLUMNS
        for idx, diff in enumerate(difficulties):
            card = diff_card(grid_container, diff, self.show_exercise_list)
            row = idx // cols
            col = idx % cols

            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            grid_container.columnconfigure(col, weight=1)


    def show_exercise_list(self, difficulty: ExerciseDifficulty):
        assert difficulty.id
        self._clear_content()

        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill="x", pady=(0, 15))

        ttk.Button(header_frame, text="Voltar", command=self.show_difficulties_grid).pack(side="left")
        default_title(header_frame, f"Exercícios: {difficulty.capitalized_name}", bold=True).pack(side="left", padx=15)

        try:
            exercises = self.controller.server.get_exercises(difficulty.id)
        except Exception as e:
            ttk.Label(self.content_frame, text=f"Erro ao carregar exercícios: {e}").pack()
            return

        if not exercises:
            ttk.Label(self.content_frame, text="Nenhum exercício encontrado para esta dificuldade").pack(pady=20)
            return

        list_container = ttk.Frame(self.content_frame)
        list_container.pack(fill="both", expand=True)

        headers_frame = ttk.Frame(list_container, padding=(5, 5))
        headers_frame.pack(fill="x")
        headers_frame.columnconfigure(0, weight=3) # Título
        headers_frame.columnconfigure(1, weight=1) # Tempo Limite
        headers_frame.columnconfigure(2, weight=1) # Autor

        default_text(headers_frame, "Título").grid(row=0, column=0, sticky="w")
        default_text(headers_frame, "Tempo Limite").grid(row=0, column=1, sticky="w")
        default_text(headers_frame, "Autor ID").grid(row=0, column=2, sticky="w")

        ttk.Separator(list_container, orient="horizontal").pack(fill="x", pady=2)

        for exercise in exercises:
            exercise_row(list_container, exercise)
            ttk.Separator(list_container, orient="horizontal").pack(fill="x")
            

    def _go_to_profile(self):
        self.controller.change_to_screen(target_screen=ScreenNames.PROFILE.value)

    def _go_to_login(self):
        self.controller.change_to_screen(target_screen=ScreenNames.LOGIN.value)

    def goto_register(self):
        self.controller.change_to_screen(target_screen=ScreenNames.REGISTER.value)


def diff_card(parent: tk.Misc, diff: ExerciseDifficulty, show_exercises: Callable[[ExerciseDifficulty], None]) -> ttk.Frame:
    card = ttk.Frame(parent, padding=15, relief="groove")
    card.columnconfigure(0, weight=1)
    card.rowconfigure(1, weight=0)
    card.rowconfigure(2, weight=2)
    card.rowconfigure(3, weight=0)

    default_title(card, diff.capitalized_name, bold=True).grid(row=0, sticky="w")
    default_text(card, diff.description, wraplength=120).grid(row=1, sticky="w")

    ttk.Button(
        card, 
        text="Ver Exercícios", 
        command=lambda : show_exercises(diff)
    ).grid(row=2, sticky="e")
    return card

def exercise_row(parent: tk.Misc, exercise: ExerciseModel) -> ttk.Frame:
    row_frame = ttk.Frame(parent, padding=(5, 8))
    row_frame.pack(fill="x")
    row_frame.columnconfigure(0, weight=3)
    row_frame.columnconfigure(1, weight=1)
    row_frame.columnconfigure(2, weight=1)

    author_display = str(exercise.author_id) if exercise.author_id is not None else "Desconhecido"

    default_text(row_frame, exercise.title).grid(row=0, column=0, sticky="w")
    default_text(row_frame, f"{exercise.time_limit}s").grid(row=0, column=1, sticky="w")
    default_text(row_frame, author_display).grid(row=0, column=2, sticky="w")

    return row_frame
