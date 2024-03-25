# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 2024
@author: rbj
"""

import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QSlider, QLabel, QMessageBox, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PyQt5.QtCore import Qt

class ApplicationWindow(QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.numeric_key_pressed = False
        self.threshold_levels = {}
        self.selected_column = None
        self.inflection_points = {}
        self.pressed = False
        self.start_x = None
        self.end_x = None

        # Create the matplotlib FigureCanvas object
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        self.axes = self.figure.add_subplot(111)  # Create the axes here

        self.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.canvas.mpl_connect('button_release_event', self.on_button_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion_notify)
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
        self.window_slider.setValue(int(len(df)/10))  # Set to 10% of the DataFrame length
        self.window_slider.valueChanged.connect(self.update_plot)
        vbox.addWidget(QLabel("Window width:"))
        vbox.addWidget(self.window_slider)

        self.setLayout(vbox)

        # Draw the initial plot
        self.draw_plot()

    def draw_plot(self):
        # Store the current x-axis limits
        xlim = self.axes.get_xlim() if self.axes.get_xlim() != (0, 1) else (0, 1000)
        # Clear the axes
        self.axes.clear()
        # Plot the signal and the thresholded signal
        #I remmoved time from this so X is just datapoints now...
        self.axes.plot(self.df["Noisy Current"], 'b', label="Noisy Current")
        self.axes.plot(self.df["Channels"], 'r', label="Channels")

        # Plot the inflection points and threshold levels
        for column, inflection_points in self.inflection_points.items():
            threshold_level = self.threshold_levels.get(column, self.df[column].median())
            self.axes.axhline(y=threshold_level, color='k', linestyle='--', label=f"{column} Threshold")
            x_values, _ = zip(*inflection_points)
            y_values = [threshold_level] * len(inflection_points)
            self.axes.plot(x_values, y_values, 'ko', markersize=5)  # Plot inflection points as black dots

        # Draw the selection rectangle
        if self.start_x is not None and self.end_x is not None:
            x1, x2 = sorted([self.start_x, self.end_x])
            y1, y2 = self.axes.get_ylim()
            self.axes.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor='r', linewidth=2))

        # Restore the x-axis limits
        self.axes.set_xlim(xlim)
        self.axes.legend()
        # Redraw the canvas
        self.canvas.draw()

    def draw_selection(self, start_x, end_x):
        self.axes.clear()
        self.draw_plot()

        x1, x2 = sorted([start_x, end_x])
        y1, y2 = self.axes.get_ylim()
        self.axes.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor='r', linewidth=2))

        self.canvas.draw()

    def select_region(self, start_x, end_x):
        if self.selected_column is not None:
            x1, x2 = sorted([start_x, end_x])
            mask = (self.df["Time"] >= x1) & (self.df["Time"] <= x2)
            threshold_level = self.df[self.selected_column][mask].median()
            self.threshold_levels[self.selected_column] = threshold_level
            self.inflection_points[self.selected_column] = [(x1, threshold_level), (x2, threshold_level)]
            self.draw_plot()

    def on_button_press(self, event):
        if event.button == 1:  # Left mouse button
            self.pressed = True
            self.start_x = event.xdata

    def on_button_release(self, event):
        if event.button == 1:  # Left mouse button
            self.pressed = False
            self.end_x = event.xdata
            self.select_region(self.start_x, self.end_x)

    def on_motion_notify(self, event):
        if self.pressed:
            self.end_x = event.xdata
            self.draw_selection(self.start_x, self.end_x)

    def on_key_press(self, event):
        if event.key.isdigit():
            column_index = int(event.key) - 1
            if column_index == 0:
                self.selected_column = "Noisy Current"
            elif column_index == 1:
                self.selected_column = "Channels"
            else:
                return

            if self.selected_column not in self.inflection_points:
                self.inflection_points[self.selected_column] = []

            self.numeric_key_pressed = True
        elif event.key == ' ':
            if self.selected_column in self.inflection_points:
                del self.inflection_points[self.selected_column]
            self.selected_column = None
            self.numeric_key_pressed = False
            self.draw_plot()

    def update_plot(self, value):
        # Update the plot based on the scrollbar position and window width
        start = self.scrollbar.value()
        window_width = self.window_slider.value()
        self.axes.set_xlim(start, start + window_width)
        self.canvas.draw()

def main():
    # Open a file dialog to select the CSV file
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.AnyFile)

    if dialog.exec_():
        filename = dialog.selectedFiles()[0]
    else:
        print("No file selected.")
        return

    msgBox = QMessageBox()
    msgBox.setText("Hit a numeric key to choose the column you want to adjust:\n1 - Noisy Current\n2 - Channels\nThen click and drag to select a region.")
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

    # Create the application window
    window = ApplicationWindow(df)
    window.show()

    # Start the application
    app.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main()