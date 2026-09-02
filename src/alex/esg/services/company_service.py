from alex.esg.domain.company import Company
from alex.esg.repositories.company_repository import CompanyRepository
from alex.esg.repositories.in_memory_company_repository import InMemoryCompanyRepository


class CompanyService:
    def __init__(
        self,
        repository: CompanyRepository | None = None,
    ) -> None:
        if repository is None:
            repository = InMemoryCompanyRepository()

        if not isinstance(
            repository,
            CompanyRepository,
        ):
            raise TypeError("repository must be a CompanyRepository")

        self._repository = repository

    def create_company(
        self,
        *,
        name: str,
        tax_number: str,
        country: str | None = None,
    ) -> Company:
        existing = (self._repository.get_by_tax_number(tax_number))

        if existing is not None:
            raise ValueError(
                "company with same tax_number "
                "already exists"
            )

        company = Company(
            name=name,
            tax_number=tax_number,
            country=country,
        )

        return self._repository.add(company)

    def list_companies(
        self,
    ) -> tuple[Company, ...]:
        return self._repository.list_all()

    def remove_company(
            self,
            company_key: str,
    ) -> Company:
        return self._repository.remove(company_key)

    def get_by_tax_number(
        self,
        tax_number: str,
    ) -> Company | None:
        return (self._repository.get_by_tax_number(tax_number))

    def get_by_key(
        self,
        company_key: str,
    ) -> Company | None:
        return (self._repository.get_by_key(company_key))

    def update_company(
        self,
        company: Company | None = None,
        *,
        tax_number: str | None = None,
        name: str | None = None,
        country: str | None = None,
    ) -> Company:
        if company is not None:
            if not isinstance(
                company,
                Company,
            ):
                raise TypeError("company must be a Company")

            existing = (self._repository.get_by_key(company.company_key))

            if existing is None:
                raise ValueError("company does not exist")

        else:
            if tax_number is None:
                raise ValueError("tax_number is required")

            company = (self._repository.get_by_tax_number(tax_number))

            if company is None:
                raise ValueError("company does not exist")

        company.update(
            name=name,
            country=country,
        )

        return company