#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qt-based Channel Modifier - Adds an integer value to the Channels column in CSV/Parquet files
"""

import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QApplication, QInputDialog, QMessageBox
import os
import numpy as np
from pathlib import Path

def modify_channels_file(file_path, channels_increment):
    """
    Modify the Channels column by adding an integer value and save in place.
    """
    file_path = Path(file_path)
    
    print(f"\nProcessing file: {file_path.name}")
    
    try:
        # Read the file based on extension
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.parquet', '.pq']:
            df = pd.read_parquet(file_path)
        else:
            print(f"Unsupported file type: {file_path.suffix}")
            return False
        
        print("File read successfully")
        
        # Rename columns if they don't match expected format
        if len(df.columns) >= 2 and df.columns[1] != "Channels":
            # Assume standard format: Time, Channels, Noisy Current (or similar)
            if len(df.columns) >= 3:
                df.columns = ['Time', 'Channels', 'Noisy Current']
            else:
                df.columns = ['Time', 'Channels']
            print("Renamed columns to standard format")
        
        # Check if Channels column exists
        if 'Channels' not in df.columns:
            print("Error: 'Channels' column not found in file")
            return False
        
        # Get original Channels column info
        original_dtype = df['Channels'].dtype
        original_min = df['Channels'].min()
        original_max = df['Channels'].max()
        
        print(f"Original Channels range: {original_min} to {original_max}")
        
        # Modify the Channels column
        df['Channels'] = (df['Channels'] + channels_increment).round().astype(int)
        
        
        # Show new range
        new_min = df['Channels'].min()
        new_max = df['Channels'].max()
        print(f"New Channels range: {new_min} to {new_max}")
        
        # Save the file back in place
        if file_path.suffix.lower() == '.csv':
            df.to_csv(file_path, index=False)
        else:  # parquet
            df.to_parquet(file_path)
        
        print(f"Successfully updated {file_path.name}")
        return True
    
    except Exception as e:
        print(f"\nError processing {file_path.name}: {str(e)}")
        # Print more detailed error information
        import traceback
        print(f"Detailed error:\n{traceback.format_exc()}")
        return False

def process_multiple_files(file_paths, channels_increment):
    """
    Process multiple files and modify the Channels column in each.
    """
    print(f"\nStarting to process {len(file_paths)} files...")
    print(f"Adding {channels_increment} to Channels column in each file")
    
    successful = 0
    failed = 0
    failed_files = []
    
    for file_path in file_paths:
        result = modify_channels_file(file_path, channels_increment)
        if result:
            successful += 1
        else:
            failed += 1
            failed_files.append(Path(file_path).name)
    
    print(f"\nProcessing complete:")
    print(f"Successfully processed: {successful} files")
    print(f"Failed to process: {failed} files")
    
    if failed_files:
        print(f"Failed files: {', '.join(failed_files)}")
    
    return successful, failed, failed_files

def main():
    # Initialize Qt application
    app = QApplication([])
    
    # Get the increment value for Channels column
    channels_increment, ok = QInputDialog.getInt(
        None,  # parent widget
        "Channels Increment",  # dialog title
        "Enter the value to add to each Channels value:",  # prompt text
        1,     # default value
        -1000000,  # minimum value
        1000000,   # maximum value
        1      # step
    )
    
    if not ok:
        print("Channels increment selection cancelled.")
        return
    
    # Confirm the operation since it modifies files in place
    reply = QMessageBox.question(
        None,
        "Confirm Operation",
        f"This will add {channels_increment} to the Channels column in all selected files.\n"
        f"Files will be modified in place (no backup will be created).\n\n"
        f"Do you want to continue?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if reply != QMessageBox.Yes:
        print("Operation cancelled by user.")
        return
    
    # Open file dialog to select multiple files
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_dialog.setNameFilter("Data files (*.csv *.parquet *.pq)")
    file_dialog.setWindowTitle("Select files to modify")
    
    if file_dialog.exec_():
        file_paths = file_dialog.selectedFiles()
        if file_paths:
            successful, failed, failed_files = process_multiple_files(file_paths, channels_increment)
            
            # Show final results in a message box
            if failed == 0:
                QMessageBox.information(
                    None,
                    "Operation Complete",
                    f"Successfully processed all {successful} files!\n"
                    f"Added {channels_increment} to Channels column in each file."
                )
            else:
                QMessageBox.warning(
                    None,
                    "Operation Complete with Errors",
                    f"Successfully processed: {successful} files\n"
                    f"Failed to process: {failed} files\n\n"
                    f"Failed files: {', '.join(failed_files[:5])}"
                    + ("..." if len(failed_files) > 5 else "")
                )
        else:
            print("No files selected.")
    else:
        print("File selection cancelled.")

if __name__ == "__main__":
    main()