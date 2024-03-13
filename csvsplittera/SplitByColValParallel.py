# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 12:16:29 2024

@author: rbj

Currently splitting on "Channel 1"
Requires a time column called "Time"
Running with 262 PC, py3818 conda environment
will hang if include a really tiny file!
Another warning is this:

 PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use newframe = frame.copy()

new_df["Time"] = [i*average_interval for i in range(len(new_df))]

"""
import sys
import pandas as pd
from tkinter import filedialog
from tkinter import Tk
from tkinter import simpledialog


def split_dataframe(df, indices):
    # Split the subset of data now by index.
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

def split_csv_on_column_value(file_path, column_name, split_value, dead_time, parquet):
    # Read the CSV data
    if parquet:
        df = pd.read_parquet(file_path)

    else:
        df = pd.read_csv(file_path)
    df[column_name] = (df[column_name].round(-1)).astype(int)
    # Split the dataframe based on the split value and write to separate CSV files
    subset_df = df[df[column_name] == split_value].reset_index()
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
    #crop off a leading deadtime
    new_df=new_df[new_df["Time"] > dead_time]
    if parquet:
        fname=file_path.replace(".parquet","")
    else:
        fname=file_path.replace(".csv","")

    new_df.to_csv(f"{fname}_{split_value}.csv", index=False)

def main():
    # Create a GUI for file dialog
    root = Tk()
    root.withdraw()  # Hide the main window
    root.update()
    file_paths = filedialog.askopenfilenames(filetypes=[("csv files", "*.csv"),("parquet files", "*.parquet") ])  # Show the file dialog
    if file_paths == "":
        sys.exit("No files")

    # Ask the user for the split value
    split_value = simpledialog.askinteger("Input", "Split value", initialvalue=60)
    # Ask the user for the top to chop
    dead_time = simpledialog.askfloat("Input", "Dead Time (s)", initialvalue=0.05)
    for file_path in file_paths:
        print(file_path)
        parquet = False
        if "parquet" in file_path.lower():
            parquet = True
        # Call the function to split the CSV file
        split_csv_on_column_value(file_path, "Channel 1",
                                  split_value, dead_time, parquet)

    root.destroy()

if __name__ == "__main__":
    main()