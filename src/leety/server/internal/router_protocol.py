from typing import Optional, Protocol

from leety.common.database.models.exercise_model import BaseExerciseModel, ExerciseAttempt, ExerciseDifficulty, ExerciseModel
from leety.common.database.models.user_model import UserModel

# TODO: implementar esse router dps
# TODO: talvez fazer um sistema de autenticação simples com token JWT
class RouterProtocol(Protocol):
    def register_user(self, username: str, password: str): raise NotImplementedError()
    def delete_user(self, user_id: int, password: str): raise NotImplementedError()
    def admin_delete_user(self, user_id: int, admin_id: int, admin_password: str): raise NotImplementedError()

    def username_exists(self, username: str) -> bool: raise NotImplementedError()
    def user_exists(self, user_id: int) -> bool: raise NotImplementedError()

    # retorna o UserModel se estiver tudo ok
    def log_as_user(self, username: str, password: str) -> Optional[UserModel]: raise NotImplementedError()
    def is_admin(self, user_id: int) -> bool: raise NotImplementedError()

    def get_difficulties(self) -> list[ExerciseDifficulty]: raise NotImplementedError()
    def get_difficulty(self, id: str) -> Optional[ExerciseDifficulty]: raise NotImplementedError()
    def create_exercise_diff(self, admin_user: UserModel, diff_data: ExerciseDifficulty): raise NotImplementedError()
    def modify_difficulty(self, admin_user: UserModel, id: str, capitalized_name: Optional[str] = None, description: Optional[str] = None) -> bool: raise NotImplementedError()
    def delete_difficulty(self, admin_user: UserModel, id: str): raise NotImplementedError()

    # Cria um exercício com os dados específicos
    def get_exercises(self, diff_id: str) -> list[ExerciseModel]: raise NotImplementedError()
    def get_exercise(self, exercise_id: int) -> Optional[ExerciseModel]: raise NotImplementedError()

    def get_exercise_template(self, exercise_id: int) -> str: raise NotImplementedError()

    def create_exercise(self, admin_user: UserModel, exercise_data: ExerciseModel) -> bool: raise NotImplementedError()
    def modify_exercise(self, admin_user: UserModel, exercise_id: int, new_data: BaseExerciseModel) -> bool: raise NotImplementedError()
    def upload_sample_gen_code(self, admin_user: UserModel, exercise_id: int, code: str) -> bool: raise NotImplementedError()
    def delete_exercise(self, admin_user: UserModel, exercise_id: int): raise NotImplementedError()

    # faz upload do código de resolução de um exercício específico
    # retorna o resultado, se o código funciona ou não
    def submit_attempt(self, user: UserModel, exercise_id: int, attempt_code: str) -> tuple[bool, dict]: raise NotImplementedError()
    # retorna todos os códigos que o usuário fez upload em um exercício
    def get_user_attempts(self, user_id: int, exercise_id: int) -> list[ExerciseAttempt]: raise NotImplementedError()
    def get_exercise_attempts(self, exercise_id: int) -> list[ExerciseAttempt]: raise NotImplementedError()
