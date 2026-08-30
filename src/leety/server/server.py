
# basicamente um wrapper com os controllers necessários para fazer as coisas funcionarem
from pathlib import Path

from leety.common.database.leety_db import LeetyDatabase
from leety.server.exercise.exercise_controller import ExerciseController
from leety.server.exercise.solution_controller import SolutionController
from leety.server.sandbox.sandbox_controller import SandboxController
from leety.server.user.user_controller import UserController

import leety.server.exercise as exercise

EXERCISE_FOLDER: Path = Path(str(exercise.__path__))
INTERNAL_TEMPLATES_FOLDER: Path = EXERCISE_FOLDER / "internal_templates"
class Server:
    database: LeetyDatabase

    user_controller: UserController

    sandbox_controller: SandboxController
    exercise_controller: ExerciseController
    solution_controller: SolutionController

    def __init__(self, db_name: str = "test_database", sandbox_root: str = "_sandbox") -> None:
        self.database = LeetyDatabase(db_name)

        self.user_controller = UserController(self.database)

        self.sandbox_controller = SandboxController(
            sandbox_root,
            sample_runner_path=INTERNAL_TEMPLATES_FOLDER / "exercise_sample_runner.py",
            solution_runner_path=INTERNAL_TEMPLATES_FOLDER / "exercise_solution_runner.py",
            sample_lib_path=EXERCISE_FOLDER / "base_generator.py",
        )

        self.exercise_controller = ExerciseController(self.database, self.user_controller, self.sandbox_controller)
        self.solution_controller = SolutionController(self.database, self.sandbox_controller, self.exercise_controller)

    