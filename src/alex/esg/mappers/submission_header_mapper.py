from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SubmissionHeaderData:
    supplier_company: str | None
    supplier_tax_number: str | None

    requester_company: str | None
    requester_tax_number: str | None
    requester_mp_id: str | None

    respondent_id: str | None
    respondent_mp_id: str | None
    org_size: str | None

    submitted_at: str | None
    period: str | None

    response_organization: str | None = None

    submitter_auditor_company: str | None = None
    submitter_auditor_tax_number: str | None = None
    submitter_auditor_representative: str | None = None
    submitter_auditor_phone: str | None = None
    submitter_auditor_email: str | None = None
    submitter_auditor_period: str | None = None


class SubmissionHeaderMapper:
    def map(
        self,
        submission_data: dict[str, Any],
    ) -> SubmissionHeaderData:
        if not isinstance(submission_data, dict):
            raise TypeError(
                "submission_data must be a dictionary"
            )

        response = submission_data.get("response")

        if not isinstance(response, dict):
            raise ValueError(
                "submission response must be an object"
            )

        cover = response.get("cover")

        if not isinstance(cover, dict):
            raise ValueError(
                "response cover must be an object"
            )

        supplier = cover.get("supplier")

        if not isinstance(supplier, dict):
            raise ValueError(
                "cover supplier must be an object"
            )

        requester = cover.get("requester")

        if not isinstance(requester, dict):
            raise ValueError(
                "cover requester must be an object"
            )

        submitter_auditor = cover.get(
            "submitter_auditor"
        )

        if submitter_auditor is None:
            submitter_auditor = {}

        elif not isinstance(
            submitter_auditor,
            dict,
        ):
            raise ValueError(
                "cover submitter_auditor "
                "must be an object"
            )

        return SubmissionHeaderData(
            supplier_company=self._optional_string(
                supplier.get("company")
            ),
            supplier_tax_number=self._optional_string(
                supplier.get("tax_number")
            ),

            requester_company=self._optional_string(
                requester.get("company")
            ),
            requester_tax_number=self._optional_string(
                requester.get("tax_number")
            ),
            requester_mp_id=self._optional_string(
                requester.get("requester_MP_id")
            ),

            respondent_id=self._optional_string(
                response.get("respondent_id")
            ),
            respondent_mp_id=self._optional_string(
                response.get("respondent_MP_id")
            ),
            org_size=self._optional_string(
                response.get("org_size")
            ),

            submitted_at=self._optional_string(
                response.get("submitted_at")
            ),

            period=self._optional_string(
                supplier.get("period")
            ),

            response_organization=self._optional_string(
                response.get("organization")
            ),

            submitter_auditor_company=self._optional_string(
                submitter_auditor.get("company")
            ),
            submitter_auditor_tax_number=self._optional_string(
                submitter_auditor.get("tax_number")
            ),
            submitter_auditor_representative=self._optional_string(
                submitter_auditor.get("representative")
            ),
            submitter_auditor_phone=self._optional_string(
                submitter_auditor.get("phone")
            ),
            submitter_auditor_email=self._optional_string(
                submitter_auditor.get("email")
            ),
            submitter_auditor_period=self._optional_string(
                submitter_auditor.get("period")
            ),
        )

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                "value must be a string or None"
            )

        normalized = value.strip()

        return normalized or None