from typing import Any

import pandas as pd


def _safe_value(value: Any) -> Any:

    if pd.isna(value):
        return None

    if hasattr(value, "item"):

        try:
            return value.item()

        except (ValueError, TypeError):
            pass

    return value


def detect_datetime_format(
    series: pd.Series,
) -> str | None:

    sample = series.dropna().astype(str).head(100)

    if sample.empty:
        return None

    formats = [
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%m-%d-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
    ]

    for date_format in formats:

        parsed = pd.to_datetime(
            sample,
            format=date_format,
            errors="coerce",
        )

        valid_ratio = parsed.notna().mean()

        if valid_ratio >= 0.8:
            return date_format

    return None


def detect_column_type(
    series: pd.Series,
) -> tuple[str, str | None]:

    if pd.api.types.is_numeric_dtype(series):
        return "numeric", None

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime", None

    if pd.api.types.is_bool_dtype(series):
        return "boolean", None

    if series.dtype == "object":

        detected_format = detect_datetime_format(
            series
        )

        if detected_format:

            return (
                "datetime",
                detected_format,
            )

    return "categorical", None


def profile_dataframe(
    df: pd.DataFrame,
) -> dict[str, Any]:

    columns = {}

    datetime_columns = []

    numeric_columns = []

    categorical_columns = []

    for column in df.columns:

        series = df[column]

        detected_type, date_format = (
            detect_column_type(series)
        )

        column_info = {
            "dtype": str(series.dtype),
            "detected_type": detected_type,
            "missing": int(
                series.isna().sum()
            ),
            "missing_percentage": round(
                float(
                    series.isna().mean() * 100
                ),
                2,
            ),
            "unique": int(
                series.nunique(
                    dropna=True
                )
            ),
        }

        if date_format:

            column_info[
                "date_format"
            ] = date_format

        if detected_type == "numeric":

            column_info.update(
                {
                    "min": _safe_value(
                        series.min()
                    ),
                    "max": _safe_value(
                        series.max()
                    ),
                    "mean": _safe_value(
                        series.mean()
                    ),
                    "median": _safe_value(
                        series.median()
                    ),
                    "std": _safe_value(
                        series.std()
                    ),
                }
            )

            numeric_columns.append(
                str(column)
            )

        elif detected_type == "datetime":

            datetime_columns.append(
                str(column)
            )

        elif detected_type == "categorical":

            categorical_columns.append(
                str(column)
            )

            # Expose exact category values so SQL filters use real labels
            # (e.g. 'Returned' rather than a guessed 'Return').
            if column_info["unique"] <= 25:
                column_info["top_values"] = [
                    str(v)
                    for v in series.dropna().value_counts().head(25).index
                ]

        columns[str(column)] = column_info

    return {
        "rows": int(len(df)),

        "columns": int(
            len(df.columns)
        ),

        "column_names": [
            str(column)
            for column in df.columns
        ],

        "columns_info": columns,

        "numeric_columns": numeric_columns,

        "datetime_columns": datetime_columns,

        "categorical_columns": (
            categorical_columns
        ),

        "duplicate_rows": int(
            df.duplicated().sum()
        ),
    }