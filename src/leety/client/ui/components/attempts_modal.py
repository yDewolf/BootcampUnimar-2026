import tkinter as tk
from tkinter import ttk
from typing import List

from leety.client.app_protocol import AppProtocol
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.components.modals import CenterableModal
from leety.client.ui.ui_components import default_title
from leety.common.database.models.exercise_model import ExerciseAttempt, ExerciseModel
from leety.common.dto.attempt_result import AttemptResult, SolutionStatus


class AttemptsHistoryModal(CenterableModal, MFrame[AppProtocol]):
    def __init__(
        self, 
        parent: tk.Misc, 
        controller: AppProtocol, 
        exercise: ExerciseModel
    ):
        self.controller = controller
        self.exercise = exercise

        super().__init__(parent, "550x350")
        self.title(f"Histórico de Tentativas - Exercício #{exercise.id}")
        self._setup_widgets()

    def _setup_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self, padding=20)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        default_title(
            container, 
            text=f"Tentativas: {self.exercise.title}", 
            bold=True
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        table_frame = ttk.Frame(container)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("num", "status", "time", "correct_answers")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        tree.heading("num", text="#")
        tree.heading("status", text="Resultado")
        tree.heading("time", text="Tempo (s)")
        tree.heading("correct_answers", text="Acertos")

        tree.column("num", width=50, anchor="center")
        tree.column("status", width=180, anchor="w")
        tree.column("time", width=120, anchor="center")
        tree.column("correct_answers", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._load_attempts(tree)

        close_btn = ttk.Button(container, text="Fechar", command=self.destroy)
        close_btn.grid(row=2, column=0, sticky="e", pady=(10, 0))

    def _load_attempts(self, tree: ttk.Treeview):
        if not self.controller.logged_user or not self.controller.logged_user.id or not self.exercise.id:
            return

        attempts: List[ExerciseAttempt] = self.controller.server.get_user_attempts(
            self.controller.logged_user.id, 
            self.exercise.id
        )

        status_map = {
            SolutionStatus.ACCEPTED: "Solução Aceita",
            SolutionStatus.RUNTIME_ERROR: "Erro em Tempo de Execução",
            SolutionStatus.WRONG_ANSWER: "Resposta Incorreta",
        }
        for idx, attempt in enumerate(attempts):
            if not attempt.attempt_result: continue
            status_text = status_map.get(attempt.attempt_result.status, "Desconhecido")
            elapsed_text = f"{attempt.attempt_result.elapsed:.3f}s" if attempt.attempt_result.elapsed is not None else "N/A"

            correct_answers = f"{attempt.correct_results}/{attempt.sample_amount}"
            tree.insert("", "end", values=(idx + 1, status_text, elapsed_text, correct_answers))
