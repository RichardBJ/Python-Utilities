# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 18:00:44 2024

@author: rbj
"""
import pandas as pd
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

# Create the root Tk window
root = Tk()

# Hide the root Tk window
root.withdraw()

# Bring the Tkinter window to the front
root.lift()

# Open a file dialog for CSV or Parquet files
file_path = askopenfilename(filetypes=[("CSV files", "*.csv"), ("Parquet files", "*.parquet")])

# Check if a file was selected
if file_path:
    # Determine the file type
    if file_path.endswith('.csv'):
        # Read the CSV file with pandas
        df = pd.read_csv(file_path)
    elif file_path.endswith('.parquet'):
        # Read the Parquet file with pandas
        df = pd.read_parquet(file_path)
    print(df.info())
    print(df.head())
    
    # Ask the user if they want to convert the file
    convert = messagebox.askyesno("Convert File", "Do you want to convert the file to another format?")

    if convert:
        nc = df.shape[1]
        if nc == 3:
            df.columns = ["Time",  "Noisy Current", "Channels"]
        elif nc == 2:
            df.columns =["Time", "Noisy Current"]
        elif nc == 4:
            df.columns=df.columns
        else:
            print("Uknown file structure")
            exit()
        # Open a file dialog for saving the converted file
        save_path = asksaveasfilename(filetypes=[("CSV files", "*.csv"), ("Parquet files", "*.parquet")])

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
