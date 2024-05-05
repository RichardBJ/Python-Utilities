# -*- coding: utf-8 -*-
"""
Created on Sun May  5 09:23:29 2024

@author: rbj
"""
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QTimer
import pandas as pd
from tslearn.metrics import dtw

def calculate_dtw(df, col1, col2,window_size):
    # Calculate DTW distance between the two columns
    # Struggles with memory just use last 10k if more than 10k
    if len(df) > 10000:
        df=df[-10000:]
    dtw_distance = dtw_distance = dtw(
        df.loc[:,col1], df.loc[:,col2],sakoe_chiba_radius = window_size)      
    return dtw_distance

class FileDialogApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.file_path = None

    def get_file_path(self):
        # Open a file dialog to select the Parquet file
        file_dialog = QFileDialog()
        self.file_paths, _ = file_dialog.getOpenFileNames(None, "Select Parquet File", "", "Parquet Files (*.parquet)")
        for file_path in self.file_paths:
            if file_path:
                # Read the Parquet file
                df = pd.read_parquet(file_path)
                window_size = 10
                dtw_distance = calculate_dtw(
                    df, "y_True", "y_Predict", window_size)
                df.plot()
                print(f"DTW distance: {dtw_distance}")
        QTimer.singleShot(0, self.quit)
        self.quit()

if __name__ == "__main__":
    app = FileDialogApp(sys.argv)
    app.get_file_path()
    sys.exit(app.exec_())
