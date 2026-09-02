from dataclasses import dataclass
import os


@dataclass(frozen=True)
class SqlServerConfig:
    server: str
    database: str
    username: str
    password: str
    driver: str = "ODBC Driver 18 for SQL Server"
    trust_server_certificate: bool = True

    @classmethod
    def from_environment(
        cls,
    ) -> "SqlServerConfig":
        server = os.getenv(
            "ALEX_DB_SERVER",
            "",
        ).strip()

        database = os.getenv(
            "ALEX_DB_DATABASE",
            "",
        ).strip()

        username = os.getenv(
            "ALEX_DB_USERNAME",
            "",
        ).strip()

        password = os.getenv(
            "ALEX_DB_PASSWORD",
            "",
        )

        driver = os.getenv(
            "ALEX_DB_DRIVER",
            "ODBC Driver 18 for SQL Server",
        ).strip()

        if not server:
            raise ValueError(
                "ALEX_DB_SERVER is required"
            )

        if not database:
            raise ValueError(
                "ALEX_DB_DATABASE is required"
            )

        if not username:
            raise ValueError(
                "ALEX_DB_USERNAME is required"
            )

        if not password:
            raise ValueError(
                "ALEX_DB_PASSWORD is required"
            )

        if not driver:
            raise ValueError(
                "ALEX_DB_DRIVER cannot be empty"
            )

        return cls(
            server=server,
            database=database,
            username=username,
            password=password,
            driver=driver,
        )