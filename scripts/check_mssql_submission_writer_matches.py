from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory


BATCH_ID = ("BATCH_11107792244_20260507135421")

def main() -> None:
    config = (SqlServerConfig.from_environment())
    factory = (SqlServerConnectionFactory(config))
    connection = factory.connect()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                s.submission_id,
                s.batch_id,
                s.relation_id,
                s.external_supplier_key,
                s.respondent_id,
                s.respondent_mp_id,
                supplier.tax_number,
                supplier.company_key
            FROM dbo.SUBMISSION s

            JOIN dbo.SUPPLY_CHAIN_RELATION r
                ON r.relation_id =
                   s.relation_id

            JOIN dbo.COMPANY supplier
                ON supplier.company_key =
                   r.supplier_company_key

            WHERE s.batch_id = ?

            ORDER BY
                s.relation_id,
                s.submission_id
            """,
            BATCH_ID,
        )

        rows = cursor.fetchall()

        print()
        print("MSSQL SUBMISSION WRITER MATCH PRECHECK")
        print("=" * 70)
        print("Batch:",BATCH_ID,)
        print("Submission darabszám:",len(rows),)
        print()

        invalid_count = 0

        for row in rows:
            submission_id = int(row[0])
            relation_id = int(row[2])
            external_supplier_key = str(row[3]).strip()
            respondent_id = str(row[4]).strip()
            respondent_mp_id = row[5]
            supplier_tax = str(row[6]).strip()
            supplier_key = str(row[7]).strip()
            expected_external_supplier_key = (f"SUP_{supplier_tax}")

            respondent_ok = (respondent_id.startswith(f"RESP_{supplier_tax}_"))
            supplier_key_ok = (external_supplier_key == expected_external_supplier_key)
            match_ok = (respondent_ok and supplier_key_ok)
            if not match_ok:
                invalid_count += 1

            print(f"submission_id={submission_id}")
            print(f"  relation_id: {relation_id}")
            print(f"  supplier tax: {supplier_tax}")
            print("  external_supplier_key:",external_supplier_key,)
            print("  respondent_id:",respondent_id,)
            print("  respondent_mp_id:", respondent_mp_id,)
            print(
                "  MATCH:",
                "OK"
                if match_ok
                else "HIBÁS",
            )

            print()
        print("=" * 70)
        print("ÖSSZESÍTÉS")
        print("=" * 70)
        print("Submissionök:",len(rows),)
        print("Writer kulccsal kompatibilis:",len(rows) - invalid_count,)
        print("Eltérés:", invalid_count,)
        print()
        print("ADATBÁZIS-ÍRÁS: 0 rekord")

    finally:
        connection.close()


if __name__ == "__main__":
    main()