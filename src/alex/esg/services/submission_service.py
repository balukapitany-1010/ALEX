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