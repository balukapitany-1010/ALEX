import pytest

from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier

def test_supplier_inherits_from_company():
    assert issubclass(Supplier, Company)

def test_supplier_is_company():
    supplier = Supplier(
        name = "Teszt Beszállító Kft.",
        tax_number="1234567-2-42",

    )
    assert isinstance(supplier, Supplier)
    assert isinstance(supplier, Company)

def test_suplior_tax_number_is_immutable():
    supplier = Supplier(
        name = "Teszt Beszállító Kft.",
        tax_number = "1234567-2-42",
    )
    with pytest.raises(AttributeError):
        supplier.tax_number = "99999999-9-99"
