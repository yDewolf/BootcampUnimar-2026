from leety.common.database.models.exercise_model import ExerciseDifficulty, ExerciseModel
from leety.common.database.models.user_model import UserModel
from leety.common.internals.database.csvbase import Database
from leety.common.internals.database.protocols.csv_table import IndexableTable

# Definição do banco de dados do Leety
class LeetyDatabase(Database):
    users: IndexableTable[UserModel]

    ex_difficulties: IndexableTable[ExerciseDifficulty]
    exercises: IndexableTable[ExerciseModel]

