import json
from pathlib import Path

import pandas as pd


def read_dataset(
    file_path: Path,
) -> pd.DataFrame:

    extension = (
        file_path.suffix.lower()
    )

    if extension == ".csv":

        return pd.read_csv(
            file_path
        )

    if extension == ".xlsx":

        return pd.read_excel(
            file_path
        )

    if extension == ".json":

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return pd.DataFrame(data)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )