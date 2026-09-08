import argparse
import json
from pathlib import Path
from alex.esg.infrastructure.repositories.mssql_submission_import_context_reader import MssqlSubmissionImportContextReader
from alex.esg.infrastructure.repositories.mssql_submission_writer import MssqlSubmissionWriter
from alex.esg.services.submission_import_orchestrator import SubmissionImportOrchestrator
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "SZTFH submission JSON "
            "MSSQL import dry-run."
        )
    )

    parser.add_argument(
        "json_file",
        type=Path,
        help=("A feldolgozandó JSON fájl."),
    )

    parser.add_argument(
        "--batch-id",
        required=True,
        help=("A használni kívánt SUBMISSION_BATCH batch_id."),
    )

    return parser.parse_args()


def load_payload(
    json_file: Path,
) -> dict:
    if not json_file.exists():
        raise FileNotFoundError(json_file)

    if not json_file.is_file():
        raise ValueError("A megadott útvonal nem fájl.")

    with json_file.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        payload = json.load(handle)

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError("A JSON gyökérelemnek objektumnak kell lennie.")
    return payload


def print_result(
    *,
    json_file: Path,
    result,
) -> None:
    print()
    print("ALEX MSSQL SUBMISSION IMPORT")
    print("MÓD: DRY-RUN")
    print("=" * 70)
    print("Fájl:",json_file,)
    print("batch_id:",result.batch_id,)
    print("questionnaire:",result.questionnaire_code,)
    print("spec_version:",result.spec_version,)
    print("Submission darabszám:",result.submission_count,)
    print()

    for item in result.items:
        print("-" * 70)
        print(f"[{item.submission_index}]")
        print("supplier tax:",(item.supplier_tax_number or "HIÁNYZIK"),)
        print("requester tax:",(item.requester_tax_number or "HIÁNYZIK"),)

        if not item.is_valid:
            print("STATUS: ERROR")
            print("Ok:",item.error,)
            continue
        print("relation_id:",item.relation_id,)
        print("SUBMISSION_ANSWER:", item.answer_count,)
        print("ANSWER_VALUE:",item.answer_value_count,)

        if item.exists:
            print("STATUS: EXISTING")
            print("submission_id:",item.existing_submission_id,)

        elif item.is_new:
            print("STATUS: NEW")

        else:
            print("  STATUS: UNKNOWN")
    print()
    print("=" * 70)
    print("ÖSSZESÍTÉS")
    print("=" * 70)
    print("Submissionök:", result.submission_count,)
    print("EXISTING:", result.existing_count,)
    print("NEW:", result.new_count,)
    print("ERROR:", result.error_count,)
    print()
    print("SUBMISSION_ANSWER:",result.answer_count,)
    print("ANSWER_VALUE:", result.answer_value_count,)
    print()
    print("ADATBÁZIS-ÍRÁS: 0 rekord")


def main() -> int:
    args = parse_arguments()

    try:
        payload = load_payload(args.json_file)
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
                batch_id=args.batch_id,
            )
        )

        print_result(
            json_file=args.json_file,
            result=result,
        )

        if result.error_count:
            return 1
        return 0

    except Exception as error:
        print()
        print("IMPORT DRY-RUN HIBA")
        print(error)
        print("=" * 70)
        print()
        print("ADATBÁZIS-ÍRÁS: 0 rekord")

        return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )