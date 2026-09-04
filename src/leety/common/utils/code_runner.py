from pathlib import Path
import subprocess
import sys
from typing import Any


class CodeRunner:
    is_python_available: bool = False
    file_path: Path

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        
        result = subprocess.run(["python3", "-c", "print(1)"])
        if result.returncode == 0:
            self.is_python_available = True


    def run_python(self, timeout: float, args: list[Any]) -> tuple[str, str]:
        stringified_args = [
            str(arg) for arg in args
        ]
        
        result = subprocess.run(
            ["python3" if self.is_python_available else sys.executable, self.file_path, *stringified_args],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return result.stdout, result.stderr
