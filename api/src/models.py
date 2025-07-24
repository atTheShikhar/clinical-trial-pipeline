from typing import Any
from pydantic import BaseModel


class QueryRequestBody(BaseModel):
    sql: str


class QueryResponseBody(BaseModel):
    results: dict[str, Any] | list[Any] | None
