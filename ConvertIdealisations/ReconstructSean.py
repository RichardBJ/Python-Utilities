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


     CURRENT VERSION CREATES AN ERRONEOUS FINAL STATE!
"""
import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory

FILETYPE="abf" #Not actually the file type, but the type of file.
#File type itself will really be txt, csv or parquet
TIMEFACTOR = 0.004
#Up is typically open
FLIP=True

# Create the root Tk window
root = tk.Tk()

# Update the root window to ensure proper initialization on macOS
root.update()

# Hide the root Tk window
root.withdraw()
messagebox.showinfo("Instructions", "All the files should be in subfolders:\n"
					"1. Select the superfolder\n"
					"2. Within this there must be exactly 3 subfolders\n"
					"3. (A) raw (B) idl. Output goes into (C) combo\n"
                    "4. Every csv/txt/parquet file prefix in raw must also be in idl\n"
                    "5. For coding convience we expect filetype to be the same if it isn't, convert first\n"
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
    # print(df.head())

    return df

def find_row(series,target):
    return np.asarray((series - target)**2).argmin()

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

def parse_abf_idealisation(idldf:pd.DataFrame,
                           rawtime:np.array) -> np.array:
    need = [2,4,5]
    times = idldf.loc[:,need]
    times.columns = ["State","Start","Stop"]
    idl = [int(0)] * len(rawtime)
    for index, row in times.iterrows():
        startRow = find_row(rawtime,row["Start"])
        stopRow = find_row(rawtime,row["Stop"])
        idl[startRow:stopRow]=[int(row["State"])] * (stopRow-startRow)
    return np.asarray(idl)

idlfiles = []
rawfiles = []
outfiles = []
for file in os.listdir(IDL):
    file=file.lower()
    print(f"Creating file list based on {file}")
    if any(file.lower().endswith(ext) for ext in extensions):
        idlfiles.append(os.path.join(IDL, file))
        rawfiles.append(os.path.join(RAW, file))
        if file.endswith(".txt"):
            file=file.replace(".txt", ".parquet")
        elif file.endswith(".csv"):
            file=file.replace(".csv", ".parquet")
        outfiles.append(os.path.join(COMBO, file))

idldfs=[]
rawdfs=[]
good_idls=[]
good_raws=[]
good_outputs = []
errors = []
for i, file in enumerate(idlfiles):
    try:
        print(f"pandizing {file}")
        idldfs.append(pandize(file))
        print(f"Pandizing {rawfiles[i]}")
        #Sometimes Sean's raw files have time sometimes not.
        #It needs time!
        tdf = pandize(rawfiles[i])
        if len(tdf.columns) == 2:
            #Presumably columns are
            tdf.columns = ["Time","Noisy Current"]
            rawdfs.append(tdf)
        elif len(tdf.columns) == 1:
            #Presumably have to then add a time column
            tdf.columns = ["Noisy Current"]
            tdf["Time"]=tdf.index * TIMEFACTOR
            rawdfs.append(tdf)
        else:
            print("PRETTY BAD ERROR AROUND LINE 151")

        #In theory these should now be only the ones where no errors above!
        good_idls.append(file)
        good_raws.append(rawfiles[i])
        good_outputs.append(outfiles[i])
    except:
        print(f"\nscrew-up in {file}\n")
        errors.extend([i])
        #Crop the error off (will be the last one we appended)
        if len(idldfs) > len(rawdfs):
            idldfs = idldfs[:len(rawdfs)]
        elif len(idldfs) < len(rawdfs):
            rawdfs = rawdfs[:len(idldfs)]

#Alternatively write it as all the files not in "errors" list
idlfiles= [file for file in good_idls]
rawfiles = [file for file in good_raws]
outfiles = [file for file in good_outputs]
del good_idls
del good_raws
del good_outputs

idldata = []
for i, df in enumerate(idldfs):
    print(f"Creating idealisation of df {i+1}/{len(idldfs)}")
    if FILETYPE.lower() == "qub":
        idldata.append(parse_qub_idealisation(df))
    else:
        try:
            idldata.append(
                parse_abf_idealisation(df,rawdfs[i].loc[:,"Time"]))
        except:
            pass

#Idlfiles should be the proper list of files now
for i in range(len(idlfiles) ):
    print(f"\nsticking together file {i} of {len(idldata)-1}")
    df=rawdfs[i]
    if FLIP==True:
        try:
            df["Noisy Current"] = df["Noisy Current"] * -1
        except:
            print(f"TROUBLE FLIPPING FOR {outfiles[i]}")
    try:
        df["Channels"]=idldata[i]
        print(f"OUTPUTTING TO {outfiles[i]}")
        df.to_parquet(outfiles[i], index=False)
    except:
        print("Error probably file length mismatch\n",
              "Moving onto the next one\n\n")
        print(
            f"File in action: {idlfiles[i]}\n",
            f"lengths are RAW {len(df)} and IDL",
            f"{len(idldata[i])}")
        continue

