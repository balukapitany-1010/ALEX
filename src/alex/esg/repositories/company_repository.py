from abc import ABC, abstractmethod

from alex.esg.domain.company import Company


class CompanyRepository(ABC):
    @abstractmethod
    def add(
        self,
        company: Company,
    ) -> Company:
        pass

    @abstractmethod
    def list_all(
        self,
    ) -> tuple[Company, ...]:
        pass

    @abstractmethod
    def get_by_tax_number(
        self,
        tax_number: str,
    ) -> Company | None:
        pass

    @abstractmethod
    def get_by_key(
        self,
        company_key: str,
    ) -> Company | None:
        pass

    @abstractmethod
    def update(
            self,
            company: Company,
    ) -> Company:
        pass

    @abstractmethod
    def remove(
            self,
            company_key: str,
    ) -> Company:
        pass