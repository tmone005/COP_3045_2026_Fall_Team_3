from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

# 1. Instantiate Database
base_dir = Path(__file__).resolve().parent
db_path = base_dir / "project.db"
engine = create_engine(f"sqlite:///{db_path}")
connection = engine.connect()

# 2. Read Data
raw_data_dir = base_dir.parent / "00-Raw_data"
crashes_df = pd.read_csv(raw_data_dir / "Crashes.csv")
vehicles_df = pd.read_csv(raw_data_dir / "Vehicles.csv")

# 3. Create Tables
crashes_df.to_sql("crashes", con=connection, if_exists="replace", index=False)
vehicles_df.to_sql("vehicles", con=connection, if_exists="replace", index=False)

# 4. Close Connection
connection.close()
engine.dispose()
