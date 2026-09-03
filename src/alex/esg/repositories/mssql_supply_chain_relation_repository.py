from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.repositories.supply_chain_relation_repository import SupplyChainRelationRepository
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory


class MssqlSupplyChainRelationRepository(
    SupplyChainRelationRepository
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

        self._connection_factory = (
            connection_factory
        )

    def add(
            self,
            relation: SupplyChainRelation,
    ) -> SupplyChainRelation:
        if not isinstance(
                relation,
                SupplyChainRelation,
        ):
            raise TypeError(
                "relation must be a "
                "SupplyChainRelation"
            )

        existing = self.get_by_parties(
            requester=relation.requester,
            supplier=relation.supplier,
        )

        if existing is not None:
            raise ValueError(
                "relation between requester "
                "and supplier already exists"
            )

        connection = (
            self._connection_factory.connect()
        )

        try:
            cursor = connection.cursor()

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
                    ?,
                    SYSUTCDATETIME(),
                    SYSUTCDATETIME()
                )
                """,
                relation.requester.company_key,
                relation.supplier.company_key,
                relation.relation_status,
            )

            row = cursor.fetchone()

            if row is None:
                raise RuntimeError(
                    "relation insert did not "
                    "return a row"
                )

            connection.commit()

            return SupplyChainRelation.rehydrate(
                relation_id=row[0],
                requester=relation.requester,
                supplier=relation.supplier,
                relation_status=row[1],
                created_at=row[2],
                updated_at=row[3],
            )

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def remove(
            self,
            relation_id: str,
    ) -> SupplyChainRelation:
        relation = self.get_by_id(
            relation_id
        )

        if relation is None:
            raise ValueError(
                "relation does not exist"
            )

        connection = (
            self._connection_factory.connect()
        )

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM dbo.SUPPLY_CHAIN_RELATION
                WHERE relation_id =
                    TRY_CONVERT(bigint, ?)
                """,
                relation_id,
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "relation was not deleted"
                )

            connection.commit()

            return relation

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def list_all(
        self,
    ) -> tuple[
        SupplyChainRelation,
        ...
    ]:
        return self._fetch_relations(
            """
            ORDER BY
                r.relation_id
            """
        )

    def get_by_id(
        self,
        relation_id: str,
    ) -> SupplyChainRelation | None:
        if not isinstance(
            relation_id,
            str,
        ):
            raise TypeError("relation_id must be a string")
        normalized = (relation_id.strip())
        if not normalized:
            raise ValueError("relation_id cannot be empty")

        relations = self._fetch_relations(
            """
            WHERE
                r.relation_id =
                TRY_CONVERT(bigint, ?)

            ORDER BY
                r.relation_id
            """,
            normalized,
        )
        if not relations:
            return None
        return relations[0]

    def get_by_parties(
        self,
        *,
        requester: Company,
        supplier: Supplier,
    ) -> SupplyChainRelation | None:
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

        relations = self._fetch_relations(
            """
            WHERE
                r.requester_company_key = ?
                AND
                r.supplier_company_key = ?

            ORDER BY
                r.relation_id
            """,
            requester.company_key,
            supplier.company_key,
        )
        if not relations:
            return None
        return relations[0]

    def list_for_requester(
        self,
        requester: Company,
    ) -> tuple[
        SupplyChainRelation,
        ...
    ]:
        if not isinstance(
            requester,
            Company,
        ):
            raise TypeError("requester must be a Company")
        return self._fetch_relations(
            """
            WHERE
                r.requester_company_key = ?

            ORDER BY
                r.relation_id
            """,
            requester.company_key,
        )

    def list_for_supplier(
        self,
        supplier: Supplier,
    ) -> tuple[
        SupplyChainRelation,
        ...
    ]:
        if not isinstance(
            supplier,
            Supplier,
        ):
            raise TypeError("supplier must be a Supplier")
        return self._fetch_relations(
            """
            WHERE
                r.supplier_company_key = ?

            ORDER BY
                r.relation_id
            """,
            supplier.company_key,
        )

    def _fetch_relations(
        self,
        where_and_order_sql: str,
        *parameters,
    ) -> tuple[
        SupplyChainRelation,
        ...
    ]:
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()
            sql = (self._base_select_sql() + where_and_order_sql)
            cursor.execute(
                sql,
                *parameters,
            )
            rows = cursor.fetchall()
            return tuple(self._map_row(row) for row in rows)
        finally:
            connection.close()

    @staticmethod
    def _base_select_sql() -> str:
        return """
            SELECT
                r.relation_id,
                r.relation_status,
                r.created_at,
                r.updated_at,

                requester.company_key
                    AS requester_company_key,
                requester.name
                    AS requester_name,
                requester.tax_number
                    AS requester_tax_number,
                requester.country
                    AS requester_country,
                requester.created_at
                    AS requester_created_at,
                requester.updated_at
                    AS requester_updated_at,

                supplier.company_key
                    AS supplier_company_key,
                supplier.name
                    AS supplier_name,
                supplier.tax_number
                    AS supplier_tax_number,
                supplier.country
                    AS supplier_country,
                supplier.created_at
                    AS supplier_created_at,
                supplier.updated_at
                    AS supplier_updated_at

            FROM dbo.SUPPLY_CHAIN_RELATION r

            INNER JOIN dbo.COMPANY requester
                ON requester.company_key =
                   r.requester_company_key

            INNER JOIN dbo.COMPANY supplier
                ON supplier.company_key =
                   r.supplier_company_key
        """

    @staticmethod
    def _map_row(
        row,
    ) -> SupplyChainRelation:
        requester = Company.rehydrate(
            company_key=row[4],
            name=row[5],
            tax_number=row[6],
            country=row[7],
            created_at=row[8],
            updated_at=row[9],
        )

        supplier = Supplier.rehydrate(
            company_key=row[10],
            name=row[11],
            tax_number=row[12],
            country=row[13],
            created_at=row[14],
            updated_at=row[15],
        )

        return SupplyChainRelation.rehydrate(
            relation_id=row[0],
            requester=requester,
            supplier=supplier,
            relation_status=row[1],
            created_at=row[2],
            updated_at=row[3],
        )