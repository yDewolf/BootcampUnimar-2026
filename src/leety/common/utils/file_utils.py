
from pathlib import Path
import shutil


class FileUtils:
    @staticmethod
    def cleanup_folder(folder_path: Path) -> None:
        if folder_path.exists() and folder_path.is_dir():
            shutil.rmtree(folder_path, ignore_errors=True)

        folder_path.mkdir()        
