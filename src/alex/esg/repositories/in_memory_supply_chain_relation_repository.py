from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import (
    SupplyChainRelation,
)
from alex.esg.repositories.supply_chain_relation_repository import (
    SupplyChainRelationRepository,
)


class InMemorySupplyChainRelationRepository(
    SupplyChainRelationRepository
):
    def __init__(self) -> None:
        self._relations: list[
            SupplyChainRelation
        ] = []

    def add(
        self,
        relation: SupplyChainRelation,
    ) -> SupplyChainRelation:
        if not isinstance(
            relation,
            SupplyChainRelation,
        ):
            raise TypeError(
                "relation must be a SupplyChainRelation"
            )

        if (
            self.get_by_id(
                relation.relation_id
            )
            is not None
        ):
            raise ValueError(
                "relation with this id "
                "already exists"
            )

        if (
            self.get_by_parties(
                requester=relation.requester,
                supplier=relation.supplier,
            )
            is not None
        ):
            raise ValueError(
                "relation between requester "
                "and supplier already exists"
            )

        self._relations.append(
            relation
        )

        return relation

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

        self._relations.remove(
            relation
        )

        return relation

    def list_all(
        self,
    ) -> tuple[
        SupplyChainRelation,
        ...
    ]:
        return tuple(
            self._relations
        )

    def get_by_id(
        self,
        relation_id: str,
    ) -> SupplyChainRelation | None:
        if not isinstance(
            relation_id,
            str,
        ):
            raise TypeError(
                "relation_id must be a string"
            )

        normalized = (
            relation_id.strip()
        )

        if not normalized:
            raise ValueError(
                "relation_id cannot be empty"
            )

        for relation in self._relations:
            if (
                relation.relation_id
                == normalized
            ):
                return relation

        return None

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
            raise TypeError(
                "requester must be a Company"
            )

        if not isinstance(
            supplier,
            Supplier,
        ):
            raise TypeError(
                "supplier must be a Supplier"
            )

        for relation in self._relations:
            if (
                relation.requester.company_key
                == requester.company_key
                and
                relation.supplier.company_key
                == supplier.company_key
            ):
                return relation

        return None

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
            raise TypeError(
                "requester must be a Company"
            )

        return tuple(
            relation
            for relation in self._relations
            if (
                relation.requester.company_key
                == requester.company_key
            )
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
            raise TypeError(
                "supplier must be a Supplier"
            )

        return tuple(
            relation
            for relation in self._relations
            if (
                relation.supplier.company_key
                == supplier.company_key
            )
        )