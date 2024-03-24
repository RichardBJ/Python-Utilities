"""To allow the correction or removal of inflection points, you can add a new functionality to the onclick method. Here's how you can modify the code:

Add a new variable to store the selected inflection point index:
"""
class ApplicationWindow(QWidget):
    def __init__(self, df, signal_column):
        ...
        self.selected_inflection_index = None
"""
Modify the onclick method to handle the removal of inflection points:
"""

def onclick(self, event):
    # Check if the click is near an existing inflection point
    for i, (x, y) in enumerate(self.inflection_points):
        if abs(event.xdata - x) < 5 and abs(event.ydata - y) < 5:
            self.selected_inflection_index = i
            return

    # If no inflection point is selected, add a new one
    if self.selected_inflection_index is None:
        self.threshold = event.ydata
        self.inflection_points.append((event.xdata, self.threshold))
        self.inflection_points.sort()  # Ensure the inflection points are in order

    # Update the thresholded signal based on the inflection points
    self.update_thresholded_signal()

    # Redraw the plot
    self.draw_plot()

"""
Add a new method update_thresholded_signal to update the thresholded signal based on the inflection points:

"""
	
	
def update_thresholded_signal(self):
    for i in range(len(self.inflection_points) - 1):
        x1, y1 = self.inflection_points[i]
        x2, y2 = self.inflection_points[i + 1]
        self.df.loc[(self.df.index >= x1) & (self.df.index < x2), 'Thresholded Signal'] = np.where(
            self.df.loc[(self.df.index >= x1) & (self.df.index < x2), self.signal_column] >= y1, 1, 0)
"""
Add a new method remove_inflection_point to remove the selected inflection point:
"""

def remove_inflection_point(self):
    if self.selected_inflection_index is not None:
        del self.inflection_points[self.selected_inflection_index]
        self.selected_inflection_index = None
        self.update_thresholded_signal()
        self.draw_plot()			

"""
Connect a keyboard shortcut (e.g., 'Delete') to the remove_inflection_point method:

"""
	
def __init__(self, df, signal_column):
    ...
    self.canvas.mpl_connect('key_press_event', self.on_key_press)
	
def on_key_press(self, event):
    if event.key == 'delete':
        self.remove_inflection_point()