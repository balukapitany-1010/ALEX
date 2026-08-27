from alex.esg.domain.supplier import Supplier


class SupplierService:
    def __init__(self) -> None:
        self._suppliers: list[Supplier] = []

    def create_supplier(
        self,
        name: str,
        tax_number: str,
        country: str | None = None,
    ) -> Supplier:
        if self.get_by_tax_number(tax_number) is not None:
            raise ValueError(
                "supplier with this tax number already exists"
            )

        supplier = Supplier(
            name=name,
            tax_number=tax_number,
            country=country,
        )

        self._suppliers.append(supplier)

        return supplier

    def list_suppliers(self) -> tuple[Supplier, ...]:
        return tuple(self._suppliers)

    def get_by_tax_number(
        self,
        tax_number: str,
    ) -> Supplier | None:
        if not isinstance(tax_number, str):
            raise TypeError(
                "tax_number must be a string"
            )

        normalized_tax_number = tax_number.strip()

        if not normalized_tax_number:
            raise ValueError(
                "tax_number cannot be empty"
            )

        for supplier in self._suppliers:
            if supplier.tax_number == normalized_tax_number:
                return supplier

        return None