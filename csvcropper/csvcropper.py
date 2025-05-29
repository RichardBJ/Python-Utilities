#!/usr/bin/env python3
00# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 15:58:03 2018

@author: rbj

MAJOR BUG CROPS ACCURACY OF OUTPUT.. nope perhaps not??
"""
import os
from tkinter import filedialog
from tkinter import *
import pandas as pd

def add_silly_header(df):
    num_columns = len(df.columns)
    names = [chr(ord('Col_') + i) for i in range(num_columns)]
    df.rename(columns=dict(zip(df.columns, names)), inplace=True)
    return df

def get_file(file_path):
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
    if type(df.columns.tolist()[0]) == str:
        #We have a header
        pass
    else:
        #Yikes no header so just label them A, B, C for now
        df = add_silly_header(df)

    return df

def crop(file2open,fromer,twoer):
       print (file2open)
       df=get_file(file2open)
       if twoer <= 0:
           df=df.iloc[fromer:,:]
       else:
           df=df.iloc[fromer:twoer,:]
       df.reset_index(drop=True, inplace=True)
       _, ext = os.path.splitext(file2open)
       fileout=file2open.replace(ext,"_crop.parquet")
       df.to_parquet(fileout, index=False)

text1 = input("keep FROM X POINT\n")  # Python 3
text2 = input("retain UNTIL X POINT 0=keep until end!\n")

skiprows=int(text1)
until = int(text2)-skiprows

root = Tk()
root.filename =  filedialog.askopenfilename(
    initialdir = "/",title = "Select file",
    multiple=1, filetypes = (
    ("csv files","*.csv"),("all files","*.*"), ("parquet","*.parquet"))
        )
filelist=root.tk.splitlist(root.filename)
flist=list(filelist)
root.withdraw()
for file in flist:
    file2open=file
    crop(file2open,skiprows,until)

