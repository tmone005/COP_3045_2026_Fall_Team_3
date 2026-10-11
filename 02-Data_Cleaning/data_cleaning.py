from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parent.parent
raw_data_dir = project_dir / "00-Raw_Data"

crashes = pd.read_csv(raw_data_dir / "Crashes.csv", low_memory=False)
vehicles = pd.read_csv(raw_data_dir / "Vehicles.csv", low_memory=False)

crash_cols = [
    "CRASH_RECORD_ID",
    "CRASH_DATE",
    "WEATHER_CONDITION",
    "LIGHTING_CONDITION",
    "POSTED_SPEED_LIMIT",
    "CRASH_TYPE",
    "INJURIES_TOTAL"
]

vehicle_cols = [
    "CRASH_RECORD_ID",
    "MAKE",
    "MODEL",
    "FIRST_CONTACT_POINT",
    "EXCEED_SPEED_LIMIT_I"
]

print("Crashes missing values:")
print(crashes[crash_cols].isnull().sum())

print("\nVehicles missing values:")
print(vehicles[vehicle_cols].isnull().sum())
print("\nCrash types:")
print(crashes["CRASH_TYPE"].value_counts())

print("\nSpeed limit values:")
print(vehicles["EXCEED_SPEED_LIMIT_I"].value_counts(dropna=False))

print("\nInjuries:")
print(crashes["INJURIES_TOTAL"].describe())
# Keep the columns we need
crashes_clean = crashes[crash_cols].copy()

# Remove rows without injury information
crashes_clean = crashes_clean.dropna(subset=["INJURIES_TOTAL"])

# Keep selected vehicle information
vehicles_clean = vehicles[vehicle_cols].copy()

# Fill missing vehicle details
vehicles_clean["MAKE"] = vehicles_clean["MAKE"].fillna("UNKNOWN")
vehicles_clean["MODEL"] = vehicles_clean["MODEL"].fillna("UNKNOWN")
vehicles_clean["FIRST_CONTACT_POINT"] = vehicles_clean["FIRST_CONTACT_POINT"].fillna("UNKNOWN")

print("Clean crashes:", crashes_clean.shape)
print("Clean vehicles:", vehicles_clean.shape)
print("Unique crashes:", crashes_clean["CRASH_RECORD_ID"].nunique())
print("Total crashes:", len(crashes_clean))
print("Unique vehicle crash IDs:", vehicles_clean["CRASH_RECORD_ID"].nunique())
# Count vehicles for each crash
vehicle_counts = (
    vehicles_clean.groupby("CRASH_RECORD_ID")
    .size()
    .reset_index(name="NUM_VEHICLES")
)

# Merge with crashes data
merged_data = crashes_clean.merge(
    vehicle_counts,
    on="CRASH_RECORD_ID",
    how="left",
    validate="one_to_one"
)

# Fill crashes without matching vehicle records
merged_data["NUM_VEHICLES"] = (
    merged_data["NUM_VEHICLES"].fillna(0).astype(int)
)

print("Merged data:", merged_data.shape)
print("Unique crashes after merge:",
      merged_data["CRASH_RECORD_ID"].nunique())
print("Missing vehicle matches:",
      (merged_data["NUM_VEHICLES"] == 0).sum())
# Save cleaned data
output_dir = project_dir / "03-Processed_Data"
output_dir.mkdir(exist_ok=True)

merged_data.to_csv(output_dir / "cleaned_crashes.csv", index=False)

print("Cleaned data saved successfully!")