from pathlib import Path
import sys
from typing import Optional
import threading
import time

from leety.common.database.db_exceptions import EAdminOnlyAction
from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.exercise_model import BaseExerciseModel, ExerciseAttempt, ExerciseDifficulty, ExerciseModel
from leety.common.database.models.user_model import UserModel
from leety.common.dto.attempt_result import AttemptResult
from leety.common.utils.path_utils import ROOT_PATH
from leety.server.exercise.exercise_controller import ExerciseController
from leety.server.exercise.solution_controller import SolutionController
from leety.server.internal.router_protocol import RouterProtocol
from leety.server.sandbox.sandbox_controller import SandboxController
from leety.server.user.user_controller import UserController

import leety.server.exercise as exercise
import leety.common as common

EXERCISE_FOLDER: Path = ROOT_PATH / "_internal" / "exercise" if getattr(sys, "frozen", False) else  Path(exercise.__file__).resolve().parent 
INTERNAL_TEMPLATES_FOLDER: Path = EXERCISE_FOLDER / "internal_templates"
GENERATOR_TEMPLATE_PATH: Path = ROOT_PATH / "exercise" / "templates" / "generator.py" if getattr(sys, "frozen", False) else Path(common.__file__).resolve().parent / "exercise" / "templates" / "generator.py"
DATABASE_SAVE_INTERVAL: float = 5 * 60
# basicamente um wrapper com os controllers necessários para fazer as coisas funcionarem

class Server(RouterProtocol):
    database: LeetyDatabase
    db_save_thread: threading.Thread

    user_controller: UserController

    sandbox_controller: SandboxController
    exercise_controller: ExerciseController
    solution_controller: SolutionController

    def _save_db_worker(self):
        while True:
            self.database.save()
            time.sleep(DATABASE_SAVE_INTERVAL)

    def __init__(self, db_name: str = "test_database", sandbox_root: str = "_sandbox") -> None:
        self.database = LeetyDatabase.from_folder(db_name)
        self.user_controller = UserController(self.database)

        self.sandbox_controller = SandboxController(
            sandbox_root,
            sample_runner_path=INTERNAL_TEMPLATES_FOLDER / "exercise_sample_runner.py",
            solution_runner_path=INTERNAL_TEMPLATES_FOLDER / "exercise_solution_runner.py",
            sample_lib_path=EXERCISE_FOLDER / "base_generator.py",
        )

        self.exercise_controller = ExerciseController(self.database, self.user_controller, self.sandbox_controller)
        self.solution_controller = SolutionController(self.database, self.sandbox_controller, self.exercise_controller)
        self._setup_and_start_db_thread()

    def _setup_and_start_db_thread(self):
        self.db_save_thread = threading.Thread(target=self._save_db_worker, daemon=True)
        self.db_save_thread.start()

    # TODO: talvez enviar de volta as informações dentro de um dict
    # Rotas:

    # UserController:
    def register_user(self, username: str, password: str):
        user_data = UserModel(id=None, username=username, password=password) 
        self.user_controller.register_user(user_data)
        self.database.save()

    def delete_user(self, user_id: int, password: str): 
        return self.user_controller.delete_user(user_id, password)

    def admin_delete_user(self, user_id: int, admin_id: int, admin_password: str): 
        return self.user_controller.admin_delete_user(user_id, admin_id, admin_password)
         
    def get_user_data(self, user_id: int) -> Optional[UserModel]:
        data = self.user_controller.get_user(user_id)
        if not data: return None

        user_data = UserModel(id=user_id, username=data.username, password=None)
        return user_data

    def username_exists(self, username: str) -> bool: 
        return self.user_controller.is_username_registered(username)

    def user_exists(self, user_id: int) -> bool: 
        return self.user_controller.user_exists(user_id)

    # retorna o UserModel se estiver tudo ok
    def log_as_user(self, username: str, password: str) -> Optional[UserModel]: 
        user_data = self.user_controller.get_user_by_username(username)
        if not user_data:
            return None

        # TODO: o certo seria a senha estar encriptada no banco
        if user_data.password != password:
            return None

        return user_data

    def is_admin(self, user_id: int) -> bool:
        return self.user_controller.is_admin(user_id)

    # ExerciseController:
    def get_difficulties(self) -> list[ExerciseDifficulty]:
        return self.database.ex_difficulties.rows

    def get_difficulty(self, id: str) -> Optional[ExerciseDifficulty]: 
        return self.exercise_controller.get_difficulty(id)
    
    def create_exercise_diff(self, admin_user: UserModel, diff_data: ExerciseDifficulty): 
        self._validate_admin_only_act(admin_user, "Only admins can create difficulties")
        self.exercise_controller.create_exercise_diff(diff_data)
        self.database.save()


    def modify_difficulty(self, admin_user: UserModel, id: str, capitalized_name: Optional[str] = None, description: Optional[str] = None) -> bool:
        self._validate_admin_only_act(admin_user, "Only admins can modify difficulties")
        result = self.exercise_controller.modify_difficulty(id, capitalized_name, description)
        self.database.save()
        return result


    def delete_difficulty(self, admin_user: UserModel, id: str):
        self._validate_admin_only_act(admin_user, "Only admins can delete difficulties")
        return self.exercise_controller.delete_difficulty(id)

    # Cria um exercício com os dados específicos
    def get_all_exercises(self) -> list[ExerciseModel]:
        return self.database.exercises.rows

    def get_exercises(self, diff_id: str) -> list[ExerciseModel]:
        return self.exercise_controller.get_exercise_by_diff(diff_id)
    
    def get_exercise(self, exercise_id: int) -> Optional[ExerciseModel]:
        return self.exercise_controller.get_exercise(exercise_id)

    def get_exercise_template(self, exercise_id: int) -> Optional[str]: 
        if not self.exercise_controller.get_exercise(exercise_id):
            return None
        
        template_path = self.exercise_controller.exercise_solution_template(exercise_id)
        if not template_path.exists():
            return None
        
        return template_path.read_text(encoding="utf-8")

    def get_exercise_code(self, exercise_id: int) -> Optional[str]: 
        if not self.exercise_controller.get_exercise(exercise_id):
            return None
        
        code_path = self.exercise_controller.exercise_sample_gen_path(exercise_id)
        if not code_path.exists():
            return None
        
        return code_path.read_text(encoding="utf-8")

    def create_exercise(self, admin_user: UserModel, exercise_data: ExerciseModel) -> tuple[bool, int]: 
        self._validate_admin_only_act(admin_user, "Only admins can create exercises")
        assert admin_user.id
        is_valid, id = self.exercise_controller.create_exercise(admin_user.id, exercise_data)
        self.database.save()
        return is_valid, id

    def modify_exercise(self, admin_user: UserModel, exercise_id: int, new_data: BaseExerciseModel) -> bool: 
        self._validate_admin_only_act(admin_user, "Only admins can modify exercises")
        assert admin_user.id
        result = self.exercise_controller.modify_exercise(admin_user.id, exercise_id, new_data)
        self.database.save()
        return result

    def upload_sample_gen_code(self, admin_user: UserModel, exercise_id: int, code: str) -> bool:
        self._validate_admin_only_act(admin_user, "Only admins can modify exercises")
        assert admin_user.id
        result = self.exercise_controller.upload_sample_gen_code(exercise_id, code)
        self.database.save()
        return result

    def delete_exercise(self, admin_user: UserModel, exercise_id: int): 
        self._validate_admin_only_act(admin_user, "Only admins can modify exercises")
        assert admin_user.id
        return self.exercise_controller.delete_exercise(exercise_id)


    def get_generator_template(self) -> str:
        return GENERATOR_TEMPLATE_PATH.read_text()


    # SolutionController:
    def is_exercise_done(self, user_id: int, exercise_id: int) -> bool: 
        return self.solution_controller.is_exercise_done(user_id, exercise_id)        

    # faz upload do código de resolução de um exercício específico
    # retorna o resultado, se o código funciona ou não
    def submit_attempt(self, user: UserModel, exercise_id: int, attempt_code: str) -> tuple[bool, AttemptResult]:
        assert user.id, "User must have an id to submit attempts"
        result = self.solution_controller.submit_attempt(user.id, exercise_id, attempt_code)
        self.database.save()
        return result

    # retorna todos os códigos que o usuário fez upload em um exercício
    def get_user_attempts(self, user_id: int, exercise_id: int) -> list[ExerciseAttempt]: 
        return self.solution_controller.get_user_attempts(user_id, exercise_id)

    def get_exercise_attempts(self, exercise_id: int, valid_attempts_only: bool) -> list[ExerciseAttempt]: 
        return self.solution_controller.get_exercise_attempts(exercise_id, valid_attempts_only)


    def _validate_admin_only_act(self, admin: UserModel, message: str):
        if not self.user_controller.is_admin(admin.id):
            raise EAdminOnlyAction(message)
    