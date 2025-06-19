#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modified version of QtSplitter.py with type conversion fix
"""

import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QApplication, QInputDialog
import os
import math
import numpy as np
from pathlib import Path

def split_data_file(file_path, num_splits=50):
    """
    Split a CSV or Parquet file into multiple parts with time adjustment.
    """
    file_path = Path(file_path)
    
    # Create splits directory if it doesn't exist
    splits_dir = Path("/mnt/c/trainingstuff/splits")
    splits_dir.mkdir(exist_ok=True)
    
    print(f"\nProcessing file: {file_path.name}")
    
    try:
        # Read the file based on extension with explicit type conversion for Time column
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path, dtype={'Time': float})  # Explicitly convert Time to float
        elif file_path.suffix.lower() in ['.parquet', '.pq']:
            df = pd.read_parquet(file_path)
        else:
            print(f"Unsupported file type: {file_path.suffix}")
            return None
        
        print("File read successfully")
        
        # Rename columns if they don't match expected format
        if df.columns[0] != "Time":
            df.columns = ['Time', 'Channels', 'Noisy Current']
            print("Renamed columns to: Time, Channels, Noisy Current")
            
        # Ensure Time column is numeric
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
        
        # Check for any NaN values after conversion
        if df['Time'].isna().any():
            print("Warning: Some Time values could not be converted to numbers")
            df = df.dropna(subset=['Time'])
            print(f"Dropped {df['Time'].isna().sum()} rows with invalid Time values")
        
        # Calculate split parameters
        split_len = math.floor(len(df) / num_splits)
        
        # More robust sampling interval calculation
        try:
            # Try to calculate si using the first valid pair of points
            for i in range(len(df) - 1):
                if pd.notna(df["Time"].iloc[i]) and pd.notna(df["Time"].iloc[i+1]):
                    si = df["Time"].iloc[i+1] - df["Time"].iloc[i]
                    break
            else:
                # If no valid pair found, use a default value
                si = 1.0
                print("Warning: Could not calculate sampling interval, using default value of 1.0")
        except Exception as e:
            print(f"Warning: Error calculating sampling interval: {e}")
            si = 1.0
        
        # Split and save files
        for i, start in enumerate(range(0, len(df), split_len), 1):
            df_split = df.iloc[start:start + split_len].copy()
            
            # Adjust time values
            df_split.loc[:, "Time"] = np.arange(0, len(df_split) * si, si)
            df_split.reset_index(drop=True, inplace=True)
            
            # Create split filename
            split_file_path = splits_dir / f"{file_path.stem}_split_{i}.parquet"
            
            # Save split
            df_split.to_parquet(split_file_path)
            print(f"Saved split {i}/{num_splits}", end='\r')
        
        print(f"\nCompleted processing {file_path.name}: Created {num_splits} splits")
        return splits_dir
    
    except Exception as e:
        print(f"\nError processing {file_path.name}: {str(e)}")
        # Print more detailed error information
        import traceback
        print(f"Detailed error:\n{traceback.format_exc()}")
        return None

def process_multiple_files(file_paths, num_splits=50):
    """
    Process multiple files and create splits for each.
    """
    print(f"\nStarting to process {len(file_paths)} files...")
    
    successful = 0
    failed = 0
    
    for file_path in file_paths:
        result = split_data_file(file_path, num_splits)
        if result:
            successful += 1
        else:
            failed += 1
    
    print(f"\nProcessing complete:")
    print(f"Successfully processed: {successful} files")
    print(f"Failed to process: {failed} files")
    
def main():
    # Initialize Qt application
    app = QApplication([])
    
     # Number of splits
    num_splits, ok = QInputDialog.getInt(
        None,  # parent widget
        "Number of Splits",  # dialog title
        "Enter the number of splits per file:",  # prompt text
        50,  # default value
        1,   # minimum value
        1000,  # maximum value
        1    # step
    )
    
    if ok:
        # Open file dialog to select multiple files
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Data files (*.csv *.parquet *.pq)")
        
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                process_multiple_files(file_paths, num_splits=num_splits)
            else:
                print("No files selected.")
        else:
            print("File selection cancelled.")
    else:
        print("Split count selection cancelled.")

if __name__ == "__main__":
    main()