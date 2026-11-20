
"""Generate an automated PDF report for Chicago traffic crashes."""

from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

NAVY = colors.HexColor("#183153")
BLUE = colors.HexColor("#2764A5")
LIGHT_BLUE = colors.HexColor("#EDF3F9")
GREY = colors.HexColor("#667085")


def get_styles():
    """Create consistent styles for the report."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=19,
        leading=24,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=14,
    ))

    styles.add(ParagraphStyle(
        name="ReportSection",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=NAVY,
        spaceBefore=16,
        spaceAfter=9,
    ))

    styles.add(ParagraphStyle(
        name="ReportBody",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=15,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="TableText",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
    ))

    return styles


def add_paragraph(content, text, style):
    """Add safe text to the PDF."""
    content.append(Paragraph(escape(str(text)), style))


def add_table(
    content: list,
    dataframe: pd.DataFrame,
    title: str,
    max_rows: int = 10,
) -> None:
    """Add a formatted summary table to the PDF."""
    if dataframe.empty:
        return

    styles = get_styles()
    add_paragraph(content, title, styles["ReportSection"])

    display = dataframe.head(max_rows).copy()
    display.columns = [
        str(column).replace("_", " ").title()
        for column in display.columns
    ]

    table_data = []

    table_data.append([
        Paragraph(escape(str(column)), styles["TableText"])
        for column in display.columns
    ])

    for row in display.itertuples(index=False, name=None):
        formatted_row = []

        for value in row:
            if pd.isna(value):
                formatted = "N/A"
            elif isinstance(value, float):
                formatted = f"{value:,.2f}"
            elif isinstance(value, int):
                formatted = f"{value:,}"
            else:
                formatted = str(value)

            formatted_row.append(
                Paragraph(escape(formatted), styles["TableText"])
            )

        table_data.append(formatted_row)

    widths = [500 / len(display.columns)] * len(display.columns)

    table = Table(
        table_data,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F8FAFC")]),
        ("LINEBELOW", (0, 0), (-1, 0), 1, BLUE),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3,
         colors.HexColor("#D9E1EA")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    content.append(table)
    content.append(Spacer(1, 12))


def add_page_number(canvas, doc):
    """Add a footer with the page number."""
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9E1EA"))
    canvas.line(50, 37, 562, 37)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(50, 25, "Chicago Traffic Crashes Analysis")
    canvas.drawRightString(562, 25, f"Page {doc.page}")
    canvas.restoreState()


def generate_pdf_report(
    summary: dict,
    categories: dict,
    injuries: dict,
    time_results: dict,
    speed_results: pd.DataFrame,
    charts: list[Path],
    output_path: str | Path,
) -> Path:
    """Create a PDF report with analysis, tables, and charts."""

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(destination),
        pagesize=(612, 792),
        rightMargin=50,
        leftMargin=50,
        topMargin=45,
        bottomMargin=50,
    )

    styles = get_styles()
    content = []

    add_paragraph(
        content,
        "Chicago Traffic Crashes - Data Analysis Report",
        styles["ReportTitle"],
    )

    add_paragraph(
        content,
        "Automated analysis of traffic crash records from Chicago",
        styles["ReportBody"],
    )

    # 1. Introduction
    add_paragraph(content, "1. Introduction", styles["ReportSection"])
    add_paragraph(
        content,
        "This project analyzes traffic crashes in Chicago. "
        "It studies weather conditions, lighting, crash types, "
        "posted speed limits, injuries, and the number of vehicles "
        "involved in each crash. The goal is to identify patterns "
        "and present the results using tables and charts.",
        styles["ReportBody"],
    )

    # 2. Data sources
    add_paragraph(content, "2. Data Sources", styles["ReportSection"])
    add_paragraph(
        content,
        "The project uses two public datasets from the City of "
        "Chicago Data Portal: Traffic Crashes - Crashes "
        "(85ca-t3if) and Traffic Crashes - Vehicles (68nd-jvt3). "
        "The datasets are connected using CRASH_RECORD_ID. "
        "Each crash is counted once in the final analysis.",
        styles["ReportBody"],
    )

    # 3. Summary
    add_paragraph(content, "3. Dataset Summary", styles["ReportSection"])

    summary_lines = [
        f"Total crashes: {summary['total_crashes']:,}",
        f"Total reported injuries: {summary['total_injuries']:,}",
        f"Average injuries per crash: {summary['average_injuries']:.2f}",
        f"Average posted speed limit: {summary['average_speed_limit']:.2f} mph",
        f"Average vehicles per crash: {summary['average_vehicles']:.2f}",
    ]

    for line in summary_lines:
        add_paragraph(content, line, styles["ReportBody"])

    add_paragraph(
        content,
        "The injury average represents reported injuries per crash, "
        "not the percentage of crashes involving an injury.",
        styles["ReportBody"],
    )

    # 4. Exploratory analysis
    add_paragraph(
        content,
        "4. Exploratory Data Analysis",
        styles["ReportSection"],
    )

    for key, title in [
        ("weather", "Weather Conditions"),
        ("lighting", "Lighting Conditions"),
        ("crash_type", "Crash Types"),
    ]:
        add_table(content, categories[key], title)

    for key, title in [
        ("weather_injuries", "Average Injuries by Weather"),
        ("lighting_injuries", "Average Injuries by Lighting"),
        ("vehicle_injuries", "Average Injuries by Vehicle Count"),
    ]:
        add_table(content, injuries[key], title)

    # Show the most common posted speed limits.
    if not speed_results.empty:
        speed_display = speed_results.copy()

        if len(speed_display.columns) >= 2:
            count_column = speed_display.columns[1]
            speed_display[count_column] = pd.to_numeric(
                speed_display[count_column],
                errors="coerce",
            )
            speed_display = speed_display.sort_values(
                by=count_column,
                ascending=False,
            )

        add_table(
            content,
            speed_display,
            "Top 10 Most Common Posted Speed Limits",
        )

    for key, title in [
        ("hour", "Crashes by Hour"),
        ("month", "Crashes by Month"),
    ]:
        if key in time_results:
            add_table(content, time_results[key], title, max_rows=24)

    # 5. Charts
    add_paragraph(
        content,
        "5. Visualizations",
        styles["ReportSection"],
    )

    for index, chart_path in enumerate(charts, start=1):
        path = Path(chart_path)

        if not path.is_file():
            raise FileNotFoundError(f"Missing chart: {path}")

        image_width, image_height = ImageReader(str(path)).getSize()
        scale = min(500 / image_width, 340 / image_height)

        content.append(KeepTogether([
            Paragraph(
                f"Figure {index}: "
                f"{escape(path.stem.replace('_', ' ').title())}",
                styles["Heading3"],
            ),
            Spacer(1, 8),
            Image(
                str(path),
                width=image_width * scale,
                height=image_height * scale,
            ),
            Spacer(1, 18),
        ]))

    # 6. Findings
    add_paragraph(
        content,
        "6. Key Findings",
        styles["ReportSection"],
    )

    weather = categories["weather"]
    lighting = categories["lighting"]
    crash_types = categories["crash_type"]

    findings = []

    if not weather.empty:
        findings.append(
            f"The most frequently recorded weather condition "
            f"was {weather.iloc[0, 0]}."
        )

    if not lighting.empty:
        findings.append(
            f"The most frequently recorded lighting condition "
            f"was {lighting.iloc[0, 0]}."
        )

    if not crash_types.empty:
        findings.append(
            f"The most common first crash type "
            f"was {crash_types.iloc[0, 0]}."
        )

    findings.extend([
        "The number of crashes recorded under a condition does "
        "not show how dangerous that condition is by itself. "
        "For example, many crashes happen in clear weather, "
        "but drivers may also spend more time driving in clear weather.",

        "Average injuries per crash can be compared across "
        "weather, lighting, and vehicle-count groups. "
        "However, small groups may have less reliable averages.",

        "The hourly and monthly charts show when more crashes "
        "were recorded. These patterns may help identify "
        "periods that need further study.",

        "The analysis identifies relationships in recorded data. "
        "It does not establish that weather, lighting, or "
        "speed limits directly caused the crashes.",
    ])

    for finding in findings:
        add_paragraph(content, finding, styles["ReportBody"])

    # 7. Limitations
    add_paragraph(
        content,
        "7. Limitations",
        styles["ReportSection"],
    )

    add_paragraph(
        content,
        "The results depend on the accuracy and completeness "
        "of the reported crash records. Some fields contain "
        "unknown or missing values. The dataset includes "
        "reported crashes rather than all driving activity, "
        "so crash counts alone cannot measure the risk of "
        "driving in different conditions. The analysis is "
        "descriptive and does not establish causation.",
        styles["ReportBody"],
    )

    # 8. Conclusion
    add_paragraph(
        content,
        "8. Conclusion",
        styles["ReportSection"],
    )

    add_paragraph(
        content,
        "This application successfully combines two Chicago "
        "traffic crash datasets, cleans the records, calculates "
        "summary statistics, creates visualizations, and "
        "automatically generates a PDF report. The project "
        "uses reusable Python modules and object-oriented "
        "programming to make the analysis easier to maintain "
        "and update. Future improvements could include "
        "additional safety variables and comparisons across "
        "different years.",
        styles["ReportBody"],
    )

    doc.build(
        content,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return destination
