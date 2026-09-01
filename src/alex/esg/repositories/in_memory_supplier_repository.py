from alex.esg.domain.supplier import Supplier
from alex.esg.repositories.supplier_repository import SupplierRepository


class InMemorySupplierRepository(
    SupplierRepository
):
    def __init__(self) -> None:
        self._suppliers: list[Supplier] = []

    def add(
        self,
        supplier: Supplier,
    ) -> Supplier:
        if not isinstance(
            supplier,
            Supplier,
        ):
            raise TypeError("supplier must be a Supplier")

        if (
            self.get_by_tax_number(
                supplier.tax_number
            )
            is not None
        ):
            raise ValueError(
                "supplier with this tax number "
                "already exists"
            )

        if (
            self.get_by_key( supplier.company_key)
            is not None
        ):
            raise ValueError(
                "supplier with this key "
                "already exists"
            )

        self._suppliers.append(
            supplier
        )

        return supplier

    def list_all(
        self,
    ) -> tuple[Supplier, ...]:
        return tuple(
            self._suppliers
        )

    def get_by_tax_number(
        self,
        tax_number: str,
    ) -> Supplier | None:
        if not isinstance(
            tax_number,
            str,
        ):
            raise TypeError("tax_number must be a string")

        normalized = tax_number.strip()

        if not normalized:
            raise ValueError("tax_number cannot be empty")

        for supplier in self._suppliers:
            if (
                supplier.tax_number == normalized
            ):
                return supplier

        return None

    def get_by_key(
        self,
        company_key: str,
    ) -> Supplier | None:
        if not isinstance(
            company_key,
            str,
        ):
            raise TypeError( "company_key must be a string")

        normalized = company_key.strip()

        if not normalized:
            raise ValueError("company_key cannot be empty")

        for supplier in self._suppliers:
            if (supplier.company_key == normalized):
                return supplier

        return None