import math
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from leety.client.app_protocol import AppProtocol
from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.components.exercise_create_modal import ExerciseCreateModal
from leety.client.ui.screens.exercise_screen import ExerciseScreen
from leety.client.ui.ui_components import default_text, default_title
from leety.common.database.models.exercise_model import ExerciseDifficulty, ExerciseModel

DEFAULT_DIFF_COLUMNS = 3
ITEMS_PER_PAGE = 5

class MainScreen(MFrame[AppProtocol]):
    search_var: tk.StringVar
    content_frame: ttk.Frame

    auth_button: ttk.Button
    current_diff: Optional[ExerciseDifficulty] = None

    current_page: int = 1
    items_per_page: int = ITEMS_PER_PAGE

    def __init__(self, parent: tk.Misc, controller: AppProtocol):
        super().__init__(parent, controller)
        self.search_var = tk.StringVar()
        self._setup_widgets()
        self.show_difficulties_grid()

    def _reload(self):
        self.show_difficulties_grid()

    def _setup_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=0) # navbar
        self.rowconfigure(2, weight=1) # conteúdo
        self.setup_navbar()

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        self.content_frame = ttk.Frame(self, padding=20)
        self.content_frame.grid(row=2, column=0, sticky="nsew")

    def setup_navbar(self):
        navbar = ttk.Frame(self, padding=(10, 5))
        navbar.grid(row=0, column=0, sticky="ew")

        navbar.columnconfigure(0, weight=0)
        navbar.columnconfigure(1, weight=0)
        navbar.columnconfigure(2, weight=1)
        navbar.columnconfigure(3, weight=0)

        brand_label = default_title(navbar, text="Codei")
        brand_label.grid(row=0, column=0, padx=(0, 15), sticky="w")

        reload_button = ttk.Button(navbar, text="Recarregar", command=self._reload)
        reload_button.grid(row=0, column=1, sticky="w")

        self.auth_button = ttk.Button(navbar)
        self.auth_button.grid(row=0, column=3, padx=(15, 0), sticky="e")

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
        if not isinstance(self.controller._previous_frame, ExerciseScreen):
            self.show_difficulties_grid()
        elif self.current_diff:
            self.show_exercise_list(self.current_diff, page=self.current_page)

        super().tkraise(*args, **kwargs)

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_difficulties_grid(self):
        self.current_diff = None
        self.current_page = 1
        self._clear_content()

        info_container = ttk.Frame(self.content_frame)
        title_label = default_title(info_container, "Selecione uma dificuldade")
        title_label.pack(anchor="w")
        subtitle_label = default_text(
            info_container, 
            f"Exercícios indexados: {len(self.controller.server.get_all_exercises())}"
        )
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

    def show_exercise_list(self, difficulty: ExerciseDifficulty, page: int = 1):
        assert difficulty.id
        self.current_diff = difficulty
        self.current_page = page
        self._clear_content()

        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill="x", pady=(0, 15))

        ttk.Button(header_frame, text="Voltar", command=self.show_difficulties_grid).pack(side="left")
        default_title(header_frame, f"Exercícios: {difficulty.capitalized_name}", bold=True).pack(side="left", padx=15)
        if self.controller.is_admin():
            ttk.Button(header_frame, text="Criar Exercício", command=self._create_new_exercise).pack(side="right")

        try:
            raw_exercises = self.controller.server.get_exercises(difficulty.id)
        except Exception as e:
            default_text(self.content_frame, text=f"Erro ao carregar exercícios: {e}").pack()
            return

        is_admin = self.controller.is_admin()
        exercises = [
            ex for ex in raw_exercises 
            if ex.is_valid or is_admin
        ]

        if not exercises:
            default_text(self.content_frame, text="Nenhum exercício encontrado para esta dificuldade").pack(pady=20)
            return

        total_items = len(exercises)
        total_pages = math.ceil(total_items / self.items_per_page)
        self.current_page = max(1, min(self.current_page, total_pages))

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        paginated_exercises = exercises[start_idx:end_idx]

        list_container = ttk.Frame(self.content_frame)
        list_container.pack(fill="both", expand=True)

        exercise_headers = ttk.Frame(list_container, padding=(5, 5))
        exercise_headers.pack(fill="x")
        
        exercise_headers.columnconfigure(0, weight=0) # Status Resolvido
        if is_admin:
            exercise_headers.columnconfigure(1, weight=1) # Status do exercício
            exercise_headers.columnconfigure(2, weight=3) # Título
            exercise_headers.columnconfigure(3, weight=2) # Autor
            exercise_headers.columnconfigure(4, weight=2) # Ações
        else:
            exercise_headers.columnconfigure(1, weight=3) # Título
            exercise_headers.columnconfigure(2, weight=2) # Autor
            exercise_headers.columnconfigure(3, weight=1) # Ações

        default_text(exercise_headers, "").grid(row=0, column=0)
        col_offset = 0
        if is_admin:
            default_text(exercise_headers, "Status").grid(row=0, column=1)
            col_offset = 1

        default_text(exercise_headers, "Título").grid(row=0, column=1 + col_offset, sticky="w")
        default_text(exercise_headers, "Autor").grid(row=0, column=2 + col_offset)
        default_text(exercise_headers, "Ações").grid(row=0, column=3 + col_offset)

        ttk.Separator(list_container, orient="horizontal").pack(fill="x", pady=2)

        for exercise in paginated_exercises:
            author_name: str = "Desconhecido"
            if exercise.author_id:
                author = self.controller.server.get_user_data(exercise.author_id)
                author_name = author.username if author else author_name

            exercise_row(
                self.controller, 
                list_container, 
                exercise, 
                author_name, 
                self._access_exercise, 
                self._edit_exercise
            )
            ttk.Separator(list_container, orient="horizontal").pack(fill="x")

        pagination_wrapper = ttk.Frame(self.content_frame, padding=(0, 15, 0, 0))
        pagination_wrapper.pack(fill="x", side="bottom")

        pagination_controls = ttk.Frame(pagination_wrapper)
        pagination_controls.pack(anchor="center")

        prev_button = ttk.Button(
            pagination_controls, 
            text="< Anterior", 
            command=lambda: self.show_exercise_list(difficulty, self.current_page - 1),
            state="normal" if self.current_page > 1 else "disabled"
        )
        prev_button.pack(side="left")

        page_info = default_text(pagination_controls, f"{self.current_page}/{total_pages}")
        page_info.pack(side="left", padx=15)

        next_button = ttk.Button(
            pagination_controls, 
            text="Próxima >", 
            command=lambda: self.show_exercise_list(difficulty, self.current_page + 1),
            state="normal" if self.current_page < total_pages else "disabled"
        )
        next_button.pack(side="left")

    def _edit_exercise(self, exercise: ExerciseModel):
        if not self.controller.is_admin():
            return

        modal = ExerciseCreateModal(self, self.controller, exercise)
        self.wait_window(modal)
        if self.current_diff:
            self.show_exercise_list(self.current_diff, page=self.current_page)

    def _create_new_exercise(self):
        modal = ExerciseCreateModal(
            self, 
            self.controller, 
            exercise=None, 
            default_diff=self.current_diff.id if self.current_diff else None
        )
        self.wait_window(modal)

        if self.current_diff:
            self.show_exercise_list(self.current_diff, page=self.current_page)

    def _access_exercise(self, exercise: ExerciseModel):
        exercise_screen = self.controller._frames.get(ScreenNames.EXERCISE.value)
        if isinstance(exercise_screen, ExerciseScreen):
            exercise_screen.set_exercise(exercise)
            self.controller.change_to_screen(target_screen=ScreenNames.EXERCISE.value)

    def _go_to_profile(self):
        self.controller.change_to_screen(target_screen=ScreenNames.PROFILE.value)

    def _go_to_login(self):
        self.controller.change_to_screen(target_screen=ScreenNames.LOGIN.value)

    def goto_register(self):
        self.controller.change_to_screen(target_screen=ScreenNames.REGISTER.value)


# Componentes

def diff_card(
    parent: tk.Misc, 
    diff: ExerciseDifficulty, 
    show_exercises: Callable[[ExerciseDifficulty], None]
) -> ttk.Frame:
    card = ttk.Frame(parent, padding=15, relief="groove")
    card.columnconfigure(0, weight=1)
    card.rowconfigure(1, weight=0)
    card.rowconfigure(2, weight=2)
    card.rowconfigure(3, weight=0)

    default_title(card, diff.capitalized_name, bold=True).grid(row=0, sticky="w")
    description_txt = tk.Text(card, wrap="word", relief="flat", height=4)
    description_txt.insert(1.0, diff.description)
    description_txt.config(state="disabled")
    description_txt.grid(row=1, sticky="w", pady=5)

    ttk.Button(
        card, 
        text="Ver Exercícios", 
        command=lambda: show_exercises(diff)
    ).grid(row=2, sticky="e")
    return card


def exercise_row(
    controller: AppProtocol, 
    parent: tk.Misc, 
    exercise: ExerciseModel, 
    author_name: str, 
    access_exercise: Callable[[ExerciseModel], None], 
    edit_exercise: Callable[[ExerciseModel], None]
) -> ttk.Frame:
    row_frame = ttk.Frame(parent, padding=(5, 8))
    row_frame.pack(fill="x")
    
    is_admin = controller.is_admin()

    row_frame.columnconfigure(0, weight=0) # resolvido
    if is_admin:
        row_frame.columnconfigure(1, weight=1) # status
        row_frame.columnconfigure(2, weight=3) # título
        row_frame.columnconfigure(3, weight=2) # autor
        row_frame.columnconfigure(4, weight=2) # ações
    else:
        row_frame.columnconfigure(1, weight=3) # título
        row_frame.columnconfigure(2, weight=2) # autor
        row_frame.columnconfigure(3, weight=1) # ações

    user = controller.logged_user
    is_done: bool = False
    if user:
        assert user.id
        assert exercise.id
        is_done = controller.server.is_exercise_done(user.id, exercise.id)

    # confie em mim, eu estou usando windows + . para adicionar estes emojis !!
    default_text(row_frame, "☑️" if is_done else "✖️").grid(row=0, column=0, sticky="w")
    col_offset = 0
    if is_admin:
        valid_status = "✅" if exercise.is_valid else "❌"
        default_text(row_frame, valid_status).grid(row=0, column=1, sticky="w")
        col_offset = 1

    default_text(row_frame, exercise.title).grid(row=0, column=1 + col_offset, sticky="w")
    default_text(row_frame, author_name).grid(row=0, column=2 + col_offset, sticky="e")

    button_frame = ttk.Frame(row_frame)
    button_frame.grid(row=0, column=3 + col_offset, sticky="e")
    ttk.Button(button_frame, text="Ver Exercício", command=lambda: access_exercise(exercise)).pack(side="right")

    if is_admin:
        ttk.Button(button_frame, text="Editar", command=lambda: edit_exercise(exercise)).pack(side="right")

    return row_frame
