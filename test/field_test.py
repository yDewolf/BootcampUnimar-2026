from typing import Optional
from leety.common.protocols.field.field_model import Field, FieldModel

class TestFields(FieldModel):
    test_field: Field[float]
    optional_field: Field[Optional[str]] = Field(default_value=None)

fields = TestFields(test_field=10)
assert fields.header_keys() == ("test_field", "optional_field")

assert TestFields.test_field.id == "test_field"
assert TestFields.test_field.is_required == True
assert fields.test_field == 10

assert TestFields.optional_field.id == "optional_field"
assert TestFields.optional_field.is_required == False
assert fields.optional_field == None
fields.random_field_that_doesnt_exist = 0
# fields = TestFields(test_field=10)
print(fields.to_csv_str(True))
pass