from alex.esg.domain.supplier import Supplier
from alex.esg.repositories.supplier_repository import SupplierRepository
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory
from datetime import UTC

class MssqlSupplierRepository(SupplierRepository):
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

    def list_all(
        self,
    ) -> tuple[Supplier, ...]:
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT DISTINCT
                    c.company_key,
                    c.name,
                    c.tax_number,
                    c.country,
                    c.created_at,
                    c.updated_at
                FROM dbo.COMPANY c

                INNER JOIN dbo.SUPPLY_CHAIN_RELATION r
                    ON r.supplier_company_key =
                       c.company_key

                ORDER BY c.name, c.company_key
                """
            )
            rows = cursor.fetchall()
            return tuple(
                self._map_row(row)
                for row in rows
            )
        finally:
            connection.close()

    def get_by_key(
        self,
        company_key: str,
    ) -> Supplier | None:
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
                SELECT DISTINCT
                    c.company_key,
                    c.name,
                    c.tax_number,
                    c.country,
                    c.created_at,
                    c.updated_at
                FROM dbo.COMPANY c

                INNER JOIN dbo.SUPPLY_CHAIN_RELATION r
                    ON r.supplier_company_key =
                       c.company_key

                WHERE c.company_key = ?
                """,
                company_key,
            )

            row = cursor.fetchone()
            if row is None:
                return None
            return self._map_row(row)
        finally:
            connection.close()

    def get_by_tax_number(
        self,
        tax_number: str,
    ) -> Supplier | None:
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
                SELECT DISTINCT
                    c.company_key,
                    c.name,
                    c.tax_number,
                    c.country,
                    c.created_at,
                    c.updated_at
                FROM dbo.COMPANY c

                INNER JOIN dbo.SUPPLY_CHAIN_RELATION r
                    ON r.supplier_company_key =
                       c.company_key

                WHERE c.tax_number = ?
                """,
                tax_number,
            )

            row = cursor.fetchone()

            if row is None:
                return None
            return self._map_row(
                row
            )

        finally:
            connection.close()

    def add(
            self,
            supplier: Supplier,
    ) -> Supplier:
        if not isinstance(
                supplier,
                Supplier,
        ):
            raise TypeError("supplier must be a Supplier")

        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            # Nem csak a már beszállítóként szereplő
            # COMPANY rekordokat vizsgáljuk.
            cursor.execute(
                """
                SELECT
                    company_key
                FROM dbo.COMPANY
                WHERE
                    company_key = ?
                    OR tax_number = ?
                """,
                supplier.company_key,
                supplier.tax_number,
            )

            existing = cursor.fetchone()

            if existing is not None:
                raise ValueError(
                    "company with same company_key "
                    "or tax_number already exists"
                )

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
                VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                supplier.company_key,
                supplier.name,
                supplier.tax_number,
                supplier.country,
                self._to_db_datetime(supplier.created_at),
                self._to_db_datetime(supplier.updated_at),
            )

            connection.commit()

            return supplier

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def update(
            self,
            supplier: Supplier,
    ) -> Supplier:
        if not isinstance(
                supplier,
                Supplier,
        ):
            raise TypeError(
                "supplier must be a Supplier"
            )

        connection = (
            self._connection_factory.connect()
        )

        try:
            cursor = connection.cursor()

            # Csak olyan COMPANY módosítható ezen
            # repository-n keresztül, amely valóban
            # supplier szerepben van.
            cursor.execute(
                """
                SELECT
                    c.company_key
                FROM dbo.COMPANY c
                WHERE
                    c.company_key = ?
                    AND EXISTS (
                        SELECT 1
                        FROM dbo.SUPPLY_CHAIN_RELATION r
                        WHERE
                            r.supplier_company_key =
                            c.company_key
                    )
                """,
                supplier.company_key,
            )

            if cursor.fetchone() is None:
                raise ValueError(
                    "supplier does not exist"
                )

            cursor.execute(
                """
                UPDATE dbo.COMPANY
                SET
                    name = ?,
                    country = ?,
                    updated_at = ?
                WHERE
                    company_key = ?
                """,
                supplier.name,
                supplier.country,
                self._to_db_datetime(
                    supplier.updated_at
                ),
                supplier.company_key,
            )

            connection.commit()

            return supplier

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()
    def remove(
        self,
        company_key: str,
    ) -> Supplier:
        raise NotImplementedError(
            "MSSQL supplier removal requires "
            "supply-chain relation handling"
        )

    @staticmethod
    def _to_db_datetime(
            value,
    ):
        if value is None:
            return None

        if value.tzinfo is not None:
            value = value.astimezone(
                UTC
            ).replace(
                tzinfo=None
            )

        return value
    @staticmethod
    def _map_row(
        row,
    ) -> Supplier:
        return Supplier.rehydrate(
            company_key=row[0],
            name=row[1],
            tax_number=row[2],
            country=row[3],
            created_at=row[4],
            updated_at=row[5],
        )