import json
from collections import Counter
from pathlib import Path
from alex.esg.services.submission_persistence_mapper import (
    SubmissionPersistenceMapper,
)
from alex.esg.infrastructure.repositories.mssql_submission_import_context_reader import (
    MssqlSubmissionImportContextReader,
)
from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)
from alex.infrastructure.database.sql_server_connection_factory import (
    SqlServerConnectionFactory,
)


DOWNLOADS = Path.home() / "Downloads"


def optional_text(value):
    if value is None:
        return None

    text = str(value).strip()
    return text or None

def normalize_respondent_id(
    value,
) -> str:
    text = optional_text(value)

    if text is None:
        return ""

    text = text.upper()

    if not text.startswith(
        "RESP_"
    ):
        return text

    body = text[5:]

    identifier, separator, period = (
        body.rpartition("_")
    )

    if not separator:
        return text

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

def normalize(value):
    text = optional_text(value)

    if text is None:
        return ""

    return "".join(
        character
        for character in text.upper()
        if character.isalnum()
    )


def main():
    config = SqlServerConfig.from_environment()

    connection_factory = (
        SqlServerConnectionFactory(
            config
        )
    )

    context_reader = (
        MssqlSubmissionImportContextReader(
            connection_factory
        )
    )

    connection = (
        connection_factory.connect()
    )

    try:
        cursor = connection.cursor()

        files = sorted(
            DOWNLOADS.rglob("*.json")
        )

        print()
        print(
            "NO-BATCH JSON → MSSQL BATCH MATCH"
        )
        print("=" * 100)

        for file_path in files:
            try:
                with file_path.open(
                    "r",
                    encoding="utf-8-sig",
                ) as handle:
                    payload = json.load(handle)

                if not isinstance(payload, dict):
                    continue

                if optional_text(
                    payload.get("spec_version")
                ) != "2.0":
                    continue

                if optional_text(
                    payload.get("batch_id")
                ) is not None:
                    continue

                submissions = payload.get(
                    "submissions"
                )

                if (
                    not isinstance(
                        submissions,
                        list,
                    )
                    or not submissions
                ):
                    continue

                first_response = (
                    submissions[0].get(
                        "response"
                    )
                    or {}
                )

                if (
                    optional_text(
                        first_response.get(
                            "survey_type"
                        )
                    )
                    or "SZTFH"
                ) != "SZTFH":
                    continue

                json_natural_keys = set()
                requester_tax = None
                invalid_relation = None
                duplicate_count = 0

                for submission in submissions:
                    response = (
                        submission.get(
                            "response"
                        )
                        or {}
                    )

                    cover = (
                        response.get(
                            "cover"
                        )
                        or {}
                    )

                    requester = (
                        cover.get(
                            "requester"
                        )
                        or {}
                    )

                    supplier = (
                        cover.get(
                            "supplier"
                        )
                        or {}
                    )

                    current_requester_tax = (
                        optional_text(
                            requester.get(
                                "tax_number"
                            )
                        )
                    )

                    supplier_tax = (
                        optional_text(
                            supplier.get(
                                "tax_number"
                            )
                        )
                    )

                    if requester_tax is None:
                        requester_tax = (
                            current_requester_tax
                        )

                    if (
                        current_requester_tax
                        is None
                        or supplier_tax is None
                    ):
                        invalid_relation = (
                            "hiányzó requester/"
                            "supplier tax"
                        )
                        break

                    try:
                        relation_id = (
                            context_reader
                            .resolve_relation_id(
                                requester_tax_number=(
                                    current_requester_tax
                                ),
                                supplier_tax_number=(
                                    supplier_tax
                                ),
                            )
                        )

                        period = optional_text(
                            supplier.get(
                                "period"
                            )
                        )

                        respondent_id = optional_text(
                            response.get(
                                "respondent_id"
                            )
                        )

                        if respondent_id is None:
                            respondent_id = (
                                SubmissionPersistenceMapper
                                .create_respondent_id(
                                    supplier_tax,
                                    period,
                                )
                            )

                        respondent_mp_id = optional_text(
                            response.get(
                                "respondent_MP_id"
                            )
                        )

                        natural_key = (
                            relation_id,
                            normalize_respondent_id(
                                respondent_id
                            ),
                            respondent_mp_id,
                        )

                        if natural_key in json_natural_keys:
                            duplicate_count += 1
                        else:
                            json_natural_keys.add(
                                natural_key
                            )

                    except Exception as error:
                        invalid_relation = str(
                            error
                        )
                        break

                if invalid_relation is not None:
                    print()
                    print("Fájl:", file_path)
                    print(
                        "JSON submission:",
                        len(submissions),
                    )
                    print(
                        "requester:",
                        requester_tax
                        or "HIÁNYZIK",
                    )
                    print(
                        "STATUS: RELATION ERROR"
                    )
                    print(
                        "Ok:",
                        invalid_relation,
                    )
                    continue

                cursor.execute(
                    """
                    SELECT
                        b.batch_id,
                        s.relation_id,
                        s.respondent_id,
                        s.respondent_mp_id
                    FROM dbo.SUBMISSION_BATCH AS b

                    INNER JOIN dbo.SUBMISSION AS s
                        ON s.batch_id = b.batch_id

                    WHERE b.questionnaire_code = ?
                      AND b.spec_version = ?

                    ORDER BY
                        b.batch_id,
                        s.submission_id
                    """,
                    "SZTFH",
                    "2.0",
                )

                keys_by_batch = {}

                for row in cursor.fetchall():
                    current_batch_id = str(
                        row[0]
                    ).strip()

                    relation_id = int(
                        row[1]
                    )

                    respondent_id = (
                        normalize_respondent_id(
                            row[2]
                        )
                    )

                    respondent_mp_id = (
                        optional_text(
                            row[3]
                        )
                    )

                    natural_key = (
                        relation_id,
                        respondent_id,
                        respondent_mp_id,
                    )

                    keys_by_batch.setdefault(
                        current_batch_id,
                        set(),
                    ).add(
                        natural_key
                    )

                matches = []

                for (
                        current_batch_id,
                        db_natural_keys,
                ) in keys_by_batch.items():

                    if (
                            db_natural_keys
                            == json_natural_keys
                    ):
                        matches.append(
                            current_batch_id
                        )

                if len(matches) == 1:
                    continue

                if not matches:
                    print(
                        "JSON unique submission:",
                        len(json_natural_keys),
                    )

                    print(
                        "JSON duplicate:",
                        duplicate_count,
                    )
                    print()
                    print("Fájl:", file_path)
                    print(
                        "JSON submission:",
                        len(submissions),
                    )
                    print(
                        "requester:",
                        requester_tax
                        or "HIÁNYZIK",
                    )
                    print(
                        "STATUS: NO MATCH"
                    )

                else:
                    print()
                    print("Fájl:", file_path)
                    print(
                        "JSON submission:",
                        len(submissions),
                    )
                    print(
                        "requester:",
                        requester_tax
                        or "HIÁNYZIK",
                    )
                    print(
                        "STATUS: MULTIPLE MATCH"
                    )

                    for batch_id in matches:
                        print(
                            "candidate:",
                            batch_id,
                        )

            except (
                OSError,
                json.JSONDecodeError,
                UnicodeDecodeError,
            ):
                continue

        print()
        print("=" * 100)
        print(
            "ADATBÁZIS-ÍRÁS: 0 rekord"
        )

        return 0

    finally:
        try:
            connection.rollback()
        finally:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(
        main()
    )