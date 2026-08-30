
import json
from pathlib import Path
import time
from typing import Any, Optional

from leety.common.utils.code_runner import CodeRunner
from leety.common.utils.str_utils import split_in_lines
from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.exercise_model import BaseExerciseModel, ExerciseDifficulty, ExerciseModel
from leety.server.exercise.base_generator import TestCase
from leety.server.exercise.template_utils import TemplateUtils
from leety.server.sandbox.sandbox_controller import GENERATOR_FILENAME, RUNNER_FILENAME, SAMPLE_PATH, SOLUTION_FILENAME, SandboxController


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

    # Difficulty CRUD
    def create_exercise_diff(self, diff_data: ExerciseDifficulty):
        diff_data.validate()
        self.database.ex_difficulties.add_row(diff_data)
    
    def get_difficulty(self, id: str) -> Optional[ExerciseDifficulty]:
        return self.database.ex_difficulties.get_by_id(id)

    def modify_difficulty(self, id: str, capitalized_name: Optional[str] = None, description: Optional[str] = None) -> bool:
        difficulty = self.database.ex_difficulties.get_by_id(id)
        if not difficulty:
            return False
        
        difficulty.capitalized_name = capitalized_name or difficulty.capitalized_name
        difficulty.description = description or difficulty.description
        return True

    def delete_difficulty(self, id: str):
        self.database.ex_difficulties.remove_row_id(id)


    # Exercise CRUD:
    def create_exercise(self, exercise_data: ExerciseModel):
        sample_gen_code = exercise_data._sample_gen_code
        if not sample_gen_code:
            raise Exception(f"Missing Sample Generator Code for exercise {exercise_data}")
        
        self.database.exercises.add_row(exercise_data)
        assert exercise_data.id, "Exercise ID wasn't auto filled"
        self._setup_exercise_folder(exercise_data.id)

        code_file = self._upload_generator(sample_gen_code, exercise_data.id)
        sol_template_file = self._upload_solution_template(sample_gen_code, exercise_data)
        
        exercise_data._sample_gen_code = None
        # TODO: talvez remover isso aqui já que esses caminhos são determinísticos
        exercise_data.sample_gen_path = str(code_file)
        exercise_data.solution_template_path = str(sol_template_file)

    def get_exercise(self, exercise_id: int) -> Optional[ExerciseModel]:
        return self.database.exercises.get_by_id(exercise_id)

    def modifiy_exercise(self, exercise_id: int, new_data: BaseExerciseModel) -> bool:
        exercise = self.database.exercises.get_by_id(exercise_id)
        if not exercise:
            return False
        
        filtered_data = dict(new_data._data)
        del filtered_data["id"]
        for key in new_data._data:
            if key == "id": continue
            if new_data._data[key] is None:
                del filtered_data[key]

        exercise._set_from_dict(filtered_data)
        return True

    def reupload_sample_code(self, exercise_id: int, sample_gen: str) -> bool:
        exercise_data = self.get_exercise(exercise_id)
        if not exercise_data:
            return False

        sample_file = self.exercise_sample_gen_path(exercise_id)
        sample_file.write_text(sample_gen)

        solution_file = self._upload_solution_template(sample_gen, exercise_data)
        exercise_data.sample_gen_path = str(sample_file)
        exercise_data.solution_template_path = str(solution_file)
        return True

    def delete_exercise(self, exercise_id: int):
        self.database.exercises.remove_row_id(exercise_id)

    # Exercise Sample "CRUD":
    def generate_samples_for_exercise(self, exercise_id: int, amount: int = 50, timeout: float = 10, auto_cleanup: bool = True) -> str:
        exercise = self.get_exercise(exercise_id)
        if not exercise:
            raise Exception(f"Exercise of id {exercise_id} doesn't isn't registered in database")

        sample_path = self.exercise_sample_gen_path(exercise_id)
        code = sample_path.read_text(encoding="utf-8")
        output, time_elapsed = self._run_generator(code, exercise_id, amount, timeout, auto_cleanup=auto_cleanup)
        print(f"DEBUG: Generated {amount} samples for exercise #{exercise_id} in {time_elapsed:.2f}ms")

        sample_path = self.exercise_sample_path(exercise_id)
        sample_path.write_text(output, encoding="utf-8")

        parsed = json.loads(output)
        return parsed

    def load_samples(self, exercise_id: int) -> Optional[list[TestCase]]:
        exercise = self.get_exercise(exercise_id)
        if not exercise:
            raise Exception(f"Exercise of id {exercise_id} doesn't isn't registered in database")

        sample_path = self.exercise_sample_path(exercise_id)
        if not sample_path.exists():
            raise Exception(f"Couldn't find samples for exercise #{exercise_id} in {sample_path}")

        json_str = sample_path.read_text(encoding="utf-8")
        samples: list[TestCase] = json.loads(json_str)
        return samples


    def _run_generator(self, code: str, exercise_id: int, sample_amount: int = 10, timeout: float = 1, auto_cleanup: bool = True) -> tuple[str, float]:
        job_dir = self.sandbox_controller.prepare_generator_folder(code, str(exercise_id))
        code_path = job_dir / GENERATOR_FILENAME
        runner = CodeRunner(job_dir / RUNNER_FILENAME)

        start_time = time.process_time()
        output = runner.run_python(timeout, [code_path, "SampleGenerator", sample_amount])
        elapsed = time.process_time() - start_time

        if auto_cleanup:
            self.sandbox_controller.cleanup_job(job_dir)
        return (output, elapsed)

    # Utils:

    def _setup_exercise_folder(self, exercise_id: int) -> Path:
        exercise_folder = self._get_exercise_folder(exercise_id)
        exercise_folder.mkdir(exist_ok=True)
        return exercise_folder

    def _upload_generator(self, sample_gen_code: str, exercise_id: int) -> Path:
        code_file = self.exercise_sample_gen_path(exercise_id)
        code_file.write_text(sample_gen_code, encoding="utf-8")
        return code_file

    def _upload_solution_template(self, sample_gen_code: str, exercise_data: ExerciseModel) -> Path:
        assert exercise_data.id
        
        annotations = TemplateUtils.extract_solution_annotations(sample_gen_code)
        diff = self.get_difficulty(exercise_data.diff_id)
        template_header: str = TemplateUtils.create_exercise_header(
            exercise_data.title, str(exercise_data.id), 
            exercise_data.context, diff.capitalized_name if diff else exercise_data.diff_id
        )
        solution_template = TemplateUtils.create_solution_template(
            annotations, 
            template_header=template_header, 
            function_comments="#".join(split_in_lines("Implemente essa função para solucionar o problema descrito."))
        )

        sol_template_file = self.exercise_solution_template(exercise_data.id)
        sol_template_file.write_text(solution_template, encoding="utf-8")
        return sol_template_file

    def _get_exercise_folder(self, exercise_id: int):
        return self.exercise_uploads / f"ex_{str(exercise_id)}"

    # Paths:
    def exercise_sample_path(self, exercise_id: int) -> Path:
        return self._get_exercise_folder(exercise_id) / SAMPLE_PATH

    def exercise_sample_gen_path(self, exercise_id: int) -> Path:
        return self._get_exercise_folder(exercise_id) / GENERATOR_FILENAME

    def exercise_solution_template(self, exercise_id: int) -> Path:
        return self._get_exercise_folder(exercise_id) / SOLUTION_FILENAME
