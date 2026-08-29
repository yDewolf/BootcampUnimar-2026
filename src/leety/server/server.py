from pathlib import Path
import random

from leety.common.database.leety_db import LeetyDatabase
from leety.common.database.models.exercise_model import ExerciseModel
from leety.server.exercise.exercise_controller import ExerciseController
from leety.server.sandbox.sandbox_controller import SandboxController

database = LeetyDatabase("test_database")
sandbox_controller = SandboxController(
    "sandbox",
    sample_runner_path=Path(__file__).resolve().parent / "exercise" / "internal_templates" / "exercise_sample_runner.py",
    solution_runner_path=Path(__file__).resolve().parent / "exercise" / "internal_templates" / "exercise_solution_runner.py"
)
exercise_controller = ExerciseController(database, sandbox_controller)
exercise_controller.create_exercise(ExerciseModel(
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

pass
database.save()
sandbox_controller.cleanup_tmp()