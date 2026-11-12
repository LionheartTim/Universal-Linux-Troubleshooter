"""Read-only diagnostic result *presentation* contract for a future bridge.

Nothing in this module scans the machine or manufactures diagnostic outcomes.
"""

from dataclasses import dataclass
from enum import Enum


class ResultStatus(str, Enum):
    OK = "OK"
    WARNING = "Warning"
    PROBLEM = "Problem"
    UNKNOWN = "Unknown"
    INFO = "Info"       # Check ran; a configuration or optional feature was merely observed.
    NOT_RUN = "Not run" # User declined an optional online check; not a failed diagnosis.


@dataclass(frozen=True)
class DiagnosticResult:
    category_key: str
    check_key: str
    status: ResultStatus
    diagnosis: str
    explanation: str
    solution: str
    evidence: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.status, ResultStatus):
            raise ValueError("status must be a ResultStatus")
        if not self.category_key or not self.check_key:
            raise ValueError("A result must identify a category and a check")
        if not self.diagnosis.strip():
            raise ValueError("A result needs a nonempty diagnosis")
        if not self.explanation.strip():
            raise ValueError("A result needs an explanation")
        if not self.solution.strip():
            raise ValueError("A result needs a solution or explicit next-step guidance")
        if not all(isinstance(line, str) for line in self.evidence):
            raise ValueError("Evidence entries must be text")
