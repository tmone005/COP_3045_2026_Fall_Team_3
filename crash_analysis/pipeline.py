
"""Coordinate the Chicago traffic crash analysis workflow."""

from pathlib import Path

import pandas as pd

from .data_loader import load_datasets
from .data_cleaning import (
    clean_crashes,
    clean_vehicles,
    merge_datasets,
)
from .analysis import (
    calculate_summary,
    analyze_categories,
    analyze_injuries,
    analyze_time,
    analyze_speed,
)
from .visualization import generate_visualizations
from .report import generate_pdf_report


class CrashAnalysisPipeline:
    """Manage the complete crash analysis application."""

    def __init__(
        self,
        data_directory: str | Path,
        output_directory: str | Path,
    ) -> None:
        """Set input and output paths for the analysis."""
        self._data_directory = Path(data_directory)
        self._output_directory = Path(output_directory)
        self._data: pd.DataFrame | None = None
        self._summary: dict | None = None

    @property
    def summary(self) -> dict:
        """Return a copy of the latest analysis summary."""
        if self._summary is None:
            raise RuntimeError(
                "No summary available. Run the pipeline first."
            )
        return self._summary.copy()

    def load_and_prepare(self) -> pd.DataFrame:
        """Load, clean, and combine the two datasets."""
        crashes, vehicles = load_datasets(self._data_directory)

        cleaned_crashes = clean_crashes(crashes)
        vehicle_counts = clean_vehicles(vehicles)

        self._data = merge_datasets(
            cleaned_crashes,
            vehicle_counts,
        )

        if self._data.empty:
            raise ValueError(
                "No valid crash records remain after cleaning."
            )

        return self._data.copy()

    def run(self) -> Path:
        """Run analysis, create charts, and generate a PDF."""
        self._output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = self.load_and_prepare()

        self._summary = calculate_summary(data)
        categories = analyze_categories(data)
        injuries = analyze_injuries(data)
        time_results = analyze_time(data)
        speed_results = analyze_speed(data)

        charts = generate_visualizations(
            categories=categories,
            injuries=injuries,
            time_results=time_results,
            speed_results=speed_results,
            output_directory=self._output_directory / "figures",
        )

        report_path = generate_pdf_report(
            summary=self._summary,
            categories=categories,
            injuries=injuries,
            time_results=time_results,
            speed_results=speed_results,
            charts=charts,
            output_path=self._output_directory
            / "Chicago_Traffic_Crashes_Report.pdf",
        )

        return report_path
