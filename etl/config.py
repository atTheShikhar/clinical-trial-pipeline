import os
from dotenv import load_dotenv
from sqlmesh.core.config import (
    Config,
    ModelDefaultsConfig,
    GatewayConfig,
    DuckDBConnectionConfig
)
from sqlmesh.core.config.connection import DuckDBAttachOptions


load_dotenv()

variables = {
    "raw_gcs_bucket": os.environ["RAW_GCS_BUCKET"]
}


#NOTE: Extended the library specific class to add support for previously unsupported options
# metadata_schema is used in case the duckdb metadata table is already created by another ducklake instance
class CustomDuckDBAttachOptions(DuckDBAttachOptions):
    metadata_schema: str | None = None # NOTE: MySQL specific custom option

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

        # MotherDuck does not support aliasing
        alias_sql = (
            f" AS {alias}" if not (self.type == "motherduck" or self.path.startswith("md:")) else ""
        )
        attach_qry = f"ATTACH IF NOT EXISTS '{path}'{alias_sql}{options_sql}"
        return attach_qry


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
                    ),
                }
            ),
            state_connection=DuckDBConnectionConfig(
                type="duckdb",
                database="state.db"
            ),
            test_connection=DuckDBConnectionConfig(
                type="duckdb",
                database="test.db"
            )
        ),
    },
    default_gateway="duckdb",
    default_target_environment="dev"
)
