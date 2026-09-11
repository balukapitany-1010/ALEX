import json

from collections import Counter
from decimal import Decimal
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


def optional_text(
    value,
):
    if value is None:
        return None

    text = str(value)

    if not text:
        return ""

    return text


def normalize_decimal(
    value,
):
    if value is None:
        return None

    if isinstance(
        value,
        Decimal,
    ):
        return value

    return Decimal(
        str(value)
    )


def normalize_selected(
    value,
):
    if value is None:
        return None

    return bool(
        value
    )


def plan_value_key(
    value,
):
    return (
        value.field_type,
        value.option_id,
        value.selected,
        normalize_decimal(
            value.number_value
        ),
        value.text_value,
    )


def db_value_key(
    row,
):
    return (
        (
            None
            if row[2] is None
            else str(
                row[2]
            ).strip()
        ),
        (
            None
            if row[3] is None
            else str(
                row[3]
            ).strip()
        ),
        normalize_selected(
            row[4]
        ),
        normalize_decimal(
            row[5]
        ),
        (
            None
            if row[6] is None
            else str(
                row[6]
            )
        ),
    )


def format_value(
    value,
):
    (
        field_type,
        option_id,
        selected,
        number_value,
        text_value,
    ) = value

    return (
        "field_type="
        f"{field_type!r}, "
        "option_id="
        f"{option_id!r}, "
        "selected="
        f"{selected!r}, "
        "number_value="
        f"{number_value!r}, "
        "text_value="
        f"{text_value!r}"
    )


def main():
    with JSON_FILE.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        payload = json.load(
            handle
        )

    submissions = payload[
        "submissions"
    ]

    config = (
        SqlServerConfig
        .from_environment()
    )

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

    context = (
        context_reader.load_context(
            questionnaire_code=(
                QUESTIONNAIRE_CODE
            ),
            spec_version=(
                SPEC_VERSION
            ),
            batch_id=BATCH_ID,
        )
    )

    connection = (
        connection_factory.connect()
    )

    try:
        cursor = (
            connection.cursor()
        )

        print()
        print(
            "DB vs JSON PLAN VALUE DIFF"
        )
        print("=" * 100)

        total_common = 0
        total_identical = 0
        total_different = 0

        all_submission_results = []

        for index, submission in enumerate(
            submissions,
            start=1,
        ):
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

            requester_tax = (
                requester.get(
                    "tax_number"
                )
            )

            supplier_tax = (
                supplier.get(
                    "tax_number"
                )
            )

            relation_id = (
                context_reader
                .resolve_relation_id(
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
                    relation_id=(
                        relation_id
                    ),
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

            if len(
                submission_rows
            ) != 1:
                print()
                print(
                    f"[{index}] "
                    "DB SUBMISSION MATCH ERROR"
                )
                print(
                    "relation_id:",
                    relation_id,
                )
                print(
                    "találatok:",
                    len(
                        submission_rows
                    ),
                )

                all_submission_results.append(
                    False
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
                    sa.question_id,
                    sa.submission_answer_id,
                    av.field_type,
                    av.option_id,
                    av.selected,
                    av.number_value,
                    av.text_value
                FROM dbo.SUBMISSION_ANSWER AS sa
                LEFT JOIN dbo.ANSWER_VALUE AS av
                    ON av.submission_answer_id =
                       sa.submission_answer_id
                WHERE sa.submission_id = ?
                ORDER BY
                    sa.question_id,
                    sa.submission_answer_id,
                    av.answer_value_id
                """,
                db_submission_id,
            )

            db_answer_rows = (
                cursor.fetchall()
            )

            db_question_ids = set()

            db_values_by_question = {}

            for row in db_answer_rows:
                question_id = str(
                    row[0]
                ).strip()

                db_question_ids.add(
                    question_id
                )

                db_values_by_question.setdefault(
                    question_id,
                    [],
                )

                # LEFT JOIN esetén lehet olyan
                # SUBMISSION_ANSWER, amelyhez nincs
                # ANSWER_VALUE.
                if row[2] is not None:
                    db_values_by_question[
                        question_id
                    ].append(
                        db_value_key(
                            row
                        )
                    )

            plan_values_by_question = {
                str(
                    answer.question_id
                ).strip(): [
                    plan_value_key(
                        value
                    )
                    for value in answer.values
                ]
                for answer in plan.answers
            }

            plan_question_ids = set(
                plan_values_by_question
            )

            common_question_ids = (
                db_question_ids
                & plan_question_ids
            )

            missing_from_db = (
                plan_question_ids
                - db_question_ids
            )

            only_in_db = (
                db_question_ids
                - plan_question_ids
            )

            identical_question_ids = []
            different_question_ids = []

            for question_id in sorted(
                common_question_ids
            ):
                db_values = Counter(
                    db_values_by_question.get(
                        question_id,
                        [],
                    )
                )

                plan_values = Counter(
                    plan_values_by_question.get(
                        question_id,
                        [],
                    )
                )

                if db_values == plan_values:
                    identical_question_ids.append(
                        question_id
                    )
                else:
                    different_question_ids.append(
                        question_id
                    )

            total_common += len(
                common_question_ids
            )

            total_identical += len(
                identical_question_ids
            )

            total_different += len(
                different_question_ids
            )

            is_clean_supplement = (
                not different_question_ids
                and not only_in_db
            )

            all_submission_results.append(
                is_clean_supplement
            )

            print()
            print("-" * 100)
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
                "Közös question_id:",
                len(
                    common_question_ids
                ),
            )
            print(
                "Teljesen azonos answer:",
                len(
                    identical_question_ids
                ),
            )
            print(
                "Eltérő answer:",
                len(
                    different_question_ids
                ),
            )
            print(
                "Csak JSON planban:",
                len(
                    missing_from_db
                ),
            )
            print(
                "Csak DB-ben:",
                len(
                    only_in_db
                ),
            )

            if different_question_ids:
                print()
                print(
                    "ELTÉRŐ ANSWER-EK:"
                )

                for question_id in (
                    different_question_ids
                ):
                    print()
                    print(
                        "QUESTION:",
                        question_id,
                    )

                    db_counter = Counter(
                        db_values_by_question.get(
                            question_id,
                            [],
                        )
                    )

                    plan_counter = Counter(
                        plan_values_by_question.get(
                            question_id,
                            [],
                        )
                    )

                    only_db_values = (
                        db_counter
                        - plan_counter
                    )

                    only_plan_values = (
                        plan_counter
                        - db_counter
                    )

                    if only_db_values:
                        print(
                            "  CSAK DB-BEN:"
                        )

                        for (
                            value,
                            count,
                        ) in (
                            only_db_values.items()
                        ):
                            print(
                                "   ",
                                count,
                                "x",
                                format_value(
                                    value
                                ),
                            )

                    if only_plan_values:
                        print(
                            "  CSAK JSON PLANBAN:"
                        )

                        for (
                            value,
                            count,
                        ) in (
                            only_plan_values.items()
                        ):
                            print(
                                "   ",
                                count,
                                "x",
                                format_value(
                                    value
                                ),
                            )

            if missing_from_db:
                print()
                print(
                    "HIÁNYZÓ QUESTION_ID-K:"
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
                    "CSAK DB-BEN LÉVŐ "
                    "QUESTION_ID-K:"
                )

                for question_id in sorted(
                    only_in_db
                ):
                    print(
                        "  ",
                        question_id,
                    )

            print()
            print(
                "SUPPLEMENT-KOMPATIBILIS:",
                is_clean_supplement,
            )

        print()
        print("=" * 100)
        print(
            "ÖSSZES KÖZÖS QUESTION:",
            total_common,
        )
        print(
            "ÖSSZES AZONOS ANSWER:",
            total_identical,
        )
        print(
            "ÖSSZES ELTÉRŐ ANSWER:",
            total_different,
        )

        print()

        if (
            all_submission_results
            and all(
                all_submission_results
            )
        ):
            print(
                "EREDMÉNY: "
                "MINDEN SUBMISSION "
                "SUPPLEMENT-KOMPATIBILIS"
            )
        else:
            print(
                "EREDMÉNY: "
                "NEM MINDEN SUBMISSION "
                "SUPPLEMENT-KOMPATIBILIS"
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