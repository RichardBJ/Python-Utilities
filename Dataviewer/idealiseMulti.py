# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 16:19:49 2024
@author: rbj
"""

import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QSlider, QLabel, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from scipy.stats import linregress
import tkinter as tk
from tkinter.filedialog import askopenfilename
from PyQt5.QtCore import Qt

# Create the QApplication instance before any QWidget instances
app = QApplication(sys.argv)

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
        self.numeric_key_pressed = False
        self.threshold = df[signal_column].median()  # Initial threshold
        # Initial threshold set
        self.thresholds = [df[signal_column].median()]  
        self.selected_threshold_index = 0
        self.threshold_indexes = [0]
        self.df[self.threshed_col] = np.where(self.df[self.signal_column] > self.threshold, 1, 0)
        self.inflection_points = {0: [(0, self.threshold)]}  # Inflection points for each threshold
        self.selected_inflection_index = None
        self.point_index = None

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

        
        # Plot the inflection points and threshold lines
        for threshold_index, inflection_points in self.inflection_points.items():
            inflection_points.sort(key=lambda x: x[0])
            x_values, y_values = zip(*inflection_points)
            self.canvas.axes.plot(x_values, y_values, 'ko', markersize=5)  # Plot inflection points as black dots
            self.canvas.axes.plot(x_values, y_values, 'k-', drawstyle='steps-post')  # Draw threshold line connecting inflection points
    
        # Restore the x-axis limits
        self.canvas.axes.set_xlim(xlim)
        # Redraw the canvas
        self.canvas.draw()

    def calculate_regression_line(self, threshold_index):
        x_values = [x for x, y in self.inflection_points[threshold_index]]
        y_values = [y for x, y in self.inflection_points[threshold_index]]
        slope, intercept, _, _, _ = linregress(x_values, y_values)
        return slope, intercept

    def create_threshold(self):
        # Initialize the x and y arrays
        x = []
        y = []
 
        inflection_points = self.inflection_points[self.selected_threshold_index].copy()
        if inflection_points[-1][0] < len(self.df)-1:
            inflection_points.append((len(self.df)-1,inflection_points[-1][1]))
             
        # Loop through each segment defined by the inflection points
        for i in range(len(inflection_points)):
            # Get the start and end points for the current segment
            start_point = inflection_points[i]
            end_point = inflection_points[i + 1] if i + 1 < len(inflection_points) else None
            
            # Determine the range of x values for the current segment
            x_range = range(start_point[0], end_point[0] if end_point else start_point[0] + 1)
            
            # Extend the x array
            x.extend(x_range)
            
            # Extend the y array with repeated y values from the start point
            y.extend([start_point[1]] * len(x_range))
        self.thresholds[self.selected_threshold_index] = y

    def update_thresholded_signal(self):
        self.df[self.threshed_col] = 0  # Reset the thresholded column
        sorted_thresholds = [sorted(threshold) for threshold in self.thresholds]
    
        for i, threshold in enumerate(sorted_thresholds):
            self.df[self.threshed_col] = \
                np.where(self.df[self.signal_column].values > threshold,\
                                                  i + 1, 0) #Not zero just unchanged!
            #so need to add these columns more inelligently!

    def onclick(self, event):
        # Check if the click is inside the axes
        if event.xdata is None or event.ydata is None:
            self.selected_inflection_index = None
            return

        # Add a new inflection point for the selected threshold
        if self.numeric_key_pressed:
            self.inflection_points[self.selected_threshold_index].append((int(event.xdata), event.ydata))
            self.inflection_points[self.selected_threshold_index]=\
                sorted(self.inflection_points[self.selected_threshold_index],\
                       key = lambda point: point[0])
            self.selected_inflection_index = None
            self.create_threshold()
            self.update_thresholded_signal()
            self.draw_plot()
            self.numeric_key_pressed = False

    def on_key_press(self, event):
        if event.key.isdigit():
            threshold_index = int(event.key) - 1
            """Do we already have this many thresholds if not add"""
            if threshold_index >= len(self.thresholds):
                for index in range(len(self.thresholds), threshold_index + 1):
                    self.thresholds.append(self.df[self.signal_column].median())
                    self.inflection_points[index] = [(0, self.thresholds[index])]
                
            self.selected_threshold_index = threshold_index
            self.numeric_key_pressed = True
        elif event.key.isalpha():
            self.update_thresholded_signal()
            self.numeric_key_pressed = False
        elif event.key == ' ':
            self.remove_inflection_point()
            self.numeric_key_pressed = False

    def remove_inflection_point(self):
        if self.selected_inflection_index is not None:
            del self.inflection_points[self.selected_threshold_index][self.point_index]
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

    """No work: Nothing shows!!!"""
    msgBox = QMessageBox()
    msgBox.setText("Hit a numeric key to choose the threshold you are working\nand then left click to set the actual threshold level")
    msgBox.setWindowTitle("Instructions")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()

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

    # Create the application window
    window = ApplicationWindow(df, signal_column, threshed_col)
    window.show()

    # Start the application
    sys.exit(app.exec_())

    # Save the DataFrame with the new thresholded column to a new file
    new_filename = filename.rsplit('.', 1)[0] + '_IDL.parquet'
    df.to_parquet(new_filename)

if __name__ == '__main__':
    main()