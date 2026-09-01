from typing import Optional

from leety.common.internals.database.protocols.model.field_model import Field, FieldModel


class ClientConfig(FieldModel):
    logged_username: Field[Optional[str]] = Field(default=None)
    logged_password: Field[Optional[str]] = Field(default=None)


