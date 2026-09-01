
# basicamente um wrapper com os controllers necessários para fazer as coisas funcionarem
from pathlib import Path
from typing import Optional

from leety.common.database.db_exceptions import EAdminOnlyAction
from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.exercise_model import BaseExerciseModel, ExerciseAttempt, ExerciseDifficulty, ExerciseModel
from leety.common.database.models.user_model import UserModel
from leety.server.exercise.exercise_controller import ExerciseController
from leety.server.exercise.solution_controller import SolutionController
from leety.server.internal.router_protocol import RouterProtocol
from leety.server.sandbox.sandbox_controller import SandboxController
from leety.server.user.user_controller import UserController

import leety.server.exercise as exercise

EXERCISE_FOLDER: Path = Path(str(exercise.__path__))
INTERNAL_TEMPLATES_FOLDER: Path = EXERCISE_FOLDER / "internal_templates"
class Server(RouterProtocol):
    database: LeetyDatabase

    user_controller: UserController

    sandbox_controller: SandboxController
    exercise_controller: ExerciseController
    solution_controller: SolutionController

    def __init__(self, db_name: str = "test_database", sandbox_root: str = "_sandbox") -> None:
        self.database = LeetyDatabase(db_name)

        self.user_controller = UserController(self.database)

        self.sandbox_controller = SandboxController(
            sandbox_root,
            sample_runner_path=INTERNAL_TEMPLATES_FOLDER / "exercise_sample_runner.py",
            solution_runner_path=INTERNAL_TEMPLATES_FOLDER / "exercise_solution_runner.py",
            sample_lib_path=EXERCISE_FOLDER / "base_generator.py",
        )

        self.exercise_controller = ExerciseController(self.database, self.user_controller, self.sandbox_controller)
        self.solution_controller = SolutionController(self.database, self.sandbox_controller, self.exercise_controller)

    # TODO: talvez enviar de volta as informações dentro de um dict
    # Rotas:

    # UserController:
    def register_user(self, user_data: UserModel): 
        return self.user_controller.register_user(user_data)

    def delete_user(self, user_id: int, password: str): 
        return self.user_controller.delete_user(user_id, password)

    def admin_delete_user(self, user_id: int, admin_id: int, admin_password: str): 
        return self.user_controller.admin_delete_user(user_id, admin_id, admin_password)
         

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
    def get_difficulty(self, id: str) -> Optional[ExerciseDifficulty]: 
        return self.exercise_controller.get_difficulty(id)
    
    def create_exercise_diff(self, admin_user: UserModel, diff_data: ExerciseDifficulty): 
        self._validate_admin_only_act(admin_user, "Only admins can create difficulties")
        return self.exercise_controller.create_exercise_diff(diff_data)


    def modify_difficulty(self, admin_user: UserModel, id: str, capitalized_name: Optional[str] = None, description: Optional[str] = None) -> bool:
        self._validate_admin_only_act(admin_user, "Only admins can modify difficulties")
        return self.exercise_controller.modify_difficulty(id, capitalized_name, description)


    def delete_difficulty(self, admin_user: UserModel, id: str):
        self._validate_admin_only_act(admin_user, "Only admins can delete difficulties")
        return self.exercise_controller.delete_difficulty(id)

    # Cria um exercício com os dados específicos
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


    def create_exercise(self, admin_user: UserModel, exercise_data: ExerciseModel) -> bool: 
        self._validate_admin_only_act(admin_user, "Only admins can create exercises")
        assert admin_user.id
        return self.exercise_controller.create_exercise(admin_user.id, exercise_data)

    def modify_exercise(self, admin_user: UserModel, exercise_id: int, new_data: BaseExerciseModel) -> bool: 
        self._validate_admin_only_act(admin_user, "Only admins can modify exercises")
        assert admin_user.id
        return self.exercise_controller.modify_exercise(admin_user.id, exercise_id, new_data)

    def upload_sample_gen_code(self, admin_user: UserModel, exercise_id: int, code: str) -> bool:
        self._validate_admin_only_act(admin_user, "Only admins can modify exercises")
        assert admin_user.id
        return self.exercise_controller.upload_sample_gen_code(exercise_id, code)

    def delete_exercise(self, admin_user: UserModel, exercise_id: int): 
        self._validate_admin_only_act(admin_user, "Only admins can modify exercises")
        assert admin_user.id
        return self.exercise_controller.delete_exercise(exercise_id)


    # SolutionController:
    # faz upload do código de resolução de um exercício específico
    # retorna o resultado, se o código funciona ou não
    def submit_attempt(self, user: UserModel, exercise_id: int, attempt_code: str) -> tuple[bool, dict]:
        assert user.id, "User must have an id to submit attempts"
        return self.solution_controller.submit_attempt(user.id, exercise_id, attempt_code)

    # retorna todos os códigos que o usuário fez upload em um exercício
    def get_user_attempts(self, user_id: int, exercise_id: int) -> list[ExerciseAttempt]: 
        return self.solution_controller.get_user_attempts(user_id, exercise_id)

    def get_exercise_attempts(self, exercise_id: int) -> list[ExerciseAttempt]: 
        return self.solution_controller.get_exercise_attempts(exercise_id)


    def _validate_admin_only_act(self, admin: UserModel, message: str):
        if not self.user_controller.is_admin(admin.id):
            raise EAdminOnlyAction(message)
    