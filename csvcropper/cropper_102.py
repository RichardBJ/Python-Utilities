# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 18:00:44 2024
@author: rbj
Will read parquet files and allow you to probe the dataset
or even save to a CSV ALL IN SAM FORMAT

NOTE HAVE TO RESTART KERNEL BETWEEN QT and TK runs!!!

THIS WILL OVERWRITE THE ORIGINAL AND CROP bewtween selected points of all files
unless txt which is a pain so saves as parquet
"""

import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilenames

#Use a default sample interval of
SI = 50e-6
# TODO: Display that and check!!

text1 = input("keep FROM X POINT\n")  # Python 3
text2 = input("retain UNTIL X POINT 0=keep until end!\n")

skiprows=int(text1)
until = int(text2)-skiprows

# Create the root Tk window
root = tk.Tk()

# Update the root window to ensure proper initialization on macOS
root.update()

# Hide the root Tk window
root.withdraw()

# Bring the Tkinter window to the front
root.lift()

# Open a file dialog for CSV or Parquet files
file_paths = askopenfilenames(filetypes=[("CSV files", "*.csv"), ("Parquet files", "*.parquet"),("txt files", "*.txt")])

# Convert all file paths to lower case
file_paths = [fp.lower() for fp in file_paths]

# Check if files were selected
if file_paths:
    for file_path in file_paths:
        # Determine the file type
        if file_path.endswith('.csv'):
            # Read the CSV file with pandas
            df = pd.read_csv(file_path)
        if file_path.endswith('.txt'):
            try:
                df = pd.read_csv(file_path, sep='\t')
            except:
                df = pd.read_csv(file_path, sep='\\s+')
        elif file_path.endswith('.parquet'):
            # Read the Parquet file with pandas
            df = pd.read_parquet(file_path)
            
        df.reset_index(drop=True, inplace=True)
        print(file_path)
        print(df.info())
        print(df.head())
        
        if until <= 0:
            #Do until the end
            until = len(df)
        df = df.iloc[skiprows:until,:]

        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.txt'):
            #Hate these ...saving as parquet
            save_path = file_path.replace('.txt', '.parquet')
            df.to_parquet(save_path, index=False)
        elif file_path.endswith('.parquet'):
            # Save as Parquet
            df.to_parquet(file_path, index=False)
        elif file_path.endswith('.feather'):
            # Save as feather
            df.to_feather(file_path, index=False)
            
        else:
            print("unknown file type!?")

else:
    print("No file selected.")

# Quit the Tkinter event loop
root.quit()

# Destroy the Tkinter window
root.destroy()