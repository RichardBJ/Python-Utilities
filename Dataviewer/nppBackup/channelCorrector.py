#!/usr/bin/env python3
#!/usr/bin/env python3
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
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt

# TODO
# Get a key catcher so only select when want to this will allow native zoom in too
# When we select, PRIOR to actually changing the data, un-cornerpoint the record!

class ApplicationWindow(QWidget):
    def __init__(self, df, filename):
        super().__init__()
        self.setWindowTitle(filename)
        self.df = df
        self.filename = filename
        self.corner_points = None
        self.numeric_key_pressed = True #People may initially forget to press
        self.threshold_levels = {}
        self.selected_channels = 1
        self.selected_column = None
        self.inflection_points = {}
        self.pressed = False
        self.start_x = None
        self.end_x = None
        self.rect = None
        self.remove_triggered=True
        self.keypressed=None

        # Create the matplotlib FigureCanvas object
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        self.axes = self.figure.add_subplot(111)

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
        print(f"Initial data length = {len(self.df)}")
        self.corner_points = self.make_corners()
        print(f"Uncornered data length = {len(self.uncorner())}")
        self.setLayout(vbox)

        # Draw the initial plot
        self.draw_plot()

    def make_corners(self):
        x = self.df.index
        y = self.df["Channels"]
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

    def uncorner(self):
        # Extract x and y values from corner points
        x_values, y_values = zip(*self.corner_points)
        # Initialize lists to store reconstructed data points
        X = []
        Y = []
        if False:
            # Handle the first corner point (if it's the first index)
            if x_values[0] == self.df.index[0]:
                X.append(x_values[0])
                Y.append(y_values[0])
        # Reconstruct data points between corner points
        for i in range(1, len(x_values)):
            start_x = x_values[i-1]
            end_x = x_values[i]
            newX = list(range(start_x, end_x))  # Include the start point but not the end point
            newY = [y_values[i-1]] * len(newX)
            X.extend(newX)
            Y.extend(newY)
        #We always finish one point short
        X=X+[x_values[-1]]
        Y=Y+[y_values[-1]]
        # No need to handle the last corner point separately
        # Return the reconstructed y_values
        return Y

    def draw_plot(self):
        # Store the current x-axis limits
        xlim = self.axes.get_xlim() if self.axes.get_xlim() != (0, 1) else (0, 1000)
        # Clear the axes
        self.axes.clear()
        # Plot the signal and the thresholded signal
        #self.axes.plot(self.df["Channels"], 'r',drawstyle='steps-post')

        self.axes.plot(*zip(*self.corner_points),
                       'r', linestyle='--',
                       drawstyle='steps-post')
        self.axes.scatter(*zip(*self.corner_points),
                    color='red', marker='o')
        self.axes.scatter(self.df.index ,
                       self.df["Noisy Current"],
                       c='b', s=0.2)

        if self.start_x is not None and self.end_x is not None:
            x1, x2 = sorted([self.start_x, self.end_x])
            y1, y2 = self.axes.get_ylim()
            self.axes.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor='k', linewidth=2))

        # Restore the x-axis limits
        self.axes.set_xlim(xlim)
        #self.axes.legend()
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
        min_distance = 10
        closest_index = None

        for i, point in enumerate(data):
            distance = self.euclidean_distance(point, target_point)
            if distance < min_distance:
                min_distance = distance
                closest_index = i

        return closest_index

    def select_region(self, start_x, end_x):
        x1, x2 = sorted([start_x, end_x])
        mask = (self.df.index >= x1) & (self.df.index <= x2)
        #TODO here is the place we must uncorner
        #Uncorner the graph and write this into the channels slot
        self.df.loc[mask, "Channels"] = self.selected_channels
        self.corner_points = self.make_corners()
        self.draw_plot()

    def on_button_press(self, event):
        if event.button == 1 and event.key == 'shift': # shift + Left mouse button
            self.pressed = True
            self.start_x = event.xdata
            #self.remove_triggered==False
        elif event.button == 1 and self.keypressed=='d':
            #self.remove_inflection_point(x=event.xdata, y=event.ydata)
            self.remove_point(event.xdata,event.ydata)
            self.pressed=False
            self.start_x=None

        #Just use matplotlib zoom if click with z pressed
        elif event.button == 1 and not event.key == 'z':
            #self.remove_inflection_point(x=event.xdata, y=event.ydata)
            self.add_point(event.xdata)
            self.pressed=False
            self.start_x=None

    def on_button_release(self, event):
        if event.button == 1 and self.pressed:  # Left mouse button
            self.pressed = False
            self.end_x = event.xdata
            self.select_region(self.start_x, self.end_x)

    def on_motion_notify(self, event):
        if self.pressed and self.numeric_key_pressed:
            self.end_x = event.xdata
            # Clear any existing selection rectangle
            for patch in self.axes.patches:
                if isinstance(patch, plt.Rectangle):
                    patch.remove()
            # Draw the new selection rectangle
            x1, x2 = sorted([self.start_x, self.end_x])
            y1, y2 = self.axes.get_ylim()
            self.rect = self.axes.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor='k', linewidth=2))
            # Redraw the canvas
            self.canvas.draw()

    def remove_point(self, x,y):
        try:
            index = self.find_closest_tuple(self.corner_points,(x,y))
            del self.corner_points[index]
        except:
            pass

        self.draw_plot()
        return

    def add_point(self, x):
        try:
            self.corner_points.append((int(x), self.selected_channels))
            # Sort the points based on their x-coordinates
            self.corner_points = sorted(self.corner_points, key=lambda coord: coord[0])
        except:
            pass
        self.draw_plot()
        return

    def on_key_press(self, event):
        if event.key.lower() == 'c':  # Check if the key pressed is 'c'
            self.numeric_key_pressed = False
            # Remove the rectangle patch if it exists
            for patch in self.axes.patches:
                if isinstance(patch, plt.Rectangle):
                    patch.remove()
            self.rect = None  # Reset the self.rect attribute
            self.canvas.draw()  # Redraw the canvas
        elif event.key.lower() == 'd':
            #we are going to delete a point
            self.numeric_key_pressed = False
            self.keypressed = 'd'
            self.start_x = None
        elif event.key.lower() == 'h':
            helpDialog()
        elif event.key.isdigit():
            self.selected_channels = int(event.key) if int(event.key) >= 0 else int(event.key)
            self.numeric_key_pressed = True
            self.keypressed = None

    def update_plot(self):
        # Get the current scrollbar position and window width
        start = self.scrollbar.value()
        window_width = self.window_slider.value()

        # Update the x-axis limits based on the scrollbar position and window width
        self.axes.set_xlim(start, start + window_width)

        # Redraw the canvas
        self.canvas.draw()

    def ask_save(self):
        confirmation = QMessageBox.question(self, "Save Or Not", "Do you want to save the file?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            return True
        else:
            return False

    #Save dataframe at the end
    def save_dataframe(self):
        if self.ask_save() == True:
            Channels = self.uncorner()
            self.df["Channels"] = Channels
            new_filename = self.filename.rsplit('.', 1)[0] + '_COR.parquet'
            self.df.to_parquet(new_filename)

    #Catch the end of the window!!
    def closeEvent(self, event):
        self.save_dataframe()
        event.accept()

def scale(x, out_range=(0, 1)):
    #TODO shouldnt this be in the class?
    domain = np.min(x), np.max(x)
    y = (x - domain[0]) / (domain[1] - domain[0])
    scaled_array = y * (out_range[1] - out_range[0]) + out_range[0]
    return scaled_array

def helpDialog():
    msg = "HIT A NUMBER FIRST, then shift-drag-select a bit of trace:" \
    +"\n- Press 0 = 0 channels open"\
    +"\n- Press 1 = 1 channel open et seq" \
    +"\n- HIT A NUMBER FIRST, then just click to add a point" \
    +"\n- Npress a THEN click to delete a point" \
    +"\n- Press c to clear the rectangle"\
    +"\n- HOLD z and click the zoom to then zoom in. Scroll or home to end"\
    +"\n- PRESS H ANYTIME TO GET THIS HELP MENU AGAIN"

    msgBox = QMessageBox()
    msgBox.setText(msg)
    msgBox.setWindowTitle("Instructions")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
    return


def main():
    # Open a file dialog to select the CSV file
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.AnyFile)

    if dialog.exec_():
        filename = dialog.selectedFiles()[0]
    else:
        print("No file selected.")
        return

    helpDialog()

    # Load the data
    if ".csv" in filename.lower():
        df = pd.read_csv(filename)
    elif ".txt" in filename.lower():
        try:
            df = pd.read_csv(filename, sep='\t',
                             header=None)
        except:
            df = pd.read_csv(filename, sep='\\s+',
                             header=None)
    elif "parquet" in filename.lower():
        df = pd.read_parquet(filename)
    else:
        df = pd.read_feather(filename)
    # coumn file types sometimes screwed!
    try:
        if not pd.api.types.is_numeric_dtype(df["Time"]):
            df["Time"] = df["Time"].astype("float32")
    except:
        print("\nApparently no time column?")
    try:
       if "Channels" in df.columns:
           if not pd.api.types.is_integer_dtype(df["Channels"]):
               df["Channels"] = df["Channels"].astype("int32")
    except:
        print("\nApparently no Channels column!!?")



    maxc = max(df["Channels"].to_numpy())
    df["Noisy Current"]=scale(df["Noisy Current"],out_range=(0,maxc))
    # Create the application window
    window = ApplicationWindow(df,filename)
    window.show()

    # Start the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main()