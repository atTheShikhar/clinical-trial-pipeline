import logging
import json
import pandas as pd
import numpy as np
import duckdb
from datetime import datetime
from fastapi import HTTPException
from src.settings import sm


logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()

        return super(CustomJSONEncoder, self).default(obj)




def run_query(conn: duckdb.DuckDBPyConnection ,qry: str):
    if sm.is_prod():
        db = f"read_parquet('{sm.storage_bucket}/*/*/*.parquet')" 
    else:
        db = "t1"

    qry = qry.replace("ducklake", db)
    try:
        conn.execute(f"EXPLAIN {qry}")
    except Exception as e:
        logger.error(e)
        raise HTTPException(400, "Invalid SQL query provided!")

    df = conn.sql(qry).df()
    result = df.to_dict('records')
    print(result)
    json_result = json.dumps(result, cls=CustomJSONEncoder, indent=4)
    print(json_result)
    return json.loads(json_result)
