# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 16:19:49 2024

@author: rbj
"""
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QSlider, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename
from PyQt5.QtCore import Qt

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
        self.inflection_points = [(0, self.threshold)]

        # Create the matplotlib FigureCanvas object
        self.canvas = MplCanvas(self)
        self.canvas.mpl_connect('button_press_event', self.onclick)

        # Create a vertical box layout and add the canvas
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)

        # Add navigation toolbar for zooming and panning
        self.toolbar = NavigationToolbar(self.canvas, self)
        vbox.addWidget(self.toolbar)

        # Add a horizontal scrollbar
        self.scrollbar = QSlider(Qt.Horizontal)
        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(len(df) - 1)
        self.scrollbar.valueChanged.connect(self.update_plot)
        vbox.addWidget(QLabel("Scroll:"))
        vbox.addWidget(self.scrollbar)

        # Add a window width slider
        self.window_slider = QSlider(Qt.Horizontal)
        self.window_slider.setMinimum(1)
        self.window_slider.setMaximum(len(df))
        self.window_slider.setValue(1000)
        self.window_slider.valueChanged.connect(self.update_plot)
        vbox.addWidget(QLabel("Window width:"))
        vbox.addWidget(self.window_slider)

        self.setLayout(vbox)

        # Draw the initial plot
        self.draw_plot()

    def draw_plot(self):
        # Store the current x-axis limits
        xlim = self.canvas.axes.get_xlim() if self.canvas.axes.get_xlim() != (0, 1) else (0, 1000)

        # Clear the canvas
        self.canvas.axes.clear()

        # Plot the signal and the threshold
        self.canvas.axes.plot(self.df[self.signal_column], 'b')
        self.canvas.axes.plot(self.df['Thresholded Signal'], 'r')
        for i in range(len(self.inflection_points) - 1):
            x1, y1 = self.inflection_points[i]
            x2, y2 = self.inflection_points[i + 1]
            self.canvas.axes.plot([x1, x2], [y1, y2], color='g')  # Draw the actual threshold in green

        # Restore the x-axis limits
        self.canvas.axes.set_xlim(xlim)

        # Redraw the canvas
        self.canvas.draw()

    def onclick(self, event):
        # Update the threshold with the y-coordinate of the click
        self.threshold = event.ydata

        # Add an inflection point at the x-coordinate of the click
        self.inflection_points.append((event.xdata, self.threshold))
        self.inflection_points.sort()  # Ensure the inflection points are in order

        # Update the thresholded signal based on the new inflection points
        for i in range(len(self.inflection_points) - 1):
            x1, y1 = self.inflection_points[i]
            x2, y2 = self.inflection_points[i + 1]
            self.df.loc[(self.df.index >= x1) & (self.df.index < x2), 'Thresholded Signal'] = np.where(self.df.loc[(self.df.index >= x1) & (self.df.index < x2), self.signal_column] >= y1, 1, 0)

        # Redraw the plot with the new threshold
        self.draw_plot()

    def update_plot(self, value):
        # Update the plot based on the scrollbar position and window width
        start = self.scrollbar.value()
        window_width = self.window_slider.value()
        self.canvas.axes.set_xlim(start, start + window_width)
        self.canvas.draw()

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
