from typing import Any

from pydantic import BaseModel


class QueryRequest(BaseModel):
    dataset_id: str
    query: str


class QueryResponse(BaseModel):
    dataset_id: str
    query: str
    rows: list[dict[str, Any]]