import threading
import tkinter as tk
from tkinter import ttk
from typing import TypedDict

from leety.client.app_protocol import AppProtocol
from leety.client.enums.screen_index import ScreenNames
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.ui_components import default_title, default_text

class _DiffStats(TypedDict):
    name: str
    solved: int
    total: int

class ProfileScreen(MFrame[AppProtocol]):
    _total_solved: int
    _total_attempts: int

    _diff_stats: dict[str, _DiffStats]
    _table_data: list

    def __init__(self, parent: tk.Misc, controller: AppProtocol):
        super().__init__(parent, controller)
        self.controller = controller
        self.setup_variables()

        self.title_var = tk.StringVar(value="Perfil de Usuário")
        self._setup_widgets()

    def setup_variables(self):
        self._total_solved = 0
        self._total_attempts = 0
        self._diff_stats = {}
        self._table_data = []
        

    def tkraise(self, *args, **kwargs) -> None:
        username = self.controller.logged_user.username if self.controller.logged_user else "Usuário"
        self.title_var.set(f"Perfil de {username}")
        self.setup_variables()

        super().tkraise(*args, **kwargs)
        self._load_profile_data()

    def _setup_widgets(self):
        self.root = ttk.Frame(self, padding=10)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.root.grid(column=0, row=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)

        self.header_frame = ttk.Frame(self.root)
        self.header_frame.grid(row=0, column=0, sticky="ew")

        header_bar = ttk.Frame(self.header_frame)
        header_bar.pack(anchor="n", fill="x", pady=(0, 10))
        header_bar.columnconfigure(0, weight=0)
        header_bar.columnconfigure(1, weight=1)
        header_bar.columnconfigure(2, weight=0)

        ttk.Button(header_bar, text="Voltar", command=self.controller.back).grid(row=0, column=0, sticky="w", padx=(0, 10))
        default_title(header_bar, textvariable=self.title_var, text="", bold=True).grid(row=0, column=1, sticky="ew")

        actions_frame = ttk.Frame(header_bar)
        actions_frame.grid(row=0, column=2, sticky="we")
        ttk.Button(actions_frame, text="Editar", command=self._handle_edit).grid(row=0, column=0)
        ttk.Button(actions_frame, text="Sair", command=self._handle_logout).grid(row=0, column=1, padx=(10, 0))

        self.lbl_total_solved = default_text(self.header_frame, "Exercícios Resolvidos: Carregando...")
        self.lbl_total_solved.pack(anchor="w")
        
        self.lbl_total_attempts = default_text(self.header_frame, "Tentativas Totais: Carregando...")
        self.lbl_total_attempts.pack(anchor="w")

        default_title(self.header_frame, "Resoluções por dificuldade").pack(anchor="w", pady=(10, 5))

        self.cards_frame = ttk.Frame(self.root)
        self.cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.lbl_cards_loading = default_text(self.cards_frame, "Carregando estatísticas por dificuldade...")
        self.lbl_cards_loading.pack(anchor="center")

        lbl_table = default_title(self.root, "Histórico de Exercícios")
        lbl_table.grid(row=2, column=0, sticky="w", pady=(10, 10))

        table_container = ttk.Frame(self.root)
        table_container.grid(row=3, column=0, sticky="nsew")
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)

        columns = ("id", "title", "difficulty", "status", "attempts")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="#")
        self.tree.heading("title", text="Título")
        self.tree.heading("difficulty", text="Dificuldade")
        self.tree.heading("status", text="Status")
        self.tree.heading("attempts", text="Tentativas")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("title", width=250, anchor="w")
        self.tree.column("difficulty", width=100, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("attempts", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _load_profile_data(self):
        if not self.controller.logged_user:
            return

        threading.Thread(target=self._fetch_data, daemon=True).start()

    def _fetch_data(self):
        assert self.controller.logged_user
        user_id = self.controller.logged_user.id
        assert user_id

        server = self.controller.server

        try:
            difficulties = server.get_difficulties()

            for diff in difficulties:
                assert diff.id
                self._diff_stats[diff.id] = {
                    "name": diff.capitalized_name, 
                    "solved": 0, 
                    "total": 0
                }

                exercises = server.get_exercises(diff.id)
                self._diff_stats[diff.id]["total"] = len(exercises)

                for ex in exercises:
                    assert ex.id
                    is_done = server.is_exercise_done(user_id, ex.id)
                    attempts = server.get_user_attempts(user_id, ex.id)
                    attempts_count = len(attempts)

                    self._total_attempts += attempts_count
                    if is_done:
                        self._diff_stats[diff.id]["solved"] += 1
                        self._total_solved += 1

                    if attempts_count > 0:
                        status = "Resolvido" if is_done else "Tentado"
                        self._table_data.append((ex.id, ex.title, diff.capitalized_name, status, attempts_count))

            self.after(0, self._update_ui)
            
        except Exception as e:
            print(f"Erro ao carregar perfil: {e}")
            self.after(0, lambda: self.lbl_cards_loading.config(text="Erro ao carregar dados."))


    def _update_ui(self):
        self.lbl_total_solved.config(text=f"Exercícios Resolvidos: {self._total_solved}")
        self.lbl_total_attempts.config(text=f"Tentativas Totais: {self._total_attempts}")

        self.lbl_cards_loading.destroy()
        for index, (diff_id, stats) in enumerate(self._diff_stats.items()):
            self.cards_frame.columnconfigure(index, weight=1, uniform="card")

            card = ttk.Frame(self.cards_frame, relief="ridge", borderwidth=2, padding=10)
            card.grid(row=0, column=index, sticky="nsew", padx=5)

            default_title(card, stats["name"], bold=True).pack(anchor="center", pady=(0, 5))
            
            info_text = f"{stats['solved']} / {stats['total']}"
            default_text(card, info_text).pack(anchor="center")

        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for row_data in self._table_data:
            tags = ("solved",) if row_data[3] == "Resolvido" else ("attempted",)
            self.tree.insert("", "end", values=row_data, tags=tags)
            
        self.tree.tag_configure("solved", foreground="green")
        self.tree.tag_configure("attempted", foreground="gray")

    
    def _handle_edit(self):
        pass

    def _handle_logout(self):
        self.controller.log_out()
        self.controller.change_to_screen(ScreenNames.MAIN.value)
