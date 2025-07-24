from fastapi import APIRouter

from src.handlers.query import run_query
from src.models import QueryRequestBody, QueryResponseBody


queryRouter = APIRouter(prefix="/query", tags=["Query Routes"])


@queryRouter.post("", response_model=QueryResponseBody)
async def query_database(
    req: QueryRequestBody
):
    resp = run_query(req.sql)
    return {"results": resp}

    