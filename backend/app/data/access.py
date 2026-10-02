from pathlib import Path

import pandas as pd

from app.data.ingestion.service import read_dataset
from app.data.repository import DatasetRepository


class DatasetAccess:
    """
    Provides a clean interface for loading datasets.

    Agents should use this service instead of directly
    accessing storage paths.
    """

    def __init__(self) -> None:

        self.repository = DatasetRepository()

    def get_path(
        self,
        dataset_id: str,
    ) -> Path:

        return self.repository.get_dataset_path(
            dataset_id
        )

    def load_dataframe(
        self,
        dataset_id: str,
        file_path: str = "",
    ) -> pd.DataFrame:

        if file_path:
            path = Path(file_path)
        else:
            path = self.get_path(dataset_id)

        return read_dataset(path)

    def exists(
        self,
        dataset_id: str,
    ) -> bool:

        return self.repository.exists(
            dataset_id
        )