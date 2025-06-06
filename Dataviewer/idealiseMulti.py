#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 16:19:49 2024
@author: rbj

#This idealises a record, but note that:
    (1) It creates an enitrely new idealisation alongside the existing one!
    (2) It seems to be using a channels column called "Thresholded" not Channels?
"""

import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QSlider, QLabel, QMessageBox
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from scipy.stats import linregress

from PyQt5.QtCore import Qt

# Create the QApplication instance before any QWidget instances
app = QApplication(sys.argv)

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class ApplicationWindow(QWidget):
    def __init__(self, df, signal_column, threshed_col, filename):
        super().__init__()
        self.df = df
        self.x_len = len(df.index)
        self.signal_column = signal_column
        self.threshed_col = threshed_col
        self.filename = filename
        self.numeric_key_pressed = False
        self.remove_triggered = False
        self.scalerMax=df["Channels"].max()
        self.domain = None #Holds the range of the original unscaled data
        #Give the signal a quick scale for visibility
        self.df[signal_column]=self.scale(self.df[signal_column], max_val=self.scalerMax)
        
        self.threshold = df[signal_column].median()  # Initial threshold
        # Initial threshold set
        self.thresholds = [df[signal_column].median()]
        self.selected_threshold_index = 0
        self.threshold_indexes = [0]
        self.df[self.threshed_col] = np.where(self.df[self.signal_column] > self.threshold, 1, 0)
        self.inflection_points = {0: [(0, self.threshold)]}  # Inflection points for each threshold
        self.selected_inflection_index = None
        self.point_index = None
        self.endpoint_created = False

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
        self.window_slider.setValue(2000)
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
        self.canvas.axes.plot(self.df[self.threshed_col], 'r')
        self.canvas.axes.scatter(self.df.index,
                                 self.df[self.signal_column], 
                                 c='b', s=0.1)
        

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
        
    def scale(self, data, min_val=0, max_val=1):
        self.domain = np.min(data), np.max(data)
        y = (data - self.domain[0]) / (self.domain[1] - self.domain[0])
        scaled_array = y * (max_val - min_val) + min_val
        return scaled_array
    
    def unscale(self, scaled_array) -> np.array:
        scaled_min, scaled_max = self.domain
        unscaled_array = (scaled_array - scaled_min) / (scaled_max - scaled_min)
        return unscaled_array

    def calculate_regression_line(self, threshold_index):
        # Not actually implimented this!
        x_values = [x for x, y in self.inflection_points[threshold_index]]
        y_values = [y for x, y in self.inflection_points[threshold_index]]
        slope, intercept, _, _, _ = linregress(x_values, y_values)
        return slope, intercept
    
    def euclidean_distance(self, point1, point2):
        """
        Calculates the Euclidean distance between two points.
        """
        x1, y1 = point1
        x2, y2 = point2
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def find_closest_tuple(self, data, target_point):
        """
        Finds the index of the closest tuple in 'data' to the 'target_point'.
        """
        min_distance = float('inf')
        closest_index = None
    
        for i, point in enumerate(data):
            distance = self.euclidean_distance(point, target_point)
            if distance < min_distance:
                min_distance = distance
                closest_index = i
  
        return closest_index

    def create_threshold(self):
        # Initialize the x and y arrays
        x = []
        y = []

        inflection_points = self.inflection_points[self.selected_threshold_index].copy()
        """if inflection_points[-1][0] < len(self.df)-1:
            inflection_points.append((len(self.df)-1,inflection_points[-1][1]))"""

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

    def add_threshs(self, arrays: list) -> np.array:
        results = np.zeros_like(arrays[0])
        for arr in arrays:
            results[arr != 0] = arr[arr != 0]
        return results

    def update_thresholded_signal(self):
        mean_thresholds = [np.mean(threshold) for threshold in self.thresholds]
        # Sort the thresholds based on mean threshold values in ascending order
        sorted_thresholds = [threshold for _,
                             threshold in sorted(zip(mean_thresholds, self.thresholds))]

        arrays=[]
        for i, threshold in enumerate(sorted_thresholds):
            arrays.append(np.where(self.df[self.signal_column].values > threshold,\
                          i + 1, 0) ) #Not necessarily zero just above threshold!
        #so need to add these columns more intelligently!
        self.df[self.threshed_col] = self.add_threshs(arrays)

    def onclick(self, event):
        if self.remove_triggered==True:
            self.remove_inflection_point(x=event.xdata, y=event.ydata)
            return
        
        # Check if the click is inside the axes
        if event.xdata is None or event.ydata is None:
            self.selected_inflection_index = None
            return

        # Check it is not beyond the last datapoint
        if int(event.xdata) >= self.x_len:
            event.xdata = float(self.x_len - 1)

        # Add a new inflection point for the selected threshold
        
        if self.numeric_key_pressed:
            self.inflection_points[self.selected_threshold_index].append((int(event.xdata), event.ydata))
            self.inflection_points[self.selected_threshold_index]=\
                sorted(self.inflection_points[self.selected_threshold_index],\
                       key = lambda point: point[0])
            #Set the first inflection point to be the origin for  x=0
            if len(self.inflection_points[self.selected_threshold_index])>1:
                self.inflection_points[self.selected_threshold_index][0]=\
                    (0,self.inflection_points[self.selected_threshold_index][1][1])
            #Tbh better to set a provisional inflection point at end of record too
            if not self.endpoint_created:
                self.inflection_points[self.selected_threshold_index].append((self.x_len - 1, event.ydata))
                self.endpoint_created=True

            self.selected_inflection_index = None
            self.create_threshold()
            self.update_thresholded_signal()
            self.draw_plot()
            #self.numeric_key_pressed = False

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
            self.remove_triggered = False
        elif event.key.isalpha():
            #I think I'm doing this anyway so can clear this?
            self.update_thresholded_signal()
            self.numeric_key_pressed = False
            self.remove_triggered = False
        elif event.key == ' ':
            self.remove_triggered = True
            self.numeric_key_pressed = False  

    def remove_inflection_point(self, x=0, y=0):
        print(f"We are in remove: remove triggered is {self.remove_triggered}")
        data = self.inflection_points[self.selected_threshold_index]
        # Find the inflection point closest to the click within 50 points
        self.selected_inflection_index = self.find_closest_tuple(data, (x,y))
  
        print(self.selected_inflection_index)
        del self.inflection_points[self.selected_threshold_index][self.selected_inflection_index]
        
        self.create_threshold()
        self.update_thresholded_signal()
        self.draw_plot()

    def update_plot(self, value):
        # Update the plot based on the scrollbar position and window width
        start = self.scrollbar.value()
        window_width = self.window_slider.value()
        self.canvas.axes.set_xlim(start, start + window_width)
        self.canvas.draw()

    #Save dataframe at the end
    def save_dataframe(self):
        new_filename = self.filename.rsplit('.', 1)[0] + '_IDL.parquet'
        self.df[self.signal_column]=self.unscale(self.df[self.signal_column])
        self.df.to_parquet(new_filename)

    #Catch the end of the window!!
    def closeEvent(self, event):
        self.save_dataframe()
        event.accept()



def main():
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.AnyFile)

    if dialog.exec_():
        filename = dialog.selectedFiles()[0]
        print(f"You selected: {filename}")
    else:
        print("No file selected.")

    msgBox = QMessageBox()
    msgBox.setText("Hit a numeric key to choose the threshold you are working\n"
                    "and then left click to set the actual threshold level\n"
                    "To DELETE use the spacebar\n"
                    "To zoom press Z/z"
                    "hit threshold number afterwards\n"
                    "only really tested with 1 channel")
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
    window = ApplicationWindow(df, signal_column, threshed_col, filename)
    window.show()
    print("start app")
    # Start the application
    sys.exit( app.exec_() )



if __name__ == '__main__':
    main()