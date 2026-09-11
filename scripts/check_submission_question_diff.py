import json
from pathlib import Path

from alex.esg.infrastructure.repositories.mssql_submission_import_context_reader import (
    MssqlSubmissionImportContextReader,
)
from alex.esg.services.submission_persistence_plan import (
    SubmissionPersistencePlanner,
)
from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)
from alex.infrastructure.database.sql_server_connection_factory import (
    SqlServerConnectionFactory,
)


JSON_FILE = Path(
    r"C:\Users\admintbb\Downloads"
    r"\Gyermelyi Holding Zrt-20260713T142635Z-2-001"
    r"\Gyermelyi Holding Zrt"
    r"\esg-form-report-2026-05-15T06-37-54-907Z (v1)_jav.json"
)

BATCH_ID = (
    "BATCH_11182005211_20260515063754"
)

QUESTIONNAIRE_CODE = "SZTFH"
SPEC_VERSION = "2.0"


def optional_text(value):
    if value is None:
        return None

    text = str(value).strip()

    return text or None


def main():
    with JSON_FILE.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        payload = json.load(handle)

    submissions = payload["submissions"]

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

    context = context_reader.load_context(
        questionnaire_code=QUESTIONNAIRE_CODE,
        spec_version=SPEC_VERSION,
        batch_id=BATCH_ID,
    )

    connection = (
        connection_factory.connect()
    )

    try:
        cursor = connection.cursor()

        print()
        print(
            "DB vs JSON PLAN QUESTION DIFF"
        )
        print("=" * 90)

        missing_sets = []

        for index, submission in enumerate(
            submissions,
            start=1,
        ):
            response = (
                submission.get("response")
                or {}
            )

            cover = (
                response.get("cover")
                or {}
            )

            requester = (
                cover.get("requester")
                or {}
            )

            supplier = (
                cover.get("supplier")
                or {}
            )

            requester_tax = optional_text(
                requester.get("tax_number")
            )

            supplier_tax = optional_text(
                supplier.get("tax_number")
            )

            relation_id = (
                context_reader.resolve_relation_id(
                    requester_tax_number=(
                        requester_tax
                    ),
                    supplier_tax_number=(
                        supplier_tax
                    ),
                )
            )

            plan = (
                SubmissionPersistencePlanner
                .create_plan(
                    submission_payload=(
                        submission
                    ),
                    batch_id=BATCH_ID,
                    relation_id=relation_id,
                    questionnaire_question_ids=(
                        set(
                            context
                            .questionnaire_question_ids
                        )
                    ),
                    option_ids_by_question={
                        question_id: set(
                            option_ids
                        )
                        for (
                            question_id,
                            option_ids,
                        ) in (
                            context
                            .option_ids_by_question
                            .items()
                        )
                    },
                )
            )

            cursor.execute(
                """
                SELECT
                    submission_id,
                    respondent_id,
                    submitted_at
                FROM dbo.SUBMISSION
                WHERE batch_id = ?
                  AND relation_id = ?
                ORDER BY submission_id
                """,
                BATCH_ID,
                relation_id,
            )

            submission_rows = (
                cursor.fetchall()
            )

            if len(submission_rows) != 1:
                print()
                print(
                    f"[{index}] "
                    f"relation_id={relation_id}"
                )
                print(
                    "DB SUBMISSION MATCH ERROR:",
                    len(submission_rows),
                )
                continue

            db_submission_id = int(
                submission_rows[0][0]
            )

            db_respondent_id = (
                submission_rows[0][1]
            )

            db_submitted_at = (
                submission_rows[0][2]
            )

            cursor.execute(
                """
                SELECT
                    question_id
                FROM dbo.SUBMISSION_ANSWER
                WHERE submission_id = ?
                ORDER BY question_id
                """,
                db_submission_id,
            )

            db_question_ids = {
                str(row[0]).strip()
                for row in cursor.fetchall()
            }

            plan_question_ids = {
                str(answer.question_id).strip()
                for answer in plan.answers
            }

            missing_from_db = (
                plan_question_ids
                - db_question_ids
            )

            only_in_db = (
                db_question_ids
                - plan_question_ids
            )

            missing_sets.append(
                frozenset(
                    missing_from_db
                )
            )

            print()
            print("-" * 90)

            print(
                f"[{index}]"
            )

            print(
                "supplier:",
                supplier_tax,
            )

            print(
                "relation_id:",
                relation_id,
            )

            print(
                "submission_id:",
                db_submission_id,
            )

            print(
                "DB respondent_id:",
                db_respondent_id,
            )

            print(
                "PLAN respondent_id:",
                plan.submission.respondent_id,
            )

            print(
                "DB submitted_at:",
                db_submitted_at,
            )

            print(
                "PLAN submitted_at:",
                plan.submission.submitted_at,
            )

            print()

            print(
                "DB answer:",
                len(db_question_ids),
            )

            print(
                "JSON plan answer:",
                len(plan_question_ids),
            )

            print(
                "Hiányzik DB-ből:",
                len(missing_from_db),
            )

            print(
                "Csak DB-ben:",
                len(only_in_db),
            )

            if missing_from_db:
                print()
                print(
                    "HIÁNYZIK DB-BŐL:"
                )

                for question_id in sorted(
                    missing_from_db
                ):
                    print(
                        "  ",
                        question_id,
                    )

            if only_in_db:
                print()
                print(
                    "CSAK DB-BEN:"
                )

                for question_id in sorted(
                    only_in_db
                ):
                    print(
                        "  ",
                        question_id,
                    )

        print()
        print("=" * 90)

        if missing_sets:
            all_same = (
                len(
                    set(
                        missing_sets
                    )
                )
                == 1
            )

            print(
                "Mindegyik submissionnél "
                "azonos hiányzó kérdéslista:",
                all_same,
            )

            if all_same:
                common_missing = (
                    missing_sets[0]
                )

                print(
                    "Közös hiányzó kérdések:",
                    len(common_missing),
                )

                for question_id in sorted(
                    common_missing
                ):
                    print(
                        "  ",
                        question_id,
                    )

        print()
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