from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.repositories.in_memory_supply_chain_relation_repository import InMemorySupplyChainRelationRepository
from alex.esg.repositories.supply_chain_relation_repository import SupplyChainRelationRepository


class SupplyChainRelationService:
    def __init__(
        self,
        repository: SupplyChainRelationRepository | None = None,
    ) -> None:
        if repository is None:
            repository = (InMemorySupplyChainRelationRepository())

        if not isinstance(
            repository,
            SupplyChainRelationRepository,
        ):
            raise TypeError(
                "repository must be a "
                "SupplyChainRelationRepository"
            )

        self._repository = repository

    def create_relation(
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

        existing = (
            self._repository.get_by_parties(
                requester=requester,
                supplier=supplier,
            )
        )

        if existing is not None:
            raise ValueError(
                "relation between requester "
                "and supplier already exists"
            )

        relation = SupplyChainRelation(
            requester=requester,
            supplier=supplier,
        )

        return self._repository.add(relation)

    def list_relations(
        self,
    ) -> tuple[
        SupplyChainRelation,
        ...
    ]:
        return self._repository.list_all()

    def get_by_id(
        self,
        relation_id: str,
    ) -> SupplyChainRelation | None:
        return self._repository.get_by_id(relation_id)

    def get_by_parties(
        self,
        *,
        requester: Company,
        supplier: Supplier,
    ) -> SupplyChainRelation | None:
        return (self._repository.get_by_parties(
                requester=requester,
                supplier=supplier,
            )
        )

    def list_for_requester(
        self,
        requester: Company,
    ) -> tuple[
        SupplyChainRelation,
        ...
    ]:
        return (self._repository.list_for_requester(requester))

    def list_for_supplier(
        self,
        supplier: Supplier,
    ) -> tuple[
        SupplyChainRelation,
        ...
    ]:
        return (self._repository.list_for_supplier(supplier))

    def list_relations_for_requester(
            self,
            requester: Company,
    ) -> tuple[
        SupplyChainRelation,
        ...
    ]:
        return self.list_for_requester(requester)

    def list_relations_for_supplier(
            self,
            supplier: Supplier,
    ) -> tuple[
        SupplyChainRelation,
        ...
    ]:
        return self.list_for_supplier(supplier)

    def remove_relation(
            self,
            relation_id: str,
    ) -> SupplyChainRelation:
        return self._repository.remove(
            relation_id
        )
