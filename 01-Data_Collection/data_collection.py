from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parent.parent
raw_data_dir = project_dir / "00-Raw_data"

crashes = pd.read_csv(raw_data_dir / "Crashes.csv")
vehicles = pd.read_csv(raw_data_dir / "Vehicles.csv")

