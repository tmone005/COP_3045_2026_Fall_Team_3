
import pandas as pd


def calculate_summary(data: pd.DataFrame) -> dict:
    """Calculate the main crash statistics."""
    if data.empty:
        raise ValueError("Cannot analyze an empty dataset.")

    return {
        "total_crashes": len(data),
        "total_injuries": int(data["TOTAL_INJURIES"].sum()),
        "average_injuries": float(data["TOTAL_INJURIES"].mean()),
        "average_speed_limit": float(
            data["POSTED_SPEED_LIMIT"].mean()
        ),
        "average_vehicles": float(data["NUM_VEHICLES"].mean()),
    }


def analyze_categories(data: pd.DataFrame) -> dict:
    """Count crashes by weather, lighting, and crash type."""
    columns = {
        "weather": "WEATHER_CONDITION",
        "lighting": "LIGHTING_CONDITION",
        "crash_type": "FIRST_CRASH_TYPE",
    }

    results = {}

    for name, column in columns.items():
        results[name] = (
            data[column]
            .value_counts()
            .rename_axis(column)
            .reset_index(name="CRASH_COUNT")
        )

    return results


def analyze_injuries(data: pd.DataFrame) -> dict:
    """Calculate average injuries for different conditions."""
    columns = {
        "weather_injuries": "WEATHER_CONDITION",
        "lighting_injuries": "LIGHTING_CONDITION",
        "vehicle_injuries": "NUM_VEHICLES",
    }

    results = {}

    for name, column in columns.items():
        results[name] = (
            data.groupby(column)["TOTAL_INJURIES"]
            .mean()
            .reset_index(name="AVERAGE_INJURIES")
        )

    return results


def analyze_time(data: pd.DataFrame) -> dict:
    """Count crashes by hour and month when dates are available."""
    results = {}

    if "CRASH_HOUR" in data.columns:
        results["hour"] = (
            data["CRASH_HOUR"]
            .value_counts()
            .sort_index()
            .rename_axis("CRASH_HOUR")
            .reset_index(name="CRASH_COUNT")
        )

    if "CRASH_MONTH" in data.columns:
        results["month"] = (
            data["CRASH_MONTH"]
            .value_counts()
            .sort_index()
            .rename_axis("CRASH_MONTH")
            .reset_index(name="CRASH_COUNT")
        )

    return results


def analyze_speed(data: pd.DataFrame) -> pd.DataFrame:
    """Count crashes by posted speed limit."""
    return (
        data["POSTED_SPEED_LIMIT"]
        .value_counts()
        .sort_index()
        .rename_axis("POSTED_SPEED_LIMIT")
        .reset_index(name="CRASH_COUNT")
    )
