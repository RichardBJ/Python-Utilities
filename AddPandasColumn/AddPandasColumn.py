# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 10:36:04 2024

@author: rbj

SUGGEST RUN IN DEBUG MODE AND CHECK OUTPUT BEFORE "GOING"
RUNS ON PARQUET ONLY

"""
import tkinter as tk
from tkinter import filedialog
import pandas as pd

def select_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(filetypes=[('Parquet Files', '*.parquet')])
    return file_paths

def add_column(file_paths):
    for file_path in file_paths:
        df = pd.read_parquet(file_path)
        df['Channels'] = 0
        df['Channels'] = df['Channels'].astype('int8')
        # RECOMMEND BREAKPOINT AND INSPECT BEFORE CONTINUING 
        # WITH df.head() and df.info()
        print(df.head())
        print(df.info())
        df.to_parquet(file_path.replace(".parquet","_a.parquet"))

def main():
    file_paths = select_files()
    add_column(file_paths)

if __name__ == "__main__":
    main()

