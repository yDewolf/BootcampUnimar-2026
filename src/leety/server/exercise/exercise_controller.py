
from pathlib import Path

from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.exercise_model import ExerciseModel
from leety.server.sandbox.sandbox_controller import GENERATOR_FILENAME, SandboxController


class ExerciseController:
    database: LeetyDatabase
    sandbox_controller: SandboxController

    @property
    def exercise_uploads(self) -> Path:
        return self.database.file_manager.uploads_path / "exercises"

    def __init__(self, database: LeetyDatabase, sandbox_controller: SandboxController) -> None:
        self.database = database
        self.sandbox_controller = sandbox_controller
        self._setup_folders()

    def _setup_folders(self):
        self.exercise_uploads.mkdir(exist_ok=True)

    def create_exercise(self, exercise_data: ExerciseModel):
        sample_gen_code = exercise_data._sample_gen_code
        if not sample_gen_code:
            raise Exception(f"Missing Sample Generator Code for exercise {exercise_data}")
        
        self.database.exercises.add_row(exercise_data)

        exercise_folder = self.exercise_uploads / f"ex_{str(exercise_data.id)}"
        exercise_folder.mkdir(exist_ok=True)

        code_file = exercise_folder / GENERATOR_FILENAME
        code_file.write_text(sample_gen_code, encoding="utf-8")

        exercise_data._sample_gen_code = None
        exercise_data.sample_gen_path = str(code_file)
