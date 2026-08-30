from pathlib import Path
import random

from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.exercise_model import BaseExerciseModel, ExerciseModel
from leety.common.utils.code_runner import CodeRunner
from leety.server.exercise.exercise_controller import ExerciseController
from leety.server.sandbox.sandbox_controller import GENERATOR_FILENAME, RUNNER_FILENAME, SandboxController

database = LeetyDatabase("test_database")
sandbox_controller = SandboxController(
    "_sandbox",
    sample_runner_path=Path(__file__).resolve().parent / "exercise" / "internal_templates" / "exercise_sample_runner.py",
    sample_lib_path=Path(__file__).resolve().parent / "exercise" / "base_generator.py",
    solution_runner_path=Path(__file__).resolve().parent / "exercise" / "internal_templates" / "exercise_solution_runner.py",
)
exercise_controller = ExerciseController(database, sandbox_controller)
valid_generator = exercise_controller.create_exercise(ExerciseModel(
    id=None, diff_id="none", title="test", context="testing", time_limit=1.0, memory_limit=16,
    _sample_gen_code="""
from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        return {"n0": random.randint(0, 100), "n1": random.randint(0, 100)}

    def solver(self, n0: int, n1: int) -> Any:
        return n0 + n1
        """,
    )
)

exercise = database.exercises.get_by_id(1)
assert exercise
assert exercise.id

exercise_controller.modifiy_exercise(exercise.id, BaseExerciseModel(
        _auto_validate=False, # type: ignore
        id=None, title=None, time_limit=None, memory_limit=None, diff_id=None,
        context="Dois valores inteiros serão passados, o resultado deve ser a soma deles.",
))
# Teste de como rodaria o código para testar 
# (o ideal seria testar antes de ser adicionado no banco)
try:
    samples = exercise_controller.generate_samples_for_exercise(
        exercise.id, 100, timeout=10
    )

    loaded_samples = exercise_controller.load_samples(exercise.id)
    print(loaded_samples)
    pass
finally:
    database.save()
    sandbox_controller.cleanup_tmp()
