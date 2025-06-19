#!/usr/bin/env python3
#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 09:12:56 2024

@author: rbj
"""
import pandas as pd
import numpy as np
import os
import sys
from scipy import signal
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog
USESCIPY = True


def write_data(augment:pd.DataFrame, file:str, index) -> int:
    newfile = file.replace(".parquet","")
    # Save the modified DataFrame to a new Parquet file
    new_filename = f"{newfile}_aug{index}.parquet"
    # Specify the directory where you want to save the files
    output_directory = "."
    new_file_path = os.path.join(output_directory, new_filename)
    augment.to_parquet(new_file_path, engine="auto", compression="snappy", index=False)
    return 0

def shrink_df(df, factor):
    squeeze = int(1/factor)
    aug_df = df.iloc[::squeeze]
    aug_df = aug_df.reindex()
    return aug_df

def stretch_df(df, factor):
    nTime = np.linspace(0, max(df["Time"]),
        int(len(df)*factor), endpoint=True)
    # Create a new DataFrame to hold resampled data
    aug_df=pd.DataFrame(np.nan,
                     index=np.arange(int(len(df)*factor)), columns=df.columns)
    # Resample each column
    for column in df.columns:
        if df[column].name.lower() == "time":
            aug_df[column]=nTime
        elif df[column].dtypes == 'object':
           #It must be the state column
           aug_df[column] = ["C0"]*len(nTime)
        elif df[column].name.lower() == 'channels':
            write_indices = aug_df.index[aug_df.index % factor == 0]
            aug_df.loc[write_indices,column]= df.loc[:,column].values
            aug_df.loc[:,column]=aug_df.loc[:,column].ffill()
        elif df[column].name.lower() == 'noisy current':
            resampled_data = signal.resample(df[column], len(nTime))
            aug_df[column] = resampled_data
    return aug_df

def augment_dataframe(file, df, num_copies, timef, noisef):
    # Process each desired copy
    print(f"Processing {file}")
    for i in range(1, num_copies + 1):
        # resample first
        # Create a new index with double the length (upsampling by a factor of 2)
        if not USESCIPY:
            new_index = np.arange(0, len(df) * 2, 2)
            # Reindex the noisy signal with the new index
            upsampled_signal = df.reindex(new_index)
             # Interpolate or fill missing values (e.g., using linear interpolation)
            df = upsampled_signal.interpolate(method='linear')
        else:
            #Make the new output factor times as long
            factor = np.random.uniform(1 - (timef/100), 1 + (timef/100) )
            print(f"Time stretch factor = {factor}")
            if factor < 1:
                aug_df = shrink_df(df, factor)
            elif factor == 1:
                pass
            else:
                factor = int(factor)
                aug_df= stretch_df(df, factor)

        # Generate random numbers between -0.1 and +0.1
        mean = df["Noisy Current"].mean()
        random_values = np.random.uniform(low=-noisef*mean, high=noisef*mean, size=len(aug_df))

        # Add the random values to the 'Channel 0' column
        aug_df["Noisy Current"] += random_values

        write_data(aug_df, file, i)
    return 0

def process_and_save_selected_dataframes():
    app = QApplication(sys.argv)
    # Ask the user to select specific Parquet files for processing
    selected_files, _ = QFileDialog.getOpenFileNames(None, "Select Parquet files to process", "", "Parquet files (*.parquet)")
    copies, ok = QInputDialog.getInt(None, "Number of copies", "Integer value:")
    if not ok:
        sys.exit("No copies set")
        
    timeflex, ok = QInputDialog.getInt(None, "Percentage time wobble % (int)", "Integer value:")
    if not ok or timeflex == 0:
        sys.exit("No timeflex set")
        
    noiseadd, ok = QInputDialog.getDouble(None, "Noise fractise of current noixd", "float value:")
    if not ok or noiseadd <= 0:
        sys.exit("No noise set")
        
    # Check if any files were selected
    if not selected_files:
        print("No files selected. Exiting.")
        return

    # Process each selected Parquet file
    for j, selected_file in enumerate(selected_files):
        print(f"Processing file {j+1} of {len(selected_files)}")
        filename = os.path.basename(selected_file)
        try:
            # Read the selected Parquet file into a pandas DataFrame
            df = pd.read_parquet(selected_file)
            augment_dataframe(selected_file, df, copies, timeflex, noiseadd)
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    process_and_save_selected_dataframes()
