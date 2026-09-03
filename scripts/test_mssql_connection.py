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
            SELECT
                @@SERVERNAME AS server_name,
                DB_NAME() AS database_name
            """
        )
        row = cursor.fetchone()
        print("Kapcsolódás sikeres.")
        print(f"SQL Server: {row[0]}")
        print(f"Adatbázis: {row[1]}")

        print()
        print("Első 5 COMPANY rekord:")
        cursor.execute(
            """
            SELECT TOP (5)
                company_key,
                name,
                tax_number,
                country
            FROM dbo.COMPANY
            ORDER BY name
            """
        )
        rows = cursor.fetchall()

        if not rows:
            print("A COMPANY tábla üres.")
            return

        for company_row in rows:
            print(
                f"{company_row[0]} | "
                f"{company_row[1]} | "
                f"{company_row[2]} | "
                f"{company_row[3]}"
            )
    finally:
        connection.close()

if __name__ == "__main__":
    main()