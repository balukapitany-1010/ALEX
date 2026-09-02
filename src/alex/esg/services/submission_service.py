from alex.esg.domain.company import Company
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.repositories.in_memory_submission_repository import InMemorySubmissionRepository
from alex.esg.repositories.submission_repository import SubmissionRepository


class SubmissionService:
    def __init__(
        self,
        repository: SubmissionRepository | None = None,
    ) -> None:
        if repository is None:
            repository = (InMemorySubmissionRepository())

        if not isinstance(
            repository,
            SubmissionRepository,
        ):
            raise TypeError("repository must be a SubmissionRepository")

        self._repository = repository

    def create_submission(
        self,
        *,
        relation: SupplyChainRelation,
        submitter: Company | None,
        questionnaire: Questionnaire,
        period: str,
    ) -> Submission:
        submission = Submission(
            relation=relation,
            submitter=submitter,
            questionnaire=questionnaire,
            period=period,
        )

        return self._repository.add(submission)

    def add_submission(
            self,
            submission: Submission,
    ) -> Submission:
        if not isinstance(
                submission,
                Submission,
        ):
            raise TypeError(
                "submission must be a Submission"
            )

        existing = (
            self._repository.get_by_id(
                submission.submission_id
            )
        )

        if existing is not None:
            raise ValueError(
                "submission already exists"
            )

        return self._repository.add(
            submission
        )

    def list_submissions(
        self,
    ) -> tuple[
        Submission,
        ...
    ]:
        return self._repository.list_all()

    def get_by_id(
        self,
        submission_id: str,
    ) -> Submission | None:
        return self._repository.get_by_id(submission_id)

    def remove_submission(
            self,
            submission_id: str,
    ) -> Submission:
        return self._repository.remove(
            submission_id
        )