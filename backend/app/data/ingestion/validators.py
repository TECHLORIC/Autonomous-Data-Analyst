from pathlib import Path


ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".json",
}

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


def validate_file(
    filename: str,
    file_size: int,
    max_file_size: int = MAX_FILE_SIZE,
) -> None:
    if not filename or Path(filename).name != filename:
        raise ValueError("Filename must not contain a path.")

    if file_size <= 0:
        raise ValueError("File must not be empty.")

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    if file_size > max_file_size:
        raise ValueError(
            f"File is too large. Maximum allowed size is "
            f"{max_file_size // (1024 * 1024)} MB."
        )
