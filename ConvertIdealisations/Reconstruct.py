#!/usr/bin/env python3
#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 10:56:51 2024

@author: richardbarrett-jolley/Sean and Sam

Create: FOLDER with raw and idl folders within
 these must contain a matching set of files (raw) and (idl) respectively in the same file format.
 Other files can be present UNLESS they are one our formats txy, csv parquet that would screw us.
 \
     NEEDS A COMBO FOLDER FOR OUTPUT TO "combo"
"""
import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory

# Create the root Tk window
root = tk.Tk()

# Update the root window to ensure proper initialization on macOS
root.update()

# Hide the root Tk window
root.withdraw()
messagebox.showinfo("Instructions", "All the files should be in subfolders:\n"
					"1. Select the superfolder\n"
					"2. Within this there must be exactly 2 subfolders\n"
					"3. One folder is raw and one folder is idl output is going in combo\n"
                    "4. Every csv/txt/parquet file prefix in raw must also be in idl\n"
                    "5. For coding convience we expect filetype to be the same if it isn't, convert first"
                    "6. Obviously the raw contains raw with/without time, the ideal is QUB format IDL")


# Bring the Tkinter window to the front
root.lift()

# Ask the user to select a folder
folder_path = askdirectory()
# Convert all file paths to lower case
folder_path = folder_path.lower()
RAW = folder_path+r"/raw"
IDL = folder_path+r"/idl"
COMBO = folder_path+r"/combo"

extensions = [".parquet",".txt",".csv"]

idlfiles = []
rawfiles = []
outfiles = []
for file in os.listdir(IDL):
    print("Gathering lists of files")
    if any(file.lower().endswith(ext) for ext in extensions):
        idlfiles.append(os.path.join(IDL, file))
        rawfiles.append(os.path.join(RAW, file))
        outfiles.append(os.path.join(COMBO, file))
#Sanity check
if len(idlfiles) == len(rawfiles):
    print("Same number of idl and raw files")
else:
    print("OOPS number of idl and raw files not the same start again")

def pandize (file_path) -> pd.DataFrame:
    # Determine the file type
    if file_path.endswith('.csv'):
        # Read the CSV file with pandas
        df = pd.read_csv(file_path,
                         header=None)
    elif file_path.endswith('.txt'):
        # Read the tx file with pandas
        try:
            df = pd.read_csv(file_path, sep='\t',
                             header=None)
        except:
            df = pd.read_csv(file_path, sep='\\s+',
                             header=None)

    elif file_path.endswith('.parquet'):
        # Read the Parquet file with pandas
        df = pd.read_parquet(file_path)
    #print(df.info())
    print(df.head())

    return df

def parse_qub_idealisation(data:pd.DataFrame) -> np.array:
    #Sam function
    data.columns = ["Encoded_Channels", "Time"]
    grouped = {
        j: i
        for i, j in dict(
            enumerate(sorted(
                data["Encoded_Channels"].astype(float).unique()))
        ).items()
    }
    data["Channels"] = data["Encoded_Channels"].apply(
        lambda x: grouped[float(x)])
    return data["Channels"].to_numpy()

idldfs=[]
rawdfs=[]
for i, file in enumerate(idlfiles):
    print(f"pandizing {file}")
    idldfs.append(pandize(file))
    print(f"Pandizing {rawfiles[i]}")
    rawdfs.append(pandize(rawfiles[i]))

idldata = []
for i, df in enumerate(idldfs):
    print(f"Creating idealisation of df {i}/{len(idldfs)-1}")
    idldata.append(parse_qub_idealisation(df))
idldfs[0].head()

for i, array in enumerate(idldata):
    print(f"sticking together file {i} of {len(idldata)-1}\n\n")
    df=rawdfs[i]

    #Sorry simple fix for wrong lengths: pad the numpy
    try:
        df["Channels"]=array[:-1]
        print(f"OUTPUTTING TO {outfiles[i]}")
        df.to_parquet(outfiles[i])
    except:
        print("Error probably file length mismatch\n",
              "Moving onto the next one\n\n")
        print(
            f"File in action: {idlfiles[i]}\n",
            f"lengths are RAW {len(df)} and IDL",
            f"{len(array)}")
        continue



def generate_square_pulse(start_times, end_times, duration, max_value, sampling_rate):
    num_samples = int(duration * sampling_rate)
    signal = np.zeros(num_samples)
    time_points = np.linspace(0, duration, num_samples, endpoint=False)
    for start, end, value in zip(start_times, end_times, max_value):
        start_index = int(start * sampling_rate)
        end_index = int(end * sampling_rate)
        signal[start_index:end_index] = value
    return signal, time_points

# Read events from CSV file (handling floats)
def read_events_from_csv(file_path):
    include_events = []
    start_times = []
    end_times = []
    max_value = []

    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            include = int(row[0])
            start_times.append(float(row[1])) # Convert to float
            end_times.append(float(row[2]))  # Convert to float
            max_value.append(include)

    return start_times, end_times, max_value

# Example CSV file format:
# 1,5.2,10.7 # Assuming floats for timings
# 1,15.1,20.5
# 0,25.3,30.9
# 2,35.0,40.0
"""
for file in rawdata:
    get the name of the ideal file
    check if txt/parquet/feather/csv
    read that file
    process the ideal data
    concatenate the raw and ideal"""






if False:
	csv_file_path = 'Eventslist5.csv' # Path to your CSV file

	# Read events from CSV file
	start_times, end_times, max_value = read_events_from_csv(csv_file_path)

	# Determine duration based on the maximum end time
	duration = max(end_times) # Keep duration as float

	# Sampling rate (adjust as needed)
	sampling_rate = 100 # for example, 100 samples per second

	# Generate square pulse signal
	square_pulse, time_points = generate_square_pulse(start_times, end_times, duration, max_value, sampling_rate)

	# Plotting the square pulse signal
	plt.figure(figsize=(16, 5))
	plt.plot(time_points, square_pulse, drawstyle='steps-pre', linewidth=1)
	plt.title('Square Pulse Signal')
	plt.xlabel('Time')
	plt.ylabel('Amplitude')
	plt.ylim(min(max_value) - 1, max(max_value) + 1) # Adjust y-axis limits
	plt.grid(True)
	plt.show()
