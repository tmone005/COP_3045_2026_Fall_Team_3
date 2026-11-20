
"""Clean and combine Chicago traffic crash datasets."""

import pandas as pd


def clean_crashes(crashes: pd.DataFrame) -> pd.DataFrame:
    """Clean crash records and prepare important columns."""

    required = {
        "CRASH_RECORD_ID",
        "INJURIES_TOTAL",
        "POSTED_SPEED_LIMIT",
        "WEATHER_CONDITION",
        "LIGHTING_CONDITION",
        "FIRST_CRASH_TYPE",
    }

    missing = required - set(crashes.columns)

    if missing:
        raise ValueError(f"Missing crash columns: {sorted(missing)}")

    data = crashes.copy()

    # Match the new Chicago dataset column to our project code.
    data = data.rename(
        columns={"INJURIES_TOTAL": "TOTAL_INJURIES"}
    )

    # Remove records without a crash ID and duplicate crashes.
    data = data.dropna(subset=["CRASH_RECORD_ID"])
    data = data.drop_duplicates(subset=["CRASH_RECORD_ID"])

    # Convert numeric columns.
    for column in ["TOTAL_INJURIES", "POSTED_SPEED_LIMIT"]:
        data[column] = pd.to_numeric(
            data[column], errors="coerce"
        )

    # Handle missing or negative injury values.
    data["TOTAL_INJURIES"] = (
        data["TOTAL_INJURIES"].fillna(0).clip(lower=0)
    )

    # Handle missing category values.
    for column in [
        "WEATHER_CONDITION",
        "LIGHTING_CONDITION",
        "FIRST_CRASH_TYPE",
    ]:
        data[column] = data[column].fillna("UNKNOWN")

    return data


def clean_vehicles(vehicles: pd.DataFrame) -> pd.DataFrame:
    """Count the number of vehicles involved in each crash."""

    if "CRASH_RECORD_ID" not in vehicles.columns:
        raise ValueError(
            "Vehicles dataset is missing CRASH_RECORD_ID"
        )

    data = vehicles.copy()

    data = data.dropna(subset=["CRASH_RECORD_ID"])

    if "CRASH_UNIT_ID" in data.columns:
        data = data.drop_duplicates(subset=["CRASH_UNIT_ID"])
    else:
        data = data.drop_duplicates()

    counts = (
        data.groupby("CRASH_RECORD_ID")
        .size()
        .reset_index(name="NUM_VEHICLES")
    )

    return counts


def merge_datasets(
    crashes: pd.DataFrame,
    vehicle_counts: pd.DataFrame,
) -> pd.DataFrame:
    """Merge crash records with vehicle counts."""

    merged = crashes.merge(
        vehicle_counts,
        on="CRASH_RECORD_ID",
        how="left",
        validate="one_to_one",
    )

    merged["NUM_VEHICLES"] = (
        merged["NUM_VEHICLES"].fillna(0).astype(int)
    )

    return merged
