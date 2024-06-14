# -*- coding: utf-8 -*-
"""
Created on Tue May 28 16:47:21 2024
@author: rbj
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import random
import pyarrow.parquet as pq
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

MAXSIZE = 50000
ONLYNEW = True

def plot_and_save(df, x_col, y_cols, filename):
    print(f"plotting df. Shape is {df.shape}")
    fig, axes = plt.subplots(nrows=len(y_cols), ncols=1, figsize=(20, 5*len(y_cols)), sharex=True)
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    for i, y_col in enumerate(y_cols):
        axes[i].plot(df[x_col], df[y_col], label=y_col)
        axes[i].set_ylabel(y_col)
        axes[i].legend()
    n_ticks = 10  
    axes[-1].set_xlabel(x_col)  
    
    # Get the data range
    x_min, x_max = axes[-1].get_xlim()
    
    # Create fixed ticks
    ticks = np.linspace(x_min, x_max, n_ticks)
    
    # Round the ticks to a reasonable precision (optional)
    ticks = np.round(ticks, decimals=1)  # Round to 1 decimal place
    
    # Format the labels
    labels = [f'{tick:.1f}' for tick in ticks]
    
    # Set the ticks and labels
    axes[-1].set_xticks(ticks)
    axes[-1].set_xticklabels(labels)
    
    # Optionally, rotate labels if they overlap
    plt.xticks(rotation=45)
    title = os.path.basename(filename)
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def main():
    app = QApplication([])
    files, _ = QFileDialog.getOpenFileNames(None, "Select Files", "", "Parquet Files (*.parquet)")
    files = sorted(files, key=lambda x: random.random())
    y_cols = []
    x_col = None
    if files:
         # New code to create a dialog box
        msgBox = QMessageBox()
        msgBox.setText("Should ONLYNEW be True or False?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            ONLYNEW = True
        else:
            ONLYNEW = False
        df = pd.read_parquet(files[0])
        print("Columns in the DataFrame: ", df.columns.tolist())
        num_cols = input("How many Y columns do you want to plot? ")
        num_cols = int(num_cols)
        while x_col not in df.columns.tolist():
            x_col = input("Enter the name of the column for the x-axis: ")
        for _ in range(num_cols):
            y_col = input(f"Enter the name of the column for the y{len(y_cols)+1}-axis: ")
            while y_col not in df.columns.tolist():
                y_col = input(f"Invalid column name. Enter the name of the column for the y{len(y_cols)+1}-axis: ")
            y_cols.append(y_col)
        
        for i, file in enumerate(files):
            print(f"File {i} of {len(files)}")
            print(f"processing file: {file}")
            outfile = file.replace(".parquet", ".png")
            if os.path.isfile(outfile) and ONLYNEW:
                print(f"{file} already done, skipping")
                continue
                """skip if already present"""
            parquet_file = pq.ParquetFile(file)
                    
            for j, batch in enumerate( parquet_file.iter_batches()):
                print(f"Processing batch {j}")
                new_batch_df = batch.to_pandas()
                if j==0:
                    df = new_batch_df
                else:
                    df = pd.concat([df,new_batch_df],axis=1)
                if len(df) > MAXSIZE:
                    print("Cropping to size")
                    df = df[:MAXSIZE]
                    break
            """
            data = pq.read_table(file)
            try:
                df = data.to_pandas()[:MAXSIZE]
            except:
                print("EXCEPTION: Assume this was a very short file?")
                df = data.to_pandas()
            """
            try:
                plot_and_save(df, x_col, y_cols, outfile)
            except:
                print(f"Seems there was an error with {file}")
                continue

if __name__ == "__main__":
    main()