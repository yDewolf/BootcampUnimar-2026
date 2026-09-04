import os
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
import tkinter as tk
from typing import Optional

from leety.client.app_protocol import AppProtocol
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.components.modals import CenterableModal
from leety.client.ui.ui_components import default_text, default_title
from leety.common.database.models.exercise_model import BaseExerciseModel, ExerciseModel
from leety.common.database.db_exceptions import InvalidCodeException
from leety.client.ui.components.wait_thread_modal import WaitThreadModal

class ExerciseCreateModal(CenterableModal, MFrame[AppProtocol]):
    exercise_id: Optional[int] = None
    exercise: Optional[ExerciseModel]

    default_diff_id: Optional[str] = None
    diff_id_combo: ttk.Combobox
    title_var: tk.StringVar

    time_limit_var: tk.DoubleVar
    memory_limit_var: tk.IntVar

    context_txt: tk.Text
    sample_gen_path: Optional[Path] = None
    is_exercise_valid: tk.StringVar

    deleted_exercise: bool = False

    def is_editing(self):
        return self.exercise_id != None


    def __init__(self, parent: tk.Misc, controller: AppProtocol, exercise: Optional[ExerciseModel] = None, default_diff: Optional[str] = None):
        self.exercise = exercise
        self.controller = controller
        self.default_diff_id = default_diff
        if self.exercise:
            self.exercise_id = self.exercise.id
        
        super().__init__(parent, "500x500")
        self.title(f"Editar/Criar exercício")

        self.title_var = tk.StringVar(value=exercise.title if exercise else None)
        self.time_limit_var = tk.DoubleVar(value=exercise.time_limit if exercise else None)
        self.memory_limit_var = tk.IntVar(value=exercise.memory_limit if exercise else None)
        self.is_exercise_valid = tk.StringVar(value=f"{'✅' if exercise.is_valid else '❎'}" if exercise else '?')

        self._setup_widgets()

    def _update_exercise_valid(self):
        self.is_exercise_valid.set(f"{'✅' if self.exercise.is_valid else '❎'}" if self.exercise else '?')

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
        if self.exercise:
            self.diff_id_combo.set(self.exercise.diff_id)
        elif self.default_diff_id:
            self.diff_id_combo.set(self.default_diff_id)
        
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

        default_title(form_content, text="Código", bold=True).pack(anchor="w")
        code_grid = ttk.Frame(form_content)
        code_grid.columnconfigure(0, weight=0)
        code_grid.columnconfigure(1, weight=2)
        code_grid.columnconfigure(2, weight=0)
        code_grid.columnconfigure(3, weight=1)
        
        default_text(code_grid, "Código do exercício").grid(column=0, row=0, pady=5, sticky="w", padx=(0, 10))
        ttk.Button(code_grid, text="Selecionar Arquivo", command=self._select_sample_gen_path).grid(row=0, column=1, sticky="w")
        default_text(code_grid, "", textvariable=self.is_exercise_valid).grid(row=0, column=2, sticky="w", padx=10)
        if not self.is_editing():
            ttk.Button(code_grid, text="Criar Modelo", command=self._create_exercise_template).grid(row=0, column=3, sticky="we")

        else:
            ttk.Button(code_grid, text="Atualizar Arquivo de Exercício", command=self._upload_new_sample_gen).grid(row=0, column=1, sticky="w")
            ttk.Button(code_grid, text="Baixar exercício", command=self._handle_exercise_download).grid(row=0, column=3, sticky="w")

        code_grid.pack(fill="x")

        ttk.Separator(form_content, orient="horizontal").pack(fill="x", anchor="center", pady=10)

        buttons_frame = ttk.Frame(form_content)
        buttons_frame.columnconfigure(0, weight=0)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=0)
        buttons_frame.pack(fill="x")

        ttk.Frame(buttons_frame).grid(row=0, column=1)

        save_button = ttk.Button(buttons_frame, text="Salvar", command=self._handle_save_action)
        save_button.grid(row=0, column=0, sticky="w")

        if self.is_editing():
            delete_button = ttk.Button(buttons_frame, text="Excluir exercício", command=self._handle_delete_action)
            delete_button.grid(row=0, column=2, sticky="e")
        else:
            default_text(buttons_frame, text="Nota: O código será validado após salvar o exercício", fontsize=9).grid(row=0, column=2, sticky="we")

    # TODO:
    def _handle_exercise_download(self):
        if not self.exercise:
            return
        
        assert self.exercise.id
        file_path = filedialog.asksaveasfilename(
            title="Selecione onde salvar o exercício",
            filetypes=[(".py", "*.py")],
            defaultextension=".py",
            # FIXME: trocar esse path
            initialdir=str(self.controller.solutions_path),
            initialfile=f"ex_{self.exercise.id}-gen"
        )

        if not file_path:
            return

        path = Path(file_path)
        file_contents = self.controller.server.get_exercise_code(self.exercise.id)
        if not file_contents:
            return

        path.write_text(file_contents, encoding="utf-8")
        self.sample_gen_path = path

        auto_open = messagebox.askyesno("Abrir arquivo?", "Abrir exercício no editor de texto padrão?")
        if auto_open:
            os.startfile(file_path)
    
    def _handle_delete_action(self):
        if not self.exercise:
            return
        
        proceed = messagebox.askokcancel("Confirme a ação", f"Tem certeza que deseja excluir o exercício '{self.exercise.title}'?")
        if not proceed:
            return

        try:
            if not self.exercise_id:
                raise Exception("Nenhum exercício está sendo editado")

            if not self.controller.logged_user:
                raise Exception("O usuário deve estar logado para performar a ação")
            
            self.controller.server.delete_exercise(self.controller.logged_user, self.exercise_id)
            self.deleted_exercise = True

        except Exception as e:
            messagebox.showerror("Erro na exclusão", f"Algo deu errado ao excluir o exercício:\n{e}")
            return

        messagebox.showinfo("Sucesso", "O exercício foi excluído com sucesso!")
        self.destroy()
       
    def _handle_save_action(self):
        successful: bool = False
        try:
            model = self._make_exercise_model()
            if not model:
                return

            if self.is_editing():
                successful = self._edit_exercise(model)
            else:
                successful = self._save_model(model)
            
            if model.id:
                exercise_data = self.controller.server.get_exercise(model.id)
                assert exercise_data, "O Exercício não foi indexado corretamente"
                if not exercise_data.is_valid:
                    raise InvalidCodeException("O código do exercício é inválido. Edite o exercício e atualize o código para corrigir.\nAs outras alterações serão salvas normalmente")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o exercício:\n\n{e}")
            if isinstance(e, InvalidCodeException):
                self.destroy()

        self._update_exercise_valid()
        if successful:
            messagebox.showinfo("Sucesso", f"O exercício foi {"criado" if not self.is_editing() else "editado"} com sucesso!")
            self.destroy()


    def _save_model(self, model: BaseExerciseModel) -> bool:
        if not self.controller.is_admin():
            return False

        assert self.controller.logged_user
        if not self.sample_gen_path:
            raise Exception("Nenhum arquivo de exercício foi selecionado")
        
        file_contents = self._load_sample_gen()
        exercise = ExerciseModel(_sample_gen_code=file_contents, **model.get_data(raw=True))
        successful, id = WaitThreadModal.execute(
            self, 
            self.controller,
            self.controller.server.create_exercise,
            (self.controller.logged_user, exercise),
            title="Criando Exercício",
            message="O exercício está sendo validado, por favor aguarde..."
        )
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

        if self.title_var.get() == "":
            raise Exception("O título do exercício deve ser preenchido")

        if self.context_txt.get(1.0) == "":
            raise Exception("O exercício deve haver contextualização explicando o problema que o usuário deve resolver")

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

    def _upload_new_sample_gen(self):
        try:
            if not self.controller.is_admin():
                raise Exception("O usuário deve ser um admin para completar a ação")

            if not self.controller.logged_user:
                raise Exception("Você deve estar logado para realizar a ação")

            if self.exercise_id is None:
                raise Exception("Nenhum exercício está sendo editado")
            
            self._select_sample_gen_path()
            if not self.sample_gen_path:
                return
            
            file_contents = self._load_sample_gen()
            if not file_contents:
                raise Exception("Não foi possível ler os conteúdos do arquivo")

            is_valid = WaitThreadModal.execute(
                parent=self,
                controller=self.controller,
                target_func=self.controller.server.upload_sample_gen_code,
                args=(self.controller.logged_user, self.exercise_id, file_contents),
                title="Enviando Exercício",
                message="Enviando e validando o código do exercício..."
            )
            if not is_valid:
                raise InvalidCodeException("O código do exercício não é válido")

        except Exception as e:
            messagebox.showerror("Algo deu errado", f"Não foi possível atualizar o código do exercício:\n\n{e}")

        self._update_exercise_valid()

    def _select_sample_gen_path(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo do exercício",
            filetypes=[(".py", "*.py")]
        )
        if not file_path:
            return

        self.is_exercise_valid.set("...")
        self.sample_gen_path = Path(file_path)

    def _load_sample_gen(self) -> Optional[str]:
        if not self.sample_gen_path:
            return None

        if not self.sample_gen_path.exists():
            raise Exception("O arquivo não existe mais")

        return self.sample_gen_path.read_text(encoding="utf-8")


    def _create_exercise_template(self):
        file_path = filedialog.asksaveasfilename(
            title="Selecione um local para o template",
            filetypes=[(".py", "*.py")],
            defaultextension=".py",
            # FIXME: trocar esse path
            initialdir=str(self.controller.solutions_path),
            initialfile=f"exercise_template"
        )

        if not file_path:
            return

        path = Path(file_path)
        # FIXME: talvez incluir a biblioteca aqui também
        template_contents = self.controller.server.get_generator_template()
        path.write_text(template_contents, encoding="utf-8")
        if not self.is_editing():
            self.sample_gen_path = path

        auto_open = messagebox.askyesno("Abrir arquivo?", "Abrir exercício no editor de texto padrão?")
        if auto_open:
            os.startfile(file_path)
