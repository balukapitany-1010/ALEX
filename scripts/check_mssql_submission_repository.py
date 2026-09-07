from collections import Counter

from alex.esg.repositories.mssql_submission_repository import (
    MssqlSubmissionRepository,
)
from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)
from alex.infrastructure.database.sql_server_connection_factory import (
    SqlServerConnectionFactory,
)


def main() -> None:
    config = (
        SqlServerConfig.from_environment()
    )

    connection_factory = (
        SqlServerConnectionFactory(
            config
        )
    )

    repository = (
        MssqlSubmissionRepository(
            connection_factory
        )
    )

    print()
    print(
        "MSSQL beküldések beolvasása..."
    )

    submissions = (
        repository.list_all()
    )

    print()
    print(
        f"Betöltött beküldések száma: "
        f"{len(submissions)}"
    )

    status_counts = Counter(
        submission.status.value
        for submission in submissions
    )

    print()
    print("Státuszok:")

    for status, count in sorted(
        status_counts.items()
    ):
        print(
            f"  {status}: {count}"
        )

    with_period = sum(
        1
        for submission in submissions
        if submission.period is not None
    )

    without_period = (
        len(submissions)
        - with_period
    )

    print()
    print(
        f"Időszakkal:      "
        f"{with_period}"
    )

    print(
        f"Időszak nélkül:  "
        f"{without_period}"
    )

    print()
    print(
        "Első 20 beküldés:"
    )

    print(
        "-" * 120
    )

    for submission in submissions[:20]:
        requester = (
            submission
            .relation
            .requester
            .name
        )

        supplier = (
            submission
            .relation
            .supplier
            .name
        )

        questionnaire = (
            f"{submission.questionnaire.questionnaire_code} "
            f"{submission.questionnaire.spec_version}"
        )

        period = (
            submission.period
            or "-"
        )

        print(
            f"{submission.submission_id}"
            f" | {requester}"
            f" | {supplier}"
            f" | {questionnaire}"
            f" | {period}"
            f" | {submission.status.value}"
        )

    if submissions:
        first_submission_id = (
            submissions[0]
            .submission_id
        )

        print()
        print(
            "get_by_id ellenőrzés:"
        )

        found = (
            repository.get_by_id(
                first_submission_id
            )
        )

        if found is None:
            print(
                "HIBA: a beküldés "
                "nem található."
            )
        else:
            print(
                f"OK: "
                f"{found.submission_id}"
                f" | "
                f"{found.relation.supplier.name}"
            )

    print()
    print(
        "Ellenőrzés befejezve."
    )


if __name__ == "__main__":
    main()