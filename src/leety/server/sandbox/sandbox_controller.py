from pathlib import Path
import shutil
import uuid

from leety.common.utils.file_utils import FileUtils

# AVISO !!!!!
# isso aqui não é um sandbox de verdade e vai simplesmente rodar código 
# na sua máquina !!!! Ou seja, não tente testar códigos que possam destruir
# seu computador

# Estrutura de pastas:
# sandbox_0/
#   - sample_runner.py (copiado do internal_templates/exercise_sample_runner.py)
#   - solution_runner.py (copiado do internal_templates/exercise_solution_runner.py)
#   - tmp/ (arquivos aqui teoricamente serão deletados depois de um tempo)
#       - generator_code_id/
#           - base_generator.py (copiado de exercise/base_generator.py)
#           - generator.py (código enviado pelo admin)
#       - solution_id/
#           - solution.py (código enviado pelo usuário)

GENERATOR_FILENAME = "generator.py"
SAMPLE_PATH = "samples.json"
GENERATOR_LIB_FILENAME = "base_generator.py"
SOLUTION_FILENAME = "solution.py"
RUNNER_FILENAME = "runner.py"

class SandboxController:
    _sandbox_path: Path

    @property
    def sandbox_path(self) -> Path: return self._sandbox_path
    @property
    def tmp_path(self) -> Path: return self.sandbox_path / "tmp"
    @property
    def generators_path(self) -> Path: return self.tmp_path / "generators"
    @property
    def solutions_path(self) -> Path: return self.tmp_path / "solutions"

    @property
    def sample_lib_path(self) -> Path: return self.sandbox_path / "base_generator.py"
    @property
    def sample_runner_path(self) -> Path: return self.sandbox_path / "sample_runner.py"

    @property
    def solution_runner_path(self) -> Path: return self.sandbox_path / "solution_runner.py"


    def __init__(self, sandbox_path: str | Path, sample_runner_path: str | Path, sample_lib_path: str | Path, solution_runner_path: str | Path) -> None:
        self._sandbox_path = Path(sandbox_path)
        self._setup_directory(sample_runner_path, sample_lib_path, solution_runner_path)

    def _setup_directory(self, sample_runner_path: str | Path, sample_lib_path: str | Path, solution_runner_path: str | Path):
        self.sandbox_path.mkdir(parents=True, exist_ok=True)
        self.tmp_path.mkdir(exist_ok=True)
        self.generators_path.mkdir(exist_ok=True)
        self.solutions_path.mkdir(exist_ok=True)

        shutil.copyfile(sample_runner_path, self.sample_runner_path)
        shutil.copyfile(solution_runner_path, self.solution_runner_path)
        shutil.copyfile(sample_lib_path, self.sample_lib_path)


    def prepare_solution_folder(self, solution_code: str, solution_id: str) -> Path:
        job_dir = SandboxController._prepare_job_folder(
            self.solutions_path, solution_code, SOLUTION_FILENAME
        )

        shutil.copyfile(self.solution_runner_path, job_dir / RUNNER_FILENAME)
        return job_dir

    def prepare_generator_folder(self, generator_code: str, exercise_id: str) -> Path:
        job_dir = SandboxController._prepare_job_folder(
            self.generators_path, generator_code, GENERATOR_FILENAME
        )

        shutil.copyfile(self.sample_runner_path, job_dir / RUNNER_FILENAME)
        shutil.copyfile(self.sample_lib_path, job_dir / GENERATOR_LIB_FILENAME)
        return job_dir

    def cleanup_job(self, job_dir: Path):
        if job_dir.resolve().is_relative_to(self.sandbox_path.resolve()):
            FileUtils.cleanup_folder(job_dir)

    def cleanup_tmp(self):
        FileUtils.cleanup_folder(self.solutions_path)
        FileUtils.cleanup_folder(self.generators_path)

    @staticmethod
    def _prepare_job_folder(root_path: Path, code: str, code_filename: str) -> Path:
        job_dir = root_path / f"job_{uuid.uuid4().hex[:8]}"
        job_dir.mkdir()

        # TODO: copiar o exercise_generator_runner.py para a pasta
        (job_dir / code_filename).write_text(code, encoding="utf-8")
        return job_dir

