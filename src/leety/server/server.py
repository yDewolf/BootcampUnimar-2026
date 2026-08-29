from pathlib import Path

from leety.server.sandbox.sandbox_controller import SandboxController


sandbox_controller = SandboxController(
    "sandbox",
    sample_runner_path=Path(__file__).resolve().parent / "exercise" / "internal_templates" / "exercise_sample_runner.py",
    solution_runner_path=Path(__file__).resolve().parent / "exercise" / "internal_templates" / "exercise_solution_runner.py"
)
sandbox_controller.prepare_generator_folder("print('hello')", "none")
sandbox_controller.prepare_solution_folder("print('hello')", "none")
pass
sandbox_controller.cleanup_tmp()