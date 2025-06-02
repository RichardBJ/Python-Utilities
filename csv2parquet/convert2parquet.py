#!/usr/bin/env python3
#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os
from pathlib import Path

si=0.01

def convert_csvs():
   for path in Path('.').rglob('*.csv'):
       df = pd.read_csv(path)
       df["Time"] = np.arange(0, len(df)) * si
       parquet_path = path.with_suffix('.parquet')
       df.to_parquet(parquet_path)
       print(f'Converted {path} to {parquet_path}')

convert_csvs()