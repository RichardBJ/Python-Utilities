import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter.filedialog import askopenfilename

# Create the root window
root = tk.Tk()
root.title("ECG Viewer")

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

if "Time" not in df.columns:
    df["Time"] = np.arange(0, len(df) * 0.005, len(df))

print(df.info())

# Create a FigureCanvasTkAgg object
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Function to update the plot
def update_plot(start, window_width):
    ax.clear()
    ax.plot(df["Time"][start:start+window_width], df["Noisy Current"][start:start+window_width])
    ax.set_xlabel('Time')
    ax.set_ylabel('Signal')
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