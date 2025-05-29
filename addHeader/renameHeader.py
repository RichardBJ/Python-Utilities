#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, simpledialog
import pandas as pd

def select_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(filetypes=[('Parquet Files', '*.parquet')])
    return file_paths

def ask_column_names():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    old_name = simpledialog.askstring("Input", "Enter the old column name:")
    new_name = simpledialog.askstring("Input", "Enter the new column name:")
    return old_name, new_name

def add_column(file_paths, old_name, new_name):
    for file_path in file_paths:
        df = pd.read_parquet(file_path)
        df.rename(columns={old_name: new_name}, inplace=True)
        # RECOMMEND BREAKPOINT AND INSPECT BEFORE CONTINUING 
        # WITH df.head() and df.info()
        print(df.head())
        print(df.info())
        df.to_parquet(file_path.replace(".parquet","_r.parquet"))

def main():
    file_paths = select_files()
    old_name, new_name = ask_column_names()
    add_column(file_paths, old_name, new_name)

if __name__ == "__main__":
    main()
