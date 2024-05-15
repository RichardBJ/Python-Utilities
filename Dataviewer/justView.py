# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 2024
@author: rbj
"""
import os
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QSlider, QLabel, QFileDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt

MAXROWS=100000


class ApplicationWindow(QWidget):
    def __init__(self, df, freeformat, filename, file_list):
        super().__init__()
        self.setWindowTitle(filename)
        #maxc = max(abs(df["Channels"].to_numpy()))
        #df["Noisy Current"] = scale(df["Noisy Current"], out_range=(0, maxc))
        self.df = df
        self.filename = filename
        self.file_list = file_list
        self.freeformat = freeformat
        self.current_file_index = file_list.index(filename)

        # Create the matplotlib FigureCanvas object
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        self.axes = self.figure.add_subplot(111)

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
        if not self.freeformat:
            self.corner_points = self.make_corners()

        # Draw the initial plot
        self.draw_plot()

    def make_corners(self):
        x = self.df.index
        try:
            y = self.df["Channels"]
        except:
            #Ot ho perhaps no Channels column,
            print("No Channels Column?")
            corner_points= [(0,0),(max(x),0)]
            return corner_points
        if max(y) == min(y):
            #No bloody channels?
            corner_points= [(0,0),(max(x),0)]
            return corner_points
        print(len(y))
        #Trying another way get diffs
        diffs = np.diff(y)
        #Then be sure first and last points captured
        diff_first = diffs.nonzero()[0][0]
        diff_last = diffs.nonzero()[0][-1]
        diffs = np.insert(diffs,0, 1)
        diffs[-1] = 1
        corner_indices = diffs.nonzero()[0]
        corner_points = [(x[i], y[i]) for i in corner_indices]
        #TODO Gonna need to change the first and last points so there is no slope
        if False:
        # Calculate the gradient of y old way
            gradient = np.gradient(y)
            # Identify corner points (where gradient changes sign)
            corner_indices = np.where(np.diff(np.sign(gradient)))[0] + 1
            # Handle the first constant flat section
            if gradient[0] == 0:
                corner_indices = np.insert(corner_indices, 0, 0)
            # Handle the last constant flat section
            if gradient[-1] == 0:
                corner_indices = np.append(corner_indices, len(y) - 1)
            corner_points = [(x[i], y[i]) for i in corner_indices]
        return corner_points

    def draw_plot(self):
        # Clear the axes
        self.axes.clear()

        # Plot the data
        """self.axes.plot(self.df.index, self.df["Noisy Current"], 'b', drawstyle='steps-post')"""
        self.axes.plot(*zip(*self.corner_points),
                       'r', linestyle='--',
                       drawstyle='steps-post')
        self.axes.scatter(*zip(*self.corner_points),
                    color='red', marker='o')
        if self.freeformat:
            self.axes.scatter(self.df.index ,
                           self.df.iloc[:,1],
                           c='b', s=0.2)
        else:
            self.axes.scatter(self.df.index ,
                       self.df["Noisy Current"],
                       c='b', s=0.2)

        # Redraw the canvas
        self.canvas.draw()

    def update_plot(self):
        # Get the current scrollbar position and window width
        start = self.scrollbar.value()
        window_width = self.window_slider.value()
        # Update the x-axis limits based on the scrollbar position and window width
        self.axes.set_xlim(start, start + window_width)

        # Redraw the canvas
        self.canvas.draw()

    def closeEvent(self, event):
        # Ask the user if they want to open the next file or exit
        if self.current_file_index < len(self.file_list) - 1:
            reply = QMessageBox.question(self, 'Open Next File',
                    'Do you want to open the next file?',
                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                next_file = self.file_list[self.current_file_index + 1]
                self.open_file(next_file)
                self.update_plot()
                event.accept()
            else:
                event.accept()
        else:
            event.accept()

    def open_file(self, filename):
        # Load the data
        if ".csv" in filename.lower():
            df = pd.read_csv(filename)
        elif ".txt" in filename.lower():
            try:
                df = pd.read_csv(filename, sep='\t', header=None)
            except:
                df = pd.read_csv(filename, sep='\\s+', header=None)
        elif "parquet" in filename.lower():
            df = pd.read_parquet(filename)
        else:
            df = pd.read_feather(filename)

        # Fix column data types if necessary
        try:
            if not pd.api.types.is_numeric_dtype(df["Time"]):
                df["Time"] = df["Time"].astype("float32")
        except:
            print("\nApparently no time column?")

        if "Channels" in df.columns:
            if not pd.api.types.is_integer_dtype(df["Channels"]):
                df["Channels"] = df["Channels"].astype("int32")
            maxc = max(abs(df["Channels"].to_numpy()))
        else:
            print("\nApparently no Channels column!!?")
            maxc = 1

        if "Noisy Current" in df.columns:
            df["Noisy Current"] = scale(df["Noisy Current"], out_range=(0, maxc))
        else:
            print("\nApparently no Noisy Current column!!?")
            freeformat = True


        # Create a new ApplicationWindow for the loaded file
        self.new_window = ApplicationWindow(df, freeformat, filename, self.file_list)
        self.new_window.show()
        self.close()

def scale(x, out_range=(0, 1)):
    domain = np.min(x), np.max(x)
    y = (x - domain[0]) / (domain[1] - domain[0])
    scaled_array = y * (out_range[1] - out_range[0]) + out_range[0]
    return scaled_array

def main():
    # Get a list of files
    freeformat = False
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    if file_dialog.exec_():
        file_list = file_dialog.selectedFiles()
    else:
        print("No files selected.")
        return

    # Open the first file
    for filename in file_list:
        if ".csv" in filename.lower():
            df = pd.read_csv(filename)
        elif ".txt" in filename.lower():
            try:
                df = pd.read_csv(filename, sep='\t', header=None)
            except:
                df = pd.read_csv(filename, sep='\\s+', header=None)
        elif "parquet" in filename.lower():
            df = pd.read_parquet(filename)
        else:
            df = pd.read_feather(filename)
        df = df.iloc[:MAXROWS,:]
        # Create the application window
        window = ApplicationWindow(df, freeformat, filename, file_list)
        window.show()

        # Start the application
        sys.exit(app.exec_())

        reply = QMessageBox.question(None,'Open Next File',
                'Do you want to open the next file?',
                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            continue
        else:
            break



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main()