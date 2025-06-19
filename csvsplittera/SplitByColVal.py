#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 12:16:29 2024

@author: rbj

Currently splitting on "Channel 1"
Requires a time column called "Time"

"""
import numpy as np
import pandas as pd
from tkinter import filedialog
from tkinter import Tk
from tkinter import simpledialog

def split_csv_on_column_value(file_path, column_name, split_value):
    # Read the CSV file
    df = pd.read_csv(file_path)
    df[column_name] = (df[column_name].round(-1)).astype(int)
    # Split the dataframe based on the split value and write to separate CSV files
    subset_df = df[df[column_name] == split_value]
    average_interval = df["Time"].diff().mean()
    subset_df.loc[:, "Time"] = np.arange(0, len(subset_df) * average_interval, average_interval)
    subset_df.to_csv(f"{file_path}_{split_value}.csv", index=False)

def main():
    # Create a GUI for file dialog
    root = Tk()
    root.withdraw()  # Hide the main window
    root.update()
    file_path = filedialog.askopenfilename()  # Show the file dialog

    # Ask the user for the split value
    split_value = simpledialog.askinteger("Input", "Enter the split value")

    # Call the function to split the CSV file
    split_csv_on_column_value(file_path, "Channel 1", split_value)

    root.destroy()

if __name__ == "__main__":
    main()
