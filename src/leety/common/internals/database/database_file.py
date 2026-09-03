import csv
from enum import Enum
import json
from pathlib import Path
from types import NoneType
from typing import Any, get_args

from leety.common.internals.database.abstract.abs_csvbase import _Database
from leety.common.internals.database.protocols.model.field_model import Field, FieldModel


class DBFileManager:
    _database: _Database
    _db_dir: Path
    _metadata: dict

    @property
    def root_path(self) -> Path: 
        return self._db_dir

    @property
    def tables_path(self) -> Path:
        return self.root_path / "tables"

    @property
    def metadata_path(self) -> Path:
        return self.root_path / "metadata.json"

    def __init__(self, database: _Database, db_directory: str | Path, auto_setup: bool = True) -> None:
        self._database = database
        self._db_dir = Path(db_directory)
        self._metadata = {
            "database_class": self._database.__class__.__name__,
            "tables": list(self._database.table_names())
        }

        if auto_setup: self.setup_folders()


    def setup_folders(self):
        self.root_path.mkdir(parents=True, exist_ok=True)
        self.tables_path.mkdir(exist_ok=True)


    def save(self) -> None:
        with open(self.metadata_path, "w", encoding="utf-8") as file:
            json.dump(self._metadata, file, indent=1)

        for table_name, table in self._database.tables.items():
            csv_file = self.tables_path / f"{table_name}.csv"
            headers = list(table.get_headers())

            with open(csv_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()

                for row in table.rows:
                    writer.writerow(row.get_data(raw=False))


    def load(self, db_dir: str | Path) -> None:
        path = Path(db_dir)
        tables_path = path / "tables"

        if not path.exists() or not tables_path.exists():
            raise FileNotFoundError(f"Couldn't find Database Path: {path}")

        self._database.clear_all()
        for table_name in self._database.table_names():
            csv_file = tables_path / f"{table_name}.csv"
            if not csv_file.exists():
                continue

            table = self._database.get_table(table_name)
            model_cls = table.model_cls()

            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                for row_dict in reader:
                    parsed_data = DBFileManager._parse_row_data(model_cls, row_dict)
                    row_instance = model_cls(**parsed_data)
                    table.add_row(row_instance)

        self._db_dir = path

    @staticmethod
    def _parse_row_data(model_cls: type, raw_data: dict[str, Any]) -> dict[str, Any]:
        casted_data: dict[str, Any] = {}
        for field_name, value in raw_data.items():
            if value is None or value == "":
                casted_data[field_name] = None
                continue

            field_obj = getattr(model_cls, field_name, None)
            if not isinstance(field_obj, Field): continue

            target_type = field_obj._type_hint
            args = get_args(target_type)
            if NoneType in args:
                target_type = args[0]

            if target_type is int:
                casted_data[field_name] = int(value)
            elif target_type is float:
                casted_data[field_name] = float(value)
            elif target_type is bool:
                casted_data[field_name] = value.lower() in ("true", "1", "yes")
            elif issubclass(target_type, Enum):
                casted_data[field_name] = target_type(value)
            elif issubclass(target_type, FieldModel):
                casted_data[field_name] = target_type.from_dict(json.loads(value))
            else:
                casted_data[field_name] = str(value)

        return casted_data