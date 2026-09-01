import pytest

from alex.esg.domain.company import Company
from alex.esg.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
)


def test_repository_adds_company():
    repository = (
        InMemoryCompanyRepository()
    )

    company = Company(
        name="Teszt Kft.",
        tax_number="11111111-2-41",
        country="HU",
    )

    result = repository.add(
        company
    )

    assert result is company

    assert (
        repository.list_all()
        == (company,)
    )


def test_repository_gets_company_by_tax_number():
    repository = (
        InMemoryCompanyRepository()
    )

    company = Company(
        name="Teszt Kft.",
        tax_number="11111111-2-41",
        country="HU",
    )

    repository.add(
        company
    )

    result = (
        repository.get_by_tax_number(
            "11111111-2-41"
        )
    )

    assert result is company


def test_repository_gets_company_by_key():
    repository = (
        InMemoryCompanyRepository()
    )

    company = Company(
        name="Teszt Kft.",
        tax_number="11111111-2-41",
        country="HU",
    )

    repository.add(
        company
    )

    result = repository.get_by_key(
        company.company_key
    )

    assert result is company


def test_repository_returns_none_for_unknown_tax_number():
    repository = (
        InMemoryCompanyRepository()
    )

    assert (
        repository.get_by_tax_number(
            "99999999-2-41"
        )
        is None
    )


def test_repository_rejects_duplicate_tax_number():
    repository = (
        InMemoryCompanyRepository()
    )

    repository.add(
        Company(
            name="Első Kft.",
            tax_number="11111111-2-41",
            country="HU",
        )
    )

    with pytest.raises(
        ValueError,
        match="tax number",
    ):
        repository.add(
            Company(
                name="Második Kft.",
                tax_number="11111111-2-41",
                country="HU",
            )
        )