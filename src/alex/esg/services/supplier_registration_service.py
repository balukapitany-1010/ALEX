from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.repositories.supplier_registration_repository import SupplierRegistrationRepository

class SupplierRegistrationService:
    def __init__(
        self,
        repository: SupplierRegistrationRepository,
    ) -> None:
        if not isinstance(
            repository,
            SupplierRegistrationRepository,
        ):
            raise TypeError(
                "repository must be a "
                "SupplierRegistrationRepository"
            )

        self._repository = repository

    def register_supplier(
        self,
        *,
        requester: Company,
        name: str,
        tax_number: str,
        country: str | None = None,
    ) -> SupplyChainRelation:
        if not isinstance(
            requester,
            Company,
        ):
            raise TypeError(
                "requester must be a Company"
            )
        supplier = Supplier(
            name=name,
            tax_number=tax_number,
            country=country,
        )
        return self._repository.register(
            requester=requester,
            supplier=supplier,
        )