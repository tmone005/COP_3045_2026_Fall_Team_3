
"""Main entry point for the Chicago Traffic Crashes application."""

from pathlib import Path
import sys

from crash_analysis.pipeline import CrashAnalysisPipeline


def main() -> int:
    """Run the complete traffic crash analysis application."""
    project_directory = Path(__file__).resolve().parent

    data_directory = project_directory / "data"
    output_directory = project_directory / "reports"

    print("=" * 50)
    print("Chicago Traffic Crashes Analysis")
    print("=" * 50)

    pipeline = CrashAnalysisPipeline(
        data_directory=data_directory,
        output_directory=output_directory,
    )

    try:
        report_path = pipeline.run()

    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print("\nAnalysis completed successfully!")
    print(f"Total crashes: {pipeline.summary['total_crashes']:,}")
    print(f"Total injuries: {pipeline.summary['total_injuries']:,}")
    print(f"PDF report: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
