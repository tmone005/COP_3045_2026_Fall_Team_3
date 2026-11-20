
"""Create charts for the Chicago traffic crash report."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def save_chart(output_path: Path) -> None:
    """Save the chart as an image."""
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def create_bar_chart(
    data: pd.DataFrame,
    category: str,
    value: str,
    title: str,
    output_path: Path,
    horizontal: bool = False,
) -> None:
    """Create a bar chart."""
    if data.empty:
        return

    labels = data[category].astype(str)
    values = data[value]

    plt.figure(figsize=(11, 6))

    if horizontal:
        plt.barh(labels, values)
        plt.gca().invert_yaxis()
        plt.xlabel(value.replace("_", " ").title())
    else:
        plt.bar(labels, values)
        plt.ylabel(value.replace("_", " ").title())
        plt.xticks(rotation=30, ha="right")

    plt.title(title)
    save_chart(output_path)


def create_line_chart(
    data: pd.DataFrame,
    x_column: str,
    title: str,
    output_path: Path,
) -> None:
    """Create a line chart."""
    if data.empty:
        return

    plt.figure(figsize=(11, 6))
    plt.plot(
        data[x_column],
        data["CRASH_COUNT"],
        marker="o",
    )

    plt.title(title)
    plt.xlabel(x_column.replace("_", " ").title())
    plt.ylabel("Number of Crashes")
    plt.grid(alpha=0.3)

    save_chart(output_path)


def generate_visualizations(
    categories: dict,
    injuries: dict,
    time_results: dict,
    speed_results: pd.DataFrame,
    output_directory: str | Path,
) -> list[Path]:
    """Create all charts and save them in one folder."""

    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)

    charts = []

    # Show the most common crash types and conditions.
    bar_charts = [
        (
            categories["crash_type"].head(10),
            "FIRST_CRASH_TYPE",
            "CRASH_COUNT",
            "Top 10 Crash Types",
            "crash_type.png",
            True,
        ),
        (
            categories["weather"].head(10),
            "WEATHER_CONDITION",
            "CRASH_COUNT",
            "Crashes by Weather Condition",
            "weather.png",
            True,
        ),
        (
            categories["lighting"].head(10),
            "LIGHTING_CONDITION",
            "CRASH_COUNT",
            "Crashes by Lighting Condition",
            "lighting.png",
            True,
        ),
        (
            injuries["lighting_injuries"].head(10),
            "LIGHTING_CONDITION",
            "AVERAGE_INJURIES",
            "Average Injuries by Lighting",
            "lighting_injuries.png",
            True,
        ),
        (
            injuries["vehicle_injuries"].query(
                "NUM_VEHICLES >= 1 and NUM_VEHICLES <= 10"
            ),
            "NUM_VEHICLES",
            "AVERAGE_INJURIES",
            "Average Injuries by Number of Vehicles",
            "vehicle_injuries.png",
            False,
        ),
        (
            injuries["weather_injuries"].head(10),
            "WEATHER_CONDITION",
            "AVERAGE_INJURIES",
            "Average Injuries by Weather",
            "weather_injuries.png",
            True,
        ),
    ]

    # Add the 10 most common posted speed limits.
    if not speed_results.empty:
        top_speeds = speed_results.sort_values(
            by="CRASH_COUNT",
            ascending=False,
        ).head(10)

        top_speeds = top_speeds.sort_values(
            by="POSTED_SPEED_LIMIT"
        )

        bar_charts.append((
            top_speeds,
            "POSTED_SPEED_LIMIT",
            "CRASH_COUNT",
            "Top 10 Posted Speed Limits",
            "speed_limit.png",
            False,
        ))

    # Save all bar charts.
    for data, category, value, title, filename, horizontal in bar_charts:
        path = output / filename

        create_bar_chart(
            data,
            category,
            value,
            title,
            path,
            horizontal,
        )

        if not data.empty and path.exists():
            charts.append(path)

    # Create charts for hour and month.
    line_charts = [
        ("hour", "CRASH_HOUR", "Crashes by Hour", "hour.png"),
        ("month", "CRASH_MONTH", "Crashes by Month", "month.png"),
    ]

    for key, column, title, filename in line_charts:
        if key in time_results:
            path = output / filename
            data = time_results[key]

            create_line_chart(data, column, title, path)

            if not data.empty and path.exists():
                charts.append(path)

    return charts
