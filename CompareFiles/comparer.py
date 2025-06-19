#!/usr/bin/env python3
#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 12:25:47 2019

@author: richardbarrett-jolley
"""

#tkinter just not working at all with this new iMac
'''
from tkinter import filedialog
root = filedialog.Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",
        title = "Select file",
        filetypes = (("Python","*.py"),("all files","*.*")))
file2open=root.filename
print (file2open)   
'''


f1='cnnRNN_AF_190325_m103.py'
f2='cnnRNN_AF_190325_m104.py'


print('Differential contents of ',f1)

with open(f1, 'r') as file1:
    with open(f2, 'r') as file2:
        same = set(file2).intersection(file1)

with open(f1, 'r') as file1:
    originallines=file1.readlines()
    
origset=set(originallines)

changes=origset.difference(same)
for line in changes:
    print(line, end="")

f3=f1
f1=f2
f2=f3
print('#################### Contents now ############################## ',f1)

with open(f1, 'r') as file1:
    with open(f2, 'r') as file2:
        same = set(file2).intersection(file1)

with open(f1, 'r') as file1:
    originallines=file1.readlines()
    
origset=set(originallines)

changes=origset.difference(same)
for line in changes:
    print(line, end="")
