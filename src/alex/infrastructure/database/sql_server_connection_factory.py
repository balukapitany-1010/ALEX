import pyodbc

from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)


class SqlServerConnectionFactory:
    def __init__(
        self,
        config: SqlServerConfig,
    ) -> None:
        if not isinstance(
            config,
            SqlServerConfig,
        ):
            raise TypeError(
                "config must be a SqlServerConfig"
            )

        self._config = config

    @property
    def config(
        self,
    ) -> SqlServerConfig:
        return self._config

    def build_connection_string(
        self,
    ) -> str:
        trust_server_certificate = (
            "yes"
            if self._config.trust_server_certificate
            else "no"
        )

        return (
            f"DRIVER={{{self._config.driver}}};"
            f"SERVER={self._config.server};"
            f"DATABASE={self._config.database};"
            f"UID={self._config.username};"
            f"PWD={self._config.password};"
            "Encrypt=yes;"
            f"TrustServerCertificate="
            f"{trust_server_certificate};"
        )

    def connect(
        self,
    ) -> pyodbc.Connection:
        return pyodbc.connect(
            self.build_connection_string()
        )