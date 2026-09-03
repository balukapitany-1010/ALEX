from alex.esg.repositories.mssql_company_repository import (
    MssqlCompanyRepository,
)
from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)
from alex.infrastructure.database.sql_server_connection_factory import (
    SqlServerConnectionFactory,
)


def main() -> None:
    config = (
        SqlServerConfig.from_environment()
    )

    factory = (
        SqlServerConnectionFactory(
            config
        )
    )

    repository = MssqlCompanyRepository(
        factory
    )

    company = repository.get_by_key(
        "SUP_32692231241"
    )

    if company is None:
        print("A cég nem található.")
        return

    print("Company sikeresen betöltve:")
    print(
        f"company_key: {company.company_key}"
    )
    print(
        f"name:        {company.name}"
    )
    print(
        f"tax_number:  {company.tax_number}"
    )
    print(
        f"country:     {company.country}"
    )
    print(
        f"created_at:  {company.created_at}"
    )
    print(
        f"updated_at:  {company.updated_at}"
    )


if __name__ == "__main__":
    main()