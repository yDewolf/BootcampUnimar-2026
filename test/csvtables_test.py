
from typing import Optional

from leety.common.protocols.csvbase.csv_table import  IndexableTable, Table
from leety.common.protocols.csvbase.model.default_models import IdField, IndexableFieldModel, SearchableField
from leety.common.protocols.csvbase.model.field_model import Field, FieldModel


class ValidIndexableModel(IndexableFieldModel[int]):
    field_0: Field[Optional[str]] = Field(default=None)
    unique_field: Field[Optional[str]] = Field(default=None, unique=True)
    test_searchable: SearchableField[Optional[str]] = SearchableField(default=None)

# class InvalidIndexableModel(IndexableFieldModel[int]):
#     field_0: IdField[str]
# invalid_model = InvalidIndexableModel(id="A", field_0="B")

valid_model = ValidIndexableModel(id=0, unique_field="oi", test_searchable="olá eu sou seu vizinho !!")
valid_model0 = ValidIndexableModel(id=0)
auto_id_model = ValidIndexableModel(id=None)
assert valid_model.id == 0
assert valid_model0.id == 0

table = Table[ValidIndexableModel]()
table.add_row(valid_model)
assert table.rows == [valid_model]
valid_model.unique_field = "olá"

table.add_row(valid_model0) # Isso aqui é permitido, mesmo que tenham o mesmo id, como não é indexável, os ids não importam
assert table.rows == [valid_model, valid_model0]

table.remove_row(valid_model0)
assert table.rows == [valid_model]

# table.add_row(valid_model) -> Duplicidade

assert issubclass(ValidIndexableModel, FieldModel)
indexable = IndexableTable[ValidIndexableModel]()
indexable.add_row(valid_model)
# indexable.add_row(valid_model0) # Aqui já não é permitido por causa do index que depende de ids únicos
# indexable.add_row(valid_model) -> duplicidade
assert indexable.rows == [valid_model]
assert indexable._table_index == {str(valid_model.id): valid_model}
assert indexable._searchable_index == {"test_searchable": {valid_model.test_searchable: [valid_model]}}
assert indexable.match_field({ValidIndexableModel.test_searchable: valid_model.test_searchable}) == [valid_model]
assert indexable.linear_match({ValidIndexableModel.test_searchable: valid_model.test_searchable}) == [valid_model]
assert indexable.match_searchable_field({ValidIndexableModel.test_searchable: valid_model.test_searchable}) == [valid_model]

indexable.remove_row_id(0)
assert indexable.rows == []
assert indexable._table_index == {}
assert indexable._searchable_index == {"test_searchable": {}}

indexable.add_row(auto_id_model)
assert auto_id_model.id == 1
assert indexable._last_inserted_int_id == 1
assert indexable.rows == [auto_id_model]
assert indexable._table_index == {str(auto_id_model.id): auto_id_model}

print(indexable.to_csv_str())
pass