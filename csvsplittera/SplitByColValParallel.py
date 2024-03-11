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


def split_dataframe(df, indices):
    indices = sorted(indices)
    dfs = []
    start = 0
    for index in indices:
        if (index - start) > 1000:
            dfs.append(df.iloc[start:index])
            start = index
    if (len(df) - start) > 1000:
        dfs.append(df.iloc[start:])
    return dfs

def split_csv_on_column_value(file_path, column_name, split_value):
    # Read the CSV file
    df = pd.read_csv(file_path)
    df[column_name] = (df[column_name].round(-1)).astype(int)
    # Split the dataframe based on the split value and write to separate CSV files
    subset_df = df[df[column_name] == split_value]
    subset_df["Interval"] = subset_df["Time"].diff().fillna(6)
    #.shift(-1).fillna(subset_df["Time"].min())
    indices = subset_df[subset_df['Interval'] > 0.01].index
    list_of_dfs = split_dataframe(subset_df, indices)
    new_df = pd.DataFrame()

    for idx, idf in enumerate(list_of_dfs):
        cname = f"{column_name}{chr(idx + 97)}"
        print(cname)
        print(idf.head())
        if len(idf)>1000:
            new_df[cname]=idf["Channel 0"].reset_index(drop=True).fillna(0)
    average_interval = df["Time"].diff().mean()
    new_df["Time"] = [i*average_interval for i in range(len(new_df))]
    # Move it to front
    col = new_df.pop("Time")
    new_df.insert(0,"Time",col)
    # subset_df.loc[:, "Time"] = np.arange(0, len(subset_df) * average_interval, average_interval)
    new_df.to_csv(f"{file_path}_{split_value}.csv", index=False)

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