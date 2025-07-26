import logging
import json
import duckdb
from fastapi import HTTPException
from src.settings import sm


logger = logging.getLogger(__name__)


def run_query(conn: duckdb.DuckDBPyConnection ,qry: str):
    if sm.is_prod():
        db = f"read_parquet('{sm.storage_bucket}/trials/*/*/*.parquet')" 
        qry = qry.replace("ducklake", db)
    try:
        conn.execute(f"EXPLAIN {qry}")
    except Exception as e:
        logger.error(e)
        raise HTTPException(400, "Invalid SQL query provided!")

    df = conn.sql(qry).df()
    json_str = df.to_json()
    # print(json_str)
    return json.loads(json_str)