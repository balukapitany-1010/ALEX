import json
import sys
from collections import defaultdict
from pathlib import Path

from alex.esg.services.submission_persistence_validator import (
    SubmissionPersistenceValidator,
)
from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)
from alex.infrastructure.database.sql_server_connection_factory import (
    SqlServerConnectionFactory,
)


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

    return int(
        rows[0][0]
    )


def get_structural_counts(
    submission: dict,
    questionnaire_question_ids: set[str],
) -> tuple[
    int,
    int,
    tuple[str, ...],
]:
    response = (
        submission.get(
            "response"
        )
        or {}
    )

    questions = (
        response.get(
            "questions"
        )
        or []
    )

    valid_question_count = 0
    answer_value_count = 0
    skipped_question_ids = []

    for question in questions:
        question_id = optional_text(
            question.get(
                "id"
            )
        )

        if question_id is None:
            raise ValueError(
                "Hiányzó question id"
            )

        if (
            question_id
            not in questionnaire_question_ids
        ):
            skipped_question_ids.append(
                question_id
            )

            continue

        valid_question_count += 1

        fields = (
            question.get(
                "fields"
            )
            or []
        )

        for field in fields:
            values = (
                field.get(
                    "values"
                )
                or []
            )

            answer_value_count += len(
                values
            )

    return (
        valid_question_count,
        answer_value_count,
        tuple(
            skipped_question_ids
        ),
    )


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Használat:"
        )

        print(
            "python "
            "scripts\\check_mssql_submission_persistence_plan.py "
            "\"<response.json>\" "
            "\"<batch_id>\""
        )

        raise SystemExit(2)

    json_file = Path(
        sys.argv[1]
    )

    batch_id = optional_text(
        sys.argv[2]
    )

    if not json_file.exists():
        raise FileNotFoundError(
            json_file
        )

    if batch_id is None:
        raise ValueError(
            "batch_id nem lehet üres"
        )

    with json_file.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        data = json.load(
            handle
        )

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "A JSON gyökérelem "
            "nem objektum."
        )

    spec_version = optional_text(
        data.get(
            "spec_version"
        )
    )

    if spec_version is None:
        raise ValueError(
            "Hiányzik a spec_version."
        )

    submissions = data.get(
        "submissions"
    )

    if (
        not isinstance(
            submissions,
            list,
        )
        or not submissions
    ):
        raise ValueError(
            "A submissions lista "
            "hiányzik vagy üres."
        )

    first_response = (
        submissions[0].get(
            "response"
        )
        or {}
    )

    questionnaire_code = (
        optional_text(
            first_response.get(
                "survey_type"
            )
        )
        or "SZTFH"
    )

    config = (
        SqlServerConfig
        .from_environment()
    )

    factory = (
        SqlServerConnectionFactory(
            config
        )
    )

    connection = factory.connect()

    try:
        cursor = connection.cursor()

        # -------------------------------------------------
        # Batch ellenőrzése
        # -------------------------------------------------

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

        batch_questionnaire_code = str(
            batch_row[0]
        ).strip()

        batch_spec_version = str(
            batch_row[1]
        ).strip()

        if (
            batch_questionnaire_code
            != questionnaire_code
            or batch_spec_version
            != spec_version
        ):
            raise ValueError(
                "A batch kérdőív/verzió "
                "nem egyezik a JSON-nal."
            )

        # -------------------------------------------------
        # Verzióhoz tartozó kérdések
        # -------------------------------------------------

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

        questionnaire_question_ids = {
            str(
                row[0]
            ).strip()
            for row in cursor.fetchall()
        }

        # -------------------------------------------------
        # Verzióhoz tartozó optionök
        # -------------------------------------------------

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

        option_ids_by_question = defaultdict(
            set
        )

        for row in cursor.fetchall():
            question_id = str(
                row[0]
            ).strip()

            option_id = str(
                row[1]
            ).strip()

            option_ids_by_question[
                question_id
            ].add(
                option_id
            )

        # -------------------------------------------------
        # COMPANY index
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                company_key,
                tax_number
            FROM dbo.COMPANY
            """
        )

        company_keys_by_tax = defaultdict(
            list
        )

        for row in cursor.fetchall():
            normalized_tax = (
                normalize_business_identifier(
                    row[1]
                )
            )

            if normalized_tax:
                company_keys_by_tax[
                    normalized_tax
                ].append(
                    str(
                        row[0]
                    ).strip()
                )

        print()
        print(
            "SUBMISSION PERSISTENCE BATCH DRY-RUN"
        )
        print(
            "=" * 70
        )

        print(
            "Fájl:",
            json_file,
        )

        print(
            "questionnaire:",
            questionnaire_code,
        )

        print(
            "spec_version:",
            spec_version,
        )

        print(
            "batch_id:",
            batch_id,
        )

        print(
            "Submission darabszám:",
            len(
                submissions
            ),
        )

        print()

        valid_count = 0
        invalid_count = 0

        total_structural_answers = 0
        total_structural_values = 0

        total_plan_answers = 0
        total_plan_values = 0

        all_skipped_question_ids = (
            defaultdict(
                int
            )
        )

        # -------------------------------------------------
        # Minden submission ellenőrzése
        # -------------------------------------------------

        for index, submission in enumerate(
            submissions,
            start=1,
        ):
            print(
                "-" * 70
            )

            if not isinstance(
                submission,
                dict,
            ):
                invalid_count += 1

                print(
                    f"[{index}] INVALID"
                )

                print(
                    "  Ok: submission nem objektum"
                )

                continue

            response = (
                submission.get(
                    "response"
                )
                or {}
            )

            current_survey_type = (
                optional_text(
                    response.get(
                        "survey_type"
                    )
                )
                or questionnaire_code
            )

            if (
                current_survey_type
                != questionnaire_code
            ):
                invalid_count += 1

                print(
                    f"[{index}] INVALID"
                )

                print(
                    "  Ok: eltérő survey_type: "
                    f"{current_survey_type}"
                )

                continue

            cover = (
                response.get(
                    "cover"
                )
                or {}
            )

            supplier = (
                cover.get(
                    "supplier"
                )
                or {}
            )

            requester = (
                cover.get(
                    "requester"
                )
                or {}
            )

            supplier_tax = (
                normalize_business_identifier(
                    supplier.get(
                        "tax_number"
                    )
                )
            )

            requester_tax = (
                normalize_business_identifier(
                    requester.get(
                        "tax_number"
                    )
                )
            )

            print(
                f"[{index}]"
            )

            print(
                "  supplier tax:",
                supplier_tax or "HIÁNYZIK",
            )

            print(
                "  requester tax:",
                requester_tax or "HIÁNYZIK",
            )

            if not supplier_tax:
                invalid_count += 1

                print(
                    "  INVALID"
                )

                print(
                    "  Ok: supplier adószám hiányzik"
                )

                continue

            if not requester_tax:
                invalid_count += 1

                print(
                    "  INVALID"
                )

                print(
                    "  Ok: requester adószám hiányzik"
                )

                continue

            try:
                requester_key = (
                    resolve_company_key(
                        company_keys_by_tax,
                        requester_tax,
                        "requester",
                    )
                )

                supplier_key = (
                    resolve_company_key(
                        company_keys_by_tax,
                        supplier_tax,
                        "supplier",
                    )
                )

                relation_id = (
                    resolve_relation_id(
                        cursor,
                        requester_key,
                        supplier_key,
                    )
                )

            except ValueError as error:
                invalid_count += 1

                print(
                    "  INVALID"
                )

                print(
                    "  Ok:",
                    error,
                )

                continue

            print(
                "  relation_id:",
                relation_id,
            )

            try:
                (
                    structural_answer_count,
                    structural_value_count,
                    skipped_question_ids,
                ) = get_structural_counts(
                    submission,
                    questionnaire_question_ids,
                )

            except (
                ValueError,
                TypeError,
            ) as error:
                invalid_count += 1

                print(
                    "  INVALID"
                )

                print(
                    "  Ok:",
                    error,
                )

                continue

            total_structural_answers += (
                structural_answer_count
            )

            total_structural_values += (
                structural_value_count
            )

            for skipped_id in (
                skipped_question_ids
            ):
                all_skipped_question_ids[
                    skipped_id
                ] += 1

            print(
                "  strukturális answer:",
                structural_answer_count,
            )

            print(
                "  strukturális value:",
                structural_value_count,
            )

            print(
                "  kihagyott question:",
                len(
                    skipped_question_ids
                ),
            )

            result = (
                SubmissionPersistenceValidator
                .validate(
                    submission_index=index,
                    submission_payload=submission,
                    batch_id=batch_id,
                    relation_id=relation_id,
                    supplier_tax_number=(
                        supplier_tax
                    ),
                    questionnaire_question_ids=(
                        questionnaire_question_ids
                    ),
                    option_ids_by_question=dict(
                        option_ids_by_question
                    ),
                )
            )

            if result.is_valid:
                valid_count += 1

                total_plan_answers += (
                    result.answer_count
                )

                total_plan_values += (
                    result.answer_value_count
                )

                print(
                    "  PLAN: VALID"
                )

                print(
                    "  plan answer:",
                    result.answer_count,
                )

                print(
                    "  plan value:",
                    result.answer_value_count,
                )

            else:
                invalid_count += 1

                print(
                    "  PLAN: INVALID"
                )

                print(
                    "  Ok:",
                    result.error,
                )

        print()
        print(
            "=" * 70
        )

        print(
            "ÖSSZESÍTÉS"
        )

        print(
            "=" * 70
        )

        print(
            "Submissionök:",
            len(
                submissions
            ),
        )

        print(
            "Valid:",
            valid_count,
        )

        print(
            "Invalid:",
            invalid_count,
        )

        print()

        print(
            "Strukturális SUBMISSION_ANSWER:",
            total_structural_answers,
        )

        print(
            "Strukturális ANSWER_VALUE:",
            total_structural_values,
        )

        print()

        print(
            "Érvényes plan SUBMISSION_ANSWER:",
            total_plan_answers,
        )

        print(
            "Érvényes plan ANSWER_VALUE:",
            total_plan_values,
        )

        if all_skipped_question_ids:
            print()
            print(
                "Kihagyott question_id-k:"
            )

            for (
                question_id,
                count,
            ) in sorted(
                all_skipped_question_ids.items()
            ):
                print(
                    f"  {question_id}: "
                    f"{count} db"
                )

        print()
        print(
            "ADATBÁZIS-ÍRÁS: 0 rekord"
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()