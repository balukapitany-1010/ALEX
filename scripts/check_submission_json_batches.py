import json
from pathlib import Path

from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)
from alex.infrastructure.database.sql_server_connection_factory import (
    SqlServerConnectionFactory,
)


DOWNLOADS = (
    Path.home()
    / "Downloads"
)


def optional_text(
    value,
) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    return text or None


def main() -> int:
    config = (
        SqlServerConfig.from_environment()
    )

    connection_factory = (
        SqlServerConnectionFactory(
            config
        )
    )

    connection = (
        connection_factory.connect()
    )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                b.batch_id,
                COUNT(s.submission_id)
            FROM dbo.SUBMISSION_BATCH AS b
            LEFT JOIN dbo.SUBMISSION AS s
                ON s.batch_id = b.batch_id
            WHERE b.questionnaire_code = ?
              AND b.spec_version = ?
            GROUP BY
                b.batch_id
            """,
            "SZTFH",
            "2.0",
        )

        existing_batches = {
            str(row[0]).strip(): int(row[1])
            for row in cursor.fetchall()
        }

        files = sorted(
            DOWNLOADS.rglob("*.json")
        )

        results = []

        for file_path in files:
            try:
                with file_path.open(
                    "r",
                    encoding="utf-8-sig",
                ) as handle:
                    payload = json.load(
                        handle
                    )

                if not isinstance(
                    payload,
                    dict,
                ):
                    continue

                spec_version = (
                    optional_text(
                        payload.get(
                            "spec_version"
                        )
                    )
                )

                if spec_version != "2.0":
                    continue

                submissions = (
                    payload.get(
                        "submissions"
                    )
                )

                if not isinstance(
                    submissions,
                    list,
                ):
                    continue

                if not submissions:
                    continue

                first_submission = (
                    submissions[0]
                )

                if not isinstance(
                    first_submission,
                    dict,
                ):
                    continue

                response = (
                    first_submission.get(
                        "response"
                    )
                    or {}
                )

                survey_type = (
                    optional_text(
                        response.get(
                            "survey_type"
                        )
                    )
                    or "SZTFH"
                )

                if survey_type != "SZTFH":
                    continue

                batch_id = optional_text(
                    payload.get(
                        "batch_id"
                    )
                )

                if batch_id is None:
                    status = "NO BATCH ID"
                    db_submission_count = None

                elif (
                    batch_id
                    in existing_batches
                ):
                    status = "EXISTING"
                    db_submission_count = (
                        existing_batches[
                            batch_id
                        ]
                    )

                else:
                    status = "NEW"
                    db_submission_count = 0

                results.append(
                    (
                        status,
                        batch_id,
                        len(submissions),
                        db_submission_count,
                        file_path,
                    )
                )
            except (
                    OSError,
                    json.JSONDecodeError,
                    UnicodeDecodeError,
            ):
                continue

        order = {
            "NEW": 0,
            "NO BATCH ID": 1,
            "EXISTING": 2,
        }

        results.sort(
            key=lambda item: (
                order.get(
                    item[0],
                    99,
                ),
                str(
                    item[4]
                ).lower(),
            )
        )

        print()
        print(
            "SZTFH 2.0 JSON BATCH ELLENŐRZÉS"
        )
        print(
            "=" * 100
        )

        new_count = 0

        for (
            status,
            batch_id,
            json_submission_count,
            db_submission_count,
            file_path,
        ) in results:
            if status == "NEW":
                new_count += 1

            print()
            print(
                "STATUS:",
                status,
            )
            print(
                "batch_id:",
                batch_id or "HIÁNYZIK",
            )
            print(
                "JSON submission:",
                json_submission_count,
            )

            if (
                db_submission_count
                is not None
            ):
                print(
                    "DB submission:",
                    db_submission_count,
                )

            print(
                "Fájl:",
                file_path,
            )

        print()
        print(
            "=" * 100
        )
        print(
            "NEW batch jelöltek:",
            new_count,
        )
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