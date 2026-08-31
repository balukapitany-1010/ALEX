from dataclasses import dataclass

from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.mappers.submission_header_mapper import (
    SubmissionHeaderData,
)
from alex.esg.services.company_service import (
    CompanyService,
)
from alex.esg.services.supplier_service import (
    SupplierService,
)


@dataclass(frozen=True)
class ResolvedSubmissionParties:
    requester: Company
    supplier: Supplier


class SubmissionPartyResolver:
    def __init__(
        self,
        *,
        company_service: CompanyService,
        supplier_service: SupplierService,
    ) -> None:
        if not isinstance(
            company_service,
            CompanyService,
        ):
            raise TypeError("company_service must be a CompanyService")

        if not isinstance(
            supplier_service,
            SupplierService,
        ):
            raise TypeError("supplier_service must be a SupplierService")

        self._company_service = company_service
        self._supplier_service = supplier_service

    def resolve(
        self,
        header: SubmissionHeaderData,
    ) -> ResolvedSubmissionParties:
        if not isinstance(
            header,
            SubmissionHeaderData,
        ):
            raise TypeError("header must be a SubmissionHeaderData")

        self._validate_required_data(header)

        requester = self._resolve_requester(header)

        supplier = self._resolve_supplier(header)

        return ResolvedSubmissionParties(
            requester=requester,
            supplier=supplier,
        )

    def _resolve_requester(
        self,
        header: SubmissionHeaderData,
    ) -> Company:
        assert header.requester_tax_number is not None
        assert header.requester_company is not None

        existing = (
            self._company_service.get_by_tax_number(
                header.requester_tax_number
            )
        )

        if existing is not None:
            return existing

        return self._company_service.create_company(
            name=header.requester_company,
            tax_number=header.requester_tax_number,
        )

    def _resolve_supplier(
        self,
        header: SubmissionHeaderData,
    ) -> Supplier:
        assert header.supplier_tax_number is not None
        assert header.supplier_company is not None

        existing = (
            self._supplier_service.get_by_tax_number(
                header.supplier_tax_number
            )
        )

        if existing is not None:
            return existing

        return self._supplier_service.create_supplier(
            name=header.supplier_company,
            tax_number=header.supplier_tax_number,
        )

    @staticmethod
    def _validate_required_data(
        header: SubmissionHeaderData,
    ) -> None:
        if header.supplier_company is None:
            raise ValueError("supplier company is required")

        if header.supplier_tax_number is None:
            raise ValueError("supplier tax number is required")

        if header.requester_company is None:
            raise ValueError("requester company is required")

        if header.requester_tax_number is None:
            raise ValueError("requester tax number is required")