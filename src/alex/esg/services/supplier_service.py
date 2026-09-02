from alex.esg.domain.supplier import Supplier
from alex.esg.repositories.in_memory_supplier_repository import InMemorySupplierRepository
from alex.esg.repositories.supplier_repository import SupplierRepository


class SupplierService:
    def __init__(
        self,
        repository: SupplierRepository | None = None,
    ) -> None:
        if repository is None:
            repository = InMemorySupplierRepository()

        if not isinstance(
            repository,
            SupplierRepository,
        ):
            raise TypeError("repository must be a SupplierRepository")

        self._repository = repository

    def create_supplier(
        self,
        *,
        name: str,
        tax_number: str,
        country: str | None = None,
    ) -> Supplier:
        existing = (self._repository.get_by_tax_number(tax_number))

        if existing is not None:
            raise ValueError(
                "supplier with same tax_number "
                "already exists"
            )

        supplier = Supplier(
            name=name,
            tax_number=tax_number,
            country=country,
        )

        return self._repository.add(supplier)

    def list_suppliers(
        self,
    ) -> tuple[Supplier, ...]:
        return self._repository.list_all()

    def get_by_tax_number(
        self,
        tax_number: str,
    ) -> Supplier | None:
        return (self._repository.get_by_tax_number(tax_number))

    def get_by_key(
        self,
        company_key: str,
    ) -> Supplier | None:
        return (self._repository.get_by_key(company_key))

    def update_supplier(
        self,
        supplier: Supplier | None = None,
        *,
        tax_number: str | None = None,
        name: str | None = None,
        country: str | None = None,
    ) -> Supplier:
        if supplier is not None:
            if not isinstance(
                supplier,
                Supplier,
            ):
                raise TypeError("supplier must be a Supplier")

            existing = (self._repository.get_by_key(supplier.company_key))

            if existing is None:
                raise ValueError("supplier does not exist")

        else:
            if tax_number is None:
                raise ValueError("tax_number is required")

            supplier = (self._repository.get_by_tax_number(tax_number))

            if supplier is None:
                raise ValueError("supplier does not exist")

        supplier.update(
            name=name,
            country=country,
        )

        return self._repository.update(supplier)

    def remove_supplier(
            self,
            company_key: str,
    ) -> Supplier:
        return self._repository.remove(company_key)