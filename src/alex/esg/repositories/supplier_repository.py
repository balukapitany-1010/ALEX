from abc import ABC, abstractmethod

from alex.esg.domain.supplier import Supplier


class SupplierRepository(ABC):
    @abstractmethod
    def add(
        self,
        supplier: Supplier,
    ) -> Supplier:
        pass

    @abstractmethod
    def list_all(
        self,
    ) -> tuple[Supplier, ...]:
        pass

    @abstractmethod
    def get_by_tax_number(
        self,
        tax_number: str,
    ) -> Supplier | None:
        pass

    @abstractmethod
    def get_by_key(
        self,
        company_key: str,
    ) -> Supplier | None:
        pass

    @abstractmethod
    def update(
            self,
            supplier: Supplier,
    ) -> Supplier:
        pass

    @abstractmethod
    def remove(
            self,
            company_key: str,
    ) -> Supplier:
        pass