# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:28:28 2018

@author: Richard
"""





from tkinter import filedialog
root = filedialog.Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",  title = "Select file",filetypes = (("file","*.gz"),("all files","*.*")))
file2open=root.filename

import gzip
import shutil
with gzip.open(file2open, 'rb') as f_in:
    with open(file2open.replace('.gz',''), 'wb') as f_out:
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