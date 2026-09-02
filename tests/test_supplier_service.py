import pytest

from alex.esg.domain.supplier import Supplier
from alex.esg.services.supplier_service import SupplierService
from alex.esg.repositories.in_memory_supplier_repository import InMemorySupplierRepository

def test_supplier_service_can_create_supplier():
    service = SupplierService()

    supplier = service.create_supplier(
        name="Beszállító Kft.",
        tax_number="12345678-2-41",
        country="HU",
    )

    assert isinstance(supplier, Supplier)
    assert supplier.name == "Beszállító Kft."
    assert supplier.tax_number == "12345678-2-41"
    assert supplier.country == "HU"


def test_supplier_service_lists_suppliers():
    service = SupplierService()

    supplier1 = service.create_supplier(
        name="Első Kft.",
        tax_number="11111111-2-41",
    )

    supplier2 = service.create_supplier(
        name="Második Kft.",
        tax_number="22222222-2-41",
    )

    assert service.list_suppliers() == (
        supplier1,
        supplier2,
    )


def test_supplier_service_can_get_supplier_by_tax_number():
    service = SupplierService()

    supplier = service.create_supplier(
        name="Beszállító Kft.",
        tax_number="12345678-2-41",
    )

    result = service.get_by_tax_number(
        "12345678-2-41"
    )

    assert result is supplier


def test_supplier_service_rejects_duplicate_tax_number():
    service = SupplierService()

    service.create_supplier(
        name="Első Kft.",
        tax_number="12345678-2-41",
    )

    with pytest.raises(
            ValueError,
            match="supplier with same tax_number already exists",
    ):
        service.create_supplier(
            name="Második Kft.",
            tax_number="12345678-2-41",
        )

def test_supplier_service_uses_injected_repository():
    repository = (
        InMemorySupplierRepository()
    )

    service = SupplierService(
        repository=repository
    )

    supplier = service.create_supplier(
        name="Beszállító Kft.",
        tax_number="11111111-2-41",
        country="HU",
    )

    assert (
        repository.list_all()
        == (supplier,)
    )


def test_supplier_service_uses_in_memory_repository_by_default():
    service = SupplierService()

    supplier = service.create_supplier(
        name="Beszállító Kft.",
        tax_number="11111111-2-41",
        country="HU",
    )

    assert (
        service.list_suppliers()
        == (supplier,)
    )


def test_supplier_service_rejects_invalid_repository():
    with pytest.raises(
        TypeError,
        match="repository must be a SupplierRepository",
    ):
        SupplierService(
            repository="invalid"
        )
def test_supplier_service_can_remove_supplier():
    service = SupplierService()

    supplier = service.create_supplier(
        name="Beszállító Kft.",
        tax_number="11111111-2-41",
        country="HU",
    )

    removed = service.remove_supplier(
        supplier.company_key
    )

    assert removed is supplier

    assert (
        service.list_suppliers()
        == ()
    )