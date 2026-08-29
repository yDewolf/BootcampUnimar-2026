
from pathlib import Path

from leety.common.utils.str_utils import split_in_lines
from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.exercise_model import ExerciseModel
from leety.server.exercise.template_utils import TemplateUtils
from leety.server.sandbox.sandbox_controller import GENERATOR_FILENAME, SOLUTION_FILENAME, SandboxController


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

        annotations = TemplateUtils.extract_solution_annotations(sample_gen_code)
        # TODO: trocar o exercise_data.diff_id pelo nome da dificuldade
        template_header: str = TemplateUtils.create_exercise_header(
            exercise_data.title, str(exercise_data.id), 
            exercise_data.context, exercise_data.diff_id
        )
        solution_template = TemplateUtils.create_solution_template(
            annotations, 
            template_header=template_header, 
            function_comments="#".join(split_in_lines("Implemente essa função para solucionar o problema descrito."))
        )

        sol_template_file = exercise_folder / SOLUTION_FILENAME
        sol_template_file.write_text(solution_template, encoding="utf-8")
        exercise_data._sample_gen_code = None
        exercise_data.sample_gen_path = str(code_file)
        exercise_data.solution_template_path = str(sol_template_file)
