from pathlib import Path
import subprocess
from typing import Any

class CodeRunner:
    file_path: Path

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)


    def run_python(self, timeout: float, args: list[Any]) -> str:
        stringified_args = [
            str(arg) for arg in args
        ]
        result = subprocess.run(
            ["python3", self.file_path, *stringified_args],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            return result.stdout
        
        raise Exception(f"Python code failed: {result.stderr}")
