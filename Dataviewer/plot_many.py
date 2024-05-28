# -*- coding: utf-8 -*-
"""
Created on Tue May 28 16:47:21 2024

@author: rbj
"""
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QFileDialog

def plot_and_save(df, x_col, y1_col, y2_col, filename):
    plt.figure()
    plt.plot(df[x_col], df[y1_col], label=y1_col)
    if y2_col:
        plt.plot(df[x_col], df[y2_col], label=y2_col)
    plt.savefig(filename)
    plt.close()

def main():
    app = QApplication([])
    files, _ = QFileDialog.getOpenFileNames(None, "Select Files", "", "Parquet Files (*.parquet)")
    y1_col, y2_col = None,  None
    x_col=None
    if files:
        df = pd.read_parquet(files[0])
        print("Columns in the DataFrame: ", df.columns.tolist())
        cols = input("plot how many Y columns? (1 or 2):")
        cols = int(cols)
        while x_col not in df.columns.tolist():
            x_col = input("Enter the name of the column for the x-axis: ")
        while y1_col not in df.columns.tolist():
            y1_col = input("Enter the name of the column for the y1-axis: ")
        if cols == 2:
            while y2_col not in df.columns.tolist():
                y2_col = input("Enter the name of the column for the y2-axis: ")
            
        for file in files:
            print(f"processing file: {file}")
            df = pd.read_parquet(file)
            outfile = file.replace(".parquet", ".png")
            plot_and_save(df, x_col, y1_col, y2_col, outfile)

if __name__ == "__main__":
    main()
