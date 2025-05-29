#!/usr/bin/env python3
import os
from tkinter import filedialog
from tkinter import *

TIMEINMINS=1   #time in mins obviously
SAMPLERATE= 2600.104004#FIONA ECG DATA 5000 #per second catdata: 2600.104004



def split(filehandler, delimiter=',', row_limit=100001, 
          output_name_template='_%s.csv', output_path='.', keep_headers=False):
    """
    Splits a CSV file into multiple pieces.
    
    A quick bastardization of the Python CSV library.
    
    Arguments:
    
        `row_limit`: The number of rows you want in each output file. 10,000 by default.
        `output_name_template`: A %s-style template for the numbered output files.
        `output_path`: Where to stick the output files.
        `keep_headers`: Whether or not to print the headers in each output file.
    
    Example usage:
    
        >> from toolbox import csv_splitter;
        >> csv_splitter.split(open('/home/ben/input.csv', 'r'));
    
    """
    import csv
    filePath=filehandler.name
    head, tail = os.path.split(str(filePath))
    print(tail)
    tail =tail.replace(".csv", "_")
    print(tail)
    output_name_template=tail+output_name_template
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(output_path,
         output_name_template  % current_piece)
    
    current_out_writer = csv.writer(open(current_out_path, 'w',newline=''), 
                                    delimiter=delimiter)
    current_limit = row_limit
#    if keep_headers:
#        headers = reader.next()
#        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(output_path,
               output_name_template  % current_piece)
            current_out_writer = csv.writer(open(current_out_path, 'w',newline=''), 
                                            delimiter=delimiter)
#            if keep_headers:
#                current_out_writer.writerow(headers)
        current_out_writer.writerow(row)
    
root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",
        multiple=1, filetypes = (("csv DL file","*.csv"),("all files","*.*")))
filelist=root.tk.splitlist(root.filename)
flist=list(filelist)
root.withdraw()
for file in flist:
    if file.endswith(".csv"):
        file2open=file
        print (file2open)
        time=TIMEINMINS*60
        row_limit=SAMPLERATE*time
        split(open(file2open, 'r'),row_limit=row_limit)  

