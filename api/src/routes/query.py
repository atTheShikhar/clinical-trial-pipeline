import duckdb
from fastapi import APIRouter, Request

from src.auth import APIKey
from src.handlers.query import run_query
from src.models import QueryRequestBody, QueryResponseBody


queryRouter = APIRouter(prefix="/query", tags=["Query Routes"])


@queryRouter.post("", response_model=QueryResponseBody)
async def query_database(
    request: Request,
    body: QueryRequestBody,
    _: APIKey
):
    db_conn: duckdb.DuckDBPyConnection = request.app.state.db_conn
    resp = run_query(db_conn, body.sql)
    return {"results": resp}

    