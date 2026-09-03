from datetime import UTC, datetime

from alex.esg.domain.company import Company
from alex.esg.repositories.company_repository import CompanyRepository
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory


class MssqlCompanyRepository(
    CompanyRepository
):
    def __init__(
        self,
        connection_factory: SqlServerConnectionFactory,
    ) -> None:
        if not isinstance(
            connection_factory,
            SqlServerConnectionFactory,
        ):
            raise TypeError(
                "connection_factory must be a "
                "SqlServerConnectionFactory"
            )

        self._connection_factory = (connection_factory)

    def add(
        self,
        company: Company,
    ) -> Company:
        if not isinstance(
            company,
            Company,
        ):
            raise TypeError("company must be a Company")

        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO dbo.COMPANY (
                    company_key,
                    name,
                    tax_number,
                    country,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                company.company_key,
                company.name,
                company.tax_number,
                company.country,
                self._to_db_datetime(company.created_at),
                self._to_db_datetime( company.updated_at),
            )

            connection.commit()
            return company

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def update(
        self,
        company: Company,
    ) -> Company:
        if not isinstance(
            company,
            Company,
        ):
            raise TypeError("company must be a Company")

        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE dbo.COMPANY
                SET
                    name = ?,
                    country = ?,
                    updated_at = ?
                WHERE company_key = ?
                """,
                company.name,
                company.country,
                self._to_db_datetime(company.updated_at),
                company.company_key,
            )

            if cursor.rowcount == 0:
                raise ValueError("company does not exist")

            connection.commit()

            return company

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def remove(
        self,
        company_key: str,
    ) -> Company:
        company = self.get_by_key(company_key)

        if company is None:
            raise ValueError("company does not exist")

        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM dbo.COMPANY
                WHERE company_key = ?
                """,
                company_key,
            )

            if cursor.rowcount == 0:
                raise ValueError("company does not exist")

            connection.commit()
            return company

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def list_all(
        self,
    ) -> tuple[Company, ...]:
        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    company_key,
                    name,
                    tax_number,
                    country,
                    created_at,
                    updated_at
                FROM dbo.COMPANY
                ORDER BY name, company_key
                """
            )

            rows = cursor.fetchall()

            return tuple(self._map_row(row) for row in rows)

        finally:
            connection.close()

    def get_by_tax_number(
        self,
        tax_number: str,
    ) -> Company | None:
        if not isinstance(
            tax_number,
            str,
        ):
            raise TypeError("tax_number must be a string")

        tax_number = tax_number.strip()

        if not tax_number:
            raise ValueError("tax_number cannot be empty")

        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    company_key,
                    name,
                    tax_number,
                    country,
                    created_at,
                    updated_at
                FROM dbo.COMPANY
                WHERE tax_number = ?
                """,
                tax_number,
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return self._map_row(row)

        finally:
            connection.close()

    def get_by_key(
        self,
        company_key: str,
    ) -> Company | None:
        if not isinstance(
            company_key,
            str,
        ):
            raise TypeError("company_key must be a string")

        company_key = company_key.strip()

        if not company_key:
            raise ValueError("company_key cannot be empty")

        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    company_key,
                    name,
                    tax_number,
                    country,
                    created_at,
                    updated_at
                FROM dbo.COMPANY
                WHERE company_key = ?
                """,
                company_key,
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return self._map_row(row)

        finally:
            connection.close()

    @staticmethod
    def _map_row(
        row,
    ) -> Company:
        return Company.rehydrate(
            company_key=row[0],
            name=row[1],
            tax_number=row[2],
            country=row[3],
            created_at=row[4],
            updated_at=row[5],
        )

    @staticmethod
    def _to_db_datetime(
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None

        if value.tzinfo is None:
            return value

        return (
            value
            .astimezone(UTC)
            .replace(tzinfo=None)
        )