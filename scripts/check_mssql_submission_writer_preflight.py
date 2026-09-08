import json
import sys
from collections import defaultdict
from pathlib import Path
from alex.esg.infrastructure.repositories.mssql_submission_writer import MssqlSubmissionWriter
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlanner
from alex.infrastructure.database.sql_server_config import  SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

def optional_text(
    value,
) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    return text or None


def normalize_business_identifier(
    value,
) -> str:
    text = optional_text(
        value
    )

    if text is None:
        return ""

    return "".join(
        character
        for character in text.upper()
        if character.isalnum()
    )


def resolve_company_key(
    company_keys_by_tax: dict[
        str,
        list[str],
    ],
    tax_number: str,
    role: str,
) -> str:
    matches = company_keys_by_tax.get(
        tax_number,
        [],
    )

    if not matches:
        raise ValueError(
            f"{role} COMPANY nem található: "
            f"{tax_number}"
        )

    if len(matches) > 1:
        raise ValueError(
            f"{role} COMPANY többértelmű: "
            f"{tax_number}"
        )

    return matches[0]


def resolve_relation_id(
    cursor,
    requester_company_key: str,
    supplier_company_key: str,
) -> int:
    cursor.execute(
        """
        SELECT
            relation_id
        FROM dbo.SUPPLY_CHAIN_RELATION
        WHERE requester_company_key = ?
          AND supplier_company_key = ?
        ORDER BY relation_id
        """,
        requester_company_key,
        supplier_company_key,
    )

    rows = cursor.fetchall()

    if len(rows) == 0:
        raise ValueError(
            "SUPPLY_CHAIN_RELATION "
            "nem található"
        )

    if len(rows) > 1:
        raise ValueError(
            "Több SUPPLY_CHAIN_RELATION "
            "is megfelel"
        )

    return int(rows[0][0])


def main() -> None:
    if len(sys.argv) != 3:
        print("Használat:")

        print(
            "python "
            "scripts\\check_mssql_submission_writer_preflight.py "
            "\"<response.json>\" "
            "\"<batch_id>\""
        )

        raise SystemExit(2)
    json_file = Path(sys.argv[1])
    batch_id = optional_text(sys.argv[2])
    if not json_file.exists():
        raise FileNotFoundError(json_file)

    if batch_id is None:
        raise ValueError("batch_id nem lehet üres")

    with json_file.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        data = json.load(handle)

    spec_version = optional_text(data.get("spec_version"))

    if spec_version is None:
        raise ValueError("Hiányzik a spec_version")
    submissions = data.get("submissions")

    if (
        not isinstance(
            submissions,
            list,
        )
        or not submissions
    ):
        raise ValueError(
            "A submissions lista "
            "hiányzik vagy üres"
        )

    first_response = (submissions[0].get("response") or {} )
    questionnaire_code = (optional_text(first_response.get("survey_type")) or "SZTFH")
    config = (SqlServerConfig.from_environment())
    factory = (SqlServerConnectionFactory( config))
    connection = factory.connect()

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
            raise ValueError(
                "SUBMISSION_BATCH nem található: "
                f"{batch_id}"
            )

        if (
            str(batch_row[0]).strip() != questionnaire_code or str(batch_row[1]).strip() != spec_version
        ):
            raise ValueError(
                "A batch kérdőív/verzió "
                "nem egyezik a JSON-nal"
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
        questionnaire_question_ids = {str(row[0]).strip() for row in cursor.fetchall()}
        cursor.execute(
            """
            SELECT
                qo.question_id,
                qno.option_id
            FROM dbo.QUESTIONNAIRE_OPTION qno
            INNER JOIN dbo.QUESTION_OPTION qo
                ON qo.option_id = qno.option_id
            WHERE qno.questionnaire_code = ?
              AND qno.spec_version = ?
            """,
            questionnaire_code,
            spec_version,
        )
        option_ids_by_question = defaultdict(set)
        for row in cursor.fetchall():
            option_ids_by_question[str(row[0]).strip()].add(str(row[1]).strip())

        cursor.execute(
            """
            SELECT
                company_key,
                tax_number
            FROM dbo.COMPANY
            """
        )
        company_keys_by_tax = defaultdict(list)
        for row in cursor.fetchall():
            tax_number = (normalize_business_identifier(row[1]))

            if tax_number:
                company_keys_by_tax[tax_number].append(str(row[0]).strip())

    finally:
        connection.close()

    writer = MssqlSubmissionWriter(factory)

    existing_count = 0
    new_count = 0
    invalid_count = 0

    print()
    print("MSSQL SUBMISSION WRITER PREFLIGHT")
    print("=" * 70)

    print(
        "Fájl:",
        json_file,
    )

    print(
        "batch_id:",
        batch_id,
    )

    print("Submission darabszám:",len(submissions),)

    print()

    for index, submission in enumerate(
        submissions,
        start=1,
    ):
        response = (submission.get("response" )or {})

        cover = (response.get("cover") or {})
        supplier = (cover.get("supplier") or {})
        requester = (cover.get("requester")or {})
        supplier_tax = (normalize_business_identifier(supplier.get("tax_number")))
        requester_tax = (normalize_business_identifier(requester.get("tax_number")))

        print( "-" * 70)
        print(f"[{index}]")
        print("  supplier tax:",supplier_tax,)

        try:
            requester_key = (resolve_company_key(
                    company_keys_by_tax,
                    requester_tax,
                    "requester",
                )
            )

            supplier_key = (resolve_company_key(
                    company_keys_by_tax,
                    supplier_tax,
                    "supplier",
                )
            )
            relation_connection = (factory.connect())

            try:
                relation_cursor = (relation_connection.cursor())
                relation_id = (
                    resolve_relation_id(
                        relation_cursor,
                        requester_key,
                        supplier_key,
                    )
                )

            finally:
                relation_connection.close()

            plan = (SubmissionPersistencePlanner.create_plan(
                    submission_payload=(submission),
                    batch_id=batch_id,
                    relation_id=relation_id,
                    questionnaire_question_ids=(questionnaire_question_ids),
                    option_ids_by_question=dict(option_ids_by_question),
                )
            )

            result = writer.preflight(plan)

        except Exception as error:
            invalid_count += 1

            print("  PREFLIGHT: HIBA")
            print("Ok:",error,)
            continue

        print("  relation_id:",relation_id,)
        print("  respondent_id:",plan.submission.respondent_id,)
        print("  plan answer:",plan.answer_count,)
        print("  plan value:",plan.answer_value_count,)

        if result.exists:
            existing_count += 1
            print("  PREFLIGHT: EXISTING")
            print("  submission_id:",result.existing_submission_id,)

        else:
            new_count += 1

            print("  PREFLIGHT: NEW")
    print()
    print("=" * 70)
    print("ÖSSZESÍTÉS")
    print("=" * 70)
    print("Submissionök:",len(submissions),)
    print("EXISTING:",existing_count,)
    print("NEW:",new_count,)
    print("HIBA:",invalid_count,)
    print()
    print("ADATBÁZIS-ÍRÁS: 0 rekord")


if __name__ == "__main__":
    main()