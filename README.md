
# Chicago Traffic Crashes Analysis

## Project Description

This project analyzes traffic crashes in Chicago using Python.

We use two datasets from the City of Chicago. The program cleans the data, combines the datasets, and looks for patterns in traffic crashes.

We study weather conditions, lighting, crash types, speed limits, injuries, and the number of vehicles.

## Data Sources

We use two datasets from the City of Chicago Data Portal:

- [Traffic Crashes - Crashes](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if)
- [Traffic Crashes - Vehicles](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Vehicles/68nd-jvt3)

The datasets are connected using CRASH_RECORD_ID.

## Tools

- Python
- Pandas
- Matplotlib
- NumPy
- ReportLab
- Conda

## Project Files

- main.py - Runs the application.
- data_loader.py - Loads the datasets.
- data_cleaning.py - Cleans and combines the data.
- analysis.py - Analyzes the crashes.
- visualization.py - Creates charts.
- report.py - Creates the PDF report.
- pipeline.py - Connects the steps using a class.
- environment.yml - Lists the required packages.

## How to Run

First, create the environment:

```bash
conda env create -f environment.yml
```

Activate it:

```bash
conda activate chicago-crashes
```

Download the two datasets and save them as:

- data/Crashes.csv
- data/Vehicles.csv

Run the program:

```bash
python main.py
```

## Results

The program analyzes 1,115,182 crashes and 224,399 injuries from the downloaded data.

It creates nine charts and a PDF report.

The charts are saved in reports/figures.

The PDF report is saved in reports/Chicago_Traffic_Crashes_Report.pdf.

## Team

COP 3045 - Team 3

## Conclusion

This project helped us practice Python, data cleaning, data analysis, charts, modules, and object-oriented programming.

## Team Members

- Abdallah Mohameed Saif Juma Alkaabi
- Saeed Alshamsi
- Theresa Monestime

## Git LFS

This repository uses Git LFS for large files. Install Git LFS before downloading the original project datasets: https://git-lfs.com/
