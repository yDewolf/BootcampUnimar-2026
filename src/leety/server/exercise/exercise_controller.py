
import json
from pathlib import Path
import time
from typing import Any, Optional

from leety.common.database.db_exceptions import EAdminOnlyAction
from leety.common.database.models.user_model import UserModel
from leety.common.utils.code_runner import CodeRunner
from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.exercise_model import BaseExerciseModel, ExerciseDifficulty, ExerciseModel
from leety.common.utils.type_utils import is_valid_typeddict
from leety.server.exercise.base_generator import TestCase
from leety.server.exercise.template_utils import TemplateUtils
from leety.server.sandbox.sandbox_controller import GENERATOR_FILENAME, RUNNER_FILENAME, SAMPLE_PATH, SOLUTION_FILENAME, SandboxController
from leety.server.user.user_controller import UserController

DEFAULT_BENCHMARK_SAMPLES = 50
class ExerciseController:
    database: LeetyDatabase
    user_controller: UserController
    sandbox_controller: SandboxController

    @property
    def exercise_uploads(self) -> Path:
        return self.database.file_manager.uploads_path / "exercises"

    def __init__(self, database: LeetyDatabase, user_controller: UserController, sandbox_controller: SandboxController) -> None:
        self.database = database
        self.user_controller = user_controller
        self.sandbox_controller = sandbox_controller
        self._setup_folders()

    def _setup_folders(self):
        self.exercise_uploads.mkdir(exist_ok=True)

    # Difficulty CRUD
    def create_exercise_diff(self, diff_data: ExerciseDifficulty) -> bool:
        if self.get_difficulty(diff_data.id or ""):
            raise Exception(f"Difficulty #{diff_data.id} is already registered")
        
        diff_data.validate()
        self.database.ex_difficulties.add_row(diff_data)
        return True
    
    def get_difficulty(self, id: str) -> Optional[ExerciseDifficulty]:
        return self.database.ex_difficulties.get_by_id(id)

    def modify_difficulty(self, id: str, capitalized_name: Optional[str] = None, description: Optional[str] = None) -> bool:
        difficulty = self.database.ex_difficulties.get_by_id(id)
        if not difficulty:
            raise Exception(f"Couldn't find difficulty with id: {id}")
        
        difficulty.capitalized_name = capitalized_name or difficulty.capitalized_name
        difficulty.description = description or difficulty.description
        return True

    def delete_difficulty(self, id: str):
        self.database.ex_difficulties.remove_row_id(id)


    # Exercise CRUD:
    
    # Registra o exercício no banco de dados e retorna se o código de geração é válido
    def create_exercise(self, author_id: int, exercise_data: ExerciseModel) -> bool:
        if not self.user_controller.is_admin(author_id):
            raise EAdminOnlyAction(f"Author must be an admin to create exercises. id: {author_id}")

        sample_gen_code = exercise_data._sample_gen_code
        if not sample_gen_code:
            raise Exception(f"Missing Sample Generator Code for exercise {exercise_data}")
        
        self.database.exercises.add_row(exercise_data)
        assert exercise_data.id, "Exercise ID wasn't auto filled"
        self._setup_exercise_folder(exercise_data.id)
        exercise_data._sample_gen_code = None

        is_valid = self.upload_sample_gen_code(exercise_data.id, sample_gen_code)
        return is_valid

    def get_exercise(self, exercise_id: int) -> Optional[ExerciseModel]:
        return self.database.exercises.get_by_id(exercise_id)

    def get_exercise_by_diff(self, diff_id: str) -> list[ExerciseModel]:
        return self.database.exercises.match_searchable_field({
            ExerciseModel.diff_id: diff_id
        }) or []

    def modify_exercise(self, author_id: int, exercise_id: int, new_data: BaseExerciseModel) -> bool:
        if not self.user_controller.is_admin(author_id):
            raise EAdminOnlyAction(f"To modify exercises the user must be an admin. id: {author_id}")
        
        exercise = self.database.exercises.get_by_id(exercise_id)
        if not exercise:
            raise Exception(f"Couldn't find Exercise with id: {exercise_id}")
        
        assert exercise.contributors != None
        if not author_id in exercise.contributors:
            exercise.contributors.append(author_id)
        
        filtered_data = dict(new_data._data)
        if "id" in filtered_data: del filtered_data["id"]
        if "author_id" in filtered_data: del filtered_data["author_id"]
        for key in new_data._data:
            if key in ("id", "author_id"): continue
            if new_data._data[key] is None:
                del filtered_data[key]

        exercise._set_from_dict(filtered_data)
        # Atualizar o template de solução
        code_file = self.exercise_sample_gen_path(exercise_id)
        if code_file.exists():
            code = code_file.read_text(encoding="utf-8")
            self._upload_solution_template(code, exercise)
        
        return True

    # TODO: teoricamente isso aqui também precisaria de autoria
    def upload_sample_gen_code(self, exercise_id: int, sample_gen: str) -> bool:
        exercise_data = self.get_exercise(exercise_id)
        if not exercise_data:
            return False

        is_generator_valid = self._test_generator(sample_gen, exercise_id)
        exercise_data.is_valid = is_generator_valid

        if not is_generator_valid:
            return False

        output, benchmark_time = self._run_generator(sample_gen, DEFAULT_BENCHMARK_SAMPLES, timeout=90)
        exercise_data.benchmark_time = benchmark_time
        exercise_data.benchmark_samples = DEFAULT_BENCHMARK_SAMPLES
        
        sample_file = self._upload_generator(sample_gen, exercise_id)
        solution_file = self._upload_solution_template(sample_gen, exercise_data)
        # TODO: talvez remover isso aqui já que esses caminhos são determinísticos
        # exercise_data.sample_gen_path = str(sample_file)
        # exercise_data.solution_template_path = str(solution_file)
        return True

    def delete_exercise(self, exercise_id: int):
        self.database.exercises.remove_row_id(exercise_id)

    # Exercise Sample "CRUD":
    # TODO: lembrar de chamar isso aqui no servidor quando criar/modificar o exercício
    def generate_samples_for_exercise(self, exercise_id: int, amount: int = 50, timeout: float = 10, auto_cleanup: bool = True) -> Optional[list[TestCase]]:
        exercise = self.get_exercise(exercise_id)
        if not exercise:
            raise Exception(f"Exercise of id {exercise_id} doesn't isn't registered in database")

        sample_path = self.exercise_sample_gen_path(exercise_id)
        if not sample_path.exists():
            raise Exception(f"Exercise #{exercise_id} doesn't have a valid sample generator")
        
        code = sample_path.read_text(encoding="utf-8")
        output, time_elapsed = self._run_generator(code, amount, timeout, auto_cleanup=auto_cleanup)

        sample_path = self.exercise_sample_path(exercise_id)
        sample_path.write_text(output, encoding="utf-8")

        try:
            parsed: Optional[list[TestCase]] = json.loads(output)
            print(f"DEBUG: Generated {len(parsed) if parsed else 0} samples for exercise #{exercise_id} in {(time_elapsed * 1000):.2f}ms")
        except ValueError:
            parsed = None
            print(f"WARNING: Failed to generate valid samples for exercise #{exercise_id}")
        
        return parsed

    def load_samples(self, exercise_id: int) -> Optional[list[TestCase]]:
        exercise = self.get_exercise(exercise_id)
        if not exercise:
            raise Exception(f"Exercise of id {exercise_id} doesn't isn't registered in database")

        sample_path = self.exercise_sample_path(exercise_id)
        if not sample_path.exists():
            raise Exception(f"Couldn't find samples for exercise #{exercise_id} in {sample_path}")

        json_str = sample_path.read_text(encoding="utf-8")
        try:
            samples: list[TestCase] = json.loads(json_str)
            return samples
        except Exception as e:
            print(f"ERROR: couldn't parse samples for exercise #{exercise_id}", e)
            return None


    def _run_generator(self, code: str, sample_amount: int = 10, timeout: float = 1, auto_cleanup: bool = True) -> tuple[str, float]:
        job_dir = self.sandbox_controller.prepare_generator_folder(code)
        code_path = job_dir / GENERATOR_FILENAME
        runner = CodeRunner(job_dir / RUNNER_FILENAME)

        start_time = time.perf_counter()
        output = runner.run_python(timeout, [code_path, "SampleGenerator", sample_amount])
        elapsed = time.perf_counter() - start_time

        if auto_cleanup:
            self.sandbox_controller.cleanup_job(job_dir)
        return (output, elapsed)

    def _test_generator(self, code: str, exercise_id: Optional[int] = None) -> bool:
        exercise_id = exercise_id or -1
        try:
            output, elapsed = self._run_generator(code, sample_amount=5, timeout=10)
            test_cases  = json.loads(output)
            if not isinstance(test_cases, list):
                raise Exception("test_cases should be a list of TestCase (TypedDict)")
            
            for idx, case in enumerate(test_cases):
                is_valid = is_valid_typeddict(case, TestCase)
                if not is_valid:
                    raise Exception(f"Case {idx} is not a valid TestCase. Data: {case}")
            
            return True
        
        except Exception as e:
            print(f"ERROR: generator code for exercise #{exercise_id} is not valid. {e}")
            return False

    # Utils:

    def _setup_exercise_folder(self, exercise_id: int) -> Path:
        exercise_folder = self._get_exercise_folder(exercise_id)
        exercise_folder.mkdir(exist_ok=True)
        return exercise_folder

    def _upload_generator(self, sample_gen_code: str, exercise_id: int) -> Optional[Path]:
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

        contributors = []
        for id in (exercise_data.contributors or [] + [exercise_data.author_id] if exercise_data.author_id else []):
            user = self.user_controller.get_user(id)
            contributors.append(user.username if user else id)

        solution_template = TemplateUtils.create_solution_template(
            annotations, 
            template_header=template_header,
            authors=contributors,
            function_comments=TemplateUtils.create_function_comments(comment="Implemente essa função para solucionar o problema descrito.")
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
