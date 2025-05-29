#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:28:28 2018

@author: Richard
"""

import gzip
import shutil
import os
from tkinter import filedialog
os.chdir('I:\OmarStuff')
root = filedialog.Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",
        multiple=1, filetypes = (("gzfiles","*.fastq"),("all files","*.*")))
filelist=root.tk.splitlist(root.filename)
flist=list(filelist)
root.withdraw()
for file in flist:
    file2open=file
    print("Working on file ",file2open)
    with gzip.compress(file2open, 'rb') as f_in:
        with open(file2open.replace('.fastq','fastq.gz'), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
'''
import tarfile
from tkinter import filedialog
root = filedialog.Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",  title = "Select file",filetypes = (("file","*.gz"),("all files","*.*")))
file2open=root.filename
tar = tarfile.open(file2open)
tar.extractall()
tar.close()
'''