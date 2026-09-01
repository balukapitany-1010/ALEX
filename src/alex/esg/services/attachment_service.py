from alex.esg.domain.attachment import Attachment
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.submission import Submission


class AttachmentService:
    def create_attachment(
        self,
        *,
        submission: Submission,
        file_name: str,
        storage_reference: str,
        content_type: str | None = None,
        file_size: int | None = None,
        question_definition: (
            QuestionDefinition | None
        ) = None,
    ) -> Attachment:
        if not isinstance(
            submission,
            Submission,
        ):
            raise TypeError("submission must be a Submission")

        attachment = Attachment(
            submission=submission,
            file_name=file_name,
            storage_reference=storage_reference,
            content_type=content_type,
            file_size=file_size,
            question_definition=question_definition,
        )

        submission.add_attachment(
            attachment
        )

        return attachment

    def list_for_submission(
        self,
        submission: Submission,
    ) -> tuple[Attachment, ...]:
        if not isinstance(
            submission,
            Submission,
        ):
            raise TypeError("submission must be a Submission")

        return submission.attachments

    def list_submission_attachments(
        self,
        submission: Submission,
    ) -> tuple[Attachment, ...]:
        if not isinstance(
            submission,
            Submission,
        ):
            raise TypeError("submission must be a Submission")

        return submission.submission_attachments

    def list_for_question(
        self,
        *,
        submission: Submission,
        question_id: str,
    ) -> tuple[Attachment, ...]:
        if not isinstance(
            submission,
            Submission,
        ):
            raise TypeError("submission must be a Submission")

        return submission.get_attachments_for_question(question_id)

    def get_by_id(
        self,
        *,
        submission: Submission,
        attachment_id: str,
    ) -> Attachment | None:
        if not isinstance(
            submission,
            Submission,
        ):
            raise TypeError("submission must be a Submission")

        return submission.get_attachment(attachment_id)

    def remove_attachment(
        self,
        *,
        submission: Submission,
        attachment_id: str,
    ) -> Attachment:
        if not isinstance(
            submission,
            Submission,
        ):
            raise TypeError("submission must be a Submission")

        return submission.remove_attachment(attachment_id)