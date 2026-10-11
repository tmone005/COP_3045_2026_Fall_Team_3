from pathlib import Path

import pandas as pd

# 1. Read Data
project_dir = Path(__file__).resolve().parent.parent
input_path = project_dir / "02-Database" / "consolidated_data_database.csv"
output_path = Path(__file__).resolve().parent / "clean_data.csv"

df = pd.read_csv(input_path)

# 2. Inspect Data
print("Data types:\n", df.dtypes)
print("\nMissing values:\n", df.isna().sum())
print("\nDuplicate rows:", df.duplicated().sum())

# 3. Clean and Prepare Data
# Remove exact duplicate rows (do not remove valid multi-vehicle rows with same crash id)
df = df.drop_duplicates().copy()

# Convert numeric columns to numeric type
for column in ["CRASH_RECORD_ID", "CRASH_UNIT_ID", "POSTED_SPEED_LIMIT", "INJURIES_TOTAL"]:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

# Fill text fields with a neutral value when missing
for column in ["WEATHER_CONDITION", "LIGHTING_CONDITION", "CRASH_TYPE", "FIRST_CONTACT_POINT", "MAKE", "MODEL"]:
    if column in df.columns:
        df[column] = df[column].fillna("Unknown")
        df[column] = df[column].replace(r"^\s*$", "Unknown", regex=True)

# Keep rows with a valid crash record ID; fill missing numeric values conservatively
if "CRASH_RECORD_ID" in df.columns:
    df = df.dropna(subset=["CRASH_RECORD_ID"]).copy()

for column in ["POSTED_SPEED_LIMIT", "INJURIES_TOTAL"]:
    if column in df.columns:
        median_value = df[column].median()
        df[column] = df[column].fillna(median_value if pd.notna(median_value) else 0)

# 4. Save Clean Data
df.to_csv(output_path, index=False)
