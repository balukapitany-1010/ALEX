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


class SubmissionHeaderMapper:
    def map(
        self,
        submission_data: dict[str, Any],
    ) -> SubmissionHeaderData:
        if not isinstance(submission_data, dict):
            raise TypeError("submission_data must be a dictionary")

        response = submission_data.get("response")

        if not isinstance(response, dict):
            raise ValueError("submission response must be an object")

        cover = response.get("cover")

        if not isinstance(cover, dict):
            raise ValueError("response cover must be an object")

        supplier = cover.get("supplier")

        if not isinstance(supplier, dict):
            raise ValueError("cover supplier must be an object")

        requester = cover.get("requester")

        if not isinstance(requester, dict):
            raise ValueError("cover requester must be an object")

        return SubmissionHeaderData(
            supplier_company=self._optional_string(supplier.get("company")),
            supplier_tax_number=self._optional_string(supplier.get("tax_number")),

            requester_company=self._optional_string(requester.get("company")),
            requester_tax_number=self._optional_string(requester.get("tax_number")),
            requester_mp_id=self._optional_string(requester.get("requester_MP_id")),

            respondent_id=self._optional_string(response.get("respondent_id")),
            respondent_mp_id=self._optional_string(response.get("respondent_MP_id")),
            org_size=self._optional_string(response.get("org_size")),

            submitted_at=self._optional_string(response.get("submitted_at")),

            period=self._optional_string(supplier.get("period")),
        )

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError("value must be a string or None")

        normalized = value.strip()

        return normalized or None