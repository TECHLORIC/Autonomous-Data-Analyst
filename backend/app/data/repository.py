from pathlib import Path


class DatasetRepository:
    """
    Responsible only for locating datasets in storage.
    """

    def __init__(
        self,
        storage_dir: str = "storage/uploads",
    ) -> None:

        self.storage_dir = Path(storage_dir)

    def get_dataset_path(
        self,
        dataset_id: str,
    ) -> Path:

        matching_files = list(
            self.storage_dir.glob(
                f"{dataset_id}.*"
            )
        )

        if not matching_files:
            raise FileNotFoundError(
                f"Dataset '{dataset_id}' was not found."
            )

        if len(matching_files) > 1:
            raise RuntimeError(
                f"Multiple files found for dataset "
                f"'{dataset_id}'."
            )

        return matching_files[0]

    def exists(
        self,
        dataset_id: str,
    ) -> bool:

        return any(
            self.storage_dir.glob(
                f"{dataset_id}.*"
            )
        )