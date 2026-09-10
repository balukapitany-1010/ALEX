from collections import defaultdict
from dataclasses import dataclass

@dataclass(frozen=True)
class SubmissionImportContext:
    questionnaire_code: str
    spec_version: str
    batch_id: str
    batch_exists: bool

    questionnaire_question_ids: frozenset[str]

    option_ids_by_question: dict[
        str,
        frozenset[str],
    ]


class MssqlSubmissionImportContextReader:
    def __init__(
        self,
        connection_factory,
    ) -> None:
        self._connection_factory = (connection_factory)

    @staticmethod
    def _optional_text(
        value,
    ) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @classmethod
    def normalize_business_identifier(
        cls,
        value,
    ) -> str:
        text = cls._optional_text(value)
        if text is None:
            return ""
        return "".join(character for character in text.upper() if character.isalnum())

    def load_context(
        self,
        *,
        batch_id: str,
        questionnaire_code: str,
        spec_version: str,
        allow_missing_batch: bool = False,
    ) -> SubmissionImportContext:
        batch_id = self._optional_text(batch_id)
        questionnaire_code = (self._optional_text(questionnaire_code))
        spec_version = (self._optional_text(spec_version))
        if batch_id is None:
            raise ValueError("batch_id cannot be empty")

        if questionnaire_code is None:
            raise ValueError("questionnaire_code cannot be empty")

        if spec_version is None:
            raise ValueError("spec_version cannot be empty")
        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    questionnaire_code,
                    spec_version
                FROM dbo.SUBMISSION_BATCH
                WHERE batch_id = ?
                """,
                batch_id,
            )
            batch_row = cursor.fetchone()
            if batch_row is None:
                if not allow_missing_batch:
                    raise ValueError(
                        "SUBMISSION_BATCH "
                        f"does not exist: {batch_id}"
                    )

                batch_exists = False

            else:
                batch_exists = True

                actual_questionnaire_code = str(batch_row[0]).strip()
                actual_spec_version = str(batch_row[1]).strip()

                if (
                        actual_questionnaire_code != questionnaire_code or actual_spec_version != spec_version
                ):
                    raise ValueError("batch questionnaire/version does not match import")

            cursor.execute(
                """
                SELECT
                    1
                FROM dbo.QUESTIONNAIRE
                WHERE questionnaire_code = ?
                  AND spec_version = ?
                """,
                questionnaire_code,
                spec_version,
            )

            if cursor.fetchone() is None:
                raise ValueError(
                    "QUESTIONNAIRE does not exist: "
                    f"{questionnaire_code} "
                    f"{spec_version}"
                )

            cursor.execute(
                """
                SELECT
                    question_id
                FROM dbo.QUESTIONNAIRE_QUESTION
                WHERE questionnaire_code = ?
                  AND spec_version = ?
                """,
                questionnaire_code,
                spec_version,
            )

            questionnaire_question_ids = (frozenset(str(row[0]).strip() for row in cursor.fetchall()))
            cursor.execute(
                """
                SELECT
                    qo.question_id,
                    qno.option_id
                FROM dbo.QUESTIONNAIRE_OPTION qno

                INNER JOIN dbo.QUESTION_OPTION qo
                    ON qo.option_id =
                       qno.option_id

                WHERE qno.questionnaire_code = ?
                  AND qno.spec_version = ?
                """,
                questionnaire_code,
                spec_version,
            )
            mutable_options = defaultdict(set)
            for row in cursor.fetchall():
                question_id = str(row[0]).strip()
                option_id = str(row[1]).strip()
                mutable_options[question_id].add(option_id)

            option_ids_by_question = {question_id: frozenset(option_ids)
                for (
                    question_id,
                    option_ids,
                ) in mutable_options.items()
            }
            if not questionnaire_question_ids:
                raise ValueError(
                    "QUESTIONNAIRE has no linked questions: "
                    f"{questionnaire_code} "
                    f"{spec_version}"
                )

            return SubmissionImportContext(
                questionnaire_code=(
                    questionnaire_code
                ),
                spec_version=(
                    spec_version
                ),
                batch_id=batch_id,
                batch_exists=batch_exists,
                questionnaire_question_ids=(
                    questionnaire_question_ids
                ),
                option_ids_by_question=(
                    option_ids_by_question
                ),
            )
        finally:
            connection.close()

    def resolve_relation_id(
            self,
            *,
            requester_tax_number: str,
            supplier_tax_number: str,
    ) -> int:
        normalized_requester_tax = (
            self.normalize_business_identifier(
                requester_tax_number
            )
        )

        normalized_supplier_tax = (
            self.normalize_business_identifier(
                supplier_tax_number
            )
        )

        if not normalized_requester_tax:
            raise ValueError(
                "requester tax_number "
                "cannot be empty"
            )

        if not normalized_supplier_tax:
            raise ValueError(
                "supplier tax_number "
                "cannot be empty"
            )

        connection = (
            self._connection_factory.connect()
        )

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    r.relation_id,
                    requester.tax_number,
                    supplier.tax_number
                FROM dbo.SUPPLY_CHAIN_RELATION r

                INNER JOIN dbo.COMPANY requester
                    ON requester.company_key =
                       r.requester_company_key

                INNER JOIN dbo.COMPANY supplier
                    ON supplier.company_key =
                       r.supplier_company_key

                ORDER BY
                    r.relation_id
                """
            )

            matching_relation_ids = []

            for row in cursor.fetchall():
                db_requester_tax = (
                    self.normalize_business_identifier(
                        row[1]
                    )
                )

                db_supplier_tax = (
                    self.normalize_business_identifier(
                        row[2]
                    )
                )

                if (
                        db_requester_tax
                        == normalized_requester_tax
                        and db_supplier_tax
                        == normalized_supplier_tax
                ):
                    matching_relation_ids.append(
                        int(
                            row[0]
                        )
                    )

            if not matching_relation_ids:
                raise ValueError(
                    "SUPPLY_CHAIN_RELATION "
                    "does not exist for "
                    f"requester={normalized_requester_tax}, "
                    f"supplier={normalized_supplier_tax}"
                )

            if len(
                    matching_relation_ids
            ) > 1:
                raise RuntimeError(
                    "multiple matching "
                    "SUPPLY_CHAIN_RELATION rows: "
                    f"{matching_relation_ids}"
                )

            return matching_relation_ids[0]

        finally:
            connection.close()