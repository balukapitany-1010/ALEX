from dataclasses import dataclass
from alex.esg.domain.company import Company
from alex.esg.mappers.submission_header_mapper import SubmissionHeaderData
from alex.esg.services.company_service import CompanyService


@dataclass(frozen=True)
class SubmissionSubmitterResolution:
    submitter: Company | None
    is_resolved: bool


class SubmissionSubmitterResolver:
    def __init__(
        self,
        *,
        company_service: CompanyService,
    ) -> None:
        if not isinstance(
            company_service,
            CompanyService,
        ):
            raise TypeError("company_service must be a CompanyService")

        self._company_service = company_service

    def resolve(
        self,
        header: SubmissionHeaderData,
    ) -> SubmissionSubmitterResolution:
        if not isinstance(
            header,
            SubmissionHeaderData,
        ):
            raise TypeError("header must be a SubmissionHeaderData")

        company_name = (header.submitter_auditor_company)

        tax_number = (header.submitter_auditor_tax_number)

        if (
            company_name is None and tax_number is None
        ):
            return SubmissionSubmitterResolution(
                submitter=None,
                is_resolved=False,
            )

        if company_name is None:
            raise ValueError(
                "submitter company is required "
                "when submitter tax number is present"
            )

        if tax_number is None:
            raise ValueError(
                "submitter tax number is required "
                "when submitter company is present"
            )

        existing = (
            self._company_service.get_by_tax_number(tax_number)
        )

        if existing is not None:
            return SubmissionSubmitterResolution(
                submitter=existing,
                is_resolved=True,
            )

        submitter = (self._company_service.create_company(
                name=company_name,
                tax_number=tax_number,
            )
        )

        return SubmissionSubmitterResolution(
            submitter=submitter,
            is_resolved=True,
        )