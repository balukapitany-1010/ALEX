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
    text = str(value).strip()
    return text or None

def normalize_business_identifier(
    value,
) -> str:
    text = optional_text(value)
    if text is None:
        return ""
    return "".join(character for character in text.upper() if character.isalnum())

def main() -> None:
    if len(sys.argv) != 3:
        print("Használat:")
        print(
            "python "
            "scripts\\check_mssql_submission_raw_payload.py "
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
        data = json.load(handle)

    submissions = data.get("submissions")

    if not isinstance(
        submissions,
        list,
    ):
        raise ValueError(
            "submissions nem lista"
        )
    config = (SqlServerConfig.from_environment())
    factory = (SqlServerConnectionFactory(config))
    connection = factory.connect()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                s.submission_id,
                supplier.tax_number,
                s.raw_payload
            FROM dbo.SUBMISSION s

            INNER JOIN dbo.SUPPLY_CHAIN_RELATION r
                ON r.relation_id = s.relation_id

            INNER JOIN dbo.COMPANY supplier
                ON supplier.company_key =
                   r.supplier_company_key

            WHERE s.batch_id = ?

            ORDER BY
                s.submission_id
            """,
            batch_id,
        )

        db_rows_by_tax = defaultdict(list)
        for row in cursor.fetchall():
            supplier_tax = (normalize_business_identifier(row[1]))
            db_rows_by_tax[supplier_tax].append(
                (
                    int(row[0]),
                    row[2],
                )
            )

    finally:
        connection.close()


    print()
    print("SUBMISSION RAW_PAYLOAD CHECK")
    print("=" * 70)
    print("Fájl:",json_file,)
    print("batch_id:",batch_id,)
    print("Submission darabszám:",len(submissions),)
    print()
    equal_count = 0
    different_count = 0
    error_count = 0
    requester_equal_count = 0



    for index, submission in enumerate(
        submissions,
        start=1,
    ):
        response = (submission.get("response") or {})
        cover = (response.get("cover" )or {})
        supplier = (cover.get("supplier") or {})
        supplier_tax = (normalize_business_identifier(supplier.get("tax_number")))
        print( "-" * 70)
        print(
            f"[{index}] "
            f"supplier tax: {supplier_tax}"
        )
        matches = db_rows_by_tax.get(
            supplier_tax,
            [],
        )

        if len(matches) != 1:
            error_count += 1

            print(
                "HIBA: adatbázis-egyezések:",
                len(matches),
            )

            continue
        (
            submission_id,
            raw_payload,
        ) = matches[0]

        print("submission_id:",submission_id,)
        if raw_payload is None:
            error_count += 1

            print("HIBA: raw_payload NULL")

            continue
        try:
            db_payload = json.loads(raw_payload)

        except (
            json.JSONDecodeError,
            TypeError,
        ) as error:
            error_count += 1

            print(
                "  HIBA: raw_payload "
                "nem érvényes JSON:",
                error,
            )
            continue

        if not isinstance(
            db_payload,
            dict,
        ):
            error_count += 1

            print(
                "  HIBA: DB raw_payload "
                "nem objektum"
            )

            continue

        json_keys = set(submission.keys())
        db_keys = set(db_payload.keys())
        json_only = sorted(json_keys - db_keys)
        db_only = sorted(db_keys - json_keys)
        common_keys = sorted(json_keys & db_keys)
        changed_common_keys = [
            key
            for key in common_keys
            if (
                submission.get(key) != db_payload.get(key)
            )
        ]

        exact_equal = (submission == db_payload)

        response_equal = (submission.get("response") == db_payload.get("response"))
        json_requester = ((submission.get("response")or {}).get( "cover",{}).get("requester"))

        db_top_level_requester = (db_payload.get("requester"))

        requester_equal = (json_requester == db_top_level_requester)
        if requester_equal:
            requester_equal_count += 1

        print("  teljes payload egyezik:",exact_equal,)
        print(
            "top-level requester "
            "egyezik cover.requester-rel:",
            requester_equal,
        )

        print("response egyezik:",response_equal,)
        print("csak JSON-ban:",json_only,)
        print("csak DB-ben:",db_only,)
        print("  eltérő közös top-level mezők:",changed_common_keys,)
        print("JSON supplier_key:",submission.get("supplier_key"),)
        print("  DB supplier_key:",db_payload.get("supplier_key"),)
        print("DB top-level requester:",
            (
                "VAN"
                if "requester" in db_payload
                else "NINCS"
            ),
        )

        if exact_equal:
            equal_count += 1
        else:
            different_count += 1

    print()
    print("=" * 70)
    print("ÖSSZESÍTÉS")
    print("=" * 70)
    print(
        "Pontosan egyező payload:",
        equal_count,
    )

    print(
        "Eltérő payload:",
        different_count,
    )

    print(
        "requester pontos másolat:",
        requester_equal_count,
    )

    print(
        "Hiba:",
        error_count,
    )
    print()
    print("ADATBÁZIS-ÍRÁS: 0 rekord")


if __name__ == "__main__":
    main()