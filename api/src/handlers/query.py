import logging
import json
import duckdb
from fastapi import HTTPException
from src.settings import sm


logger = logging.getLogger(__name__)


def configure_duckdb():
    duckdb.sql(
        f"""
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
            HOST '{sm.mysql_db}',
            PORT 3306,
            DATABASE '{sm.mysql_db}',
            USER '{sm.mysql_user}',
            PASSWORD '{sm.mysql_pass}'
        );
        ATTACH 'ducklake:mysql:' AS my_ducklake (DATA_PATH '{sm.storage_bucket}/trials');
        USE my_ducklake;
        """
    )


def run_query(qry: str):
    try:
        qry = qry.replace("ducklake", f"read_parquet('{sm.storage_bucket}/trials/*/*/*.parquet', hive_partitioning=true)" )
        df = duckdb.sql(qry).df()
        json_str = df.to_json()
        return json.loads(json_str)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Something went wrong!")