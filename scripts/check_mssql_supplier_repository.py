from alex.esg.domain.supplier import Supplier
from alex.esg.repositories.mssql_supplier_repository import MssqlSupplierRepository
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

def main() -> None:
    config = SqlServerConfig.from_environment()
    factory = SqlServerConnectionFactory(config)
    repository = MssqlSupplierRepository(factory)
    suppliers = repository.list_all()

    print(
        f"Betöltött beszállítók száma: "
        f"{len(suppliers)}"
    )
    print()
    print("Első 10 beszállító:")
    for supplier in suppliers[:10]:
        assert isinstance(
            supplier,
            Supplier,
        )
        print(
            f"{supplier.company_key} | "
            f"{supplier.name} | "
            f"{supplier.tax_number}"
        )

    supplier = repository.get_by_tax_number("32692231-2-41")

    print()
    if supplier is None:
        print("A 4iG nem található beszállítóként.")

    else:
        print("Adószám alapján megtalálva:")
        print(
            f"{supplier.company_key} | "
            f"{supplier.name} | "
            f"{supplier.tax_number}"
        )
if __name__ == "__main__":
    main()