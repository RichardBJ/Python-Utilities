# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 2024
@author: rbj
"""
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QSlider, QLabel, QMessageBox, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd
import matplotlib.pyplot as plt

from PyQt5.QtCore import Qt

class ApplicationWindow(QWidget):
    def __init__(self, df, filename):
        super().__init__()
        self.df = df
        self.filename = filename
        self.numeric_key_pressed = False
        self.threshold_levels = {}
        self.selected_channels = 1
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

        # Draw the selection rectangle
        if self.start_x is not None and self.end_x is not None:
            x1, x2 = sorted([self.start_x, self.end_x])
            y1, y2 = self.axes.get_ylim()
            self.axes.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor='k', linewidth=2))

        # Restore the x-axis limits
        self.axes.set_xlim(xlim)
        self.axes.legend()
        # Redraw the canvas
        self.canvas.draw()

    def draw_selection(self, start_x, end_x):
        # Clear any existing selection rectangle
        for patch in self.axes.patches:
            if isinstance(patch, plt.Rectangle):
                patch.remove()

        # Draw the new selection rectangle
        x1, x2 = sorted([start_x, end_x])
        y1, y2 = self.axes.get_ylim()
        self.axes.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor='k', linewidth=2))

        # Redraw the canvas
        self.canvas.draw()

    def select_region(self, start_x, end_x):
        x1, x2 = sorted([start_x, end_x])
        mask = (self.df.index >= x1) & (self.df.index <= x2)
        self.df.loc[mask, "Channels"] = self.selected_channels
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
            # Clear any existing selection rectangle
            for patch in self.axes.patches:
                if isinstance(patch, plt.Rectangle):
                    patch.remove()
            # Draw the new selection rectangle
            x1, x2 = sorted([self.start_x, self.end_x])
            y1, y2 = self.axes.get_ylim()
            self.axes.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor='k', linewidth=2))
            # Redraw the canvas
            self.canvas.draw()


    def on_key_press(self, event):
        if event.key.isdigit():
            self.selected_channels = int(event.key) if int(event.key) >= 0 else int(event.key)
            self.numeric_key_pressed = True

    def update_plot(self):
        # Get the current scrollbar position and window width
        start = self.scrollbar.value()
        window_width = self.window_slider.value()

        # Update the x-axis limits based on the scrollbar position and window width
        self.axes.set_xlim(start, start + window_width)

        # Redraw the canvas
        self.canvas.draw()

    #Save dataframe at the end
    def save_dataframe(self):
        new_filename = self.filename.rsplit('.', 1)[0] + '_COR.parquet'
        self.df.to_parquet(new_filename)

    #Catch the end of the window!!
    def closeEvent(self, event):
        self.save_dataframe()
        event.accept()


def main():
    # Open a file dialog to select the CSV file
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.AnyFile)

    if dialog.exec_():
        filename = dialog.selectedFiles()[0]
    else:
        print("No file selected.")
        return
    msg = "HIT A NUMBER FIRST, then select a bit of trace:" \
    +"\n0 - Set to 0 channels open"\
    +"\n1 - Set to 1 channel open et seq" \
    +"\n Sorry a bug you don't see the edit rectangle until it updates"

    msgBox = QMessageBox()
    msgBox.setText(msg)
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
    window = ApplicationWindow(df,filename)
    window.show()

    # Start the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main()