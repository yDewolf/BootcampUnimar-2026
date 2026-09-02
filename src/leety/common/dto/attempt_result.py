from enum import Enum
from typing import Any, Optional

from leety.common.internals.database.protocols.model.field_model import Field, FieldModel

class SolutionStatus(Enum):
    RUNTIME_ERROR = "RUNTME_ERROR"
    WRONG_ANSWER = "WRONG_ANSWER"
    ACCEPTED = "ACCEPTED"

class AttemptResult(FieldModel):
    status: Field[SolutionStatus]
    test_case: Field[Optional[int]] = Field(default=None)

    elapsed: Field[Optional[float]] = Field(default=None)

class AcceptedAttempt(AttemptResult):
    pass

class RuntimeErrorAttempt(AttemptResult):
    error: Field[str]

class WrongAnswerAttempt(AttemptResult):
    input: Field[Optional[Any]]
    expected: Field[Optional[Any]]
    actual: Field[Optional[Any]]
