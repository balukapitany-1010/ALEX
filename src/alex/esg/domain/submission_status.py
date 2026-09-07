from enum import Enum


class SubmissionStatus(Enum):
    SUBMITTED = "submitted"
    ARCHIVED = "archived"

    IMPORTED_COMPLETE = "imported_complete"
    IMPORTED_HEADER = "imported_header"