
from pathlib import Path
import pandas as pd


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """Load a CSV file and check that it contains data."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Data file not found: {path}"
        )

    try:
        data = pd.read_csv(path, low_memory=False)
    except (OSError, pd.errors.ParserError) as error:
        raise ValueError(
            f"Could not read CSV file: {path}"
        ) from error

    if data.empty:
        raise ValueError(f"CSV file is empty: {path}")

    return data


def load_datasets(
    data_directory: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the Chicago crashes and vehicles datasets."""
    directory = Path(data_directory)

    crashes = load_csv(directory / "Crashes.csv")
    vehicles = load_csv(directory / "Vehicles.csv")

    required_column = "CRASH_RECORD_ID"

    for name, dataset in [
        ("Crashes", crashes),
        ("Vehicles", vehicles),
    ]:
        if required_column not in dataset.columns:
            raise ValueError(
                f"{name} dataset is missing {required_column}"
            )

    return crashes, vehicles
