import pytest

from alex.esg.mappers.submission_header_mapper import SubmissionHeaderData
from alex.esg.services.company_service import CompanyService
from alex.esg.services.submission_submitter_resolver import SubmissionSubmitterResolver


def _create_header(
    *,
    company: str | None = None,
    tax_number: str | None = None,
) -> SubmissionHeaderData:
    return SubmissionHeaderData(
        supplier_company="Beszállító Kft.",
        supplier_tax_number="11111111-2-41",
        requester_company="Kötelezett Zrt.",
        requester_tax_number="22222222-2-41",
        requester_mp_id=None,
        respondent_id=None,
        respondent_mp_id=None,
        org_size=None,
        submitted_at=None,
        period="2026-Q1",
        response_organization=None,
        submitter_auditor_company=company,
        submitter_auditor_tax_number=tax_number,
    )


def test_submitter_resolver_creates_explicit_submitter():
    company_service = CompanyService()

    resolver = SubmissionSubmitterResolver(company_service=company_service)

    result = resolver.resolve(
        _create_header(
            company="Audit Kft.",
            tax_number="33333333-2-41",
        )
    )

    assert result.is_resolved is True
    assert result.submitter is not None

    assert result.submitter.name == "Audit Kft."

    assert (result.submitter.tax_number == "33333333-2-41")

    assert len(company_service.list_companies()) == 1


def test_submitter_resolver_reuses_existing_company():
    company_service = CompanyService()

    existing = company_service.create_company(
        name="Audit Kft.",
        tax_number="33333333-2-41",
    )

    resolver = SubmissionSubmitterResolver(
        company_service=company_service,
    )

    result = resolver.resolve(
        _create_header(
            company="Audit Kft.",
            tax_number="33333333-2-41",
        )
    )

    assert result.is_resolved is True
    assert result.submitter is existing

    assert len(company_service.list_companies()) == 1


def test_submitter_resolver_returns_unresolved_when_missing():
    company_service = CompanyService()

    resolver = SubmissionSubmitterResolver(
        company_service=company_service,
    )

    result = resolver.resolve(
        _create_header()
    )

    assert result.is_resolved is False
    assert result.submitter is None

    assert (company_service.list_companies() == ())


def test_submitter_resolver_rejects_company_without_tax_number():
    company_service = CompanyService()

    resolver = SubmissionSubmitterResolver(
        company_service=company_service,
    )

    with pytest.raises(
        ValueError,
        match="submitter tax number is required",
    ):
        resolver.resolve(
            _create_header(
                company="Audit Kft.",
                tax_number=None,
            )
        )


def test_submitter_resolver_rejects_tax_number_without_company():
    company_service = CompanyService()

    resolver = SubmissionSubmitterResolver(
        company_service=company_service,
    )

    with pytest.raises(
        ValueError,
        match="submitter company is required",
    ):
        resolver.resolve(
            _create_header(
                company=None,
                tax_number="33333333-2-41",
            )
        )