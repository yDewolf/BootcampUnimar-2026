import json
from pathlib import Path
import time

from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.exercise_model import ExerciseAttempt, ExerciseModel
from leety.common.database.models.user_model import UserModel
from leety.common.utils.code_runner import CodeRunner
from leety.server.exercise.base_generator import TestCase
from leety.server.exercise.exercise_controller import ExerciseController
from leety.server.exercise.template_utils import SolutionStatus
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
    def upload_attempt(self, user_id: int, exercise_id: int, code_attempt: str) -> tuple[bool, dict]:
        user_data = self.database.users.get_by_id(user_id)
        if not user_data:
            raise Exception(f"Can't upload attempt as a non existent user. id: {user_id}")
        
        exercise_data = self.exercise_controller.get_exercise(exercise_id)
        if not exercise_data:
            raise Exception(f"Exercise of id {exercise_id} doesn't exist")


        samples = self.exercise_controller.load_samples(exercise_id)
        if not samples:
            raise Exception(f"Missing samples for exercise #{exercise_id}")
        
        is_valid, output = self._validate_attempt(exercise_data, code_attempt, samples)
        correct_results: int = 0
        if is_valid:
            correct_results = len(samples)
        elif output["status"] == SolutionStatus.RUNTIME_ERROR.value or output["status"] == SolutionStatus.WRONG_ANSWER.value:
            correct_results = len(samples) - output["test_case"]
        
        attempt_data = ExerciseAttempt(
            id=None, author_id=user_id, exercise_id=exercise_id, valid=is_valid,
            sample_amount=len(samples), solve_time=output["elapsed"],
            correct_results=correct_results
        )

        self.database.ex_attempts.add_row(attempt_data)
        return (is_valid, output)


    def _run_solution(self, code: str, samples: list[TestCase], timeout: float = 5, memory_limit: int = 64, auto_cleanup: bool = True):
        job_dir = self.sandbox_controller.prepare_solution_folder(code)
        runner = CodeRunner(job_dir / RUNNER_FILENAME)

        start_time = time.perf_counter()
        # TODO: melhorar typesafety desse output
        output = runner.run_python(timeout, [json.dumps(samples)])
        elapsed = time.perf_counter() - start_time

        if auto_cleanup:
            self.sandbox_controller.cleanup_job(job_dir)
        return (output, elapsed)

    def _validate_attempt(self, exercise: ExerciseModel, code: str, samples: list[TestCase]) -> tuple[bool, dict]:
        assert exercise.id, "Exercise wasn't indexed properly"
        
        output, elapsed = self._run_solution(code, samples, timeout=exercise.time_limit, memory_limit=exercise.memory_limit)
        parsed_output = json.loads(output)
        parsed_output["elapsed"] = elapsed
        match parsed_output["status"]:
            case SolutionStatus.ACCEPTED.value:
                return (True, parsed_output)
            
            case SolutionStatus.RUNTIME_ERROR.value:
                return (False, parsed_output)

            case SolutionStatus.WRONG_ANSWER.value:
                return (False, parsed_output)
            case _:
                return (False, parsed_output)

        