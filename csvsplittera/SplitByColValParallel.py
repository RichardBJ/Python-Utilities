#!/usr/bin/env python3
#!/usr/bin/env python3
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
from tkinter import Tk, simpledialog, messagebox
from scipy.signal import butter, filtfilt

# Define the filter
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Parameters
order = 6
cutoff = 1000.0   # desired cutoff frequency of the filter, Hz



def Do_preprocess(dataIn, column="Channel 0"):
    print("preprocessing")
    dataOut = []
    for df in dataIn:
        if len(df)>100:
            df = df.reset_index(drop=True)
            mean = df[column].mean()
            sd = df[column].std()
    
            # Identify outliers
            outliers = df[column] > mean + 6 * sd
    
            # Replace outliers with mean
            df.loc[outliers, column] = mean
            
            # Assuming 'df' is your DataFrame and 'column' is the column of interest
            fs = 1 / ((df['Time'][10] - df['Time'][0])/10)  # calculate the sample rate
            print(fs)
            # Get the filter coefficients 
            b, a = butter_lowpass(cutoff, fs, order)
    
            # Assuming 'df' is your DataFrame and 'column' is the column of interest
            df.loc[:, column] = butter_lowpass_filter(df[column], cutoff, fs, order)
            dataOut.append(df)
        
    return dataOut
    
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

def split_csv_on_column_value(file_path, column_name, split_value, dead_time, 
                              parquet, preprocess):
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
    if preprocess:
        list_of_dfs = Do_preprocess(list_of_dfs)
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
    file_paths = filedialog.askopenfilenames(filetypes=[("parquet files", "*.parquet"),("csv files", "*.csv")])  # Show the file dialog
    if file_paths == "":
        sys.exit("No files")

    # Ask the user for the split value
    split_value = simpledialog.askinteger("Input", "Split value", initialvalue=60)
    root.update()
    # Ask the user for the top to chop
    dead_time = simpledialog.askfloat("Input", "Dead Time (s)", initialvalue=0.05)
    root.update()
    print(f'Dead time is {dead_time}s')
    preprocess = messagebox.askyesno("Question", "Preprocess?")
    root.update()
    for file_path in file_paths:
        print(file_path)
        parquet = False
        if "parquet" in file_path.lower():
            parquet = True
        # Call the function to split the CSV file
        split_csv_on_column_value(file_path, "Channel 1",
                                  split_value, dead_time, parquet, preprocess)

    root.destroy()

if __name__ == "__main__":
    main()