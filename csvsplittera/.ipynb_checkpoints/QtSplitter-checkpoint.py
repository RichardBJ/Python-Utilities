# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 14:49:40 2024

@author: rbj
"""
import pandas as pd
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QApplication
import os
import math
import numpy as np
"""
splits parquet format files. Also this version assumes there is
a Time column. Set the number of splits within the code as indicated.
Output will be a set of parquet files with {number} at the end.

"""

app = QApplication([])

# Open file dialog to select the parquet file
file_dialog = QFileDialog()
parquet_file_path, _ = file_dialog.getOpenFileName()
# Define the number of splits
num_splits = 50  # Change this to your desired number of splits
if parquet_file_path:
    # Read the parquet file
    print(f"Reading file {parquet_file_path}")
    df = pd.read_parquet(parquet_file_path)
    print("File read")
    # Calculate the length of each split
    split_len = math.floor(len(df) / num_splits)
    si = (df["Time"][100]-df["Time"][50])/50
    # Split the dataframe and save each split
    for i, start in enumerate(range(0, len(df), split_len), 1):
        df_split = df.iloc[start:start + split_len]
        split_file_path = f"{os.path.splitext(parquet_file_path)[0]}_{i}.parquet"
        df_split.loc[:,"Time"] = np.arange(0, len(df_split)*si, si)
        df_split.reset_index(drop=True, inplace=True)
        df_split.to_parquet(split_file_path)

    print(f"Split the file into {i} parts.")
else:
    print("No file selected.")
