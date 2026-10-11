import pandas as pd

# Read the cleaned data
df = pd.read_csv("03-Processed_Data/cleaned_crashes.csv")

# Basic information
print("Total crashes:", len(df))
print("Total injuries:", df["INJURIES_TOTAL"].sum())

# Numerical statistics
print("\nNumerical Statistics:")
print(df[["INJURIES_TOTAL", "POSTED_SPEED_LIMIT", "NUM_VEHICLES"]].describe())

# Categorical statistics
print("\nWeather Conditions:")
print(df["WEATHER_CONDITION"].value_counts())

print("\nLighting Conditions:")
print(df["LIGHTING_CONDITION"].value_counts())

print("\nCrash Types:")
print(df["CRASH_TYPE"].value_counts())
# Summary table by weather
weather_summary = df.groupby("WEATHER_CONDITION")["INJURIES_TOTAL"].agg(
    ["count", "mean", "sum"]
)

print("\nWeather Summary:")
print(weather_summary)

# Summary table by lighting
lighting_summary = df.groupby("LIGHTING_CONDITION")["INJURIES_TOTAL"].agg(
    ["count", "mean", "sum"]
)

print("\nLighting Summary:")
print(lighting_summary)