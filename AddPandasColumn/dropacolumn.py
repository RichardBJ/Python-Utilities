#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:38:33 2024

@author: rbj
REMOVE A COLUMN PARQUET ONLY
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
    filetypes=[("Parquet files", "*.parquet")])
for file_path in file_paths:
    if file_path:
            df = pd.read_parquet(file_path)
            df.drop(columns=["Unnamed: 0"], inplace=True)
            df.to_parquet(file_path)
