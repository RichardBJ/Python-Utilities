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
from scipy.stats import linregress
import tkinter as tk
from tkinter.filedialog import askopenfilename
from PyQt5.QtCore import Qt

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class ApplicationWindow(QWidget):
    def __init__(self, df, signal_column, threshed_col):
        super().__init__()
        self.df = df
        self.signal_column = signal_column
        self.threshed_col = threshed_col
        self.threshold = df[signal_column].median()  # Initial threshold
        self.df[self.threshed_col] = np.where(self.df[self.signal_column] > self.threshold, 1, 0)
        self.inflection_points = [(0, self.threshold)]
        self.selected_inflection_index = None
        self.point_index = None
        self.max = self.df[signal_column].max()


        # Create the matplotlib FigureCanvas object
        self.canvas = MplCanvas(self)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)

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
        # Plot the signal and the thresholded signal
        self.canvas.axes.plot(self.df[self.signal_column], 'b')
        self.canvas.axes.plot(self.df[self.threshed_col], 'r')

        # Plot the regression line segments
        for i in range(len(self.inflection_points) - 1):
            x1, y1 = self.inflection_points[i]
            x2, y2 = self.inflection_points[i + 1]

            self.canvas.axes.plot([x1, x2], [y1, y2], color='g')  # Draw the actual threshold in green

            if (x1, y1) == self.selected_inflection_index:
                self.canvas.axes.plot(x1, y1, 'ro', markersize=10)  # Change color and size for selected inflection point
            else:
                self.canvas.axes.plot(x1, y1, 'go', markersize=5)
            if (x2, y2) == self.selected_inflection_index:
                self.canvas.axes.plot(x2, y2, 'ro', markersize=10)  # Change color and size for selected inflection point
            else:
                self.canvas.axes.plot(x2, y2, 'go', markersize=5)

            # Calculate the regression line equation for the segment
            slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
            intercept = y1 - slope * x1

            # Plot the regression line segment
            segment_indices = (self.df.index >= x1) & (self.df.index < x2)
            x_values = self.df.loc[segment_indices, :].index.values
            y_values = slope * x_values + intercept
            self.canvas.axes.plot(x_values, y_values, 'g', label='Regression Line Segment')

        # Restore the x-axis limits
        self.canvas.axes.set_xlim(xlim)
        # Redraw the canvas
        self.canvas.draw()

    def calculate_regression_line(self):
        x_values = [x for x, y in self.inflection_points]
        y_values = [y for x, y in self.inflection_points]
        slope, intercept, _, _, _ = linregress(x_values, y_values)
        return slope, intercept

    def update_thresholded_signal(self):
        for i in range(len(self.inflection_points) - 1):
            x1, y1 = self.inflection_points[i]
            x2, y2 = self.inflection_points[i + 1]

            # Calculate the regression line equation for the segment
            slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
            intercept = y1 - slope * x1

            # Update the thresholded signal for the segment
            segment_indices = (self.df.index >= x1) & (self.df.index < x2)
            x_values = self.df.loc[segment_indices, :].index.values
            threshold_values = slope * x_values + intercept
            self.df.loc[segment_indices, self.threshed_col] = (self.df.loc[segment_indices, self.signal_column].values >= threshold_values).astype(int)*self.max

    def onclick(self, event):
        # Check if the click is inside the axes
        if event.xdata is None or event.ydata is None:
            self.selected_inflection_point = None
            return

        # Check if the click is near an existing inflection point
        nearest_inflection_point = None
        nearest_distance = float('inf')
        p=0
        for x, y in self.inflection_points:
            distance = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_inflection_point = (x, y)
                self.point_index = p
            p+=1

        if nearest_distance < 100:
            self.selected_inflection_index = nearest_inflection_point
        else:
            self.selected_inflection_index = None

        # If no inflection point is selected, add a new one
        if self.selected_inflection_index is None:
            self.threshold = event.ydata
            self.inflection_points.append((event.xdata, self.threshold))
            self.inflection_points.sort()  # Ensure the inflection points are in order

        # If this is the first point we are adding set the entry point too
        if len(self.inflection_points) > 1:
            zero =  (0,self.inflection_points[1][1])
            self.inflection_points[0] = zero

        # Update the thresholded signal based on the inflection points
        self.update_thresholded_signal()

        # Redraw the plot
        self.draw_plot()

    def on_key_press(self, event):
        if event.key == ' ':
            self.remove_inflection_point()

    """ ORIGINAL VERSION
    def update_thresholded_signal(self):
        for i in range(len(self.inflection_points) - 1):
            x1, y1 = self.inflection_points[i]
            x2, y2 = self.inflection_points[i + 1]
            self.df.loc[(self.df.index >= x1) & (self.df.index < x2), self.threshed_col] = np.where(
                self.df.loc[(self.df.index >= x1) & (self.df.index < x2), self.signal_column] >= y1, 1, 0)
    """
    def remove_inflection_point(self):
        if self.selected_inflection_index is not None:
            del self.inflection_points[self.point_index]
            self.point_index = None
            self.selected_inflection_index = None
            self.update_thresholded_signal()
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
    if "Channels" in df.columns:
        threshed_col = "Thresholded"
    else:
        threshed_col = "Channels"

    # Create the application
    app = QApplication(sys.argv)
    window = ApplicationWindow(df, signal_column, threshed_col)
    window.show()

    # Start the application
    app.exec_()

    # Save the DataFrame with the new thresholded column to a new file
    new_filename = filename.rsplit('.', 1)[0] + '_IDL.parquet'
    df.to_parquet(new_filename)

if __name__ == '__main__':
    main()
