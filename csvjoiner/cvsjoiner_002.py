#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 15:58:03 2018

@author: rbj

MAJOR BUG CROPS ACCURACY OF OUTPUT.. nope perhaps not??
THIS COMBINES TOP TO TAIL
"""
import os
from tkinter import filedialog
from tkinter import *
import pandas as pd

def read_dataframe(file_path):
    # Determine the file type
    if file_path.endswith('.csv'):
        # Read the CSV file with pandas
        df = pd.read_csv(file_path)
    if file_path.endswith('.txt'):
        try:
            df = pd.read_csv(file_path, sep='\t')
        except:
            df = pd.read_csv(file_path, sep='\\s+')
    elif file_path.endswith('.parquet'):
        # Read the Parquet file with pandas
        df = pd.read_parquet(file_path)
    return df

def save_df(df, file_path):
    # Determine the file type
    if file_path.endswith('.csv'):
        save_path = file_path.replace(".csv","combined.csv")
        # Read the CSV file with pandas
        df.to_csv(save_path)
    if file_path.endswith('.txt'):
        # Hate txt using csv
        save_path = file_path.replace(".csv","combined.csv")
        df.to_csv(save_path)

    elif file_path.endswith('.parquet'):
        save_path = file_path.replace(".parquet","combined.parquet")
        df.to_parquet(save_path)
    
    

root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",
        multiple=1, filetypes = (("parquet","*.parquet"),("csv","*.csv"),("all files","*.*")))
filelist=root.tk.splitlist(root.filename)
flist=list(filelist)
root.withdraw()

for count, file in enumerate(flist):
    if count == 0:
        filea=file
        dfa=read_dataframe(file)
        #dfa.rename(index={0: "x"})
        print("a",dfa.shape)
    else:
        print("adding file",file)
        dfb=read_dataframe(file)
        #dfb.rename(index={0: "x"})
        print("b",dfb.shape)
        dfa = pd.concat([dfa, dfb], ignore_index=True)
        print("newshape",dfa.shape)
 
        
if "Time" in dfa.columns:
    #Re-write the time
    dfa.reset_index(drop=True, inplace=True)
    si = dfa.loc[10,"Time"] - dfa.loc[9,"Time"]
    dfa["Time"] = si * dfa.index
    
save_df(dfa, filea)












