import sys
from pathlib import Path
from alex.esg.mappers.questionnaire_definition_mapper import QuestionnaireDefinitionMapper
from alex.esg.services.json_import_service import JsonImportService
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

QUESTIONNAIRE_CODE = "SZTFH"


def canonical_question_type(
    value,
) -> str:
    if value is None:
        return ""

    normalized = str(value).strip().lower()

    aliases = {
        "radio": "radio",
        "radiogroup": "radio",
        "checkbox": "checkbox",
        "dropdown": "dropdown",
        "text": "text",
        "comment": "comment",
        "number": "number",
        "mixed": "mixed",
        "table": "table",
    }
    return aliases.get(
        normalized,
        normalized,
    )

def optional_text(
    value,
) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def extract_storage_options(
    data: dict,
) -> dict[str, dict]:
    result: dict[
        str,
        dict,
    ] = {}

    pages = data.get(
        "pages",
        [],
    )

    for page in pages:
        elements = page.get(
            "elements",
            [],
        )

        for element in elements:
            question_id = str(element["ID"]).strip()

            question_title = (optional_text(element.get("title"))
                or optional_text(element.get("name"))
                or question_id
            )

            def add_option(
                    *,
                    option_id,
                    text=None,
                    status="active",
                    step_value=None,
                    max_value=None,
                    min_value=None,
                    unit=None,
                    input_type=None,
            ) -> None:
                if option_id is None:
                    return
                option_id = str(option_id).strip()

                if not option_id:
                    return
                existing = result.get(option_id)

                if existing is not None:
                    if (existing["question_id"] != question_id
                    ):
                        raise ValueError(
                            "same option_id belongs "
                            "to multiple questions: "
                            f"{option_id}"
                        )
                    return
                result[option_id] = {
                    "question_id": question_id,
                    "text": optional_text(text),
                    "status": optional_text(status),
                    "step_value": step_value,
                    "max_value": max_value,
                    "min_value": min_value,
                    "unit": optional_text(unit),
                    "input_type": optional_text(
                        input_type
                    ),
                }
            choices = (element.get("choices") or [])
            for choice in choices:
                if not isinstance(
                    choice,
                    dict,
                ):
                    continue

                add_option(option_id=(choice.get("value")),
                    text=(choice.get("text")),
                )

            columns = (element.get("columns") or [])

            for column in columns:
                if not isinstance(
                    column,
                    dict,
                ):
                    continue
                cells = (column.get("cells") or [])

                for cell in cells:
                    if not isinstance(
                        cell,
                        dict,
                    ):
                        continue
                    add_option(
                        option_id=(cell.get("value")),
                        text=(cell.get("text")),
                    )
            element_type = str(element.get("type", "",)).strip().lower()

            if element_type == "number":
                add_option(
                    option_id=question_id,
                    text=None,
                    status=(
                            element.get("status")
                            or "active"
                    ),
                    step_value=element.get(
                        "step"
                    ),
                    max_value=element.get(
                        "max"
                    ),
                    min_value=element.get(
                        "min"
                    ),
                    unit=element.get(
                        "unit"
                    ),
                    input_type="number",
                )
    return result

def main() -> None:
    if len(sys.argv) != 2:
        print("Használat:")
        print(
            "python "
            "scripts\\check_mssql_"
            "questionnaire_definition_import.py "
            "\"<definition.json>\""
        )
        raise SystemExit(2)

    definition_file = Path(sys.argv[1])
    json_service = (JsonImportService())
    mapper = (QuestionnaireDefinitionMapper())
    data = (json_service.load_file(definition_file))
    (
        questionnaire,
        definitions,
    ) = mapper.map(
        data,
        questionnaire_code=(QUESTIONNAIRE_CODE),
    )
    incoming_questions = {
        definition.question.question_id: {
            "question_code": (definition.question.question_code),
            "category": (definition.category.value),
            "type": (definition.question_type.value),
            "title": (definition.title),
        }
        for definition in definitions
    }
    incoming_options = (extract_storage_options(data))
    config = (SqlServerConfig.from_environment())
    factory = (SqlServerConnectionFactory(config))
    connection = (factory.connect())
    try:
        cursor = (connection.cursor())
        cursor.execute(
            """
            SELECT
                questionnaire_code,
                spec_version,
                locale
            FROM dbo.QUESTIONNAIRE
            WHERE
                questionnaire_code = ?
                AND spec_version = ?
            """,
            questionnaire.questionnaire_code,
            questionnaire.spec_version,
        )

        questionnaire_row = (cursor.fetchone())
        cursor.execute(
            """
            SELECT
                question_id,
                question_code,
                category,
                type,
                title
            FROM dbo.QUESTION
            """
        )

        existing_questions = {str(row[0]).strip(): row
            for row
            in cursor.fetchall()
        }

        cursor.execute(
            """
            SELECT
                option_id,
                question_id,
                text
            FROM dbo.QUESTION_OPTION
            """
        )

        existing_options = {
            str(row[0]).strip(): row
            for row in cursor.fetchall()
        }

        cursor.execute(
            """
            SELECT
                question_id
            FROM dbo.QUESTIONNAIRE_QUESTION
            WHERE
                questionnaire_code = ?
                AND spec_version = ?
            """,
            questionnaire.questionnaire_code,
            questionnaire.spec_version,
        )

        existing_question_links = {
            str(row[0]).strip()
            for row in cursor.fetchall()
        }

        cursor.execute(
            """
            SELECT
                option_id
            FROM dbo.QUESTIONNAIRE_OPTION
            WHERE
                questionnaire_code = ?
                AND spec_version = ?
            """,
            questionnaire.questionnaire_code,
            questionnaire.spec_version,
        )

        existing_option_links = {
            str(row[0]).strip()
            for row in cursor.fetchall()
        }

    finally:
        connection.close()

    question_new = []
    question_reused = []
    question_conflicts = []
    question_warnings = []

    for (
        question_id,
        incoming,
    ) in incoming_questions.items():
        existing = (existing_questions.get(question_id))

        if existing is None:
            question_new.append(question_id)
            continue
        question_reused.append(question_id)
        existing_code = (optional_text(existing[1]))
        existing_category = (optional_text(existing[2]))
        existing_type = (canonical_question_type(existing[3]))
        if (
            existing_code != incoming["question_code"]
        ):
            question_conflicts.append(
                (
                    question_id,
                    "question_code",
                    existing_code,
                    incoming["question_code"],
                )
            )

        if (
            existing_category != incoming["category"]
        ):
            question_conflicts.append(
                (
                    question_id,
                    "category",
                    existing_category,
                    incoming["category"],
                )
            )
        if (
            existing_type != incoming["type"]
        ):
            question_conflicts.append(
                (
                    question_id,
                    "type",
                    existing_type,
                    incoming["type"],
                )
            )
        existing_title = (optional_text(existing[4]))
        incoming_title = ( optional_text(incoming["title"]))

        if (existing_title and incoming_title and existing_title != incoming_title):
            question_warnings.append(
                (
                    question_id,
                    existing_title,
                    incoming_title,
                )
            )

    option_new = []
    option_reused = []
    option_conflicts = []
    option_warnings = []

    for (
        option_id,
        incoming,
    ) in incoming_options.items():
        existing = (existing_options.get(option_id))
        if existing is None:
            option_new.append(option_id)
            continue
        option_reused.append(option_id)
        existing_question_id = str(existing[1]).strip()

        if (
            existing_question_id != incoming["question_id"]
        ):
            option_conflicts.append(
                (
                    option_id,
                    existing_question_id,
                    incoming["question_id"],
                )
            )
        existing_text = (optional_text(existing[2]))
        incoming_text = (incoming["text"])

        if (
            existing_text and incoming_text and existing_text != incoming_text
        ):
            option_warnings.append(
                (
                    option_id,
                    existing_text,
                    incoming_text,
                )
            )

    questionnaire_conflict = None
    if questionnaire_row is not None:
        db_locale = (str(questionnaire_row[2]).strip())
        if (
            db_locale.lower() != questionnaire.locale.lower()
        ):
            questionnaire_conflict = (
                f"DB locale={db_locale}, "
                f"JSON locale={questionnaire.locale}"
            )

    new_question_links = (set(incoming_questions) - existing_question_links)
    reused_question_links = (set(incoming_questions) & existing_question_links)
    question_types_by_id = {
        definition.question.question_id:
            definition.question_type.value
        for definition in definitions
    }

    linkable_option_ids = {
        option_id
        for option_id, data
        in incoming_options.items()
        if (
                question_types_by_id.get(
                    data["question_id"]
                )
                not in {
                    "number",
                    "table",
                }
        )
    }

    new_option_links = (
            linkable_option_ids
            - existing_option_links
    )

    reused_option_links = (
            linkable_option_ids
            & existing_option_links
    )

    print()
    print("KÉRDŐÍV MSSQL IMPORT DRY-RUN")
    print( "=" * 70)

    print(
        "Fájl:",
        definition_file,
    )

    print(
        "Kérdőív:",
        questionnaire.questionnaire_code,
        questionnaire.spec_version,
        questionnaire.locale,
    )

    print()

    print(
        "QUESTIONNAIRE rekord:",
        (
            "MÁR LÉTEZIK"
            if questionnaire_row is not None
            else "ÚJ"
        ),
    )

    if questionnaire_conflict:
        print(
            "QUESTIONNAIRE ÜTKÖZÉS:",
            questionnaire_conflict,
        )

    print()
    print("Kérdések összesen:",len(incoming_questions),)
    print("  új:",len(question_new),)
    print("  újrahasznált:",len(question_reused),)
    print("  konfliktus:",len(question_conflicts),)
    print("  címeltérés/figyelmeztetés:",len(question_warnings),)
    print()
    print("Opciók/értékazonosítók összesen:",len(incoming_options),)
    print("  új:",len(option_new),)
    print("  újrahasznált:",len(option_reused),)
    print("  konfliktus:",len(option_conflicts),)
    print("  szövegeltérés/figyelmeztetés:",len(option_warnings),)
    print()
    print("QUESTIONNAIRE_QUESTION link:")
    print("  új:",len(new_question_links),)
    print("  már létezik:",len(reused_question_links),)
    print()
    print("QUESTIONNAIRE_OPTION link:")
    print("  új:",len(new_option_links),)
    print("  már létezik:",len(reused_option_links),)

    if question_conflicts:
        print()
        print("Első kérdés-konfliktusok:")

        for conflict in (
            question_conflicts[:10]
        ):
            print(" ", conflict,)

    if option_conflicts:
        print()
        print("Első opció-konfliktusok:" )
        for conflict in (option_conflicts[:10]
        ):
            print(" ", conflict,)
    if question_warnings:
        print()
        print(
            "Első címeltérések:"
        )
        for warning in (question_warnings[:5]
        ):
            print(" ",warning[0],)

    if option_warnings:
        print()
        print("Első opciószöveg-eltérések:")
        for warning in (option_warnings[:5]
        ):
            print(" ", warning[0],)

    print()
    if option_new:
        print()
        print("Új QUESTION_OPTION rekordok:")

        for option_id in sorted(option_new
        ):
            data = incoming_options[option_id]

            print(
                " ",
                option_id,
                "| question_id:",
                data["question_id"],
                "| text:",
                data["text"],
                "| status:",
                data["status"],
                "| min:",
                data["min_value"],
                "| max:",
                data["max_value"],
                "| step:",
                data["step_value"],
                "| unit:",
                data["unit"],
                "| input_type:",
                data["input_type"],
            )
    if new_option_links:
        print()
        print(
            "Hiányzó QUESTIONNAIRE_OPTION "
            "kapcsolatok:"
        )

        for option_id in sorted(new_option_links
        ):
            data = incoming_options[option_id]

            print(
                " ",
                option_id,
                "| question_id:",
                data["question_id"],
                "| text:",
                data["text"],
                "| status:",
                data["status"],
                "| min:",
                data["min_value"],
                "| max:",
                data["max_value"],
                "| step:",
                data["step_value"],
                "| unit:",
                data["unit"],
                "| input_type:",
                data["input_type"],
            )
    print("ADATBÁZIS-ÍRÁS: 0 rekord")
    print("Ez a script csak ellenőrzött.")

if __name__ == "__main__":
    main()