import re

from alex.esg.domain.company import Company
from alex.esg.domain.questionnaire import (
    Questionnaire,
)
from alex.esg.domain.submission import (
    Submission,
)
from alex.esg.domain.submission_status import (
    SubmissionStatus,
)
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import (
    SupplyChainRelation,
)
from alex.esg.repositories.submission_repository import (
    SubmissionRepository,
)
from alex.infrastructure.database.sql_server_connection_factory import (
    SqlServerConnectionFactory,
)


class MssqlSubmissionRepository(
    SubmissionRepository
):
    _PERIOD_PATTERN = re.compile(
        r"(?:^|_)(20\d{2})Q([1-4])(?:_|$)",
        re.IGNORECASE,
    )

    def __init__(
        self,
        connection_factory: SqlServerConnectionFactory,
    ) -> None:
        if not isinstance(
            connection_factory,
            SqlServerConnectionFactory,
        ):
            raise TypeError(
                "connection_factory must be a "
                "SqlServerConnectionFactory"
            )

        self._connection_factory = (
            connection_factory
        )

    def add(
        self,
        submission: Submission,
    ) -> Submission:
        raise NotImplementedError(
            "MSSQL submission creation is "
            "not implemented yet"
        )

    def remove(
        self,
        submission_id: str,
    ) -> Submission:
        raise NotImplementedError(
            "MSSQL submission removal is "
            "not implemented yet"
        )

    def list_all(
        self,
    ) -> tuple[Submission, ...]:
        return self._fetch_submissions()

    def get_by_id(
        self,
        submission_id: str,
    ) -> Submission | None:
        if not isinstance(
            submission_id,
            str,
        ):
            raise TypeError(
                "submission_id must be a string"
            )

        submission_id = (
            submission_id.strip()
        )

        if not submission_id:
            raise ValueError(
                "submission_id cannot be empty"
            )

        submissions = self._fetch_submissions(
            where_sql=(
                "WHERE s.submission_id = "
                "TRY_CONVERT(bigint, ?)"
            ),
            parameters=(
                submission_id,
            ),
        )

        if not submissions:
            return None

        return submissions[0]

    def _fetch_submissions(
        self,
        *,
        where_sql: str = "",
        parameters: tuple = (),
    ) -> tuple[Submission, ...]:
        connection = (
            self._connection_factory.connect()
        )

        try:
            cursor = connection.cursor()

            sql = f"""
                SELECT
                    s.submission_id,
                    s.respondent_id,
                    s.batch_id,
                    s.org_size,
                    s.submitted_at,
                    s.status,
                    s.created_at,
                    s.updated_at,

                    sb.questionnaire_code,
                    sb.spec_version,

                    q.locale,

                    r.relation_id,
                    r.relation_status,
                    r.created_at,
                    r.updated_at,

                    requester.company_key,
                    requester.name,
                    requester.tax_number,
                    requester.country,
                    requester.created_at,
                    requester.updated_at,

                    supplier.company_key,
                    supplier.name,
                    supplier.tax_number,
                    supplier.country,
                    supplier.created_at,
                    supplier.updated_at

                FROM dbo.SUBMISSION s

                INNER JOIN dbo.SUBMISSION_BATCH sb
                    ON sb.batch_id = s.batch_id

                INNER JOIN dbo.QUESTIONNAIRE q
                    ON q.questionnaire_code =
                       sb.questionnaire_code
                    AND q.spec_version =
                        sb.spec_version

                INNER JOIN dbo.SUPPLY_CHAIN_RELATION r
                    ON r.relation_id =
                       s.relation_id

                INNER JOIN dbo.COMPANY requester
                    ON requester.company_key =
                       r.requester_company_key

                INNER JOIN dbo.COMPANY supplier
                    ON supplier.company_key =
                       r.supplier_company_key

                {where_sql}

                ORDER BY
                    s.submission_id DESC
            """

            cursor.execute(
                sql,
                *parameters,
            )

            rows = cursor.fetchall()

            return tuple(
                self._map_row(row)
                for row in rows
            )

        finally:
            connection.close()

    def _map_row(
        self,
        row,
    ) -> Submission:
        requester = Company.rehydrate(
            company_key=row[15],
            name=row[16],
            tax_number=row[17],
            country=row[18],
            created_at=row[19],
            updated_at=row[20],
        )

        supplier = Supplier.rehydrate(
            company_key=row[21],
            name=row[22],
            tax_number=row[23],
            country=row[24],
            created_at=row[25],
            updated_at=row[26],
        )

        relation = (
            SupplyChainRelation.rehydrate(
                relation_id=row[11],
                requester=requester,
                supplier=supplier,
                relation_status=row[12],
                created_at=row[13],
                updated_at=row[14],
            )
        )

        questionnaire = Questionnaire(
            questionnaire_code=row[8],
            spec_version=row[9],
            locale=row[10],
        )

        status = self._map_status(
            row[5]
        )

        period = self._extract_period(
            respondent_id=row[1],
            batch_id=row[2],
        )

        return Submission.rehydrate(
            submission_id=row[0],
            relation=relation,

            # A respondent_id nem COMPANY kulcs,
            # ezért egyelőre nem találunk ki
            # submittert.
            submitter=None,

            questionnaire=questionnaire,
            period=period,
            submitted_at=row[4],
            status=status,
            organization_size=row[3],
            created_at=row[6],
            updated_at=row[7],
        )

    @classmethod
    def _extract_period(
        cls,
        *,
        respondent_id: str | None,
        batch_id: str | None,
    ) -> str | None:
        for value in (
            respondent_id,
            batch_id,
        ):
            if not value:
                continue

            match = (
                cls._PERIOD_PATTERN.search(
                    value
                )
            )

            if match is None:
                continue

            year = match.group(1)
            quarter = match.group(2)

            return (
                f"{year}-Q{quarter}"
            )

        return None

    @staticmethod
    def _map_status(
        value: str,
    ) -> SubmissionStatus:
        try:
            return SubmissionStatus(
                value
            )

        except ValueError as error:
            raise ValueError(
                "unknown submission status: "
                f"{value}"
            ) from error