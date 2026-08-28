from typing import Protocol

# TODO: implementar esse router dps
# TODO: talvez fazer um sistema de autenticação simples com token JWT
class RouterProtocol(Protocol):
    def register_user(self, username: str, password: str): pass
    def delete_user(self, user_id: int): pass

    # retorna o UserModel se estiver tudo ok
    def log_as_user(self, username: str, password: str): pass
    def user_exists(self, username: str) -> bool: return False

    # retorna os ExerciseModels que existem no banco
    def get_exercises(self, filter) -> list: return []
    def get_exercise(self, exercise_id: int): pass

    # faz upload do código de resolução de um exercício específico
    # retorna o resultado, se o código funciona ou não
    def submit_code(self, code: str, exercise_id: int, user): pass
    # retorna todos os códigos que o usuário fez upload em um exercício
    def get_user_attempts(self, user_id: int, exercise_id: int): pass

    # Cria um exercício com os dados específicos
    def create_exercise(self, admin_user, exercise_data): pass
    def delete_exercise(self, admin_user, exercise_id: int): pass

    # substitui os dados de um exercício específico para exercise_data
    def alter_exercise(self, admin_user, exercise_data, exercise_id: int): pass
