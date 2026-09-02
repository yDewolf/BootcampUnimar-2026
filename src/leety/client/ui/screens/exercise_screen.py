from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from typing import Optional

from leety.client.app_protocol import AppProtocol
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.components.submission_modal import SubmissionModal
from leety.client.ui.ui_components import default_text, default_title
from leety.common.database.models.exercise_model import ExerciseModel
from leety.common.database.models.user_model import UserModel

# TODO: Adicionar opção para ver a lista de soluções e tentativas
# TODO: Adicionar opções de admin (create, delete, update)
class ExerciseScreen(MFrame[AppProtocol]):
    current_exercise: Optional[ExerciseModel] = None
    header_frame: ttk.Frame
    content_container: ttk.Frame

    _submit_button: ttk.Button

    def __init__(self, parent: tk.Misc, controller: AppProtocol):
        super().__init__(parent, controller)
        self._setup_widgets()

    def set_exercise(self, exercise: ExerciseModel):
        self.current_exercise = exercise
        self._render_exercise_details()

    def tkraise(self, *args, **kwargs) -> None:
        self.refresh_submit_button()
        super().tkraise(*args, **kwargs)

    def refresh_submit_button(self):
        if not self.controller.logged_user:
            self._submit_button.config(state="disabled")
            return

        self._submit_button.config(state="normal")

    def _setup_widgets(self):
        self.config(padx=10, pady=10)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.header_frame = ttk.Frame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.columnconfigure(0, weight=0)
        self.header_frame.columnconfigure(1, weight=1)

        ttk.Button(self.header_frame, text="Voltar", command=self.controller.back).grid(sticky="w", column=0, row=0)

        self.content_container = ttk.Frame(self, padding=20)
        self.content_container.grid(row=1, column=0, sticky="nsew")

    def _render_exercise_header(self, exercise: ExerciseModel):
        header_info_frame = ttk.Frame(self.header_frame)
        header_info_frame.grid(column=1, row=0, sticky="we")
        header_info_frame.columnconfigure(0, weight=1)
        header_info_frame.columnconfigure(1, weight=0)
        header_info_frame.columnconfigure(2, weight=1)

        header_title = default_title(header_info_frame, text=f"Exercício #{exercise.id}")
        header_title.grid(sticky="w", row=0, column=0)

        separator = ttk.Separator(header_info_frame, orient="vertical")
        separator.grid(row=0, column=1, sticky="ns", pady=5)

        diff = self.controller.server.get_difficulty(exercise.diff_id)
        diff_name = diff.capitalized_name if diff else exercise.diff_id
        header_diff = default_title(header_info_frame, text=f"Dificuldade: {diff_name}")
        header_diff.grid(sticky="e", row=0, column=2)

    def _render_exercise_details(self):
        for widget in self.content_container.winfo_children():
            widget.destroy()

        if not self.current_exercise:
            default_text(self.content_container, text="Nenhum exercício selecionado.").pack()
            return

        exercise = self.current_exercise
        
        self._render_exercise_header(exercise)
        title_label = default_title(self.content_container, text=exercise.title, bold=True)
        title_label.pack(anchor="w")

        author_names: list[str] = []
        for id in (exercise.contributors or [exercise.author_id]):
            if not id: continue
            author = self.controller.server.get_user_data(id)
            author_names.append(author.username if author else "Desconhecido")
        if author_names == []: author_names = ["Desconhecido"]

        author_label = default_text(
            self.content_container, f"Autores: {",".join(author_names)}", fontsize=9
        )
        author_label.pack(anchor="w", pady=(0, 10))

        constraint_title = default_text(self.content_container, text="Restrições do Programa:")
        constraint_title.pack(anchor="w")
        meta_text = f"Tempo de execução: {exercise.time_limit}s | Memória: {exercise.memory_limit}MB"
        default_text(self.content_container, text=meta_text, fontsize=9).pack(anchor="w", pady=(0, 15))

        ttk.Separator(self.content_container, orient="horizontal").pack(fill="x", pady=5)

        context_title = default_text(self.content_container, text="Contextualização:")
        context_title.pack(anchor="w", pady=(10, 5))

        # FIXME
        context_body = tk.Text(
            self.content_container, height=8, wrap="word", relief="flat",
        )
        context_body.insert(1.0, exercise.context)
        context_body.config(state="disabled")
        context_body.pack(fill="x", pady=(0, 15))

        ttk.Separator(self.content_container, orient="horizontal").pack(fill="x", pady=5)

        exercise_actions = ttk.Frame(self.content_container)
        exercise_actions.pack(fill="x", pady=(10, 0))
        exercise_actions.rowconfigure(0)
        exercise_actions.columnconfigure(0, weight=0)
        exercise_actions.columnconfigure(1, weight=0)

        template_buton = ttk.Button(exercise_actions, text="Criar solução", command=self._create_solution_template)
        template_buton.grid(sticky="w", row=0, column=0)
        self._submit_button = ttk.Button(exercise_actions, text="Enviar solução", command=self._submit_solution)
        self._submit_button.grid(sticky="e", row=0, column=1)


    def _create_solution_template(self):
        if not self.current_exercise:
            messagebox.showwarning("Aviso", "Nenhum exercício foi selecionado")
            return

        file_path = filedialog.asksaveasfilename(
            title="Selecione um local para o template",
            filetypes=[(".py", "*.py")],
            defaultextension=".py",
            initialdir=str(self.controller.solutions_path),
            initialfile=f"Solution_{self.current_exercise.diff_id}-{self.current_exercise.id}"
        )

        if not file_path:
            return

        try:
            assert self.current_exercise.id, "Exercise must be indexed"
            exercise_template = self.controller.server.get_exercise_template(self.current_exercise.id)
            if not exercise_template:
                raise Exception(f"Failed to fetch solution template for exercise #{self.current_exercise.id}")

            path = Path(file_path)
            path.write_text(exercise_template, encoding="utf-8")

        except Exception as e:
            messagebox.showerror(
                "Erro de Leitura",
                f"Não foi possível ler o arquivo selecionado: \n{str(e)}"
            )

    def _submit_solution(self):
        if not self.controller.logged_user:
            messagebox.showwarning("Aviso", "Você deve estar logado para enviar tentativas")

        if not self.current_exercise:
            messagebox.showwarning("Aviso", "Nenhum exercício foi selecionado")
            return

        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo da sua solução",
            filetypes=[(".py", "*.py")]
        )

        if not file_path:
            return

        try:
            user = self.controller.logged_user
            assert user

            path = Path(file_path)
            file_contents = path.read_text(encoding="utf-8")

            modal = SubmissionModal(self, self.controller, self.current_exercise, file_contents)
            thread = threading.Thread(target=lambda: self.process_submission(user, modal, file_contents), daemon=True)
            thread.start()
            self.wait_window(modal)

            # FIXME
            thread.join(timeout=5)

        except Exception as e:
            messagebox.showerror(
                "Erro de Leitura",
                f"Não foi possível ler o arquivo selecionado: \n{str(e)}"
            )

    def process_submission(self, user: UserModel, modal: SubmissionModal, file_contents: str):
        assert user
        assert self.current_exercise
        assert self.current_exercise.id, "Exercise must be indexed"

        try:
            is_valid, output = self.controller.server.submit_attempt(
                user, self.current_exercise.id, file_contents
            )
            modal.after(0, lambda: modal.show_results(is_valid, output))
        except Exception as e:
            modal.after(0, lambda: messagebox.showerror("Erro", f"Erro no servidor: {e}"))
            modal.after(0, modal.destroy)
