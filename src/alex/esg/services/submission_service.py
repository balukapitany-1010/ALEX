

from alex.esg.domain.company import Company
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.domain.supply_chain_relation import SupplyChainRelation


class SubmissionService:
    def __init__(self) -> None:
        self._submissions: list[Submission] = []

    def create_submission(
        self,
        relation: SupplyChainRelation,
        submitter: Company,
        questionnaire: Questionnaire,
        period: str,
    ) -> Submission:
        submission = Submission(
            relation=relation,
            submitter=submitter,
            questionnaire=questionnaire,
            period=period,
        )

        self._submissions.append(submission)

        return submission

    def list_submissions(
        self,
    ) -> tuple[Submission, ...]:
        return tuple(self._submissions)

    def get_by_id(
            self,
            submission_id: str,
    ) -> Submission | None:
        if not isinstance(submission_id, str):
            raise TypeError("submission_id must be a string")
        normalized_id = submission_id.strip()
        if not normalized_id:
            raise ValueError("submission_id must not be empty")
        for submission in self._submissions:
            if str(submission.submission_id) == normalized_id:
                return submission
        return None