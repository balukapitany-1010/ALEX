from dataclasses import dataclass
from enum import Enum


class ImportIssueSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class ImportIssue:
    severity: ImportIssueSeverity
    code: str
    message: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.severity,
            ImportIssueSeverity,
        ):
            raise TypeError("severity must be an ImportIssueSeverity")

        if not isinstance(self.code, str):
            raise TypeError("code must be a string")

        if not self.code.strip():
            raise ValueError("code cannot be empty")

        if not isinstance(self.message, str):
            raise TypeError("message must be a string")

        if not self.message.strip():
            raise ValueError("message cannot be empty")