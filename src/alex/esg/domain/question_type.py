from enum import Enum


class QuestionType(Enum):
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    TEXT = "text"
    COMMENT = "comment"
    NUMBER = "number"
    MIXED = "mixed"
    TABLE = "table"