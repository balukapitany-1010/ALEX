from datetime import UTC
from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.repositories.supplier_registration_repository import SupplierRegistrationRepository
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory


class MssqlSupplierRegistrationRepository(SupplierRegistrationRepository):
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

    def register(
        self,
        *,
        requester: Company,
        supplier: Supplier,
    ) -> SupplyChainRelation:
        if not isinstance(
            requester,
            Company,
        ):
            raise TypeError("requester must be a Company")
        if not isinstance(
            supplier,
            Supplier,
        ):
            raise TypeError("supplier must be a Supplier")
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    company_key
                FROM dbo.COMPANY
                WHERE company_key = ?
                """,
                requester.company_key,
            )

            if cursor.fetchone() is None:
                raise ValueError("requester company does not exist")

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
                WHERE
                    tax_number = ?
                    OR company_key = ?
                """,
                supplier.tax_number,
                supplier.company_key,
            )

            existing_row = (cursor.fetchone())
            if existing_row is None:
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
                registered_supplier = (supplier)
            else:
                if (
                    existing_row[0] == supplier.company_key and existing_row[2] != supplier.tax_number
                ):
                    raise ValueError(
                        "company_key already belongs "
                        "to another tax number"
                    )
                registered_supplier = (
                    Supplier.rehydrate(
                        company_key=existing_row[0],
                        name=existing_row[1],
                        tax_number=existing_row[2],
                        country=existing_row[3],
                        created_at=existing_row[4],
                        updated_at=existing_row[5],
                    )
                )
            cursor.execute(
                """
                SELECT
                    relation_id
                FROM dbo.SUPPLY_CHAIN_RELATION
                WHERE
                    requester_company_key = ?
                    AND supplier_company_key = ?
                """,
                requester.company_key,
                registered_supplier.company_key,
            )

            if cursor.fetchone() is not None:
                raise ValueError(
                    "relation between requester "
                    "and supplier already exists"
                )
            cursor.execute(
                """
                INSERT INTO dbo.SUPPLY_CHAIN_RELATION (
                    requester_company_key,
                    supplier_company_key,
                    relation_status,
                    created_at,
                    updated_at
                )
                OUTPUT
                    INSERTED.relation_id,
                    INSERTED.relation_status,
                    INSERTED.created_at,
                    INSERTED.updated_at
                VALUES (
                    ?,
                    ?,
                    'active',
                    SYSUTCDATETIME(),
                    SYSUTCDATETIME()
                )
                """,
                requester.company_key,
                registered_supplier.company_key,
            )

            relation_row = (cursor.fetchone())
            if relation_row is None:
                raise RuntimeError(
                    "relation insert did not "
                    "return a row"
                )
            relation = (
                SupplyChainRelation.rehydrate(
                    relation_id=relation_row[0],
                    requester=requester,
                    supplier=registered_supplier,
                    relation_status=relation_row[1],
                    created_at=relation_row[2],
                    updated_at=relation_row[3],
                )
            )

            connection.commit()
            return relation
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _to_db_datetime(value):
        if value is None:
            return None
        if value.tzinfo is not None:
            value = value.astimezone(UTC).replace(tzinfo=None)
        return value