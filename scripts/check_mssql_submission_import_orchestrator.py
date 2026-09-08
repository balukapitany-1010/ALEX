import json
import sys
from pathlib import Path
from alex.esg.infrastructure.repositories.mssql_submission_import_context_reader import MssqlSubmissionImportContextReader
from alex.esg.infrastructure.repositories.mssql_submission_writer import MssqlSubmissionWriter
from alex.esg.services.submission_import_orchestrator import SubmissionImportOrchestrator
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

def optional_text(
    value,
) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None

def main() -> None:
    if len(sys.argv) != 3:
        print("Használat:")
        print(
            "python "
            "scripts\\check_mssql_submission_import_orchestrator.py "
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
        payload = json.load(handle)
    config = (SqlServerConfig.from_environment())
    connection_factory = (SqlServerConnectionFactory(config))
    context_reader = (MssqlSubmissionImportContextReader(connection_factory))
    submission_writer = (MssqlSubmissionWriter(connection_factory))
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(context_reader),
            submission_writer=(submission_writer),
        )
    )

    result = (orchestrator.run_dry_run(
            payload=payload,
            batch_id=batch_id,
        )
    )
    print()
    print("SUBMISSION IMPORT ORCHESTRATOR DRY-RUN")
    print("=" * 70)
    print("Fájl:",json_file,)
    print("batch_id:", result.batch_id,)
    print("questionnaire:", result.questionnaire_code,)
    print("spec_version:", result.spec_version,)
    print("Submission darabszám:", result.submission_count,)
    print()
    for item in result.items:
        print("-" * 70)
        print(f"[{item.submission_index}]")
        print("supplier tax:", (item.supplier_tax_number or "HIÁNYZIK"),)
        print("requester tax:",(item.requester_tax_number or "HIÁNYZIK"),)

        if not item.is_valid:
            print("STATUS: ERROR")
            print("Ok:", item.error,)

            continue
        print("relation_id:",item.relation_id,)
        print("plan answer:", item.answer_count,)
        print("plan value:", item.answer_value_count,)

        if item.exists:
            print("STATUS: EXISTING")
            print("submission_id:", item.existing_submission_id,)

        elif item.is_new:
            print("STATUS: NEW")
        else:
            print("STATUS: ISMERETLEN")

    print()
    print("=" * 70)
    print("ÖSSZESÍTÉS")
    print("=" * 70)
    print("Submissionök:", result.submission_count,)
    print("EXISTING:",result.existing_count,)
    print("NEW:", result.new_count,)
    print("ERROR:",result.error_count,)
    print()
    print("SUBMISSION_ANSWER:", result.answer_count,)
    print("ANSWER_VALUE:", result.answer_value_count,)
    print()
    print("ADATBÁZIS-ÍRÁS: 0 rekord")

if __name__ == "__main__":
    main()