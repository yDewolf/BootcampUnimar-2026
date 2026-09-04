from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from typing import Callable, Optional

from leety.client.app_protocol import AppProtocol
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.components.modals import CenterableModal
from leety.client.ui.ui_components import default_text, default_title
from leety.common.database.models.exercise_model import ExerciseModel
from leety.common.dto.attempt_result import AcceptedAttempt, AttemptResult, RuntimeErrorAttempt, SolutionStatus, WrongAnswerAttempt

class SubmissionModal(CenterableModal, MFrame[AppProtocol]):
    root: ttk.Frame
    result_root: ttk.Frame
    user_code: str = ""

    exercise: ExerciseModel
    _local_attempt: int = 1
    current_attempt: int = 1

    _start_submission_thread: Callable[[Path], tuple[Optional[threading.Thread], str]]
    _submission_thread: Optional[threading.Thread] = None
    _code_path: Path

    _resubmit_button: ttk.Button
    _attempt_label: ttk.Label
    _local_attempt_label: ttk.Label
    _output_box: scrolledtext.ScrolledText

    def __init__(
        self, 
        parent: tk.Misc, 
        controller: AppProtocol, 
        exercise: ExerciseModel, 
        start_submission_thread: Callable[[Path], tuple[Optional[threading.Thread], str]], 
        code_file_path: Path
    ):
        self.controller = controller
        self.exercise = exercise
        self._start_submission_thread = start_submission_thread
        self._code_path = code_file_path
        assert self.controller.logged_user
        assert self.controller.logged_user.id
        assert exercise.id

        previous_attempts = self.controller.server.get_user_attempts(self.controller.logged_user.id, exercise.id)
        self.current_attempt = len(previous_attempts) + 1
        self._local_attempt = 1
        super().__init__(parent, "500x500")
        
        self.title(f"Submissão Exercício #{exercise.id}")
        self._setup_widgets()

    def submit_attempt(self):
        if not self.is_able_to_submit():
            return

        self.show_loading()
        self._resubmit_button.config(state="disabled")

        self._submission_thread, self.user_code = self._start_submission_thread(self._code_path)
        self._update_user_code_display()

    def resubmit_attempt(self):
        if not self.is_able_to_submit():
            return
        
        self.current_attempt += 1
        self._local_attempt += 1
        self._update_header_labels()

        self.submit_attempt()

    def is_able_to_submit(self) -> bool:
        if not self._submission_thread:
            return True
        return not self._submission_thread.is_alive()

    def _clear_content(self):
        for widget in self.result_root.winfo_children():
            widget.destroy()

    def show_results(self, is_valid: bool, output: AttemptResult):
        self._clear_content()
        self.result_root.columnconfigure(0, weight=1)
        self.result_root.rowconfigure(2, weight=1)
        if not is_valid:
            self._resubmit_button.config(state="normal")

        match output.status:
            case SolutionStatus.ACCEPTED:
                status_text = "Solução Aceita!"
                status_color = "green"
            case SolutionStatus.RUNTIME_ERROR:
                status_text = "Erro em Tempo de Execução"
                status_color = "red"
            case SolutionStatus.WRONG_ANSWER:
                status_text = "Resposta Incorreta"
                status_color = "red"
            case _:
                status_text = "Resultado Desconhecido"
                status_color = "orange"

        status_label = default_title(
            self.result_root, 
            text=status_text, 
            bold=True,
            foreground=status_color
        )
        status_label.grid(row=0, column=0, sticky="n", pady=(0, 2))

        elapsed_str = f"Tempo de execução: {output.elapsed:.3f}s" if output.elapsed is not None else "Tempo de execução: N/A"
        elapsed_label = default_text(self.result_root, elapsed_str, fontsize=8)
        elapsed_label.grid(row=1, column=0, sticky="n", pady=(0, 5))

        details_text = ""
        if isinstance(output, AcceptedAttempt):
            details_text = "Sua solução passou em todos os testes!"

        elif isinstance(output, RuntimeErrorAttempt):
            details_text = f"Erro lançado durante a execução:\n\n{output.error}"

        elif isinstance(output, WrongAnswerAttempt):
            details_text = (
                f"Sua solução produziu um resultado diferente do esperado.\n\n"
                f"--- ENTRADA ---\n{output.input}\n\n"
                f"--- ESPERADO ---\n{output.expected}\n\n"
                f"--- OBTIDO ---\n{output.actual}"
            )

        details_box = scrolledtext.ScrolledText(
            self.result_root,
            wrap="word",
            font=("Consolas", 9),
            relief="sunken",
            height=12
        )
        details_box.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        details_box.insert(1.0, details_text)
        details_box.config(state="disabled")

    def show_loading(self):
        self._clear_content()
        self.result_root.rowconfigure(0, weight=1)
        processing = default_text(self.result_root, text="Processando sua submissão...", fontsize=9)
        processing.pack(pady=20)

    def setup_submission_content(self):
        container = ttk.Frame(self.root)
        container.grid(row=1, column=0, sticky="ew", pady=10)

        default_text(container, "Sua resolução:").pack(anchor="w")

        self._output_box = scrolledtext.ScrolledText(
            container, wrap="word", font=("Consolas", 9), relief="sunken", height=8
        )
        self._output_box.pack(fill="both", expand=True, pady=(0, 5))
        self._update_user_code_display()

    def _update_user_code_display(self):
        if hasattr(self, "_output_box"):
            self._output_box.config(state="normal")
            self._output_box.delete(1.0, tk.END)
            self._output_box.insert(1.0, self.user_code if self.user_code else "Nenhuma saída gerada.")
            self._output_box.config(state="disabled")

    def _update_header_labels(self):
        self._attempt_label.config(text=f"Tentativa nº {self.current_attempt}")
        self._local_attempt_label.config(text=f"Tentativas seguidas: {self._local_attempt}")

    def _setup_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.root = ttk.Frame(self, padding=20)
        self.root.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=1)

        header_container = ttk.Frame(self.root)
        header_container.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_container.columnconfigure(0, weight=1)

        title_frame = ttk.Frame(header_container)
        title_frame.pack(fill="x", expand=True)

        default_title(title_frame, f"{self.exercise.title}", bold=True).pack(side="left", anchor="w")

        self._resubmit_button = ttk.Button(
            title_frame,
            text="Reenviar",
            command=self.resubmit_attempt
        )
        self._resubmit_button.pack(side="right", anchor="e")

        self._attempt_label = default_text(header_container, f"Tentativa nº {self.current_attempt}")
        self._attempt_label.pack(anchor="w")

        self._local_attempt_label = default_text(header_container, f"Tentativas seguidas: {self._local_attempt}")
        self._local_attempt_label.pack(anchor="w")

        self.setup_submission_content()

        self.result_root = ttk.Frame(self.root)
        self.result_root.grid(row=2, column=0, sticky="nsew")
        self.result_root.columnconfigure(0, weight=1)

        self.show_loading()