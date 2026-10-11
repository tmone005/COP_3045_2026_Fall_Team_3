from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

# 1. Connect to Database
base_dir = Path(__file__).resolve().parent
db_path = base_dir / "project.db"
engine = create_engine(f"sqlite:///{db_path}")
connection = engine.connect()

# 2. Read Tables
crashes_df = pd.read_sql_table("crashes", con=connection)
vehicles_df = pd.read_sql_table("vehicles", con=connection)

# 3. Create Analytical DataFrame
df = crashes_df.merge(
    vehicles_df,
    how="left",
    on="CRASH_RECORD_ID",
)
output_path = base_dir / "consolidated_data_database.csv"
df.to_csv(output_path, index=False)

# 4. Close Connection
connection.close()
engine.dispose()
