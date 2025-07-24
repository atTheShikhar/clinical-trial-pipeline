import logging
import json
import duckdb
from fastapi import HTTPException
from src.settings import sm


logger = logging.getLogger(__name__)



def configure_ducklake():
    duckdb.sql("INSTALL ducklake;")
    duckdb.sql(f"ATTACH 'ducklake:metadata.ducklake' AS my_ducklake (DATA_PATH '{sm.storage_bucket}/trials');")
    duckdb.sql("USE my_ducklake;")


def configure_cloud_storage():
    duckdb.sql("INSTALL httpfs;")
    duckdb.sql("LOAD httpfs;")
    duckdb.sql(
        f"""
            CREATE SECRET (
                TYPE gcs,
                KEY_ID '{sm.storage_access_id}',
                SECRET '{sm.storage_secret}'
            );
        """
    )


def configure_duckdb():
    configure_cloud_storage()
    configure_ducklake()


def run_query(qry: str):
    try:
        qry = qry.replace("ducklake", f"read_parquet('{sm.storage_bucket}/trials/*/*/*.parquet', hive_partitioning=true)" )
        df = duckdb.sql(qry).df()
        json_str = df.to_json()
        return json.loads(json_str)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Something went wrong!")