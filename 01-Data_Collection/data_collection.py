from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parent.parent
raw_data_dir = project_dir / "00-Raw_data"

crashes = pd.read_csv(raw_data_dir / "Crashes.csv")
vehicles = pd.read_csv(raw_data_dir / "Vehicles.csv")

consolidated = crashes.merge(
    vehicles,
    on="CRASH_RECORD_ID",
    how="left",
    suffixes=("_crash", "_vehicle"),
    validate="one_to_many",
)

output_file = raw_data_dir / "Crashes_Vehicles_Consolidated.csv"
consolidated.to_csv(output_file, index=False)

print("Consolidated file created:", output_file)
print(consolidated.head())
