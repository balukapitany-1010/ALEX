import pytest

from alex.esg.domain.supplier import Supplier
from alex.esg.repositories.in_memory_supplier_repository import (
    InMemorySupplierRepository,
)


def _create_supplier(
    *,
    name: str = "Beszállító Kft.",
    tax_number: str = "11111111-2-41",
) -> Supplier:
    return Supplier(
        name=name,
        tax_number=tax_number,
        country="HU",
    )


def test_repository_adds_supplier():
    repository = (
        InMemorySupplierRepository()
    )

    supplier = _create_supplier()

    result = repository.add(
        supplier
    )

    assert result is supplier

    assert (
        repository.list_all()
        == (supplier,)
    )


def test_repository_gets_supplier_by_tax_number():
    repository = (
        InMemorySupplierRepository()
    )

    supplier = _create_supplier()

    repository.add(
        supplier
    )

    result = (
        repository.get_by_tax_number(
            "11111111-2-41"
        )
    )

    assert result is supplier


def test_repository_gets_supplier_by_key():
    repository = (
        InMemorySupplierRepository()
    )

    supplier = _create_supplier()

    repository.add(
        supplier
    )

    result = repository.get_by_key(
        supplier.company_key
    )

    assert result is supplier


def test_repository_returns_none_for_unknown_tax_number():
    repository = (
        InMemorySupplierRepository()
    )

    assert (
        repository.get_by_tax_number(
            "99999999-2-41"
        )
        is None
    )


def test_repository_rejects_duplicate_tax_number():
    repository = (
        InMemorySupplierRepository()
    )

    repository.add(
        _create_supplier()
    )

    with pytest.raises(
        ValueError,
        match="tax number",
    ):
        repository.add(
            _create_supplier(
                name="Másik Beszállító Kft.",
            )
        )


def test_repository_rejects_company_instead_of_supplier():
    from alex.esg.domain.company import Company

    repository = (
        InMemorySupplierRepository()
    )

    company = Company(
        name="Nem beszállító Kft.",
        tax_number="22222222-2-41",
        country="HU",
    )

    with pytest.raises(
        TypeError,
        match="supplier must be a Supplier",
    ):
        repository.add(
            company
        )