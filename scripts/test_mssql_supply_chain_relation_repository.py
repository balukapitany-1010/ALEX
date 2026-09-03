from alex.esg.domain.supply_chain_relation import (
    SupplyChainRelation,
)
from alex.esg.repositories.mssql_supply_chain_relation_repository import (
    MssqlSupplyChainRelationRepository,
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

    repository = (
        MssqlSupplyChainRelationRepository(
            factory
        )
    )

    relations = repository.list_all()

    print(
        "Betöltött kapcsolatok száma: "
        f"{len(relations)}"
    )

    print()
    print("Első 10 kapcsolat:")

    for relation in relations[:10]:
        assert isinstance(
            relation,
            SupplyChainRelation,
        )

        print(
            f"{relation.relation_id} | "
            f"{relation.requester.name} | "
            f"{relation.supplier.name} | "
            f"{relation.relation_status}"
        )

    print()
    print("298-as kapcsolat:")

    relation = repository.get_by_id(
        "298"
    )

    if relation is None:
        print(
            "A 298-as kapcsolat nem található."
        )

    else:
        print(
            f"relation_id: "
            f"{relation.relation_id}"
        )

        print(
            f"requester:   "
            f"{relation.requester.name}"
        )

        print(
            f"supplier:    "
            f"{relation.supplier.name}"
        )

        print(
            f"status:      "
            f"{relation.relation_status}"
        )

        print(
            f"created_at:  "
            f"{relation.created_at}"
        )

        print(
            f"updated_at:  "
            f"{relation.updated_at}"
        )


if __name__ == "__main__":
    main()