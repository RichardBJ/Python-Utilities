#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 17:56:28 2024
SIMPLE CONVERSION BOTHWAYS between parquet and csv
@author: rbj
straight forward conversion to and from parquet and csv Should include txt with either tab or spaces. multiple spaces treated as one.
Formatting all retained.

"""

import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

# Create the root Tk window
root = Tk()

# Hide the root Tk window
root.withdraw()

# Bring the Tkinter window to the front
root.lift()

# Open a file dialog for CSV or Parquet files
file_paths = askopenfilenames(
    filetypes=[("CSV files", "*.csv"),
               ("Parquet files", "*.parquet"),
               ("txt files", "*.txt")])
# Check if a file was selected

for file_path in file_paths:
    if file_path:
        # Determine the file type
        if file_path.endswith('.csv'):
            # Read the CSV file with pandas
            df = pd.read_csv(file_path)
            # Convert to Parquet and save
            df.to_parquet(file_path.replace(".csv", ".parquet"))
        elif file_path.endswith('.txt'):
            # Read the tx file with pandas
            try:
                df = pd.read_csv(file_path, sep='\t',
                                 header=None)
            except:
                df = pd.read_csv(file_path, sep='\\s+',
                                 header=None)
            df.to_parquet(file_path.replace(".txt", ".parquet"))
        elif file_path.endswith('.parquet'):
            # Read the Parquet file with pandas
            df = pd.read_parquet(file_path)
            df.to_csv(file_path.replace(".parquet", ".csv"), index=False)
        print(df.info())
        print(df.head())



