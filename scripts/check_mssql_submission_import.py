import json
import sys
from collections import defaultdict
from pathlib import Path
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

def optional_text(
    value,
) -> str | None:
    if value is None:
        return None

    value = str(value).strip()
    return value or None

def normalize_business_identifier(
    value,
) -> str:
    value = optional_text(value)

    if value is None:
        return ""

    return "".join(character for character in value.upper() if character.isalnum())


def main() -> None:
    if len(sys.argv) != 2:
        print("Használat:")
        print(
            "python "
            "scripts\\check_mssql_submission_import.py "
            "\"<response.json>\""
        )
        raise SystemExit(2)

    json_file = Path(sys.argv[1])
    if not json_file.exists():
        raise FileNotFoundError(json_file)
    with json_file.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        data = json.load(handle)

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError("A JSON gyökérelemnek objektumnak kell lennie.")
    spec_version = optional_text(data.get("spec_version"))
    batch_id = optional_text(data.get("batch_id"))
    submissions = data.get("submissions")
    if not spec_version:
        raise ValueError("Hiányzik a spec_version.")
    if not isinstance(
        submissions,
        list,
    ):
        raise ValueError("A submissions mezőnek listának kell lennie.")
    if not submissions:
        raise ValueError("A submissions lista üres.")

    config = (SqlServerConfig.from_environment())
    factory = (SqlServerConnectionFactory(config))
    connection = factory.connect()
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                questionnaire_code,
                spec_version
            FROM dbo.QUESTIONNAIRE
            """
        )

        existing_questionnaires = {
            (
                str(row[0]).strip(),
                str(row[1]).strip(),
            )
            for row in cursor.fetchall()
        }

        cursor.execute(
            """
            SELECT
                question_id,
                question_code
            FROM dbo.QUESTION
            """
        )

        existing_questions = {str(row[0]).strip(): (optional_text(row[1]))
            for row in cursor.fetchall()
        }
        cursor.execute(
            """
            SELECT
                questionnaire_code,
                spec_version,
                question_id
            FROM dbo.QUESTIONNAIRE_QUESTION
            """
        )

        existing_questionnaire_questions = {
            (
                str(row[0]).strip(),
                str(row[1]).strip(),
                str(row[2]).strip(),
            )
            for row in cursor.fetchall()
        }

        cursor.execute(
            """
            SELECT
                option_id,
                question_id
            FROM dbo.QUESTION_OPTION
            """
        )
        existing_options = {str(row[0]).strip(): str(row[1]).strip() for row in cursor.fetchall()}
        cursor.execute(
            """
            SELECT
                company_key,
                tax_number
            FROM dbo.COMPANY
            """
        )

        company_keys_by_tax = (
            defaultdict(list)
        )

        for row in cursor.fetchall():
            normalized_tax = (normalize_business_identifier(row[1]))
            if normalized_tax:
                company_keys_by_tax[normalized_tax].append(str(row[0]).strip())
        cursor.execute(
            """
            SELECT
                relation_id,
                requester_company_key,
                supplier_company_key
            FROM dbo.SUPPLY_CHAIN_RELATION
            """
        )

        relations = {}
        for row in cursor.fetchall():
            key = (
                str(row[1]).strip(),
                str(row[2]).strip(),
            )
            relations.setdefault(key, [],).append(int(row[0]))


        cursor.execute(
            """
            SELECT
                batch_id,
                questionnaire_code,
                spec_version
            FROM dbo.SUBMISSION_BATCH
            """
        )

        existing_batches = {
            str(row[0]).strip(): (
                str(row[1]).strip(),
                str(row[2]).strip(),
            )
            for row in cursor.fetchall()
        }

        cursor.execute(
            """
            SELECT
                submission_id,
                batch_id,
                relation_id,
                respondent_id,
                respondent_mp_id
            FROM dbo.SUBMISSION
            """
        )
        existing_submission_keys = {}

        existing_batch_relations = (
            defaultdict(list)
        )

        existing_submissions_by_batch_relation = (
            defaultdict(list)
        )

        for row in cursor.fetchall():
            submission_id = int(
                row[0]
            )

            db_batch_id = str(
                row[1]
            ).strip()

            db_relation_id = int(
                row[2]
            )

            db_respondent_id = optional_text(
                row[3]
            )

            db_respondent_mp_id = optional_text(
                row[4]
            )

            natural_key = (
                db_batch_id,
                db_relation_id,
                db_respondent_id,
                db_respondent_mp_id,
            )

            existing_submission_keys[
                natural_key
            ] = submission_id

            existing_batch_relations[
                db_batch_id
            ].append(
                db_relation_id
            )

            existing_submissions_by_batch_relation[
                (
                    db_batch_id,
                    db_relation_id,
                )
            ].append(
                submission_id
            )
    finally:
        connection.close()

    print()
    print("SUBMISSION MSSQL IMPORT DRY-RUN")
    print("=" * 70)
    print("Fájl:",json_file,)
    print("spec_version:", spec_version,)
    print("batch_id:", batch_id or "HIÁNYZIK",)
    print("Submission darabszám:", len(submissions),)

    total_questions = 0
    total_values = 0

    valid_questions = 0
    valid_values = 0

    not_in_questionnaire_questions = defaultdict(int)
    not_in_questionnaire_values = 0

    unknown_questions = set()
    unknown_options = set()
    wrong_option_question = []
    duplicate_question_ids = []
    unresolved_companies = []
    ambiguous_companies = []
    unresolved_relations = []
    existing_submissions = []
    new_submissions = []
    ambiguous_submission_matches = []

    survey_types = set()
    resolved_relation_ids = []

    for (
        submission_index,
        submission,
    ) in enumerate(
        submissions,
        start=1,
    ):
        if not isinstance(
            submission,
            dict,
        ):
            raise ValueError(
                "Minden submission elemnek "
                "objektumnak kell lennie."
            )

        response = submission.get("response") or {}
        survey_type = (optional_text(response.get("survey_type")) or "SZTFH")
        survey_types.add(survey_type)
        respondent_id = optional_text(response.get("respondent_id"))
        respondent_mp_id = optional_text(response.get("respondent_MP_id"))
        if respondent_mp_id is None:
            respondent_mp_id = (optional_text(response.get("respondent_mp_id")))
        cover = response.get("cover") or {}
        supplier = cover.get("supplier") or {}
        requester = cover.get("requester") or {}
        supplier_tax = (normalize_business_identifier(supplier.get("tax_number")))
        requester_tax = (normalize_business_identifier(requester.get("tax_number")))
        supplier_matches = (
            company_keys_by_tax.get(
                supplier_tax,
                [],
            )
            if supplier_tax
            else []
        )

        requester_matches = (
            company_keys_by_tax.get(
                requester_tax,
                [],
            )
            if requester_tax
            else []
        )
        supplier_key = None
        requester_key = None

        if len(supplier_matches) == 1:
            supplier_key = supplier_matches[0]

        elif len(supplier_matches) == 0:
            unresolved_companies.append(
                (
                    submission_index,
                    "supplier",
                    supplier_tax,
                )
            )

        else:
            ambiguous_companies.append(
                (
                    submission_index,
                    "supplier",
                    supplier_tax,
                    supplier_matches,
                )
            )

        if len(requester_matches) == 1:
            requester_key = requester_matches[0]

        elif len(requester_matches) == 0:
            unresolved_companies.append(
                (
                    submission_index,
                    "requester",
                    requester_tax,
                )
            )

        else:
            ambiguous_companies.append(
                (
                    submission_index,
                    "requester",
                    requester_tax,
                    requester_matches,
                )
            )

        relation_id = None

        if (
                supplier_key is not None
                and requester_key is not None
        ):
            relation_matches = relations.get(
                (
                    requester_key,
                    supplier_key,
                ),
                [],
            )

            if len(relation_matches) == 1:
                relation_id = relation_matches[0]

            else:
                unresolved_relations.append(
                    (
                        submission_index,
                        requester_key,
                        supplier_key,
                        relation_matches,
                    )
                )
        if relation_id is not None:
            resolved_relation_ids.append(
                (
                    submission_index,
                    relation_id,
                )
            )

        if (
            batch_id is not None and relation_id is not None
        ):
            natural_key = (
                batch_id,
                relation_id,
                respondent_id,
                respondent_mp_id,
            )

            existing_submission_id = (existing_submission_keys.get(natural_key))
            if (
                existing_submission_id is not None
            ):
                existing_submissions.append(
                    (
                        submission_index,
                        existing_submission_id,
                        natural_key,
                    )
                )
            else:
                new_submissions.append(
                    (
                        submission_index,
                        natural_key,
                    )
                )
        questions = response.get( "questions") or []

        if not isinstance(
            questions,
            list,
        ):
            raise ValueError("response.questions nem lista " f"a(z) {submission_index}. submissionben.")


        technical_question_ids = []
        for question in questions:
            technical_question_id = (optional_text(question.get("id" )))
            question_code = (optional_text(question.get("question_id")))
            if (
                technical_question_id
                is None
            ):
                unknown_questions.add("<HIÁNYZÓ id>")
                continue
            technical_question_ids.append(
                technical_question_id
            )

            total_questions += 1

            question_known = (
                    technical_question_id
                    in existing_questions
            )

            question_in_version = False

            if not question_known:
                unknown_questions.add(
                    technical_question_id
                )

            else:
                questionnaire_question_key = (
                    survey_type,
                    spec_version,
                    technical_question_id,
                )

                question_in_version = (
                        questionnaire_question_key
                        in existing_questionnaire_questions
                )

                if question_in_version:
                    valid_questions += 1

                else:
                    not_in_questionnaire_questions[
                        technical_question_id
                    ] += 1

            fields = question.get(
                "fields"
            ) or []
            if not isinstance(
                fields,
                list,
            ):
                raise ValueError("question.fields nem lista: " f"{technical_question_id}"
                )
            for field in fields:
                field_type = optional_text(field.get("type"))
                if field_type not in {
                    "single",
                    "multi",
                    "text",
                    "number",
                }:
                    raise ValueError("Ismeretlen field type: " f"{field_type} " f"({technical_question_id})")

                values = field.get("values") or []
                if not isinstance(
                    values,
                    list,
                ):
                    raise ValueError("field.values nem lista: " f"{technical_question_id}")
                for value in values:
                    total_values += 1

                    if (
                            question_known
                            and not question_in_version
                    ):
                        not_in_questionnaire_values += 1
                        continue

                    if not question_known:
                        continue

                    valid_values += 1

                    option_id = (
                        optional_text(
                            value.get(
                                "optionId"
                            )
                        )
                    )
                    if option_id is None:
                        continue
                    option_question_id = (existing_options.get(option_id))
                    if (
                        option_question_id is None
                    ):
                        unknown_options.add(option_id)

                    elif (
                        option_question_id != technical_question_id
                    ):
                        wrong_option_question.append(
                            (
                                option_id,
                                option_question_id,
                                technical_question_id,
                                question_code,
                            )
                        )

        counts = defaultdict(int)
        for question_id in (technical_question_ids):
            counts[question_id] += 1
        for (
            question_id,
            count,
        ) in counts.items():
            if count > 1:
                duplicate_question_ids.append(
                    (
                        submission_index,
                        question_id,
                        count,
                    )
                )
    inferred_batch_id = None
    batch_candidates = []

    if (
        batch_id is None
        and len(resolved_relation_ids)
        == len(submissions)
    ):
        incoming_relation_ids = [
            relation_id
            for (
                submission_index,
                relation_id,
            )
            in resolved_relation_ids
        ]

        for (
            candidate_batch_id,
            batch_data,
        ) in existing_batches.items():
            candidate_questionnaire_code = (
                batch_data[0]
            )

            candidate_spec_version = (
                batch_data[1]
            )

            if (
                candidate_questionnaire_code
                not in survey_types
            ):
                continue

            if (
                candidate_spec_version
                != spec_version
            ):
                continue

            db_relation_ids = (
                existing_batch_relations.get(
                    candidate_batch_id,
                    [],
                )
            )

            if (
                len(db_relation_ids)
                != len(incoming_relation_ids)
            ):
                continue

            if (
                sorted(db_relation_ids)
                != sorted(incoming_relation_ids)
            ):
                continue

            batch_candidates.append(
                candidate_batch_id
            )

    if len(batch_candidates) == 1:
        inferred_batch_id = (
            batch_candidates[0]
        )
    if inferred_batch_id is not None:
        for (
                submission_index,
                relation_id,
        ) in resolved_relation_ids:
            matches = (
                existing_submissions_by_batch_relation.get(
                    (
                        inferred_batch_id,
                        relation_id,
                    ),
                    [],
                )
            )

            if len(matches) == 1:
                existing_submissions.append(
                    (
                        submission_index,
                        matches[0],
                        inferred_batch_id,
                        relation_id,
                    )
                )

            elif len(matches) == 0:
                new_submissions.append(
                    (
                        submission_index,
                        inferred_batch_id,
                        relation_id,
                    )
                )

            else:
                ambiguous_submission_matches.append(
                    (
                        submission_index,
                        inferred_batch_id,
                        relation_id,
                        matches,
                    )
                )
    print()
    print("Survey type:", ", ".join(sorted(survey_types)),)
    questionnaire_missing = []
    for survey_type in survey_types:
        if (
            (
                survey_type,
                spec_version,
            )
            not in existing_questionnaires
        ):
            questionnaire_missing.append(
                (
                    survey_type,
                    spec_version,
                )
            )
    print()
    print(
        "JSON kérdésrekordok:",
        total_questions,
    )

    print(
        "Érvényes kérdésrekordok:",
        valid_questions,
    )

    print(
        "Verzióhoz nem tartozó kérdésrekordok:",
        sum(
            not_in_questionnaire_questions.values()
        ),
    )

    print()

    print(
        "JSON válaszértékek:",
        total_values,
    )

    print(
        "Érvényes válaszértékek:",
        valid_values,
    )

    print(
        "Kihagyott válaszértékek "
        "(verzión kívüli kérdés):",
        not_in_questionnaire_values,
    )
    print()
    print("Ismeretlen question_id-k:",len(unknown_questions),)
    print("Ismeretlen option_id-k:",len(unknown_options),)
    print("Rossz kérdéshez tartozó option_id:",len(wrong_option_question),)
    print("Duplikált question id egy submissionön belül:",len( duplicate_question_ids),)
    print()
    print("Nem feloldható COMPANY-k:",len(unresolved_companies),)
    print("Többértelmű COMPANY-k:", len(ambiguous_companies),)
    print("Nem feloldható kapcsolatok:", len(unresolved_relations),)
    print()

    if batch_id is None:
        if inferred_batch_id is not None:
            print(
                "SUBMISSION_BATCH felismerve:",
                inferred_batch_id,
            )

            print(
                "Batch felismerés módja:"
            )

            print(
                "  questionnaire + verzió + "
                "relation halmaz + darabszám"
            )

            print()

            print(
                "Már létező submission:",
                len(existing_submissions),
            )

            print(
                "Új submission:",
                len(new_submissions),
            )

            print(
                "Többértelmű submission-egyezés:",
                len(ambiguous_submission_matches),
            )

        elif batch_candidates:
            print(
                "SUBMISSION_BATCH:"
            )

            print(
                "  TÖBB LEHETSÉGES BATCH"
            )

            for candidate in batch_candidates:
                print(
                    " ",
                    candidate,
                )

        else:
            print(
                "SUBMISSION_BATCH:"
            )

            print(
                "  NEM TALÁLHATÓ MEGLÉVŐ BATCH"
            )

    else:
        print(
            "Már létező submission:",
            len(existing_submissions),
        )

        print(
            "Új submission:",
            len(new_submissions),
        )

        batch_record = (
            existing_batches.get(
                batch_id
            )
        )

        if batch_record is None:
            print(
                "SUBMISSION_BATCH:",
                "ÚJ",
            )

        else:
            print(
                "SUBMISSION_BATCH:",
                "MÁR LÉTEZIK",
                batch_record,
            )

    if questionnaire_missing:
        print()
        print("HIÁNYZÓ QUESTIONNAIRE:")

        for item in (questionnaire_missing):
            print(" ", item,)

    if not_in_questionnaire_questions:
        print()
        print(
            "Verzióhoz nem tartozó kérdések:"
        )

        for (
            question_id,
            count,
        ) in sorted(
            not_in_questionnaire_questions.items()
        ):
            print(
                " ",
                question_id,
                "|",
                count,
                "db",
            )

    if unknown_questions:
        print()
        print("Első ismeretlen kérdések:")

        for question_id in sorted(unknown_questions)[:20]:
            print(" ", question_id,)

    if unknown_options:
        print()
        print("Első ismeretlen opciók:")
        for option_id in sorted(unknown_options)[:20]:
            print(" ", option_id,)

    if wrong_option_question:
        print()
        print("Első hibás option/question kapcsolatok:")
        for item in (wrong_option_question[:20]):
            print(" ",item,)

    if duplicate_question_ids:
        print()
        print("Duplikált kérdések:")

        for item in (duplicate_question_ids[:20]):
            print(" ", item,)

    if unresolved_companies:
        print()
        print("Első nem feloldható cégek:")
        for item in (unresolved_companies[:20]):
            print(" ",item,)

    if ambiguous_companies:
        print()
        print("Első többértelmű cégek:")
        for item in (ambiguous_companies[:20]):
            print(" ", item,)

    if unresolved_relations:
        print()
        print("Első nem feloldható kapcsolatok:")

        for item in (unresolved_relations[:20]):
            print( " ", item,)
    if ambiguous_submission_matches:
        print()
        print(
            "Többértelmű submission-egyezések:"
        )

        for item in (
                ambiguous_submission_matches[:20]
        ):
            print(
                " ",
                item,
            )

    if existing_submissions:
        print()
        print("Már létező submissionök:")
        for item in (existing_submissions[:20]):
            print( " ", item,)

    print()
    print("ADATBÁZIS-ÍRÁS: 0 rekord")
    print("Ez a script csak ellenőrzött.")

if __name__ == "__main__":
    main()