import argparse
import json
from pathlib import Path
import sys
from alex.esg.infrastructure.repositories.mssql_submission_import_context_reader import MssqlSubmissionImportContextReader
from alex.esg.infrastructure.repositories.mssql_submission_writer import MssqlSubmissionWriter
from alex.esg.services.submission_import_orchestrator import SubmissionImportOrchestrator
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory
from alex.esg.infrastructure.repositories.mssql_submission_batch_writer import MssqlSubmissionBatchWriter
from alex.esg.infrastructure.repositories.mssql_submission_import_writer import MssqlSubmissionImportWriter
from alex.esg.infrastructure.repositories.mssql_submission_import_verifier import MssqlSubmissionImportVerifier

if hasattr(
    sys.stdout,
    "reconfigure",
):
    sys.stdout.reconfigure( errors="replace")

if hasattr(
    sys.stderr,
    "reconfigure",
):
    sys.stderr.reconfigure(errors="replace")
def parse_arguments():
    parser = argparse.ArgumentParser(
        description=("SZTFH submission JSON MSSQL import dry-run.")
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
    mode_group = (parser.add_mutually_exclusive_group())

    mode_group.add_argument(
        "--execute",
        action="store_true",
        help=("A validált submissionök tényleges MSSQL mentése."),
    )
    mode_group.add_argument(
        "--execute-supplements",
        action="store_true",
        help=("Kizárólag SUPPLEMENT státuszú submissionök tényleges MSSQL kiegészítése."),
    )

    mode_group.add_argument(
        "--rollback-test",
        action="store_true",
        help=("Az MSSQL írási folyamat lefuttatása kötelező rollbackkel."),
    )
    parser.add_argument(
        "--confirm-write",
        default=None,
        help=("Írás esetén kötelező érték: WRITE"),
    )
    parser.add_argument(
        "--confirm-supplements",
        default=None,
        help=("Supplement íráshoz kötelező érték: SUPPLEMENT"),
    )
    parser.add_argument(
        "--confirm-rollback",
        default=None,
        help=(
            "Rollback teszthez kötelező érték: ROLLBACK"),
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
    print("BATCH STATUS:",("EXISTING" if result.batch_exists  else "NEW"),)
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
        if item.plan is not None:
            print(
                "plan batch_id:",
                item.plan.submission.batch_id,
            )

            print(
                "plan respondent_id:",
                item.plan.submission.respondent_id,
            )

            print(
                "plan respondent_mp_id:",
                item.plan.submission.respondent_mp_id,
            )
        print("SUBMISSION_ANSWER:", item.answer_count,)
        print("ANSWER_VALUE:",item.answer_value_count,)

        if item.is_supplement:
            print("STATUS: SUPPLEMENT")
            print(
                "submission_id:",
                item.existing_submission_id,
            )
            print(
                "SUPPLEMENT_ANSWER:",
                item.supplement_answer_count,
            )
            print(
                "SUPPLEMENT_VALUE:",
                item.supplement_answer_value_count,
            )

        elif item.exists:
            print("STATUS: EXISTING")
            print(
                "submission_id:",
                item.existing_submission_id,
            )

        elif item.is_new:
            print("STATUS: NEW")

        else:
            print("STATUS: UNKNOWN")
    print()
    print("=" * 70)
    print("ÖSSZESÍTÉS")
    print("=" * 70)
    print("Submissionök:", result.submission_count,)
    print(
        "EXISTING:",
        result.existing_count,
    )
    print(
        "NEW:",
        result.new_count,
    )
    print(
        "SUPPLEMENT:",
        result.supplement_count,
    )
    print(
        "ERROR:",
        result.error_count,
    )
    print()
    print()
    print(
        "SUPPLEMENT_ANSWER:",
        result.supplement_answer_count,
    )
    print(
        "SUPPLEMENT_VALUE:",
        result.supplement_answer_value_count,
    )
    print()
    print("ADATBÁZIS-ÍRÁS: 0 rekord")

def print_execution_result(
    execution_result,
) -> None:
    print("Batch létrehozva:",("IGEN" if execution_result.batch_created else "NEM"),)
    print()
    print("=" * 70)
    print("ADATBÁZIS-ÍRÁS EREDMÉNYE")
    print("=" * 70)
    print("Létrehozott submission:", execution_result.created_count,)
    print("Már létező submission:",execution_result.existing_count,)
    print("Létrehozott SUBMISSION_ANSWER:",execution_result.created_answer_count,)
    print("Létrehozott ANSWER_VALUE:",execution_result.created_answer_value_count,)

def print_supplement_execution_result(
    execution_result,
) -> None:
    print()
    print("=" * 70)
    print("SUPPLEMENT ÍRÁS EREDMÉNYE")
    print("=" * 70)
    print("Kiegészített submission:", execution_result.supplement_submission_count,)
    print("Létrehozott SUBMISSION_ANSWER:", execution_result.created_answer_count,)
    print("Létrehozott ANSWER_VALUE:", execution_result.created_answer_value_count,)

def print_supplement_verification_result(
    execution_result,
) -> None:
    print()
    print("=" * 70)
    print("SUPPLEMENT UTÓELLENŐRZÉS")
    print("=" * 70)

    if (execution_result.verification_error is not None
    ):
        print("ELLENŐRZÉS: HIBA")
        print("Ok:", execution_result.verification_error,)
        return

    verification = (execution_result.verification_result)
    if verification is None:
        print("ELLENŐRZÉS: NINCS EREDMÉNY")
        return

    print("Submissionök:", verification.submission_count,)
    print("SUBMISSION_ANSWER:", f"{verification.actual_answer_count}" " / "f"{verification.expected_answer_count}",)
    print(
        "ANSWER_VALUE:",
        f"{verification.actual_answer_value_count}"
        " / "
        f"{verification.expected_answer_value_count}",
    )

    print()

    for item in verification.items:
        print("submission_id:", item.submission_id,)

        print("SUBMISSION_ANSWER:",
            f"{item.actual_answer_count}"
            " / "
            f"{item.expected_answer_count}",
        )

        print(
            "ANSWER_VALUE:",
            f"{item.actual_answer_value_count}"
            " / "
            f"{item.expected_answer_value_count}",
        )

        print("parent:",
            (
                "OK"
                if item.parent_matches
                else "HIBÁS"
            ),
        )

        print("question_id:",
            (
                "OK"
                if item.question_ids_match
                else "HIBÁS"
            ),
        )

        print("values:",
            (
                "OK"
                if item.answer_values_match
                else "HIBÁS"
            ),
        )

        print("RESULT:",
            (
                "OK"
                if item.is_valid
                else "HIBÁS"
            ),
        )

    print()

    print("ELLENŐRZÉS:",
        (
            "SIKERES"
            if verification.is_valid
            else "HIBÁS"
        ),
    )

def main() -> int:
    args = parse_arguments()
    mode_name = "DRY-RUN"
    if args.rollback_test:
        mode_name = "ROLLBACK-TEST"
    elif args.execute_supplements:
        mode_name = "EXECUTE-SUPPLEMENTS"
    elif args.execute:
        mode_name = "EXECUTE"
    try:
        payload = load_payload(args.json_file)
        config = (SqlServerConfig.from_environment())
        connection_factory = (SqlServerConnectionFactory(config))
        submission_writer = MssqlSubmissionWriter(connection_factory)
        batch_writer = MssqlSubmissionBatchWriter(connection_factory)
        import_verifier = (MssqlSubmissionImportVerifier(connection_factory))
        import_writer = MssqlSubmissionImportWriter(
            connection_factory=connection_factory,
            batch_writer=batch_writer,
            submission_writer=submission_writer,
        )
        context_reader = MssqlSubmissionImportContextReader(connection_factory)
        orchestrator = SubmissionImportOrchestrator(
            context_reader=context_reader,
            submission_writer=submission_writer,
            import_writer=import_writer,
            import_verifier=import_verifier,
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
        if args.rollback_test:
            if (args.confirm_rollback!= "ROLLBACK"
            ):
                print()
                print("ROLLBACK TESZT MEGSZAKÍTVA")
                print("A --rollback-test használatához szükséges:")
                print("--confirm-rollback ROLLBACK")
                print()
                print("ADATBÁZIS-ÍRÁS: 0 rekord")

                return 2

            print()
            print("MÓD: ROLLBACK-TEST")
            print("Az SQL írási lánc lefut, de COMMIT nem történik.")

            execution_result = (orchestrator.execute_rollback(
                    payload=payload,
                    batch_id=args.batch_id,
                )
            )

            print_execution_result(execution_result)
            print()
            print("TRANZAKCIÓ EREDMÉNYE: ROLLBACK")
            print("TARTÓSAN MENTETT REKORD: 0")

            return 0
        if args.execute_supplements:
            if (args.confirm_supplements != "SUPPLEMENT"
            ):
                print()
                print("SUPPLEMENT ÍRÁS MEGSZAKÍTVA")
                print("Az --execute-supplements használatához szükséges:")
                print("--confirm-supplements SUPPLEMENT")
                print()
                print("ADATBÁZIS-ÍRÁS: 0 rekord")
                return 2
            print()
            print("MÓD: EXECUTE-SUPPLEMENTS")
            print("A validált supplementek atomikus mentése indul.")

            execution_result = (orchestrator.execute_supplements(
                    payload=payload,
                    batch_id=args.batch_id,
                )
            )
            print_supplement_execution_result(execution_result)
            print_supplement_verification_result(execution_result)
            if (execution_result.verification_succeeded is not True
            ):
                return 3
            return 0

        if not args.execute:
            return 0

        if args.confirm_write != "WRITE":
            print()
            print("ÍRÁS MEGSZAKÍTVA")
            print("Az --execute használatához szükséges:")
            print("--confirm-write WRITE")
            print()
            print("ADATBÁZIS-ÍRÁS: 0 rekord")
            return 2

        print()
        print("MÓD: EXECUTE")
        print("A validált batch mentése indul.")

        execution_result = (orchestrator.execute(
                payload=payload,
                batch_id=args.batch_id,
            )
        )

        print_execution_result(execution_result)
        print_verification_result(execution_result)

        if (execution_result.created_count > 0 and execution_result.verification_succeeded is not True
        ):
            return 3

        return 0

    except Exception as error:
        print()
        print(f"IMPORT {mode_name} HIBA")
        print(error)
        print("=" * 70)
        print()
        print("ADATBÁZIS-ÍRÁS: 0 rekord")

        return 1

def print_verification_result(
    execution_result,
) -> None:
    if execution_result.created_count == 0:
        print()
        print(
            "IMPORT UTÓELLENŐRZÉS: "
            "NEM SZÜKSÉGES"
        )
        print(
            "Nem jött létre új submission."
        )
        return

    if (
        execution_result.verification_error
        is not None
    ):
        print()
        print("=" * 70)
        print("IMPORT UTÓELLENŐRZÉS")
        print("=" * 70)
        print("ELLENŐRZÉS: HIBA")
        print(
            "Ok:",
            execution_result.verification_error,
        )
        return

    verification = (
        execution_result.verification_result
    )

    if verification is None:
        print()
        print("=" * 70)
        print("IMPORT UTÓELLENŐRZÉS")
        print("=" * 70)
        print(
            "ELLENŐRZÉS: NINCS EREDMÉNY"
        )
        return

    print()
    print("=" * 70)
    print("IMPORT UTÓELLENŐRZÉS")
    print("=" * 70)

    #
    # Existing batch + új submission:
    # exact submission verification.
    #
    if hasattr(
        verification,
        "items",
    ):
        print(
            "Típus: ÚJ SUBMISSION "
            "MEGLÉVŐ BATCHBEN"
        )

        print(
            "Ellenőrzött submission:",
            verification.submission_count,
        )

        print("SUBMISSION_ANSWER:",
            f"{verification.actual_answer_count}"
            " / "
            f"{verification.expected_answer_count}",
        )

        print(
            "ANSWER_VALUE:",
            f"{verification.actual_answer_value_count}"
            " / "
            f"{verification.expected_answer_value_count}",
        )

        print()

        for item in verification.items:
            print(
                "submission_id:",
                item.submission_id,
            )

            print(
                "  submission_exists:",
                (
                    "OK"
                    if item.submission_exists
                    else "HIBÁS"
                ),
            )

            print(
                "  parent:",
                (
                    "OK"
                    if item.parent_matches
                    else "HIBÁS"
                ),
            )

            print(
                "  SUBMISSION_ANSWER:",
                f"{item.actual_answer_count}"
                " / "
                f"{item.expected_answer_count}",
            )

            print(
                "  ANSWER_VALUE:",
                f"{item.actual_answer_value_count}"
                " / "
                f"{item.expected_answer_value_count}",
            )

            print(
                "  question_id:",
                (
                    "OK"
                    if item.question_ids_match
                    else "HIBÁS"
                ),
            )

            print(
                "  values:",
                (
                    "OK"
                    if item.answer_values_match
                    else "HIBÁS"
                ),
            )

            print(
                "  RESULT:",
                (
                    "OK"
                    if item.is_valid
                    else "HIBÁS"
                ),
            )

        print()

        print(
            "ELLENŐRZÉS:",
            (
                "SIKERES"
                if verification.is_valid
                else "HIBÁS"
            ),
        )

        return

    #
    # Teljesen új batch:
    # batch szintű verification.
    #
    print("Típus: ÚJ BATCH")

    print(
        "batch_id:",
        verification.batch_id,
    )

    print(
        "questionnaire:",
        verification.questionnaire_code,
    )

    print(
        "spec_version:",
        verification.spec_version,
    )

    print(
        "batch:",
        (
            "OK"
            if verification.batch_exists
            else "HIBÁS"
        ),
    )

    print(
        "questionnaire:",
        (
            "OK"
            if verification.questionnaire_matches
            else "HIBÁS"
        ),
    )

    print(
        "SUBMISSION:",
        f"{verification.actual_submission_count}"
        " / "
        f"{verification.expected_submission_count}",
    )

    print(
        "SUBMISSION_ANSWER:",
        f"{verification.actual_answer_count}"
        " / "
        f"{verification.expected_answer_count}",
    )

    print(
        "ANSWER_VALUE:",
        f"{verification.actual_answer_value_count}"
        " / "
        f"{verification.expected_answer_value_count}",
    )

    print()

    print(
        "ELLENŐRZÉS:",
        (
            "SIKERES"
            if verification.is_valid
            else "HIBÁS"
        ),
    )

if __name__ == "__main__":
    raise SystemExit(
        main()
    )