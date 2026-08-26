
from typing import Optional

from leety.common.protocols.csvbase.csv_table import Table
from leety.common.protocols.field.default_fields import IdField, IndexableFieldModel
from leety.common.protocols.field.field_model import Field


class ValidIndexableModel(IndexableFieldModel[int]):
    field_0: Field[Optional[str]]

# class InvalidIndexableModel(IndexableFieldModel[int]):
#     field_0: IdField[str]
# invalid_model = InvalidIndexableModel(id="A", field_0="B")

valid_model = ValidIndexableModel(id=0)
assert valid_model.id.value == 0



table = Table[ValidIndexableModel]()
pass