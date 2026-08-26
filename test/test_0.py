from typing import Optional
from leety.common.protocols.field.field_model import Field, FieldModel

class TestFields(FieldModel):
    test_field: Field[float]
    optional_field: Field[Optional[str]]

fields = TestFields(test_field=10)
assert fields.header_keys() == ("test_field", "optional_field")
assert fields.test_field.is_required == True
assert fields.test_field.value == 10
assert fields.optional_field.is_required == False
assert fields.optional_field.value == None
# fields = TestFields(test_field=10)
pass