from datetime import timezone

import pytest

from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.mappers.submission_header_mapper import SubmissionHeaderData
from alex.esg.services.company_service import CompanyService
from alex.esg.services.submission_builder_service import SubmissionBuilderService
from alex.esg.services.submission_party_resolver import SubmissionPartyResolver
from alex.esg.services.submission_relation_resolver import SubmissionRelationResolver
from alex.esg.services.submission_submitter_resolver import SubmissionSubmitterResolver
from alex.esg.services.supplier_service import SupplierService
from alex.esg.services.supply_chain_relation_service import SupplyChainRelationService


def _create_builder():
    company_service = CompanyService()
    supplier_service = SupplierService()
    relation_service = SupplyChainRelationService()

    party_resolver = SubmissionPartyResolver(
        company_service=company_service,
        supplier_service=supplier_service,
    )

    relation_resolver = SubmissionRelationResolver(
        relation_service=relation_service,
    )

    submitter_resolver = SubmissionSubmitterResolver(
        company_service=company_service,
    )

    builder = SubmissionBuilderService(
        party_resolver=party_resolver,
        relation_resolver=relation_resolver,
        submitter_resolver=submitter_resolver,
    )

    return (
        builder,
        company_service,
        supplier_service,
        relation_service,
    )


def _create_header(
    *,
    period: str | None = "2026-Q1",
    submitted_at: str | None = (
        "2026-02-12T11:54:29Z"
    ),
    submitter_company: str | None = None,
    submitter_tax_number: str | None = None,
) -> SubmissionHeaderData:
    return SubmissionHeaderData(
        supplier_company="Beszállító Kft.",
        supplier_tax_number="11111111-2-41",

        requester_company="Kötelezett Zrt.",
        requester_tax_number="22222222-2-41",
        requester_mp_id="REQ-1",

        respondent_id="RESP-1",
        respondent_mp_id="RESP-MP-1",
        org_size="Large",

        submitted_at=submitted_at,
        period=period,

        response_organization=None,

        submitter_auditor_company=(submitter_company),
        submitter_auditor_tax_number=(submitter_tax_number),
    )


def _create_questionnaire():
    return Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )


def test_builder_creates_submission():
    (
        builder,
        _,
        _,
        relation_service,
    ) = _create_builder()

    questionnaire = _create_questionnaire()

    submission = builder.build(
        header=_create_header(),
        questionnaire=questionnaire,
    )

    assert (submission.questionnaire is questionnaire)

    assert submission.period == "2026-Q1"

    assert (submission.organization_size == "Large")

    assert submission.submitter is None

    assert (submission.relation.requester.name == "Kötelezett Zrt.")

    assert (submission.relation.supplier.name == "Beszállító Kft.")

    assert len(relation_service.list_relations()) == 1


def test_builder_maps_submitted_at():
    builder, _, _, _ = _create_builder()

    submission = builder.build(
        header=_create_header(
            submitted_at=(
                "2026-02-12T11:54:29Z"
            )
        ),
        questionnaire=_create_questionnaire(),
    )

    assert submission.submitted_at is not None

    assert (submission.submitted_at.year == 2026)

    assert (submission.submitted_at.month == 2)

    assert (submission.submitted_at.day == 12)

    assert (submission.submitted_at.tzinfo == timezone.utc)


def test_builder_allows_unknown_submitter():
    builder, _, _, _ = _create_builder()

    submission = builder.build(
        header=_create_header(),
        questionnaire=_create_questionnaire(),
    )

    assert submission.submitter is None


def test_builder_resolves_explicit_submitter():
    builder, _, _, _ = _create_builder()

    submission = builder.build(
        header=_create_header(
            submitter_company="Audit Kft.",
            submitter_tax_number=(
                "33333333-2-41"
            ),
        ),
        questionnaire=_create_questionnaire(),
    )

    assert submission.submitter is not None

    assert (submission.submitter.name == "Audit Kft.")

    assert (submission.submitter.tax_number == "33333333-2-41")


def test_builder_rejects_missing_period():
    builder, _, _, _ = _create_builder()

    with pytest.raises(
        ValueError,
        match="submission period is required",
    ):
        builder.build(
            header=_create_header(
                period=None
            ),
            questionnaire=_create_questionnaire(),
        )


def test_builder_rejects_invalid_submitted_at():
    builder, _, _, _ = _create_builder()

    with pytest.raises(
        ValueError,
        match=(
            "submitted_at must be a valid "
            "ISO 8601 datetime"
        ),
    ):
        builder.build(
            header=_create_header(
                submitted_at="nem-datum"
            ),
            questionnaire=_create_questionnaire(),
        )


def test_builder_rejects_datetime_without_timezone():
    builder, _, _, _ = _create_builder()

    with pytest.raises(
        ValueError,
        match=(
            "submitted_at must contain "
            "timezone information"
        ),
    ):
        builder.build(
            header=_create_header(
                submitted_at=(
                    "2026-02-12T11:54:29"
                )
            ),
            questionnaire=_create_questionnaire(),
        )