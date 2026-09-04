from pathlib import Path
import subprocess
import sys
from typing import Any, Optional

class CodeRunner:
    file_path: Path

    _is_python_available: Optional[bool] = None
    
    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        
        if self.__class__._is_python_available is None:
            result = subprocess.run(["python3", "-c", "print(1)"])
            if result.returncode == 0:
                self.__class__._is_python_available = True
            else: 
                self.__class__._is_python_available = False


    def run_python(self, timeout: float, args: list[Any]) -> tuple[str, str]:
        stringified_args = [
            str(arg) for arg in args
        ]
        
        result = subprocess.run(
            ["python3" if self.__class__._is_python_available else sys.executable, self.file_path, *stringified_args],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return result.stdout, result.stderr
