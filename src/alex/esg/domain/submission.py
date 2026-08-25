from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission_status import SubmissionStatus
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.domain.company import Company
from uuid import uuid4
from datetime import datetime, timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from alex.esg.domain.answer import Answer

class Submission:
    def __init__(self, relation: SupplyChainRelation, submitter: Company, questionnaire: Questionnaire, period: str,submitted_at: datetime | None = None, status: SubmissionStatus = SubmissionStatus.SUBMITTED,):
        if not isinstance(relation, SupplyChainRelation):
            raise TypeError("relation must be supplychain relation")

        if not isinstance(period, str):
            raise TypeError("period must be a string")

        if not period.strip():
            raise ValueError("period must not be empty")

        if not isinstance(submitter, Company):
            raise TypeError("submitter must be a Company")
        if submitted_at is not None and not isinstance(submitted_at, datetime):
            raise TypeError("submitted_at must be a datetime object")
        if not isinstance(status, SubmissionStatus):
            raise TypeError("status must be a SubmissionStatus")
        if not isinstance(questionnaire, Questionnaire):
            raise TypeError("questionnaire must be a Questionnaire")




        now = datetime.now(timezone.utc)
        self.relation = relation
        self.period = period
        self.submission_id = str(uuid4())
        self.submitter = submitter
        self.submitted_at = submitted_at
        self.created_at = now
        self.updated_at = now
        self._status = status
        self.questionnaire = questionnaire
        self._answers: list[Answer] = []

    def add_answer(self, answer: "Answer") -> None:
        from alex.esg.domain.answer import Answer
        if not isinstance(answer, Answer):
            raise  TypeError("answer must be a Answer")
        if answer.submission is not self:
            raise ValueError("answer must belong to this Submission")
        question_id = (
            answer
            .question_definition
            .question
            .question_id
        )
        for existing_answer in self._answers:
            existing_question_id = (
                existing_answer
                .question_definition
                .question
                .question_id
            )
            if existing_question_id == question_id:
                raise ValueError("an Answer for this Qustion alredy exists in the Submission")

        self._answers.append(answer)
        self.updated_at = datetime.now(timezone.utc)

    @property
    def status(self) -> SubmissionStatus:
        return self._status
    def archive(self) -> None:
        if self._status == SubmissionStatus.ARCHIVED:
            return
        self._status = SubmissionStatus.ARCHIVED
        self.updated_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        if self._status == SubmissionStatus.SUBMITTED:
            return
        self._status = SubmissionStatus.SUBMITTED
        self.updated_at = datetime.now(timezone.utc)

    @property
    def answers(self) -> tuple["Answer", ...]:
        return tuple(self._answers)

