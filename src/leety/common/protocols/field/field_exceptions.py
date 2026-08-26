from typing import Any


class FieldException(Exception):
    # TODO: provavelmente usar um Protocol no lugar do Any
    def __init__(self, field: Any, *args):
        super().__init__(*args)

class FieldMissingValue(FieldException):
    pass

