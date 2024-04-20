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

def crop(file2open,fromer,twoer):
       print (file2open)
       df=pd.read_csv(file2open,skiprows=fromer,nrows=twoer)
#       print(df.values[:10,:])
       fileout=file2open.replace('.csv','crop.csv')
       df.to_csv(fileout,header=False,index=False)
       

text1 = input("keep FROM X POINT\n")  # Python 3
text2 = input("retain UNTIL X POINT 0=keep until end!\n")

skiprows=int(text1)
until = int(text2)-skiprows
if until<0:
    until=500000000
print (skiprows,"-",until)

root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",
        multiple=1, filetypes = (("csv DL file","*.csv"),("all files","*.*")))
filelist=root.tk.splitlist(root.filename)
flist=list(filelist)
root.withdraw()
for file in flist:
    file2open=file
    crop(file2open,skiprows,until)  

