from datetime import datetime, timezone

from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.mappers.submission_header_mapper import SubmissionHeaderData
from alex.esg.services.submission_party_resolver import SubmissionPartyResolver
from alex.esg.services.submission_relation_resolver import SubmissionRelationResolver
from alex.esg.services.submission_submitter_resolver import SubmissionSubmitterResolver


class SubmissionBuilderService:
    def __init__(
        self,
        *,
        party_resolver: SubmissionPartyResolver,
        relation_resolver: SubmissionRelationResolver,
        submitter_resolver: SubmissionSubmitterResolver,
    ) -> None:
        if not isinstance(
            party_resolver,
            SubmissionPartyResolver,
        ):
            raise TypeError(
                "party_resolver must be a "
                "SubmissionPartyResolver"
            )

        if not isinstance(
            relation_resolver,
            SubmissionRelationResolver,
        ):
            raise TypeError(
                "relation_resolver must be a "
                "SubmissionRelationResolver"
            )

        if not isinstance(
            submitter_resolver,
            SubmissionSubmitterResolver,
        ):
            raise TypeError(
                "submitter_resolver must be a "
                "SubmissionSubmitterResolver"
            )

        self._party_resolver = party_resolver
        self._relation_resolver = relation_resolver
        self._submitter_resolver = submitter_resolver

    def build(
        self,
        *,
        header: SubmissionHeaderData,
        questionnaire: Questionnaire,
    ) -> Submission:
        if not isinstance(
            header,
            SubmissionHeaderData,
        ):
            raise TypeError("header must be a SubmissionHeaderData")

        if not isinstance(
            questionnaire,
            Questionnaire,
        ):
            raise TypeError("questionnaire must be a Questionnaire")

        if header.period is None:
            raise ValueError("submission period is required")

        parties = self._party_resolver.resolve(header)

        relation = self._relation_resolver.resolve(parties)

        submitter_resolution = (self._submitter_resolver.resolve(header))

        submitted_at = self._parse_submitted_at(header.submitted_at)

        return Submission(
            relation=relation,
            submitter=(
                submitter_resolution.submitter
            ),
            questionnaire=questionnaire,
            period=header.period,
            submitted_at=submitted_at,
            organization_size=header.org_size,
        )

    @staticmethod
    def _parse_submitted_at(
        value: str | None,
    ) -> datetime | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError("submitted_at must be a string or None")

        normalized = value.strip()

        if not normalized:
            return None

        if normalized.endswith("Z"):
            normalized = (normalized[:-1] + "+00:00")

        try:
            result = datetime.fromisoformat(normalized)
        except ValueError as error:
            raise ValueError(
                "submitted_at must be a valid "
                "ISO 8601 datetime"
            ) from error

        if result.tzinfo is None:
            raise ValueError("submitted_at must contain timezone information")

        return result.astimezone(timezone.utc)