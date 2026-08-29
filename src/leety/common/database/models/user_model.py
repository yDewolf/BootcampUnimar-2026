from leety.common.internals.database.protocols.model.default_models import IndexableFieldModel, SearchableField
from leety.common.internals.database.protocols.model.field_model import Field

# Definição do modelo de usuário
class UserModel(IndexableFieldModel[int]):
    username: Field[str] = Field(unique=True)
    password: Field[str]
    is_admin: SearchableField[bool] = SearchableField(default=False)
