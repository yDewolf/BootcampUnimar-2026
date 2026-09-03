from tkinter import messagebox, scrolledtext, ttk
import tkinter as tk
from typing import Optional

from leety.client.app_protocol import AppProtocol
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.components.modals import CenterableModal
from leety.client.ui.ui_components import default_text, default_title
from leety.common.database.models.exercise_model import BaseExerciseModel, ExerciseModel

class ExerciseCreateModal(CenterableModal, MFrame[AppProtocol]):
    exercise_id: Optional[int] = None
    exercise: Optional[ExerciseModel]

    diff_id_combo: ttk.Combobox
    title_var: tk.StringVar

    time_limit_var: tk.DoubleVar
    memory_limit_var: tk.IntVar

    context_txt: tk.Text

    def is_editing(self):
        return self.exercise_id != None


    def __init__(self, parent: tk.Misc, controller: AppProtocol, exercise: Optional[ExerciseModel] = None):
        self.exercise = exercise
        self.controller = controller
        if self.exercise:
            self.exercise_id = self.exercise.id
        
        super().__init__(parent, "500x400")
        self.title(f"Editar/Criar exercício")

        self.title_var = tk.StringVar(value=exercise.title if exercise else None)
        self.time_limit_var = tk.DoubleVar(value=exercise.time_limit if exercise else None)
        self.memory_limit_var = tk.IntVar(value=exercise.memory_limit if exercise else None)

        self._setup_widgets()

    def _setup_widgets(self):
        self.grid()
        self.config(padx=20, pady=20)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        header_frame = ttk.Frame(self)
        header_frame.grid(column=0, row=0, sticky="we")

        default_title(header_frame, text="Informações do Exercício:", bold=True).pack(anchor="w")

        form_content = ttk.Frame(self)
        form_content.grid(column=0, row=1, sticky="nsew")

        diffs = self.controller.server.get_difficulties()
        diff_ids = [str(diff.id) for diff in diffs]

        form_grid = ttk.Frame(form_content)
        form_grid.columnconfigure(0, weight=0)
        form_grid.columnconfigure(1, weight=1)
        default_text(form_grid, "ID da dificuldade").grid(column=0, row=0, sticky="w", pady=5, padx=(0, 10))
        self.diff_id_combo = ttk.Combobox(form_grid, values=diff_ids)
        self.diff_id_combo.set(self.exercise.diff_id if self.exercise else None)
        self.diff_id_combo.grid(column=1, row=0, sticky="ew", pady=5)

        default_text(form_grid, "Título").grid(column=0, row=1, sticky="w", padx=(0, 10))
        title_entry = ttk.Entry(form_grid, textvariable=self.title_var)
        title_entry.grid(column=1, row=1, sticky="ew")
        form_grid.pack(fill="x", pady=(0, 10))

        default_text(form_content, "Contextualização").pack(anchor="w")
        self.context_txt = scrolledtext.ScrolledText(
            form_content, wrap="word", relief="sunken", height=8, width=40
        )
        if self.exercise:
            self.context_txt.insert(tk.INSERT, self.exercise.context)
        self.context_txt.pack(anchor="w", fill="x")

        default_title(form_content, text="Restrições", bold=True).pack(anchor="w")
        restriction_grid = ttk.Frame(form_content)
        restriction_grid.columnconfigure(0, weight=0)
        restriction_grid.columnconfigure(1, weight=1)

        default_text(restriction_grid, "Tempo limite").grid(column=0, row=0, pady=5, sticky="w", padx=(0, 10))
        ttk.Entry(restriction_grid, textvariable=self.time_limit_var).grid(column=1, row=0, pady=5, sticky="ew")

        default_text(restriction_grid, "Memória Limite").grid(column=0, row=1, pady=5, sticky="w", padx=(0, 10))
        ttk.Entry(restriction_grid, textvariable=self.memory_limit_var).grid(column=1, row=1, pady=5, sticky="ew")

        restriction_grid.pack(fill="x")

        buttons_frame = ttk.Frame(form_content)
        buttons_frame.pack(fill="x")

        save_button = ttk.Button(buttons_frame, text="Salvar", command=self._handle_save_action)
        save_button.grid(row=0, column=0, sticky="w")

    def _handle_save_action(self):
        model = self._make_exercise_model()
        if not model:
            return
        
        if self.is_editing():
            successful = self._edit_exercise(model)
        else:
            successful = self._save_model(model)

        if successful:
            messagebox.showinfo("Sucesso", f"O exercício foi {"criado" if not self.is_editing() else "editado"} com sucesso!")


    def _save_model(self, model: BaseExerciseModel) -> bool:
        if not self.controller.is_admin():
            return False

        assert self.controller.logged_user
        # TODO: adicionar o sample_gen_code coisas
        exercise = ExerciseModel.from_dict(model.get_data(raw=True))
        successful = self.controller.server.create_exercise(self.controller.logged_user, exercise)
        return successful

    def _edit_exercise(self, exercise: BaseExerciseModel) -> bool:
        if not self.controller.is_admin():
            return False

        assert self.controller.logged_user
        assert self.exercise_id, "Não há nenhum exercício sendo editado"
        successful = self.controller.server.modify_exercise(self.controller.logged_user, self.exercise_id, exercise)
        return successful

    def _make_exercise_model(self) -> Optional[BaseExerciseModel]:
        if not self.controller.logged_user:
            return
        
        new_model = BaseExerciseModel(
            id=self.exercise_id,
            diff_id=self.diff_id_combo.get(),
            author_id=self.controller.logged_user.id,
            title=self.title_var.get(),
            context=self.context_txt.get(1.0, "end-1c"),
            time_limit=self.time_limit_var.get(),
            memory_limit=self.memory_limit_var.get()
        )
        return new_model