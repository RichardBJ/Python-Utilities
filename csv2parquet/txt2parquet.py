#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 12:03:14 2024

@author: rbj
"""
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
import pandas as pd

def open_file_dialog():
    app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    file_dialog.setNameFilter("Tab-Delimited Files (*.txt *.tsv *.tab)")
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    if file_dialog.exec_():
        selected_file = file_dialog.selectedFiles()[0]
        return selected_file
    else:
        return None

def main():
    selected_file = open_file_dialog()
    if selected_file:
        df = pd.read_csv(selected_file, sep='\t')
        df.columns = ["Time", "Noisy Current"]
        output_file = selected_file.rsplit('.', 1)[0] + '.parquet'
        df.to_parquet(output_file)
        print(f"File converted and saved as {output_file}")
    else:
        print("No file selected.")

if __name__ == '__main__':
    main()