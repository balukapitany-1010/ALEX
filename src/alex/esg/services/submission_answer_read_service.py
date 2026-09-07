from alex.esg.domain.submission import Submission
from alex.esg.repositories.mssql_submission_answer_loader import (
    MssqlSubmissionAnswerLoader,
)


class SubmissionAnswerReadService:
    def __init__(
        self,
        loader: MssqlSubmissionAnswerLoader,
    ) -> None:
        if not isinstance(
            loader,
            MssqlSubmissionAnswerLoader,
        ):
            raise TypeError(
                "loader must be an "
                "MssqlSubmissionAnswerLoader"
            )

        self._loader = loader

    def load_answers(
        self,
        submission: Submission,
    ) -> Submission:
        if not isinstance(
            submission,
            Submission,
        ):
            raise TypeError("submission must be a Submission")

        if submission.answers:
            return submission

        return self._loader.load(
            submission
        )