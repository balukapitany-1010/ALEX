from alex.esg.domain.supplier import Supplier
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

def main() -> None:
    config = SqlServerConfig.from_environment()

    factory = SqlServerConnectionFactory(config)
    connection = factory.connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT DISTINCT TOP (10)
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
            ORDER BY c.name
            """
        )
        rows = cursor.fetchall()
        suppliers: list[Supplier] = []
        for row in rows:
            supplier = Supplier.rehydrate(
                company_key=row[0],
                name=row[1],
                tax_number=row[2],
                country=row[3],
                created_at=row[4],
                updated_at=row[5],
            )

            suppliers.append(supplier)
        print(
            f"Betöltött beszállítók: "
            f"{len(suppliers)}"
        )
        print()
        for supplier in suppliers:
            assert isinstance(
                supplier,
                Supplier,
            )

            print(
                f"{supplier.company_key} | "
                f"{supplier.name} | "
                f"{supplier.tax_number}"
            )
    finally:
        connection.close()


if __name__ == "__main__":
    main()