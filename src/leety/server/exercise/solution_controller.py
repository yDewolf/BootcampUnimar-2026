import json
from pathlib import Path
import time
from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.exercise_model import ExerciseAttempt, ExerciseModel
from leety.common.database.models.user_model import UserModel
from leety.common.dto.attempt_result import AttemptResult, RuntimeErrorAttempt, SolutionStatus, WrongAnswerAttempt
from leety.common.utils.code_runner import CodeRunner
from leety.server.exercise.base_generator import TestCase
from leety.server.exercise.exercise_controller import ExerciseController
from leety.server.sandbox.sandbox_controller import RUNNER_FILENAME, SOLUTION_FILENAME, SandboxController

class SolutionController:
    database: LeetyDatabase
    sandbox_controller: SandboxController

    exercise_controller: ExerciseController

    def __init__(self, database: LeetyDatabase, sandbox_controller: SandboxController, exercise_controller: ExerciseController) -> None:
        self.database = database
        self.sandbox_controller = sandbox_controller
        self.exercise_controller = exercise_controller

    # Attempt CRUD:
    def submit_attempt(self, user_id: int, exercise_id: int, attempt_code: str) -> tuple[bool, AttemptResult]:
        user_data, exercise_data = self._ensure_user_and_exercise(user_id, exercise_id)
        samples = self.exercise_controller.load_samples(exercise_id)
        if not samples:
            raise Exception(f"Missing samples for exercise #{exercise_id}")
        
        is_valid, output = self._validate_attempt(exercise_data, attempt_code, samples)
        correct_results: int = 0
        if is_valid:
            correct_results = len(samples)
        elif output.status == SolutionStatus.RUNTIME_ERROR.value or output.status == SolutionStatus.WRONG_ANSWER.value:
            correct_results = (output.test_case or 1) - 1
        
        attempt_data = ExerciseAttempt(
            id=None, author_id=user_id, exercise_id=exercise_id, valid=is_valid,
            sample_amount=len(samples), solve_time=output.elapsed,
            correct_results=correct_results
        )

        self.database.ex_attempts.add_row(attempt_data)
        if is_valid:
            self._upload_attempt(attempt_data, attempt_code)

        return (is_valid, output)

    def _upload_attempt(self, attempt: ExerciseAttempt, code: str):
        assert attempt.id, "Attempt must have ID setup"
        attempts_folder = self.exercise_attempts_folder(attempt.exercise_id)
        if not attempts_folder.exists():
            attempts_folder.mkdir()

        attempt_file = self.attempt_filename(attempt.author_id, attempt.exercise_id, attempt.id)
        attempt_file.write_text(code, encoding="utf-8")

    def get_user_attempts(self, user_id: int, exercise_id: int) -> list[ExerciseAttempt]:
        user, exercise = self._ensure_user_and_exercise(user_id, exercise_id)
        return self.database.ex_attempts.match_searchable_field({
            ExerciseAttempt.author_id: user.id,
            ExerciseAttempt.exercise_id: exercise.id
        }) or []

    def get_exercise_attempts(self, exercise_id: int) -> list[ExerciseAttempt]:
        return self.database.ex_attempts.match_searchable_field({
            ExerciseAttempt.exercise_id: exercise_id
        }) or []

    # Utils:

    def _ensure_user_and_exercise(self, user_id: int, exercise_id: int) -> tuple[UserModel, ExerciseModel]:
        user_data = self.database.users.get_by_id(user_id)
        if not user_data:
            raise Exception(f"Can't upload attempt as a non existent user. id: {user_id}")
        
        exercise_data = self.exercise_controller.get_exercise(exercise_id)
        if not exercise_data:
            raise Exception(f"Exercise of id {exercise_id} doesn't exist")

        return user_data, exercise_data

    def _run_solution(self, code: str, samples: list[TestCase], timeout: float = 5, memory_limit: int = 64, auto_cleanup: bool = True):
        job_dir = self.sandbox_controller.prepare_solution_folder(code)
        runner = CodeRunner(job_dir / RUNNER_FILENAME)

        start_time = time.perf_counter()
        # TODO: melhorar typesafety desse output
        output, error = runner.run_python(timeout, [json.dumps(samples)])
        elapsed = time.perf_counter() - start_time

        if auto_cleanup:
            self.sandbox_controller.cleanup_job(job_dir)
        return (output, elapsed)

    def _validate_attempt(self, exercise: ExerciseModel, code: str, samples: list[TestCase]) -> tuple[bool, AttemptResult]:
        assert exercise.id, "Exercise wasn't indexed properly"
        
        output, elapsed = self._run_solution(code, samples, timeout=exercise.time_limit, memory_limit=exercise.memory_limit)
        dict_output: dict = json.loads(output)

        output_model = AttemptResult(
            status=SolutionStatus(dict_output["status"]),
            test_case=dict_output.get("test_case"),
            elapsed=elapsed
        )
        match output_model.status:
            case SolutionStatus.ACCEPTED:
                return (True, AttemptResult.from_dict(output_model._data))
            
            case SolutionStatus.RUNTIME_ERROR:
                return (False, RuntimeErrorAttempt(error=dict_output["error"], **output_model._data))

            case SolutionStatus.WRONG_ANSWER:
                return (False, WrongAnswerAttempt(
                    input=dict_output["input"], expected=dict_output["expected"], actual=dict_output["actual"], **output_model._data
                ))
            case _:
                return (False, dict_output)

    # Paths:

    # TODO: talvez mudar isso daqui e seguir a seguinte estrutura:
    # uploads/
    #   - attempts/
    #       - ex_<id>_<code_hash>/
    #           - attempt_<user_id>_<attempt_id>.py
    def exercise_attempts_folder(self, exercise_id: int) -> Path:
        return self.exercise_controller._get_exercise_folder(exercise_id) / "attempts"

    def attempt_filename(self, user_id: int, exercise_id: int, attempt_id: int) -> Path:
        return self.exercise_attempts_folder(exercise_id) / f"attempt_usr{user_id}_att{attempt_id}.py"
