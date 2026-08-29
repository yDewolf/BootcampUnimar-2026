from pathlib import Path
from typing import Optional, Self

from leety.common.internals.database.abstract.abs_csvbase import _Database
from leety.common.internals.database.database_file import DBFileManager

# Aqui vai ter as coisas que são úteis mas não 100% necessárias para qualquer database
class Database(_Database):
    _file_manager: DBFileManager
    _default_path: Path
    
    @property
    def file_manager(self) -> DBFileManager: return self._file_manager

    def __init__(self, db_path: str | Path, file_manager: Optional[DBFileManager] = None) -> None:
        super().__init__()
        self._default_path = Path(db_path)
        self._file_manager = file_manager or DBFileManager(self, self._default_path)

    @classmethod
    def from_folder(cls, path: str | Path) -> Self:
        database = cls(path)
        database.reload_folder()
        return database
    

    def save(self):
        self._file_manager.save()

    def reload_folder(self):
        self._file_manager.load(self._default_path)

    def load_from_folder(self, path: str | Path):
        self._default_path = Path(path)
        self._file_manager.load(path)
