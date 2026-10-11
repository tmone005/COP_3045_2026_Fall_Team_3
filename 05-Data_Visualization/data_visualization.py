
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Project folders
project_dir = Path(__file__).resolve().parent.parent
results_dir = project_dir / "04-Data_Analysis" / "results"
charts_dir = project_dir / "05-Data_Visualization" / "charts"

charts_dir.mkdir(parents=True, exist_ok=True)

# Load analysis results
weather = pd.read_csv(results_dir / "weather_analysis.csv")
lighting = pd.read_csv(results_dir / "lighting_analysis.csv")
hour = pd.read_csv(results_dir / "hour_analysis.csv")
speed = pd.read_csv(results_dir / "speed_analysis.csv")
severity = pd.read_csv(results_dir / "severity_analysis.csv")
month = pd.read_csv(results_dir / "month_analysis.csv")

# 1. Crashes by weather
weather_top = weather.nlargest(10, "total_crashes")
weather_top = weather_top.sort_values("total_crashes")

plt.figure(figsize=(11, 6))
plt.barh(
    weather_top["WEATHER_CONDITION"],
    weather_top["total_crashes"],
    color="steelblue"
)
plt.title("Top 10 Weather Conditions in Chicago Crashes")
plt.xlabel("Number of Crashes")
plt.ylabel("Weather Condition")
plt.grid(axis="x", alpha=0.2)
plt.tight_layout()
plt.savefig(charts_dir / "weather_crashes.png", dpi=150)
plt.close()

# 2. Crashes by lighting
lighting_plot = lighting.sort_values("total_crashes")

plt.figure(figsize=(11, 6))
plt.barh(
    lighting_plot["LIGHTING_CONDITION"],
    lighting_plot["total_crashes"],
    color="steelblue"
)
plt.title("Chicago Crashes by Lighting Condition")
plt.xlabel("Number of Crashes")
plt.ylabel("Lighting Condition")
plt.grid(axis="x", alpha=0.2)
plt.tight_layout()
plt.savefig(charts_dir / "lighting_crashes.png", dpi=150)
plt.close()

# 3. Crashes by hour
hour_plot = hour.sort_values("CRASH_HOUR")

plt.figure(figsize=(11, 6))
plt.plot(
    hour_plot["CRASH_HOUR"],
    hour_plot["total_crashes"],
    marker="o",
    color="steelblue"
)
plt.title("Chicago Traffic Crashes by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Number of Crashes")
plt.xticks(range(0, 24))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(charts_dir / "hourly_crashes.png", dpi=150)
plt.close()

# 4. Crashes by posted speed limit
speed_plot = speed[
    (speed["POSTED_SPEED_LIMIT"] > 0) &
    (speed["POSTED_SPEED_LIMIT"] <= 80)
].copy()

speed_plot = speed_plot.sort_values("POSTED_SPEED_LIMIT")

plt.figure(figsize=(11, 6))
plt.bar(
    speed_plot["POSTED_SPEED_LIMIT"],
    speed_plot["total_crashes"],
    width=0.8,
    color="steelblue"
)
plt.title("Chicago Crashes by Posted Speed Limit")
plt.xlabel("Posted Speed Limit (mph)")
plt.ylabel("Number of Crashes")
plt.xticks(range(0, 81, 5))
plt.grid(axis="y", alpha=0.2)
plt.tight_layout()
plt.savefig(charts_dir / "speed_crashes.png", dpi=150)
plt.close()

# 5. Crash severity
severity_plot = severity.sort_values("total_crashes")

plt.figure(figsize=(11, 6))
plt.barh(
    severity_plot["CRASH_TYPE"],
    severity_plot["total_crashes"],
    color="steelblue"
)
plt.title("Chicago Crashes by Severity")
plt.xlabel("Number of Crashes")
plt.ylabel("Crash Type")
plt.grid(axis="x", alpha=0.2)
plt.tight_layout()
plt.savefig(charts_dir / "crash_severity.png", dpi=150)
plt.close()

# 6. Crashes by month
month_plot = month.sort_values("CRASH_MONTH")

plt.figure(figsize=(11, 6))
plt.plot(
    month_plot["CRASH_MONTH"],
    month_plot["total_crashes"],
    marker="o",
    color="steelblue"
)
plt.title("Chicago Traffic Crashes by Month")
plt.xlabel("Month")
plt.ylabel("Number of Crashes")
plt.xticks(range(1, 13))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(charts_dir / "monthly_crashes.png", dpi=150)
plt.close()

# 7. Crashes by number of vehicles
vehicle = pd.read_csv(results_dir / "vehicle_analysis.csv")

vehicle_plot = vehicle[
    (vehicle["NUM_VEHICLES"] >= 1) &
    (vehicle["NUM_VEHICLES"] <= 10)
]

plt.figure(figsize=(10, 6))
plt.bar(
    vehicle_plot["NUM_VEHICLES"].astype(str),
    vehicle_plot["average_injuries"]
)

plt.title("Average Injuries by Number of Vehicles")
plt.xlabel("Number of Vehicles")
plt.ylabel("Average Injuries per Crash")
plt.tight_layout()
plt.savefig(charts_dir / "vehicle_injuries.png", dpi=150)
plt.close()

print("All 7 charts created successfully!")
print("Charts saved in:", charts_dir)
