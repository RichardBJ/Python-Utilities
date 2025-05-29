#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 08:10:39 2024

@author: rbj
"""
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
import pandas as pd

def reset_index_parquet_files():
    app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    file_paths, _ = file_dialog.getOpenFileNames(caption="Select Parquet Files", filter="Parquet Files (*.parquet)")

    for file_path in file_paths:
        df = pd.read_parquet(file_path)
        df.reset_index(drop=True, inplace=True)
        df.to_parquet(file_path)

    print("All files have been processed and saved.")
    app.exit()

if __name__ == "__main__":
    reset_index_parquet_files()

