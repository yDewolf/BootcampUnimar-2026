
from pathlib import Path
import shutil


class FileUtils:
    @staticmethod
    def cleanup_folder(folder_path: Path, remove_folder_too: bool = True) -> None:
        if folder_path.exists() and folder_path.is_dir():
            shutil.rmtree(folder_path, ignore_errors=True)

        if not remove_folder_too:
            folder_path.mkdir()        
