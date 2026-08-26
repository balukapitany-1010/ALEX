from datetime import datetime, timezone
from uuid import uuid4
from alex.esg.domain.submission import Submission
from alex.esg.domain.question_definition import QuestionDefinition

class Attachment:
    def __init__(
            self,
            submission: Submission,
            file_name: str,
            storage_reference: str,
            content_type: str | None = None,
            file_size: int | None = None,
            question_definition: QuestionDefinition | None = None,
    ):
        if file_size is not None:
            if isinstance(file_size, bool) or not isinstance(file_size, int):
                raise TypeError("file_size must be an int or None")
            if file_size < 0:
                raise ValueError("file_size cannot be negative")

        if content_type is not None and not isinstance(content_type, str):
            raise TypeError("content_type must be a string or None")

        if content_type is not None and not content_type.strip():
            raise ValueError("content_type cannot be empty")

        if not isinstance(storage_reference, str):
            raise TypeError("storage_reference must be a string")
        if not storage_reference.strip():
            raise ValueError("storage_reference must not be empty")

        if not isinstance(submission, Submission):
            raise TypeError("submission must be a Submission")

        if(question_definition is not None and not isinstance(question_definition, QuestionDefinition)):
            raise TypeError("question_definition must be a QuestionDefinition or None")

        if not isinstance(file_name, str):
            raise TypeError("file_name must be a string")
        if not file_name.strip():
            raise ValueError("file_name must not be empty")

        if (question_definition is not None and submission.questionnaire.questionnaire_key != question_definition.questionnaire.questionnaire_key):
            raise ValueError("question_definition must belong to the same questionnaire as the submission")

        self._submission = submission
        self._question_definition = question_definition
        self._attachment_id = str(uuid4())
        self._file_name = file_name
        self._storage_reference = storage_reference
        self._content_type = content_type
        self._file_size = file_size
        self._created_at = datetime.now(timezone.utc)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def file_size(self) -> int | None:
        return self._file_size

    @property
    def content_type(self) -> str | None:
        return self._content_type

    @property
    def storage_reference(self) -> str:
        return self._storage_reference

    @property
    def file_name(self) -> str:
        return self._file_name

    @property
    def attachment_id(self) -> str:
        return self._attachment_id
    @property
    def submission(self) -> Submission:
        return self._submission
    @property
    def question_definition(self) -> QuestionDefinition | None:
        return self._question_definition