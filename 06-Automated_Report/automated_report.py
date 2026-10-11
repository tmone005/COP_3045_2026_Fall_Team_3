
from pathlib import Path
import pandas as pd
from fpdf import FPDF

# -----------------------------------
# 1. Project folders
# -----------------------------------

project_dir = Path(__file__).resolve().parent.parent

data_file = (
    project_dir / "03-Processed_Data" / "cleaned_crashes.csv"
)

results_dir = project_dir / "04-Data_Analysis" / "results"
charts_dir = project_dir / "05-Data_Visualization" / "charts"
report_dir = project_dir / "06-Automated_Report" / "reports"

report_dir.mkdir(parents=True, exist_ok=True)

# -----------------------------------
# 2. Load cleaned data
# -----------------------------------

if not data_file.exists():
    raise FileNotFoundError(
        f"Cleaned data not found: {data_file}"
    )

df = pd.read_csv(data_file, low_memory=False)

required_columns = [
    "CRASH_RECORD_ID",
    "CRASH_DATE",
    "INJURIES_TOTAL",
    "NUM_VEHICLES",
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )

df["CRASH_DATE"] = pd.to_datetime(
    df["CRASH_DATE"],
    errors="coerce"
)

df["INJURIES_TOTAL"] = pd.to_numeric(
    df["INJURIES_TOTAL"],
    errors="coerce"
)

df["NUM_VEHICLES"] = pd.to_numeric(
    df["NUM_VEHICLES"],
    errors="coerce"
)

# Dataset summary
total_crashes = df["CRASH_RECORD_ID"].nunique()
total_injuries = df["INJURIES_TOTAL"].sum()
average_injuries = df["INJURIES_TOTAL"].mean()
average_vehicles = df["NUM_VEHICLES"].mean()

start_date = df["CRASH_DATE"].min()
end_date = df["CRASH_DATE"].max()

# -----------------------------------
# 3. Load analysis results
# -----------------------------------

files = {
    "Weather Conditions": "weather_analysis.csv",
    "Lighting Conditions": "lighting_analysis.csv",
    "Crashes by Hour": "hour_analysis.csv",
    "Posted Speed Limits": "speed_analysis.csv",
    "Crash Severity": "severity_analysis.csv",
    "Crashes by Month": "month_analysis.csv",
    "Number of Vehicles": "vehicle_analysis.csv",
}

data = {}

for section, filename in files.items():
    path = results_dir / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing analysis result: {path}"
        )

    data[section] = pd.read_csv(path)
    print("Loaded:", filename)

# -----------------------------------
# 4. PDF setup
# -----------------------------------

class Report(FPDF):

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 10)
            self.cell(
                0, 8,
                "Chicago Traffic Crashes - Data Analysis Report",
                align="C"
            )
            self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 9)
        self.cell(
            0, 10,
            f"Page {self.page_no()}",
            align="C"
        )


pdf = Report()
pdf.set_auto_page_break(auto=True, margin=18)
pdf.set_margins(15, 15, 15)

# -----------------------------------
# 5. Helper functions
# -----------------------------------

def add_title(title):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 15)
    pdf.multi_cell(pdf.epw, 9, str(title))
    pdf.ln(3)


def add_text(text):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(pdf.epw, 6, str(text))
    pdf.ln(3)


def format_value(value, column=""):
    if pd.isna(value):
        return "Missing"

    column = str(column).lower()

    if column in [
        "crash_hour",
        "crash_month",
        "num_vehicles",
        "posted_speed_limit",
    ]:
        return str(int(value))

    if "average" in column or "mean" in column:
        return f"{float(value):.2f}"

    if isinstance(value, (int, float)):
        if float(value).is_integer():
            return f"{int(value):,}"
        return f"{value:,.2f}"

    return str(value)


def prepare_table(df, section):
    result = df.copy()

    # Show the most common speed limits
    if section == "Posted Speed Limits":
        if "total_crashes" in result.columns:
            result = result.sort_values(
                "total_crashes",
                ascending=False
            )

    # Show the busiest crash hours
    if section == "Crashes by Hour":
        if "total_crashes" in result.columns:
            result = result.sort_values(
                "total_crashes",
                ascending=False
            )

    return result.head(10)


def add_table(df, section, max_rows=10):
    if df is None or df.empty:
        add_text("No data available.")
        return

    df = prepare_table(df, section).head(max_rows)

    columns = list(df.columns)
    column_count = len(columns)

    # Calculate table width
    table_width = pdf.epw
    col_width = table_width / column_count
    row_height = 8

    def draw_header():
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(225, 232, 238)

        for column in columns:
            label = (
                str(column)
                .replace("_", " ")
                .title()
            )

            if len(label) > 22:
                label = label[:19] + "..."

            pdf.cell(
                col_width,
                row_height,
                label,
                border=1,
                align="C",
                fill=True
            )

        pdf.ln(row_height)

    if pdf.get_y() + 25 > pdf.page_break_trigger:
        pdf.add_page()

    draw_header()

    pdf.set_font("Helvetica", "", 8)

    for _, row in df.iterrows():

        if pdf.get_y() + row_height > pdf.page_break_trigger:
            pdf.add_page()
            draw_header()

        pdf.set_font("Helvetica", "", 8)

        for column in columns:
            value = format_value(
                row[column],
                column
            )

            # Shorten long labels to fit table
            max_chars = max(
                10,
                int(col_width / 1.8)
            )

            if len(value) > max_chars:
                value = value[:max_chars - 3] + "..."

            pdf.cell(
                col_width,
                row_height,
                value,
                border=1,
                align="C"
            )

        pdf.ln(row_height)

    pdf.ln(8)


def add_chart(filename, title):
    chart_path = charts_dir / filename

    if not chart_path.exists():
        raise FileNotFoundError(
            f"Missing chart: {chart_path}"
        )

    pdf.add_page()
    add_title(title)

    # Fit chart on page
    pdf.image(
        str(chart_path),
        x=pdf.l_margin,
        y=pdf.get_y() + 5,
        w=pdf.epw
    )


# -----------------------------------
# 6. Cover page
# -----------------------------------

pdf.add_page()
pdf.ln(35)

pdf.set_font("Helvetica", "B", 23)
pdf.multi_cell(
    pdf.epw,
    13,
    "Chicago Traffic Crashes",
    align="C"
)

pdf.set_font("Helvetica", "B", 17)
pdf.multi_cell(
    pdf.epw,
    11,
    "Data Analysis Report",
    align="C"
)

pdf.ln(18)

pdf.set_font("Helvetica", "", 12)
pdf.multi_cell(
    pdf.epw,
    9,
    "COP 3045 - Python Programming II\n"
    "Florida International University\n"
    "Team 3",
    align="C"
)

pdf.ln(15)

pdf.set_font("Helvetica", "", 11)
pdf.multi_cell(
    pdf.epw,
    8,
    "Team Members:\n"
    "Saeed Alshamsi\n"
    "Abdallah Mohamed Saif Juma Alkaabi\n"
    "Theresa Monestime",
    align="C"
)

# -----------------------------------
# 7. Introduction
# -----------------------------------

pdf.add_page()

add_title("1. Introduction")

add_text(
    "This project analyzes traffic crashes in Chicago. "
    "The goal is to explore how weather, lighting, "
    "time of day, speed limits, and the number of "
    "vehicles are related to crashes and injuries."
)

add_text(
    "The project uses two related datasets from the "
    "City of Chicago Data Portal. The datasets are "
    "connected using CRASH_RECORD_ID."
)

# -----------------------------------
# 8. Data sources
# -----------------------------------

add_title("2. Data Sources")

add_text(
    "Dataset 1: Traffic Crashes - Crashes\n"
    "Source: City of Chicago Data Portal\n"
    "Dataset ID: 85ca-t3if"
)

add_text(
    "Dataset 2: Traffic Crashes - Vehicles\n"
    "Source: City of Chicago Data Portal\n"
    "Dataset ID: 68nd-jvt3"
)

add_text(
    "The vehicle dataset was grouped by crash ID "
    "to calculate the number of vehicles in each crash. "
    "The counts were then merged with the crash dataset."
)

# -----------------------------------
# 9. Dataset summary
# -----------------------------------

add_title("3. Dataset Summary")

if pd.notna(start_date) and pd.notna(end_date):
    add_text(
        "Time period: "
        f"{start_date:%B %d, %Y} to "
        f"{end_date:%B %d, %Y}"
    )

add_text(
    f"Total crash records: {total_crashes:,}\n"
    f"Total recorded injuries: {total_injuries:,.0f}\n"
    f"Average injuries per crash: {average_injuries:.2f}\n"
    f"Average vehicles per crash: {average_vehicles:.2f}"
)

add_text(
    "The data includes numerical variables such as "
    "injuries, speed limit, and number of vehicles. "
    "Categorical variables include weather condition, "
    "lighting condition, and crash type."
)

# -----------------------------------
# 10. Exploratory Data Analysis
# -----------------------------------

pdf.add_page()

add_title("4. Exploratory Data Analysis")

add_text(
    "The following tables summarize traffic crash "
    "patterns across different conditions. "
    "Only the first 10 selected rows of each result "
    "are shown."
)

for section, table in data.items():

    if pdf.get_y() > pdf.h - 75:
        pdf.add_page()

    add_title(section)
    add_table(table, section)

# -----------------------------------
# 11. Visualizations
# -----------------------------------

charts = [
    (
        "weather_crashes.png",
        "5.1 Crashes by Weather"
    ),
    (
        "lighting_crashes.png",
        "5.2 Crashes by Lighting"
    ),
    (
        "hourly_crashes.png",
        "5.3 Crashes by Hour"
    ),
    (
        "speed_crashes.png",
        "5.4 Crashes by Speed Limit"
    ),
    (
        "crash_severity.png",
        "5.5 Crash Severity"
    ),
    (
        "monthly_crashes.png",
        "5.6 Crashes by Month"
    ),
    (
        "vehicle_injuries.png",
        "5.7 Injuries by Number of Vehicles"
    ),
]

for filename, title in charts:
    add_chart(filename, title)

# -----------------------------------
# 12. Key findings
# -----------------------------------

pdf.add_page()
add_title("6. Key Findings")

weather = data["Weather Conditions"]
lighting = data["Lighting Conditions"]
hours = data["Crashes by Hour"]
vehicles = data["Number of Vehicles"]

if not weather.empty:
    top_weather = weather.sort_values(
        "total_crashes",
        ascending=False
    ).iloc[0]

    add_text(
        "The most common recorded weather condition "
        f"was {top_weather['WEATHER_CONDITION']}, "
        f"with {int(top_weather['total_crashes']):,} crashes."
    )

if not lighting.empty:
    top_lighting = lighting.sort_values(
        "total_crashes",
        ascending=False
    ).iloc[0]

    add_text(
        "The most common recorded lighting condition "
        f"was {top_lighting['LIGHTING_CONDITION']}, "
        f"with {int(top_lighting['total_crashes']):,} crashes."
    )

if not hours.empty:
    peak_hour = hours.sort_values(
        "total_crashes",
        ascending=False
    ).iloc[0]

    hour = int(peak_hour["CRASH_HOUR"])

    add_text(
        "The hour with the highest recorded number "
        f"of crashes was {hour:02d}:00, "
        f"with {int(peak_hour['total_crashes']):,} crashes."
    )

if not vehicles.empty:
    valid_vehicles = vehicles[
        vehicles["NUM_VEHICLES"].between(1, 10)
    ].copy()

    if not valid_vehicles.empty:
        common_vehicles = valid_vehicles.sort_values(
            "total_crashes",
            ascending=False
        ).iloc[0]

        add_text(
            "The most common number of vehicles "
            "involved in a crash was "
            f"{int(common_vehicles['NUM_VEHICLES'])}, "
            "with "
            f"{int(common_vehicles['total_crashes']):,} "
            "recorded crashes."
        )

        add_text(
            "The analysis also compares average injuries "
            "across crashes involving different numbers "
            "of vehicles."
        )

add_text(
    "These findings describe patterns in the dataset. "
    "They do not prove that any specific condition "
    "causes a crash."
)

# -----------------------------------
# 13. Conclusion
# -----------------------------------

add_title("7. Conclusion")

add_text(
    "This project demonstrates an automated data "
    "analysis workflow using Python."
)

add_text(
    "The application reads and prepares two related "
    "datasets, creates summary statistics and charts, "
    "and automatically generates a PDF report."
)

add_text(
    "Pandas was used for data processing and analysis, "
    "Matplotlib for creating charts, and fpdf2 for "
    "generating the report."
)

# -----------------------------------
# 14. Save report
# -----------------------------------

output_file = (
    report_dir / "Chicago_Traffic_Crashes_Report.pdf"
)

pdf.output(str(output_file))

print("\nPDF report created successfully!")
print("Report saved in:", output_file)
