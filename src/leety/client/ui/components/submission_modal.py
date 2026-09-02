import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

from leety.client.app_protocol import AppProtocol
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.components.modals import CenterableModal
from leety.client.ui.ui_components import default_text, default_title
from leety.common.database.models.exercise_model import ExerciseModel
from leety.common.dto.attempt_result import AcceptedAttempt, AttemptResult, RuntimeErrorAttempt, SolutionStatus, WrongAnswerAttempt

class SubmissionModal(CenterableModal, MFrame[AppProtocol]):
    root: ttk.Frame
    result_root: ttk.Frame
    user_code: str

    exercise: ExerciseModel
    _local_attempt: int = 1
    current_attempt: int = 1

    def __init__(self, parent: tk.Misc, controller: AppProtocol, exercise: ExerciseModel, code: str):
        self.controller = controller
        self.exercise = exercise
        assert self.controller.logged_user
        assert self.controller.logged_user.id
        assert exercise.id
        self.user_code = code

        # FIXME: por algum motivo o match não tá funcionando corretamente
        previous_attempts = self.controller.server.get_user_attempts(self.controller.logged_user.id, exercise.id)
        self.current_attempt = len(previous_attempts) + 1
        self._local_attempt = 1
        super().__init__(parent, "500x600")
        
        self.title(f"Submissão Exercício #{exercise.id}")
        self._setup_widgets()

    def _clear_content(self):
        for widget in self.result_root.winfo_children():
            widget.destroy()

    def show_results(self, is_valid: bool, output: AttemptResult):
        self._clear_content()
        self.result_root.columnconfigure(0, weight=1)
        self.result_root.rowconfigure(1, weight=1)

        status_text = ""
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
        status_label.grid(row=0, column=0, sticky="n", pady=(0, 5))

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
        details_box.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        details_box.insert("1.0", details_text)
        details_box.config(state="disabled")

    def show_loading(self):
        self._clear_content()
        self.result_root.rowconfigure(0, weight=1)
        processing = default_text(self.result_root, text="Processando sua submissão...", fontsize=9)
        processing.pack()

    def setup_submission_content(self):
        container = ttk.Frame(self.root)
        container.grid(row=1, column=0, pady=10)

        default_text(container, "Sua resolução:").pack(anchor="w")

        output_box = scrolledtext.ScrolledText(container, wrap="word", font=("Consolas", 9), relief="sunken", height=12)
        output_box.insert(1.0, self.user_code if self.user_code else "Nenhuma saída gerada.")
        output_box.config(state="disabled")
        output_box.pack(fill="both", expand=True, pady=(0, 15))


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

        default_title(header_container, f"{self.exercise.title}", bold=True).pack(anchor="w")
        default_text(header_container, f"Tentativa nº {self.current_attempt}").pack(anchor="w")
        default_text(header_container, f"Tentativas seguidas: {self._local_attempt}").pack(anchor="w")

        self.setup_submission_content()

        self.result_root = ttk.Frame(self.root)
        self.result_root.grid(row=2, column=0, sticky="nsew")
        self.result_root.columnconfigure(0, weight=1)

        self.show_loading()