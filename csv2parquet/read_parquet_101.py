# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 18:00:44 2024
@author: rbj
Will read parquet files and allow you to probe the dataset
or even save to a CSV

NOTE HAVE TO RESTART KERNEL BETWEEN QT and TK runs!!!
"""

import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilenames

# Create the root Tk window
root = tk.Tk()

# Update the root window to ensure proper initialization on macOS
root.update()

# Hide the root Tk window
root.withdraw()

# Bring the Tkinter window to the front
root.lift()

# Open a file dialog for CSV or Parquet files
file_paths = askopenfilenames(filetypes=[("CSV files", "*.csv"), ("Parquet files", "*.parquet")])

# Ask the user if they want to convert the file
convert = messagebox.askyesno("Convert File", "Do you want to convert the file to another format?")

# Check if files were selected
if file_paths:
    for file_path in file_paths:
        # Determine the file type
        if file_path.endswith('.csv'):
            # Read the CSV file with pandas
            df = pd.read_csv(file_path)
        elif file_path.endswith('.parquet'):
            # Read the Parquet file with pandas
            df = pd.read_parquet(file_path)

        print(file_path)
        print(df.info())
        print(df.head())

        if convert:
            nc = df.shape[1]
            if nc == 3:
                # Then we have Simple time format and wish to convert to Sam format
                df.columns = ["Time", "Noisy Current", "Channels"]
                df['State of Channel 0'] = df.apply(
                    lambda row: f"C{int(row['Channels'])}" if row['Channels'] == 0 else f"O{int(row['Channels'])}",
                    axis=1
                )
            elif nc == 2:
                # Then we have Simple format and need to convert to Sam
                # IT COULD BE time and noisy current
                # or Channel and noisy current. Infer this
                # So to clarify this may be unlabelled real data...
                df.columns = ["Time", "Noisy Current"]
                if df["Time"].is_monotonic_increasing:
                    pass
                else:
                    # If there is no time-base we must add it assuming a sample interval
                    df.columns = ["Noisy Current", "Channels"]
                    df["Time"] = df['Time'] = np.arange(0, len(df) * 50e-6, 50e-6)
            elif nc == 4:
                # I guess we already have Sam format
                df.columns = df.columns
            else:
                print("Unknown file structure")
                print(file_path)
                exit()

            if file_path.endswith('.csv'):
                save_path = file_path.replace('.csv', '.parquet')
            else:
                save_path = file_path.replace('.parquet', '.csv')

            if save_path:
                # Determine the desired output format
                if save_path.endswith('.csv'):
                    # Save as CSV
                    df.to_csv(save_path, index=False)
                elif save_path.endswith('.parquet'):
                    # Save as Parquet
                    df.to_parquet(save_path, index=False)
                else:
                    print("Unsupported file format. Please choose either CSV or Parquet.")
            else:
                print("No save location selected.")
        else:
            print("File not converted.")
else:
    print("No file selected.")

# Quit the Tkinter event loop
root.quit()

# Destroy the Tkinter window
root.destroy()