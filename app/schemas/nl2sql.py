from typing import Any

from pydantic import BaseModel, Field


class NL2SQLQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class NL2SQLQueryResponse(BaseModel):
    question: str
    sql: str
    rows: list[dict[str, Any]]
    answer: str
