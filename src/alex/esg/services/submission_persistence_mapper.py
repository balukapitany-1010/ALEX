from dataclasses import dataclass
from datetime import (
    datetime,
    timezone,
)
import json
import re

@dataclass(frozen=True)
class SubmissionPersistenceData:
    batch_id: str
    relation_id: int
    external_supplier_key: str
    respondent_id: str
    respondent_mp_id: str | None
    org_size: str | None
    submitted_at: datetime | None
    status: str
    raw_payload: str

class SubmissionPersistenceMapper:
    @staticmethod
    def normalize_tax_number(
            tax_number: str,
    ) -> str:
        if not isinstance(
                tax_number,
                str,
        ):
            raise TypeError("tax_number must be a string")

        normalized = "".join(character for character in tax_number.upper() if character.isalnum()
        )

        if not normalized:
            raise ValueError("tax_number cannot be empty")

        return normalized

    @classmethod
    def create_external_supplier_key(
        cls,
        supplier_tax_number: str,
    ) -> str:
        return ("SUP_" + cls.normalize_tax_number(supplier_tax_number))

    @classmethod
    def create_respondent_id(
        cls,
        supplier_tax_number: str,
        period: str | None,
    ) -> str:
        normalized_tax_number = (cls.normalize_tax_number(supplier_tax_number))

        if period is None:
            return (f"RESP_{normalized_tax_number}""_NOPERIOD")

        normalized_period = str(period).strip()

        if not normalized_period:
            return (f"RESP_{normalized_tax_number}""_NOPERIOD")

        return (
            f"RESP_{normalized_tax_number}_"
            f"{normalized_period}"
        )

    @classmethod
    def create_batch_id(
        cls,
        requester_tax_number: str,
        created_at: datetime,
    ) -> str:
        normalized_tax_number = (cls.normalize_tax_number(requester_tax_number))
        timestamp = created_at.strftime("%Y%m%d%H%M%S")
        return (
            f"BATCH_{normalized_tax_number}_"
            f"{timestamp}"
        )

    @staticmethod
    def serialize_raw_payload(
        submission_payload: dict,
    ) -> str:
        return json.dumps(
            submission_payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @staticmethod
    def optional_text(
        value,
    ) -> str | None:
        if value is None:
            return None

        text = str(value).strip()

        if not text:
            return None

        return text

    @classmethod
    def parse_submitted_at(
        cls,
        value,
    ) -> datetime | None:
        text = cls.optional_text(
            value
        )

        if text is None:
            return None

        if text.endswith("Z"):
            text = (
                text[:-1]
                + "+00:00"
            )

        try:
            parsed = datetime.fromisoformat(
                text
            )
        except ValueError as error:
            raise ValueError(
                "invalid submitted_at: "
                f"{value}"
            ) from error

        if parsed.tzinfo is not None:
            parsed = (
                parsed
                .astimezone(
                    timezone.utc
                )
                .replace(
                    tzinfo=None
                )
            )

        return parsed

    @classmethod
    def map_submission(
        cls,
        submission_payload: dict,
        batch_id: str,
        relation_id: int,
        status: str = "imported_complete",
    ) -> SubmissionPersistenceData:
        if not isinstance(
            submission_payload,
            dict,
        ):
            raise TypeError("submission_payload must be a dict")

        batch_id = cls.optional_text(batch_id)

        if batch_id is None:
            raise ValueError("batch_id cannot be empty")

        if (
            not isinstance(
                relation_id,
                int,
            )
            or isinstance(
                relation_id,
                bool,
            )
        ):
            raise TypeError("relation_id must be an integer")

        response = (submission_payload.get("response") or {})
        cover = (response.get("cover") or {})
        supplier = (cover.get("supplier") or {})

        supplier_tax_number = (cls.optional_text(supplier.get("tax_number")))
        if supplier_tax_number is None:
            raise ValueError("supplier tax_number is required")
        period = cls.optional_text(supplier.get("period"))
        external_supplier_key = (cls.optional_text(submission_payload.get("supplier_key")))
        if external_supplier_key is None:
            external_supplier_key = (cls.create_external_supplier_key(supplier_tax_number))
        respondent_id = cls.optional_text(response.get("respondent_id"))
        if respondent_id is None:
            respondent_id = (cls.create_respondent_id(
                    supplier_tax_number,
                    period,
                )
            )
        respondent_mp_id = (cls.optional_text(response.get("respondent_MP_id")))
        org_size = cls.optional_text(response.get("org_size"))
        submitted_at = (
            cls.parse_submitted_at(
                response.get("submitted_at")
            )
        )

        raw_payload_data = (
            cls._build_raw_payload(
                submission_payload
            )
        )

        return SubmissionPersistenceData(
            batch_id=batch_id,
            relation_id=relation_id,
            external_supplier_key=external_supplier_key,
            respondent_id=respondent_id,
            respondent_mp_id=respondent_mp_id,
            org_size=org_size,
            submitted_at=submitted_at,
            status=status,
            raw_payload=(
                cls.serialize_raw_payload(
                    raw_payload_data
                )
            ),
        )

    @staticmethod
    def _build_raw_payload(
            submission_payload: dict,
    ) -> dict:
        raw_payload = dict(submission_payload)
        response = (submission_payload.get( "response") or {})
        cover = (response.get("cover")or {})
        requester = cover.get("requester")
        if isinstance(
                requester,
                dict,
        ):
            raw_payload["requester"] = dict(requester)
        return raw_payload