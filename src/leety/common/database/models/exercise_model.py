from typing import Optional

from leety.common.dto.attempt_result import AttemptResult
from leety.common.internals.database.protocols.model.default_models import IndexableFieldModel, SearchableField
from leety.common.internals.database.protocols.model.field_model import Field

class ExerciseDifficulty(IndexableFieldModel[str]):
    # Aqui o id vai ser usado como "nome" da dificuldade
    capitalized_name: Field[str]
    description: Field[str] = Field(default=None)

# basicamente metadados
# FIXME: esse idType: int aqui é gambiarra pra fazer o setup correto
# do ExerciseModel
class BaseExerciseModel[idType: int](IndexableFieldModel[int]):
    # TODO: a implementação do relacionamento vai ser manual mesmo e gg, 
    # porque vai dar muito trabalho implementar o sistema de relação agora
    # talvez se sobrar tempo
    diff_id: SearchableField[str]
    author_id: Field[Optional[int]] = Field(default=None)
    contributors: Field[Optional[list[int]]] = Field(default=[])
    
    title: Field[str]
    context: Field[str] = Field(default="")

    time_limit: Field[float]
    memory_limit: Field[int]

# informações que são geradas após o exercício ser testado
class ExerciseModel(BaseExerciseModel[int]):
    _sample_gen_code: Field[Optional[str]] = Field(default=None)

    # FIXME: teoricamente essas variáveis de path não são necessárias
    # sample_gen_path: Field[Optional[str]] = Field(default=None)
    # solution_template_path: Field[Optional[str]] = Field(default=None)

    # usado para comparar com o tempo das soluções
    benchmark_time: Field[Optional[float]] = Field(default=0)
    benchmark_samples: Field[Optional[int]] = Field(default=None)

    # Define se o exercício é válido, ou seja pode ser executado pelo servidor,
    # tem samples e apresenta template para resolução
    is_valid: Field[Optional[bool]] = Field(default=False)


# Quando a solução é inválida
class ExerciseAttempt(IndexableFieldModel[int]):
    author_id: SearchableField[int]
    exercise_id: SearchableField[int]

    valid: SearchableField[bool]
    attempt_result: Field[Optional[AttemptResult]]

    solve_time: Field[Optional[float]] = Field(default=None)
    sample_amount: Field[Optional[int]] = Field(default=None)
    correct_results: Field[Optional[int]] = Field(default=None)
