from typing import Any

from pydantic import BaseModel


class DatasetProfileResponse(BaseModel):
    dataset_id: str
    rows: int
    columns: int
    column_names: list[str]
    columns_info: dict[str, Any]
    duplicate_rows: int