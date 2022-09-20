# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 15:58:03 2018

@author: rbj

MAJOR BUG CROPS ACCURACY OF OUTPUT.. nope perhaps not??
"""
import os
from tkinter import filedialog
from tkinter import *
import pandas as pd

def join(filea,fileb):
       print (filea,fileb)
       dfa=pd.read_csv(filea)
       dfb=pd.read_csv(fileb)
       dfa=dfa.append(dfb)
       
#       print(df.values[:10,:])
       fileout=filea.replace('.csv','join.csv')
       dfa.to_csv(fileout,header=False,index=False)
       return dfa

root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",
        multiple=1, filetypes = (("csv DL file","*.csv"),("all files","*.*")))
filelist=root.tk.splitlist(root.filename)
flist=list(filelist)
root.withdraw()
for count, file in enumerate(flist):
    if count == 0:
        filea=file
        dfa=pd.read_csv(file,header=None)
        #dfa.rename(index={0: "x"})
        print("a",dfa.shape)
    else:
        print("adding file",file)
        dfb=pd.read_csv(file,header=None)
        #dfb.rename(index={0: "x"})
        print("b",dfb.shape)
        dfa=dfa.append(dfb)
        
        print("newshape",dfa.shape)
        
    
fileout=filea.replace('.csv','join.csv')
dfa.to_csv(fileout,header=False,index=False)












