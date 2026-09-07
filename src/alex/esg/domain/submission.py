from __future__ import annotations

from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission_status import SubmissionStatus
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.domain.company import Company
from uuid import uuid4
from datetime import datetime, timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from alex.esg.domain.answer import Answer
    from alex.esg.domain.attachment import Attachment

class Submission:
    def __init__(self, relation: SupplyChainRelation, submitter: Company | None, questionnaire: Questionnaire, period: str | None,submitted_at: datetime | None = None, status: SubmissionStatus = SubmissionStatus.SUBMITTED, organization_size:str | None = None):



        if not isinstance(relation, SupplyChainRelation):
            raise TypeError("relation must be supplychain relation")

        if (
                period is not None and not isinstance(
            period,
            str,
        )
        ):
            raise TypeError("period must be a string or None")

        if period is not None:
            period = period.strip()

            if not period:
                raise ValueError("period must not be empty")

        if (
                submitter is not None
                and not isinstance(submitter, Company)
        ):
            raise TypeError(
                "submitter must be a Company or None"
            )
        if submitted_at is not None and not isinstance(submitted_at, datetime):
            raise TypeError("submitted_at must be a datetime object")
        if not isinstance(status, SubmissionStatus):
            raise TypeError("status must be a SubmissionStatus")
        if not isinstance(questionnaire, Questionnaire):
            raise TypeError("questionnaire must be a Questionnaire")
        if (
            organization_size is not None and not isinstance(organization_size, str)
        ):
            raise TypeError("organization_size must be a string or None")
        if (organization_size is not None and not organization_size.strip()):
            raise ValueError("organization_size cannot be empty")




        now = datetime.now(timezone.utc)
        self.relation = relation
        self.period = period
        self.submission_id = str(uuid4())
        self._submitter = submitter
        self.submitted_at = submitted_at
        self.created_at = now
        self.updated_at = now
        self._status = status
        self.questionnaire = questionnaire
        self._answers: list[Answer] = []
        self._attachments: list[Attachment] = []
        self.organization_size = organization_size

    def add_answer(
            self,
            answer: "Answer",
            *,
            touch_updated_at: bool = True,
    ) -> None:
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

        if touch_updated_at:
            self.updated_at = datetime.now(timezone.utc)

    def remove_attachment(
            self,
            attachment_id: str,
    ) -> "Attachment":
        if not isinstance(attachment_id, str):
            raise TypeError("attachment_id must be a string")

        if not attachment_id.strip():
            raise ValueError("attachment_id cannot be empty")

        for attachment in self._attachments:
            if attachment.attachment_id == attachment_id:
                self._attachments.remove(attachment)
                self.updated_at = datetime.now(timezone.utc)
                return attachment

        raise ValueError(
            "attachment does not exist in the Submission"
        )



    @property
    def submission_attachments(self) -> tuple[Attachment, ...]:
        return tuple(attachment for attachment in self._attachments if attachment.question_definition is None)

    @property
    def question_attachments(self) -> tuple:
        return tuple(
            attachment
            for attachment in self._attachments
            if attachment.question_definition is not None
        )

    def get_attachments_for_question(self, question_id: str) -> tuple:
        if not isinstance(question_id, str):
            raise TypeError("question_id must be a string")

        if not question_id.strip():
            raise ValueError("question_id cannot be empty")

        return tuple(
            attachment
            for attachment in self._attachments
            if (
                    attachment.question_definition is not None
                    and attachment.question_definition.question.question_id
                    == question_id
            )
        )



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

    def get_answer(self, question_id: str) -> Answer | None:
        if not isinstance(question_id, str):
            raise TypeError("question_id must be a string")

        if not question_id.strip():
            raise ValueError("question_id cannot be empty")

        for answer in self._answers:
            if (
                    answer.question_definition.question.question_id
                    == question_id
            ):
                return answer

        return None
    def has_answer(self, question_id: str) -> bool:
        return self.get_answer(question_id) is not None
    def is_question_answered(self, question_id: str) -> bool:
        answer = self.get_answer(question_id)
        if answer is None:
            return False
        return answer.is_answered
    @property
    def answered_count(self) -> int:
        return sum (
            1 for answer in self._answers if answer.is_answered
        )

    @property
    def answered_answers(self) -> tuple["Answer", ...]:
        return tuple(answer for answer in self._answers if answer.is_answered)

    @property
    def submitter(self) -> Company | None:
        return self._submitter

    @property
    def attachments(self) -> tuple["Attachment", ...]:
        return tuple(self._attachments)

    def add_attachment(self, attachment: "Attachment") -> None:
        from alex.esg.domain.attachment import Attachment

        if not isinstance(attachment, Attachment):
            raise TypeError("attachment must be an Attachment")

        if attachment.submission is not self:
            raise ValueError(
                "attachment must belong to this Submission"
            )

        for existing_attachment in self._attachments:
            if existing_attachment.attachment_id == attachment.attachment_id:
                raise ValueError(
                    "attachment already exists in the Submission"
                )

        self._attachments.append(attachment)
        self.updated_at = datetime.now(timezone.utc)

    def get_attachment(
            self,
            attachment_id: str,
    ) -> Attachment | None:
        if not isinstance(attachment_id, str):
            raise TypeError("attachment_id must be a string")

        if not attachment_id.strip():
            raise ValueError("attachment_id cannot be empty")

        for attachment in self._attachments:
            if attachment.attachment_id == attachment_id:
                return attachment

        return None

    def has_attachment(self, attachment_id: str) -> bool:
        return self.get_attachment(attachment_id) is not None

    @classmethod
    def rehydrate(
            cls,
            *,
            submission_id: int | str,
            relation: SupplyChainRelation,
            submitter: Company | None,
            questionnaire: Questionnaire,
            period: str | None,
            submitted_at: datetime | None,
            status: SubmissionStatus,
            organization_size: str | None,
            created_at: datetime,
            updated_at: datetime | None,
    ) -> "Submission":
        if not isinstance(
                submission_id,
                (int, str),
        ):
            raise TypeError(
                "submission_id must be an int or string"
            )

        normalized_submission_id = str(
            submission_id
        ).strip()

        if not normalized_submission_id:
            raise ValueError(
                "submission_id cannot be empty"
            )

        if not isinstance(
                created_at,
                datetime,
        ):
            raise TypeError(
                "created_at must be a datetime"
            )

        if (
                updated_at is not None
                and not isinstance(
            updated_at,
            datetime,
        )
        ):
            raise TypeError(
                "updated_at must be a datetime or None"
            )

        if created_at.tzinfo is None:
            created_at = (
                created_at.replace(
                    tzinfo=timezone.utc
                )
            )
        else:
            created_at = (
                created_at.astimezone(
                    timezone.utc
                )
            )

        if updated_at is not None:
            if updated_at.tzinfo is None:
                updated_at = (
                    updated_at.replace(
                        tzinfo=timezone.utc
                    )
                )
            else:
                updated_at = (
                    updated_at.astimezone(
                        timezone.utc
                    )
                )

            if updated_at < created_at:
                raise ValueError(
                    "updated_at cannot be before created_at"
                )

        if submitted_at is not None:
            if not isinstance(
                    submitted_at,
                    datetime,
            ):
                raise TypeError(
                    "submitted_at must be a datetime or None"
                )

            if submitted_at.tzinfo is None:
                submitted_at = (
                    submitted_at.replace(
                        tzinfo=timezone.utc
                    )
                )
            else:
                submitted_at = (
                    submitted_at.astimezone(
                        timezone.utc
                    )
                )
        if organization_size is not None:
            if not isinstance(
                    organization_size,
                    str,
            ):
                raise TypeError(
                    "organization_size must be "
                    "a string or None"
                )

            organization_size = (
                    organization_size.strip()
                    or None
            )

        submission = cls(
            relation=relation,
            submitter=submitter,
            questionnaire=questionnaire,
            period=period,
            submitted_at=submitted_at,
            status=status,
            organization_size=organization_size,
        )

        submission.submission_id = (
            normalized_submission_id
        )

        submission.created_at = (
            created_at
        )

        submission.updated_at = (
            updated_at
        )

        return submission



