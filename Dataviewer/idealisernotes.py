#!/usr/bin/env python3
#!/usr/bin/env python3
def draw_plot(self):
    # ... (existing code) ...

    # Plot the signal and the thresholded signal
    self.canvas.axes.plot(self.df[self.signal_column], 'b')
    self.canvas.axes.plot(self.df[self.threshed_col], 'r')

    # Plot the regression line segments
    for i in range(len(self.inflection_points) - 1):
        x1, y1 = self.inflection_points[i]
        x2, y2 = self.inflection_points[i + 1]

        # Calculate the regression line equation for the segment
        slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
        intercept = y1 - slope * x1

        # Plot the regression line segment
        segment_indices = (self.df.index >= x1) & (self.df.index < x2)
        x_values = self.df.loc[segment_indices, :].index.values
        y_values = slope * x_values + intercept
        self.canvas.axes.plot(x_values, y_values, 'g', label='Regression Line Segment')

    # ... (existing code) ...