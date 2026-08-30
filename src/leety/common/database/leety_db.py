from pathlib import Path

from leety.common.database.models.exercise_model import ExerciseAttempt, ExerciseDifficulty, ExerciseModel
from leety.common.database.models.user_model import UserModel
from leety.common.internals.database.csvbase import Database
from leety.common.internals.database.database_file import DBFileManager
from leety.common.internals.database.protocols.csv_table import IndexableTable

class LeetyFileManager(DBFileManager):
    @property
    def uploads_path(self) -> Path:
        return self.root_path / "uploads"
    
    def setup_folders(self):
        super().setup_folders()
        self.uploads_path.mkdir(exist_ok=True)
    

# Definição do banco de dados do Leety
class LeetyDatabase(Database):
    def __init__(self, db_path: str | Path) -> None:
        super().__init__(db_path, file_manager=LeetyFileManager(self, db_path))

    users: IndexableTable[UserModel]

    ex_difficulties: IndexableTable[ExerciseDifficulty]
    exercises: IndexableTable[ExerciseModel]

    ex_attempts: IndexableTable[ExerciseAttempt]

    @property
    def file_manager(self) -> LeetyFileManager:  
        return super().file_manager # type: ignore
