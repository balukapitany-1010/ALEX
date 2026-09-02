from alex.esg.domain.submission import Submission
from alex.esg.repositories.submission_repository import SubmissionRepository

class InMemorySubmissionRepository(SubmissionRepository):
    def __init__(self) -> None:
        self._submissions: list[
            Submission
        ] = []

    def add(
        self,
        submission: Submission,
    ) -> Submission:
        if not isinstance(
            submission,
            Submission,
        ):
            raise TypeError("submission must be a Submission")

        if (
            self.get_by_id(submission.submission_id)
            is not None
        ):
            raise ValueError(
                "submission with this id "
                "already exists"
            )

        self._submissions.append(submission)

        return submission

    def list_all(
        self,
    ) -> tuple[
        Submission,
        ...
    ]:
        return tuple(self._submissions)

    def get_by_id(
        self,
        submission_id: str,
    ) -> Submission | None:
        if not isinstance(
            submission_id,
            str,
        ):
            raise TypeError("submission_id must be a string")

        normalized = (submission_id.strip())

        if not normalized:
            raise ValueError("submission_id cannot be empty")

        for submission in (self._submissions):
            if (submission.submission_id == normalized):
                return submission

        return None

    def remove(
            self,
            submission_id: str,
    ) -> Submission:
        submission = self.get_by_id(
            submission_id
        )

        if submission is None:
            raise ValueError("submission does not exist")

        self._submissions.remove(submission)

        return submission