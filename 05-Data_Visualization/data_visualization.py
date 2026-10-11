import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Read the cleaned data
df = pd.read_csv("03-Processed_Data/cleaned_crashes.csv")

# Folder for saving charts
output = Path("05-Data_Visualization")
output.mkdir(exist_ok=True)

# Chart 1: Crashes by weather
weather = df["WEATHER_CONDITION"].value_counts().head(5)

plt.figure(figsize=(9, 5))
weather.plot(kind="bar")
plt.title("Crashes by Weather Condition")
plt.xlabel("Weather")
plt.ylabel("Number of Crashes")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(output / "weather_crashes.png")
plt.close()

# Chart 2: Average injuries by lighting
lighting = df.groupby("LIGHTING_CONDITION")["INJURIES_TOTAL"].mean()
lighting = lighting.drop("UNKNOWN", errors="ignore")

plt.figure(figsize=(9, 5))
lighting.plot(kind="bar")
plt.title("Average Injuries by Lighting Condition")
plt.xlabel("Lighting")
plt.ylabel("Average Injuries per Crash")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(output / "lighting_injuries.png")
plt.close()

# Chart 3: Crashes by crash type
crash_types = df["CRASH_TYPE"].value_counts()

plt.figure(figsize=(9, 5))
crash_types.plot(kind="bar")
plt.title("Crashes by Crash Type")
plt.xlabel("Crash Type")
plt.ylabel("Number of Crashes")
plt.xticks(rotation=15, ha="right")
plt.tight_layout()
plt.savefig(output / "crash_types.png")
plt.close()

print("All 3 charts saved successfully!")