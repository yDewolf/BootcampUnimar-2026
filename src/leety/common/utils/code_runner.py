from pathlib import Path
import subprocess
from typing import Any

class CodeRunner:
    file_path: Path

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)


    def run_python(self, timeout: float, args: list[Any]) -> tuple[str, str]:
        stringified_args = [
            str(arg) for arg in args
        ]
        result = subprocess.run(
            ["python3", self.file_path, *stringified_args],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return result.stdout, result.stderr
