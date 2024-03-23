# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 16:19:49 2024

@author: rbj
"""
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class ApplicationWindow(QWidget):
    def __init__(self, df, signal_column):
        super().__init__()
        self.df = df
        self.signal_column = signal_column
        self.threshold = df[signal_column].median()  # Initial threshold
        self.df['Thresholded Signal'] = np.where(self.df[self.signal_column] > self.threshold, 1, 0)

        # Create the matplotlib FigureCanvas object
        self.canvas = MplCanvas(self)
        self.canvas.mpl_connect('button_press_event', self.onclick)

        # Create a vertical box layout and add the canvas
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)

        # Draw the initial plot
        self.draw_plot()

    def draw_plot(self):
        # Clear the canvas
        self.canvas.axes.clear()

        # Plot the signal and the threshold
        self.canvas.axes.plot(self.df[self.signal_column], 'b')
        self.canvas.axes.plot(self.df['Thresholded Signal'], 'r')

        # Redraw the canvas
        self.canvas.draw()

    def onclick(self, event):
        # Update the threshold with the y-coordinate of the click
        self.threshold = event.ydata
        self.df['Thresholded Signal'] = np.where(self.df[self.signal_column] > self.threshold, 1, 0)

        # Redraw the plot with the new threshold
        self.draw_plot()

def main():
    # Use tkinter to get the filename
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    # Open a file dialog to select the CSV file
    filename = askopenfilename(filetypes=[("CSV files", "*.csv"), 
                                      ("Parquet files", "*.parquet"),
                                      ("Feather files", "*.feather")])
    root.destroy()
    # Load the data
    if "csv" in filename.lower():
        df = pd.read_csv(filename)
    elif "parquet" in filename.lower():
        df = pd.read_parquet(filename)
    else:
        df = pd.read_feather(filename)
    signal_column = 'Noisy Current'  # Replace with your column name

    # Create the application
    app = QApplication(sys.argv)
    window = ApplicationWindow(df, signal_column)
    window.show()

    # Start the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
