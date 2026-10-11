import pandas as pd
from pathlib import Path
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Image, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Read the cleaned data
df = pd.read_csv("03-Processed_Data/cleaned_crashes.csv")

# Create PDF report
output = Path("06-Automated_Report/chicago_crashes_report.pdf")
doc = SimpleDocTemplate(str(output))

styles = getSampleStyleSheet()
content = []

# Project title
content.append(Paragraph("Chicago Traffic Crashes Analysis", styles["Title"]))
content.append(Spacer(1, 20))

# Dataset summary
content.append(Paragraph("Dataset Summary", styles["Heading2"]))

content.append(Paragraph(
    f"Total crashes: {len(df):,}<br/>"
    f"Total injuries: {df['INJURIES_TOTAL'].sum():,.0f}<br/>"
    f"Average injuries per crash: {df['INJURIES_TOTAL'].mean():.2f}<br/>"
    f"Average speed limit: {df['POSTED_SPEED_LIMIT'].mean():.2f} mph<br/>"
    f"Average vehicles per crash: {df['NUM_VEHICLES'].mean():.2f}",
    styles["Normal"]
))

content.append(Spacer(1, 20))

# Summary statistics
content.append(Paragraph("Summary Statistics", styles["Heading2"]))

columns = ["INJURIES_TOTAL", "POSTED_SPEED_LIMIT", "NUM_VEHICLES"]
names = ["Injuries", "Speed Limit", "Vehicles"]

stats = df[columns].agg(["mean", "min", "max"])

table_data = [
    ["Variable", "Average", "Minimum", "Maximum"]
]

for name, column in zip(names, columns):
    table_data.append([
        name,
        f"{stats.loc['mean', column]:.2f}",
        f"{stats.loc['min', column]:.0f}",
        f"{stats.loc['max', column]:.0f}"
    ])

table = Table(table_data, colWidths=[120, 100, 100, 100])

table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))

content.append(table)
content.append(Spacer(1, 20))

# Key findings
content.append(Paragraph("Key Findings", styles["Heading2"]))

rain = df.loc[
    df["WEATHER_CONDITION"] == "RAIN", "INJURIES_TOTAL"
].mean()

clear = df.loc[
    df["WEATHER_CONDITION"] == "CLEAR", "INJURIES_TOTAL"
].mean()

night = df.loc[
    df["LIGHTING_CONDITION"] == "DARKNESS, LIGHTED ROAD",
    "INJURIES_TOTAL"
].mean()

day = df.loc[
    df["LIGHTING_CONDITION"] == "DAYLIGHT",
    "INJURIES_TOTAL"
].mean()

most_common_weather = df["WEATHER_CONDITION"].value_counts().idxmax()
most_common_type = df["CRASH_TYPE"].value_counts().idxmax()

findings = [
    f"The most common weather condition was {most_common_weather}.",
    f"Average injuries per crash were {rain:.3f} in rain and {clear:.3f} in clear weather.",
    f"Average injuries per crash were {night:.3f} on lighted roads at night and {day:.3f} during daylight.",
    f"The most common crash type was {most_common_type}."
]

for finding in findings:
    content.append(Paragraph("- " + finding, styles["Normal"]))
    content.append(Spacer(1, 8))

content.append(Spacer(1, 15))

# Add the three charts
charts = [
    ("Crashes by Weather", "05-Data_Visualization/weather_crashes.png"),
    ("Average Injuries by Lighting", "05-Data_Visualization/lighting_injuries.png"),
    ("Crashes by Crash Type", "05-Data_Visualization/crash_types.png")
]

for title, path in charts:
    chart_section = [
        Paragraph(title, styles["Heading2"]),
        Spacer(1, 10),
        Image(path, width=450, height=250),
        Spacer(1, 20)
    ]

    content.append(KeepTogether(chart_section))

# Save PDF
doc.build(content)

print("PDF report created successfully!")