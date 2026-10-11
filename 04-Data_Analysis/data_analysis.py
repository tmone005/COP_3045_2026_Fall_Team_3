
from pathlib import Path
import pandas as pd

# Project folders
project_dir = Path(__file__).resolve().parent.parent
data_file = project_dir / "03-Processed_Data" / "cleaned_crashes.csv"
output_dir = project_dir / "04-Data_Analysis" / "results"

output_dir.mkdir(parents=True, exist_ok=True)

# 1. Load cleaned data
print("Loading cleaned data...")

if not data_file.exists():
    raise FileNotFoundError(f"Data file not found: {data_file}")

df = pd.read_csv(data_file, low_memory=False)

print("Total records:", len(df))
print("Total columns:", len(df.columns))

# 2. Check required columns
required_cols = [
    "CRASH_RECORD_ID",
    "CRASH_DATE",
    "WEATHER_CONDITION",
    "LIGHTING_CONDITION",
    "POSTED_SPEED_LIMIT",
    "CRASH_TYPE",
    "INJURIES_TOTAL",
    "NUM_VEHICLES"
]

missing_cols = [
    col for col in required_cols
    if col not in df.columns
]

if missing_cols:
    raise ValueError(f"Missing columns: {missing_cols}")

# 3. Prepare data
print("\nPreparing data...")

# Remove records without a crash ID
df = df.dropna(subset=["CRASH_RECORD_ID"]).copy()

# Remove duplicate crash records
df = df.drop_duplicates(subset=["CRASH_RECORD_ID"])

# Convert numerical columns
numeric_cols = [
    "INJURIES_TOTAL",
    "POSTED_SPEED_LIMIT",
    "NUM_VEHICLES"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove invalid injury and vehicle counts
df.loc[df["INJURIES_TOTAL"] < 0, "INJURIES_TOTAL"] = pd.NA
df.loc[df["NUM_VEHICLES"] < 0, "NUM_VEHICLES"] = pd.NA

# Fill missing categorical values
categorical_cols = [
    "WEATHER_CONDITION",
    "LIGHTING_CONDITION",
    "CRASH_TYPE"
]

for col in categorical_cols:
    df[col] = df[col].fillna("UNKNOWN")

# Convert dates
df["CRASH_DATE"] = pd.to_datetime(
    df["CRASH_DATE"],
    errors="coerce",
    format="mixed"
)

df["CRASH_HOUR"] = df["CRASH_DATE"].dt.hour
df["CRASH_MONTH"] = df["CRASH_DATE"].dt.month

print("Data preparation completed!")
print("Records after preparation:", len(df))

# 4. Numerical summary statistics
print("\n--- Numerical Statistics ---")

numerical_summary = df[numeric_cols].describe().transpose()
numerical_summary.to_csv(
    output_dir / "numerical_summary.csv"
)

print(numerical_summary)

# 5. Categorical summaries
print("\n--- Categorical Statistics ---")

for col in categorical_cols:
    summary = (
        df[col]
        .value_counts(dropna=False)
        .rename_axis(col)
        .reset_index(name="count")
    )

    summary.to_csv(
        output_dir / f"{col.lower()}_summary.csv",
        index=False
    )

    print(f"\n{col}:")
    print(summary.head(10))

# 6. Crashes by weather
weather_analysis = (
    df.groupby("WEATHER_CONDITION", dropna=False)
    .agg(
        total_crashes=("CRASH_RECORD_ID", "count"),
        average_injuries=("INJURIES_TOTAL", "mean"),
        total_injuries=("INJURIES_TOTAL", "sum")
    )
    .reset_index()
    .sort_values("total_crashes", ascending=False)
)

weather_analysis.to_csv(
    output_dir / "weather_analysis.csv",
    index=False
)

# 7. Crashes by lighting
lighting_analysis = (
    df.groupby("LIGHTING_CONDITION", dropna=False)
    .agg(
        total_crashes=("CRASH_RECORD_ID", "count"),
        average_injuries=("INJURIES_TOTAL", "mean"),
        total_injuries=("INJURIES_TOTAL", "sum")
    )
    .reset_index()
    .sort_values("total_crashes", ascending=False)
)

lighting_analysis.to_csv(
    output_dir / "lighting_analysis.csv",
    index=False
)

# 8. Crashes by hour
hour_analysis = (
    df.groupby("CRASH_HOUR")
    .agg(
        total_crashes=("CRASH_RECORD_ID", "count"),
        total_injuries=("INJURIES_TOTAL", "sum")
    )
    .reset_index()
    .sort_values("CRASH_HOUR")
)

hour_analysis.to_csv(
    output_dir / "hour_analysis.csv",
    index=False
)

# 9. Crashes by speed limit
speed_analysis = (
    df.groupby("POSTED_SPEED_LIMIT")
    .agg(
        total_crashes=("CRASH_RECORD_ID", "count"),
        average_injuries=("INJURIES_TOTAL", "mean")
    )
    .reset_index()
    .sort_values("POSTED_SPEED_LIMIT")
)

speed_analysis.to_csv(
    output_dir / "speed_analysis.csv",
    index=False
)

# 10. Crash severity
severity_analysis = (
    df.groupby("CRASH_TYPE", dropna=False)
    .agg(
        total_crashes=("CRASH_RECORD_ID", "count"),
        average_injuries=("INJURIES_TOTAL", "mean"),
        total_injuries=("INJURIES_TOTAL", "sum")
    )
    .reset_index()
    .sort_values("total_crashes", ascending=False)
)

severity_analysis.to_csv(
    output_dir / "severity_analysis.csv",
    index=False
)

# 11. Crashes by month
month_analysis = (
    df.groupby("CRASH_MONTH")
    .agg(
        total_crashes=("CRASH_RECORD_ID", "count")
    )
    .reset_index()
    .sort_values("CRASH_MONTH")
)

month_analysis.to_csv(
    output_dir / "month_analysis.csv",
    index=False
)

# 12. Crashes by number of vehicles
vehicle_analysis = (
    df.groupby("NUM_VEHICLES")
    .agg(
        total_crashes=("CRASH_RECORD_ID", "count"),
        average_injuries=("INJURIES_TOTAL", "mean"),
        total_injuries=("INJURIES_TOTAL", "sum")
    )
    .reset_index()
    .sort_values("NUM_VEHICLES")
)

vehicle_analysis.to_csv(
    output_dir / "vehicle_analysis.csv",
    index=False
)

print("\nCrashes by number of vehicles:")
print(vehicle_analysis.head(10))

# 13. Missing values summary
missing_summary = (
    df[required_cols]
    .isnull()
    .sum()
    .reset_index()
)

missing_summary.columns = [
    "column",
    "missing_values"
]

missing_summary.to_csv(
    output_dir / "missing_values_summary.csv",
    index=False
)

# 14. Overall summary
print("\n--- Analysis Summary ---")

print("Total crashes:", len(df))
print("Total injuries:", df["INJURIES_TOTAL"].sum())
print(
    "Average injuries:",
    round(df["INJURIES_TOTAL"].mean(), 3)
)

print(
    "Average vehicles per crash:",
    round(df["NUM_VEHICLES"].mean(), 2)
)

print("\nTop weather conditions:")
print(weather_analysis.head())

print("\nTop lighting conditions:")
print(lighting_analysis.head())

print("\nCrash severity:")
print(severity_analysis.head())

print("\nAnalysis completed successfully!")
print("Results saved in:", output_dir)
