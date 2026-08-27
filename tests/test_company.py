import time
import unittest

import pytest

from src.alex.esg.domain.company import Company

class TestCompany(unittest.TestCase):
    def test_company_creation(self) -> None:
        company = Company(
            name = "Minta kft.",
            tax_number = "12345678-2-42",
            country = "HU",
        )

        self.assertEqual(company.name,"Minta kft.")
        self.assertEqual(company.tax_number,"12345678-2-42")
        self.assertEqual(company.country,"HU")
        self.assertEqual(company.company_key, "COM_12345678242")

    def test_company_name_is_required(self) -> None:
        with self.assertRaises(ValueError):
            Company(
                name ="",
                tax_number = "12345678-2-42",
            )

    def test_company_tax_number_is_required(self) -> None:
        with self.assertRaises(ValueError):
            Company(
                name = "Minta kft.",
                tax_number = "",
            )

    def test_tax_number_cannot_be_changed(self) -> None:
        company = Company(
            name = "Minta kft.",
            tax_number = "12345678-2-42",
        )
        with self.assertRaises(AttributeError):
            company.tax_number = "87654321-2-42"

    def test_company_key_cannot_be_changed(self) -> None:
        company = Company(
            name = "Minta kft.",
            tax_number = "12345678-2-42",
        )

        with self.assertRaises(AttributeError):
            company.company_key = "COM_87654321242"


    def test_rename_updates_name_and_timestamp(self) -> None:
        company = Company(
            name = "Régi kft.",
            tax_number = "12345678-2-42",
        )

        original_updated_at = company.updated_at
        original_tax_number = company.tax_number
        original_company_key = company.company_key
        time.sleep(0.01)

        company.rename("Új Kft.")

        self.assertEqual(company.name, "Új Kft.")
        self.assertEqual(company.tax_number, original_tax_number)
        self.assertEqual(company.company_key, original_company_key)
        self.assertGreater(company.updated_at, original_updated_at)

    def test_rename_rejects_empty_name(self) -> None:
        company = Company(
            name = "Minta kft.",
            tax_number = "12345678-2-42",
        )

        original_name = company.name
        original_updated_at = company.updated_at

        with self.assertRaises(ValueError):
            company.rename("   ")

        self.assertEqual(company.name, original_name)
        self.assertEqual(company.updated_at, original_updated_at)


    def test_change_country_updates_country_and_timestamp(self) -> None:
        company = Company(
            name = "Minta kft.",
            tax_number = "12345678-2-42",
            country = "HU",
        )
        original_updated_at = company.updated_at
        original_tax_number = company.tax_number
        original_company_key = company.company_key

        time.sleep(0.01)
        company.change_country("DE")
        self.assertEqual(company.country, "DE")
        self.assertEqual(company.tax_number, original_tax_number)
        self.assertEqual(company.company_key, original_company_key)
        self.assertGreater(company.updated_at, original_updated_at)


    def test_change_country_does_not_update_timestamp_when_value_is_same(self) -> None:
        company = Company(
            name = "Minta kft.",
            tax_number = "12345678-2-42",
            country = "HU",
        )


        original_updated_at = company.updated_at
        time.sleep(0.01)
        company.change_country("HU")
        self.assertEqual(company.country, "HU")
        self.assertEqual(company.updated_at, original_updated_at)

    def test_change_country_whitespace_is_normalized_to_none(self) -> None:
        company = Company(
            name="Minta Kft.",
            tax_number="12345678-2-42",
            country="HU",
        )

        original_updated_at = company.updated_at

        time.sleep(0.001)

        company.change_country("   ")

        self.assertIsNone(company.country)
        self.assertGreater(company.updated_at, original_updated_at)

    def test_company_key_is_generated_from_hungarian_tax_number(self) -> None:
        company = Company(
            name="Minta Kft.",
            tax_number="12345678-2-42",
            country="HU",
        )

        self.assertEqual(
            company.company_key,
            "COM_12345678242",
        )

    def test_company_key_is_generated_from_foreign_tax_number(self) -> None:
        company = Company(
            name="Swiss AG",
            tax_number="CHE-153.922.051",
            country="CH",
        )

        self.assertEqual(
            company.company_key,
            "COM_CHE153922051",
        )


    def test_company_key_rejects_tax_number_without_alphanumeric_characters(self) -> None:
        with  self.assertRaises(ValueError):
            Company(
                name="Minta kft.",
                tax_number="----",
            )
    def test_company_can_update_name_and_country(self) -> None:
        company = Company(
            name="Régi Kft.",
            tax_number="12345678-2-41",
            country="HU",
        )
        company.update(
            name = "Új Kft.",
            country = "AT",
        )
        assert company.name == "Új Kft."
        assert company.country == "AT"

    def test_company_update_changes_updated_at(self) -> None:
        company = Company(
            name="Teszt kft.",
            tax_number="12345678-2-41",
        )
        previus_updated_at = company.updated_at
        company.update(
            name = "Módósított Kft.",
            country = "HU",
        )
        assert company.updated_at >= previus_updated_at

    def test_company_update_rejects_empty_name(self) -> None:
        company = Company(
            name="Teszt kft.",
            tax_number="12345678-2-41",
        )
        with pytest.raises(ValueError, match="name cannot be empty"):
            company.update(
                name = "",
                country = "HU",
            )
    def test_company_update_does_not_change_tax_number(self) -> None:
        company = Company(
            name="Teszt kft.",
            tax_number="12345678-2-41",
        )
        original_tax_number = company.tax_number
        original_company_key = company.company_key
        company.update(
            name = "Módósított kft.",
            country = "HU",
        )
        assert company.tax_number == original_tax_number
        assert company.company_key == original_company_key




    if __name__=="__main__":
        unittest.main()

