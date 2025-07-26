import duckdb
from src.settings import sm


def connect_db() -> duckdb.DuckDBPyConnection:
    if sm.is_prod():
        qry = f"""
            INSTALL httpfs;
            INSTALL ducklake;
            INSTALL mysql;
            LOAD httpfs;
            CREATE SECRET (
                TYPE gcs,
                KEY_ID '{sm.storage_access_id}',
                SECRET '{sm.storage_secret}'
            );
            CREATE SECRET (
                TYPE mysql,
                HOST '{sm.mysql_host}',
                PORT 3306,
                DATABASE '{sm.mysql_db}',
                USER '{sm.mysql_user}',
                PASSWORD '{sm.mysql_pass}'
            );
            ATTACH 'ducklake:mysql:' AS my_ducklake (DATA_PATH '{sm.storage_bucket}/trials', METADATA_SCHEMA '{sm.mysql_db}');
            ATTACH ':memory:' AS memory_db;
            USE my_ducklake;
        """
    else:
        qry = f"""
            ATTACH DATABASE 'local.duckdb' AS local_db;
            ATTACH ':memory:' AS memory_db;
            USE local_db;
        """
    conn = duckdb.execute(qry)
    return conn


def disconnect_db():
    duckdb.sql(
        """
        USE memory_db;
        DETACH DATABASE IF EXISTS my_ducklake;
        DETACH DATABASE IF EXISTS local_db;
        """
    )