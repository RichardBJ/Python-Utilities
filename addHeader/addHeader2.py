# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 16:03:59 2022

@author: rbj
"""
import os
import pandas as pd
import numpy as np
from tkinter import filedialog
from tkinter import *

HEADER="Index","State of Channel 0","Channels","Time","State of Channel 1",	"State of Channel 2",	"Noisy Current"

ADD_TIME=False
SI=1e-5


def create_time(current):
    return np.linspace(0,len(current)*SI,num=len(current))

def dofile(file):
    print (file)
    df=pd.read_csv(file)
    print(df.head())
    df.columns = HEADER
    if ADD_TIME:
        df['Time']=create_time(df['Channels'])
    '''file specific version to sort column order'''
    '''df=df.iloc[:,[3,0,1]]'''
    print(df.head())
    jfile = os.path.basename(file)
    path = os.path.dirname(file)
    print(path+"/processed/"+jfile)
    df.to_csv(path+"/processed/"+jfile)
    dummy=0


root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",
        multiple=1, filetypes = (("csv DL file","*.csv"),("all files","*.*")))
filelist=root.tk.splitlist(root.filename)
flist=list(filelist)
root.withdraw()
for file in flist:
    if file.endswith(".csv"):
        file2open=file
        dofile(file2open)  
