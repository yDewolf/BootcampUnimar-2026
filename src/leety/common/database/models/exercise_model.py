from typing import Optional

from leety.common.internals.database.protocols.model.default_models import IndexableFieldModel, SearchableField
from leety.common.internals.database.protocols.model.field_model import Field

class ExerciseDifficulty(IndexableFieldModel[str]):
    # Aqui o id vai ser usado como "nome" da dificuldade
    capitalized_name: Field[str]
    description: Field[str] = Field(default=None)

class ExerciseModel(IndexableFieldModel[int]):
    # TODO: a implementação do relacionamento vai ser manual mesmo e gg, 
    # porque vai dar muito trabalho implementar o sistema de relação agora
    # talvez se sobrar tempo
    diff_id: SearchableField[str]

    title: Field[str]
    context: Field[str] = Field(default=None)

    time_limit: Field[float]
    memory_limit: Field[int]

    _sample_gen_code: Field[Optional[str]] = Field(default=None)
    sample_gen_path: Field[Optional[str]] = Field(default=None)
    # solver_code: Field[str] = Field(default=None)        
