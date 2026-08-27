import pytest

from alex.esg.domain.supplier import Supplier
from alex.esg.services.supplier_service import SupplierService


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
        match="supplier with this tax number already exists",
    ):
        service.create_supplier(
            name="Második Kft.",
            tax_number="12345678-2-41",
        )