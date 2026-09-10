from dataclasses import dataclass

@dataclass(frozen=True)
class MssqlSubmissionBatchWriteResult:
    batch_id: str
    created: bool
    questionnaire_code: str
    spec_version: str


class MssqlSubmissionBatchWriter:
    def __init__(
        self,
        connection_factory,
    ) -> None:
        self._connection_factory = (connection_factory)

    @staticmethod
    def _required_text(
        value,
        field_name: str,
    ) -> str:
        if value is None:
            raise ValueError(f"{field_name} cannot be empty")

        text = str(value).strip()

        if not text:
            raise ValueError(f"{field_name} cannot be empty")

        return text

    def ensure_batch(
        self,
        *,
        batch_id: str,
        questionnaire_code: str,
        spec_version: str,
    ) -> MssqlSubmissionBatchWriteResult:
        batch_id = self._required_text(
            batch_id,
            "batch_id",
        )

        questionnaire_code = (self._required_text(
                questionnaire_code,
                "questionnaire_code",
            )
        )

        spec_version = (self._required_text(
                spec_version,
                "spec_version",
            )
        )

        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            result = self.ensure_batch_on_cursor(
                cursor,
                batch_id=batch_id,
                questionnaire_code=(
                    questionnaire_code
                ),
                spec_version=spec_version,
            )

            if result.created:
                connection.commit()
            else:
                connection.rollback()

            return result
        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    @staticmethod
    def _normalize_respondent_id_for_match(
            value,
    ) -> str:
        if value is None:
            return ""

        text = str(value).strip()

        if not text:
            return ""

        upper_text = text.upper()

        if not upper_text.startswith(
                "RESP_"
        ):
            return "".join(
                character
                for character in upper_text
                if character.isalnum()
            )

        body = upper_text[5:]

        identifier, separator, period = (
            body.rpartition("_")
        )

        if not separator:
            return "".join(
                character
                for character in upper_text
                if character.isalnum()
            )

        normalized_identifier = "".join(
            character
            for character in identifier
            if character.isalnum()
        )

        normalized_period = "".join(
            character
            for character in period
            if character.isalnum()
        )

        return (
            f"RESP_{normalized_identifier}_"
            f"{normalized_period}"
        )

    @staticmethod
    def _find_batch_for_write(
        cursor,
        batch_id: str,
    ) -> tuple[
        str,
        str,
    ] | None:
        cursor.execute(
            """
            SELECT
                questionnaire_code,
                spec_version
            FROM dbo.SUBMISSION_BATCH WITH (
                UPDLOCK,
                HOLDLOCK
            )
            WHERE batch_id = ?
            """,
            batch_id,
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return (str(row[0]).strip(), str(row[1]).strip(),)

    def ensure_batch_on_cursor(
            self,
            cursor,
            *,
            batch_id: str,
            questionnaire_code: str,
            spec_version: str,
    ) -> MssqlSubmissionBatchWriteResult:
        batch_id = self._required_text(
            batch_id,
            "batch_id",
        )

        questionnaire_code = (
            self._required_text(
                questionnaire_code,
                "questionnaire_code",
            )
        )

        spec_version = (
            self._required_text(
                spec_version,
                "spec_version",
            )
        )

        existing = (
            self._find_batch_for_write(
                cursor,
                batch_id,
            )
        )

        if existing is not None:
            (
                existing_questionnaire_code,
                existing_spec_version,
            ) = existing

            if (
                    existing_questionnaire_code != questionnaire_code or existing_spec_version != spec_version
            ):
                raise ValueError("existing SUBMISSION_BATCH questionnaire/version does not match import")

            return (MssqlSubmissionBatchWriteResult(
                    batch_id=batch_id,
                    created=False,
                    questionnaire_code=(questionnaire_code),
                    spec_version=(spec_version),
                )
            )

        self._ensure_questionnaire_exists(
            cursor,
            questionnaire_code,
            spec_version,
        )

        cursor.execute(
            """
            INSERT INTO dbo.SUBMISSION_BATCH (
                batch_id,
                questionnaire_code,
                spec_version,
                created_at
            )
            VALUES (
                ?,
                ?,
                ?,
                SYSUTCDATETIME()
            )
            """,
            batch_id,
            questionnaire_code,
            spec_version,
        )

        return (MssqlSubmissionBatchWriteResult(
                batch_id=batch_id,
                created=True,
                questionnaire_code=(questionnaire_code),
                spec_version=(spec_version),
            )
        )

    @staticmethod
    def _ensure_questionnaire_exists(
        cursor,
        questionnaire_code: str,
        spec_version: str,
    ) -> None:
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