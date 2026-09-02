from alex.esg.domain.company import Company
from alex.esg.repositories.company_repository import (
    CompanyRepository,
)


class InMemoryCompanyRepository(
    CompanyRepository
):
    def __init__(self) -> None:
        self._companies: list[Company] = []

    def add(
        self,
        company: Company,
    ) -> Company:
        if not isinstance(
            company,
            Company,
        ):
            raise TypeError("company must be a Company")

        if (self.get_by_tax_number(company.tax_number)is not None):
            raise ValueError(
                "company with this tax number "
                "already exists"
            )

        if (self.get_by_key(company.company_key) is not None
        ):
            raise ValueError(
                "company with this key "
                "already exists"
            )

        self._companies.append(company)
        return company

    def list_all(
        self,
    ) -> tuple[Company, ...]:
        return tuple(self._companies)

    def get_by_tax_number(
        self,
        tax_number: str,
    ) -> Company | None:
        if not isinstance(
            tax_number,
            str,
        ):
            raise TypeError("tax_number must be a string")

        normalized = tax_number.strip()

        if not normalized:
            raise ValueError("tax_number cannot be empty")

        for company in self._companies:
            if (company.tax_number == normalized):
                return company

        return None

    def get_by_key(
        self,
        company_key: str,
    ) -> Company | None:
        if not isinstance(
            company_key,
            str,
        ):
            raise TypeError("company_key must be a string")

        normalized = company_key.strip()

        if not normalized:
            raise ValueError("company_key cannot be empty")

        for company in self._companies:
            if (company.company_key == normalized
            ):
                return company

        return None

    def update(
            self,
            company: Company,
    ) -> Company:
        if not isinstance(
                company,
                Company,
        ):
            raise TypeError("company must be a Company")

        existing = self.get_by_key(company.company_key)

        if existing is None:
            raise ValueError("company does not exist")

        return company

    def remove(
            self,
            company_key: str,
    ) -> Company:
        company = self.get_by_key(company_key)

        if company is None:
            raise ValueError("company does not exist")

        self._companies.remove(company)

        return company