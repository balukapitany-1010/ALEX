import pytest
from alex.esg.repositories.in_memory_company_repository import InMemoryCompanyRepository
from alex.esg.services.company_service import CompanyService

def test_company_services_can_create_companies():
    service = CompanyService()

    company = service.create_company(
        name = "Teszt Kft.",
        tax_number = "12345678-2-41",
        country = "HU",
    )
    assert company.name == "Teszt Kft."
    assert company.tax_number == "12345678-2-41"
    assert company.country == "HU"


def test_company_service_lists_companies():
    service = CompanyService()
    company1 = service.create_company(
        name = "Első Kft.",
        tax_number = "12345678-2-41",
    )
    company2 = service.create_company(
        name = "Második Kft.",
        tax_number = "22222222-2-41",
    )
    assert service.list_companies() == (company1, company2)

def test_company_service_can_get_company_by_tax_number():
    service = CompanyService()
    company = service.create_company(
        name = "Teszt Kft.",
        tax_number = "12345678-2-41",
    )
    result = service.get_by_tax_number("12345678-2-41")
    assert result is company

def test_company_service_returns_none_for_missing_tax_number():
    service = CompanyService()
    result = service.get_by_tax_number("12345678-2-41")
    assert result is None

def test_company_service_rejects_duplicate_tax_number():
    service = CompanyService()
    service.create_company(
        name = "Első Kft.",
        tax_number = "12345678-2-41",
    )
    with pytest.raises(ValueError, match = "company with same tax_number already exists"):
        service.create_company(
            name = "Második Kft.",
            tax_number = "12345678-2-41",
        )

def test_company_service_can_update_company():
    service = CompanyService()
    company = service.create_company(
        name = "Régi Kft.",
        tax_number = "12345678-2-41",
        country = "HU",
    )
    result = service.update_company(
        tax_number = "12345678-2-41",
        name = "Új Kft.",
        country = "AT",
    )
    assert result is company
    assert company.name == "Új Kft."
    assert company.tax_number == "12345678-2-41"
    assert company.country == "AT"

def test_company_service_uses_injected_repository():
    repository = (
        InMemoryCompanyRepository()
    )

    service = CompanyService(
        repository=repository
    )

    company = service.create_company(
        name="Teszt Kft.",
        tax_number="11111111-2-41",
        country="HU",
    )

    assert (repository.list_all() == (company,))

    assert ( repository.get_by_tax_number("11111111-2-41")is company)
def test_company_service_uses_in_memory_repository_by_default():
    service = CompanyService()

    company = service.create_company(
        name="Teszt Kft.",
        tax_number="11111111-2-41",
        country="HU",
    )

    assert (service.list_companies() == (company,))

def test_company_service_rejects_invalid_repository():
    with pytest.raises(
        TypeError,
        match="repository must be a CompanyRepository",
    ):
        CompanyService(repository="invalid")
def test_company_service_can_remove_company():
    service = CompanyService()

    company = service.create_company(
        name="Teszt Kft.",
        tax_number="11111111-2-41",
        country="HU",
    )

    removed = service.remove_company(
        company.company_key
    )

    assert removed is company

    assert (
        service.list_companies()
        == ()
    )