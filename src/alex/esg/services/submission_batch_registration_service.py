from alex.esg.services.submission_batch_json_importer import SubmissionBatchJsonImportResult
from alex.esg.services.submission_service import  SubmissionService


class SubmissionBatchRegistrationService:
    def __init__(
        self,
        *,
        submission_service: SubmissionService,
    ) -> None:
        if not isinstance(
            submission_service,
            SubmissionService,
        ):
            raise TypeError(
                "submission_service must be a "
                "SubmissionService"
            )

        self._submission_service = (submission_service)

    def register_import_result(
        self,
        result: SubmissionBatchJsonImportResult,
    ) -> tuple:
        if not isinstance(
            result,
            SubmissionBatchJsonImportResult,
        ):
            raise TypeError(
                "result must be a "
                "SubmissionBatchJsonImportResult"
            )

        registered = []

        for item in result.items:
            if not item.is_imported:
                continue

            submission = item.submission

            if submission is None:
                continue

            self._submission_service.add_submission(submission)

            registered.append(submission)

        return tuple(registered)