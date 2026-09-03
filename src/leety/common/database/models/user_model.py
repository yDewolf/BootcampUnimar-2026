from typing import Optional

from leety.common.internals.database.protocols.model.default_models import IndexableFieldModel, SearchableField
from leety.common.internals.database.protocols.model.field_model import Field

# Definição do modelo de usuário
MIN_PASSWORD_LENGTH: int = 6
class UserModel(IndexableFieldModel[int]):
    username: SearchableField[str] = SearchableField(unique=True)
    password: Field[Optional[str]]
    is_admin: SearchableField[bool] = SearchableField(default=False)

    def validate(self):
        if not self.password is None:
            if len(self.password) < MIN_PASSWORD_LENGTH:
                raise Exception(f"A senha deve conter no mínimo {MIN_PASSWORD_LENGTH} caracteres")
        
        return super().validate()
