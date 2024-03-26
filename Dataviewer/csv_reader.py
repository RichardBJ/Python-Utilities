import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter.filedialog import askopenfilename

class MultiInputDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title=None, field_names=None, initial_values=None):
        self.field_names = field_names or []
        self.initial_values = list(initial_values) if initial_values is not None else []
        self.entries = []
        tk.simpledialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        for field_name, initial_value in zip(self.field_names, self.initial_values):
            tk.Label(master, text=field_name).grid(row=len(self.entries))
            entry = tk.Entry(master)
            entry.insert(0, initial_value)
            entry.grid(row=len(self.entries), column=1)
            self.entries.append(entry)
        return self.entries[0]

    def apply(self):
        self.result = [entry.get() for entry in self.entries]

# Create the root window
root = tk.Tk()
root.title("csv viewer")

# Open a file dialog to select the CSV file
filename = askopenfilename(filetypes=[("CSV files", "*.csv"), 
                                      ("Parquet files", "*.parquet"),
                                      ("Feather files", "*.feather")])

# Load the data
if "csv" in filename.lower():
    df = pd.read_csv(filename)
elif "parquet" in filename.lower():
    df = pd.read_parquet(filename)
else:
    df = pd.read_feather(filename)

# Get the column names from the user
dialog = MultiInputDialog(root, "Input", ["Time column name", "Signal column name"], df.columns[:2])
time_column, signal_column = dialog.result

if time_column not in df.columns:
    df[time_column] = np.arange(0, len(df) * 0.005, len(df))

print(df.info())

# Create a FigureCanvasTkAgg object
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Function to update the plot
def update_plot(start, window_width):
    ax.clear()
    ax.plot(df[time_column][start:start+window_width], df[signal_column][start:start+window_width])
    ax.set_xlabel(time_column)
    ax.set_ylabel(signal_column)
    canvas.draw()

# Create Scale widgets
scale_start = tk.Scale(root, from_=0, to=len(df)-1000, orient=tk.HORIZONTAL,
                       command=lambda v: update_plot(int(v), window_width))
scale_start.pack(fill=tk.X)

window_width = 1000  # Initial window width
scale_width = tk.Scale(root, from_=100, to=len(df), orient=tk.HORIZONTAL,
                       command=lambda v: update_window_width(int(v)))
scale_width.pack(fill=tk.X)

def update_window_width(new_width):
    global window_width
    window_width = new_width
    update_plot(scale_start.get(), window_width)

# Initialize the plot
update_plot(0, window_width)

# Start the main loop
root.mainloop()
