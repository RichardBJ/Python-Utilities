import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog

# Create the root window
root = tk.Tk()
root.title("ECG Viewer")

# Open a file dialog to select the CSV file
filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

# Load the data
df = pd.read_csv(filename)
df["Time"]=np.arange(0,len(df)*0.005,len(df))
print(df.info())

# Create a FigureCanvasTkAgg object
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Function to update the plot
def update_plot(start):
    ax.clear()
    ax.plot(df.iloc[1,:][start:start+1000], df.iloc[2,:][start:start+1000])
    ax.set_xlabel('Time')
    ax.set_ylabel('Signal')
    canvas.draw()

# Create a Scale widget
scale = tk.Scale(root, from_=0, to=len(df)-1000, command=lambda v: update_plot(int(v)))
scale.pack(fill=tk.X)

# Initialize the plot
update_plot(0)

# Start the main loop
root.mainloop()
