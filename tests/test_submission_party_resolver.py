import pytest

from alex.esg.mappers.submission_header_mapper import (
    SubmissionHeaderData,
)
from alex.esg.services.company_service import (
    CompanyService,
)
from alex.esg.services.submission_party_resolver import (
    SubmissionPartyResolver,
)
from alex.esg.services.supplier_service import (
    SupplierService,
)


def _create_header() -> SubmissionHeaderData:
    return SubmissionHeaderData(
        supplier_company="Beszállító Kft.",
        supplier_tax_number="11111111-2-41",
        requester_company="Kötelezett Zrt.",
        requester_tax_number="22222222-2-41",
        requester_mp_id="REQ-1",
        respondent_id="RESP-1",
        respondent_mp_id=None,
        org_size="Large",
        submitted_at="2026-02-12T11:54:29Z",
        period="2026-Q1",
    )


def test_resolver_creates_missing_parties():
    company_service = CompanyService()
    supplier_service = SupplierService()

    resolver = SubmissionPartyResolver(
        company_service=company_service,
        supplier_service=supplier_service,
    )

    result = resolver.resolve(
        _create_header()
    )

    assert (
        result.requester.name
        == "Kötelezett Zrt."
    )

    assert (
        result.requester.tax_number
        == "22222222-2-41"
    )

    assert (
        result.supplier.name
        == "Beszállító Kft."
    )

    assert (
        result.supplier.tax_number
        == "11111111-2-41"
    )


def test_resolver_reuses_existing_parties():
    company_service = CompanyService()
    supplier_service = SupplierService()

    requester = company_service.create_company(
        name="Kötelezett Zrt.",
        tax_number="22222222-2-41",
    )

    supplier = supplier_service.create_supplier(
        name="Beszállító Kft.",
        tax_number="11111111-2-41",
    )

    resolver = SubmissionPartyResolver(
        company_service=company_service,
        supplier_service=supplier_service,
    )

    result = resolver.resolve(
        _create_header()
    )

    assert result.requester is requester
    assert result.supplier is supplier

    assert len(
        company_service.list_companies()
    ) == 1

    assert len(
        supplier_service.list_suppliers()
    ) == 1


def test_resolver_rejects_missing_supplier_tax_number():
    company_service = CompanyService()
    supplier_service = SupplierService()

    header = SubmissionHeaderData(
        supplier_company="Beszállító Kft.",
        supplier_tax_number=None,
        requester_company="Kötelezett Zrt.",
        requester_tax_number="22222222-2-41",
        requester_mp_id=None,
        respondent_id=None,
        respondent_mp_id=None,
        org_size=None,
        submitted_at=None,
        period="2026-Q1",
    )

    resolver = SubmissionPartyResolver(
        company_service=company_service,
        supplier_service=supplier_service,
    )

    with pytest.raises(
        ValueError,
        match="supplier tax number is required",
    ):
        resolver.resolve(header)


def test_resolver_rejects_missing_requester_tax_number():
    company_service = CompanyService()
    supplier_service = SupplierService()

    header = SubmissionHeaderData(
        supplier_company="Beszállító Kft.",
        supplier_tax_number="11111111-2-41",
        requester_company="Kötelezett Zrt.",
        requester_tax_number=None,
        requester_mp_id=None,
        respondent_id=None,
        respondent_mp_id=None,
        org_size=None,
        submitted_at=None,
        period="2026-Q1",
    )

    resolver = SubmissionPartyResolver(
        company_service=company_service,
        supplier_service=supplier_service,
    )

    with pytest.raises(
        ValueError,
        match="requester tax number is required",
    ):
        resolver.resolve(header)