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

def augment_dataframe(file, df, num_copies):
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
            factor = np.random.uniform(0.2, 5)
            nTime = np.linspace(0, max(df["Time"]), 
                int(len(df)*factor), endpoint=True)
            # Create a new DataFrame to hold resampled data
            aug_df = pd.DataFrame()
            
            # Resample each column
            for column in df.columns:
               if df[column].dtypes == 'object':
                   aug_df[column] = ["C0"]*len(nTime)
               else:
                   resampled_data = signal.resample(df[column], len(nTime))
                   aug_df[column] = resampled_data
        #  Dont let the min or max of the Channels column change!
        aug_df["Channels"] = aug_df["Channels"].astype(int)
        low = df["Channels"].min()
        hi = df["Channels"].max()
        aug_df["Channels"] = np.clip(aug_df["Channels"], low, hi)
        aug_df["Time"] = nTime    
        # Modify the 'Channel 0' column (replace with your actual augmentation logic)
        # For example, let's multiply the values by different factors
        # Generate random numbers between -0.1 and +0.1
        mean = df["Noisy Current"].mean()
        random_values = np.random.uniform(low=-0.01*mean, high=0.01*mean, size=len(aug_df))
        
        # Add the random values to the 'Channel 0' column
        aug_df["Noisy Current"] += random_values
          
        newfile = file.replace(".parquet","")
        # Save the modified DataFrame to a new Parquet file
        new_filename = f"{newfile}_aug{i}.parquet"
        # Specify the directory where you want to save the files
        output_directory = "."
        new_file_path = os.path.join(output_directory, new_filename)
        aug_df.to_parquet(new_file_path, engine="auto", compression="snappy")
    return 0

def process_and_save_selected_dataframes():
    app = QApplication(sys.argv)
    # Ask the user to select specific Parquet files for processing
    selected_files, _ = QFileDialog.getOpenFileNames(None, "Select Parquet files to process", "", "Parquet files (*.parquet)")
    copies, ok = QInputDialog.getInt(None, "Number of copies", "Integer value:")
    if not ok:
        sys.exit("No copies set")
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
            augment_dataframe(selected_file, df, copies)
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    process_and_save_selected_dataframes()
