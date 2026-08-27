from alex.esg.domain.company import Company

class CompanyService:
    def __init__(self) -> None:
        self._companies: list[Company] = []

    def create_company(
            self,
            name: str,
            tax_number: str,
            country: str | None = None,
    ) -> Company:
        if self.get_by_tax_number(tax_number) is not None:
            raise ValueError("company with same tax_number already exists")
        company = Company(
            name=name,
            tax_number=tax_number,
            country=country
        )
        self._companies.append(company)

        return company

    def list_companies(self) -> tuple[Company, ...]:
        return tuple(self._companies)

    def get_by_tax_number (
            self,
            tax_number: str,
    ) -> Company | None:
        if not isinstance(tax_number, str):
            raise ValueError("tax_number must be a string")

        normalized_tax_number = tax_number.strip()

        if not normalized_tax_number:
            raise  ValueError("tax_number must not be empty")

        for company in self._companies:
            if company.tax_number == normalized_tax_number:
                return company
        return None

    def update_company(
            self,
            tax_number: str,
            *,
            name: str,
            country: str | None = None,
    ) -> Company:
        company = self.get_by_tax_number(tax_number)
        if company is None:
            raise ValueError("company not found")
        company.update(
            name=name,
            country=country,
        )
        return company