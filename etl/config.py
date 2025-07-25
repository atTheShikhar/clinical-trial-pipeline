import os
from sqlmesh.core.config import (
    Config,
    ModelDefaultsConfig,
    GatewayConfig,
    DuckDBConnectionConfig
)
from sqlmesh.core.config.connection import DuckDBAttachOptions


variables = {
    "raw_gcs_bucket": os.environ["RAW_GCS_BUCKET"]
}


class CustomDuckDBAttachOptions(DuckDBAttachOptions):
    metadata_schema: str | None # NOTE: MySQL specific custom option

    def to_sql(self, alias: str) -> str:
        options = []
        # 'duckdb' is actually not a supported type, but we'd like to allow it for
        # fully qualified attach options or integration testing, similar to duckdb-dbt
        if self.type not in ("duckdb", "ducklake", "motherduck"):
            options.append(f"TYPE {self.type.upper()}")
        if self.read_only:
            options.append("READ_ONLY")

        # DuckLake specific options
        path = self.path
        if self.type == "ducklake":
            if not path.startswith("ducklake:"):
                path = f"ducklake:{path}"
            if self.data_path is not None:
                options.append(f"DATA_PATH '{self.data_path}'")
            if self.encrypted:
                options.append("ENCRYPTED")
            if self.data_inlining_row_limit is not None:
                options.append(f"DATA_INLINING_ROW_LIMIT {self.data_inlining_row_limit}")

            if self.metadata_schema is not None: 
                options.append(f"METADATA_SCHEMA {self.metadata_schema}")

        options_sql = f" ({', '.join(options)})" if options else ""
        alias_sql = ""
        # TODO: Add support for Postgres schema. Currently adding it blocks access to the information_schema

        # MotherDuck does not support aliasing
        alias_sql = (
            f" AS {alias}" if not (self.type == "motherduck" or self.path.startswith("md:")) else ""
        )
        return f"ATTACH IF NOT EXISTS '{path}'{alias_sql}{options_sql}"


config = Config(
    variables=variables,
    model_defaults=ModelDefaultsConfig(dialect="duckdb", start="2000-01-01"),
    gateways={
        "duckdb": GatewayConfig(
            connection=DuckDBConnectionConfig(
                type="duckdb",
                extensions=["httpfs", "mysql", "ducklake"],
                secrets=[
                    {
                        "type": "gcs",
                        "key_id": os.environ['GCP_KEY_ID'],
                        "secret": os.environ['GCP_SECRET']
                    },
                    {
                        "type": "mysql",
                        "host": os.environ["MYSQL_HOST"],
                        "port": os.environ["MYSQL_TCP_PORT"],
                        "database": os.environ["MYSQL_DATABASE"],
                        "user": os.environ["MYSQL_USER"],
                        "password": os.environ["MYSQL_PWD"]
                    }
                ],
                catalogs={
                    "my_ducklake": CustomDuckDBAttachOptions(
                        type="ducklake",
                        path="mysql:",
                        data_path=os.environ["DUCKLAKE_GCS_BUCKET"],
                        # encrypted=False,
                        # data_inlining_row_limit=10,
                        metadata_schema=os.environ["MYSQL_DATABASE"]
                    ),
                }
            ),
            state_connection=DuckDBConnectionConfig(
                type="duckdb",
                database="state.db"
            )
        ),
    },
    default_gateway="duckdb",
    default_target_environment="dev"
)
