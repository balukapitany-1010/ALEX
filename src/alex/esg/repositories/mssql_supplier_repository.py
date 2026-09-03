from alex.esg.domain.supplier import Supplier
from alex.esg.repositories.supplier_repository import SupplierRepository
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

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
        raise NotImplementedError(
            "MSSQL supplier creation requires "
            "supply-chain relation handling"
        )
    def update(
        self,
        supplier: Supplier,
    ) -> Supplier:
        raise NotImplementedError(
            "MSSQL supplier update is not "
            "implemented yet"
        )
    def remove(
        self,
        company_key: str,
    ) -> Supplier:
        raise NotImplementedError(
            "MSSQL supplier removal requires "
            "supply-chain relation handling"
        )
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