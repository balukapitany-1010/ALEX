"""Company domain model."""

import re
from datetime import UTC, datetime, timezone


class Company:
    """Az ALEX rendszerben nyilvántartott vállalat alap domain objektuma."""

    def __init__(
        self,
        name: str,
        tax_number: str,
        country: str | None = None,
    ) -> None:
        name = name.strip()
        tax_number = tax_number.strip()

        if not name:
            raise ValueError("A cégnév megadása kötelező.")

        if not tax_number:
            raise ValueError("Az adószám megadása kötelező.")

        if country is not None:
            country = country.strip() or None

        self._name = name
        self._tax_number = tax_number
        self._company_key = self._generate_company_key(tax_number)
        self._country = country

        now = datetime.now(UTC)
        self.created_at = now
        self.updated_at = now


    @property
    def company_key(self) -> str:
        return self._company_key


    @property
    def country(self) -> str |None:
        return self._country


    @property
    def name(self) -> str:
        return self._name

    @property
    def tax_number(self) -> str:
        return self._tax_number

    def rename(self, new_name: str) -> None:
        new_name = new_name.strip()

        if not new_name:
            raise ValueError("A cégnév megadása kötelező")
        self._name = new_name
        self.updated_at = datetime.now(UTC)



    @staticmethod
    def _generate_company_key(tax_number: str) -> str:
        normalized_tax_number = re.sub(r"[^A-Za-z0-9]", "", tax_number).upper()

        if not normalized_tax_number:
            raise ValueError("Az adószámból nem generálható company_key.")

        return f"COM_{normalized_tax_number}"

    def rename(self, new_name: str) -> None:
        new_name = new_name.strip()

        if not new_name:
            raise ValueError("A cégnév megadása kötelező")
        self._name = new_name
        self.updated_at = datetime.now(UTC)



    def change_country(self, new_country: str | None) -> None:
        if new_country is not None:
            new_country = new_country.strip() or None

        if self._country == new_country:
            return
        self._country = new_country
        self.updated_at = datetime.now(UTC)

    def update(
            self,
            *,
            name: str,
            country: str | None = None,
    ) -> None:
        if not isinstance(name, str):
            raise TypeError("name must be a string.")
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("name cannot be empty.")
        if country is not None:
            if not isinstance(country, str):
                raise TypeError("country must be a string or None.")
            country = country.strip() or None

        self._name = normalized_name
        self._updated_at = datetime.now(timezone.utc)
        self._country = country