# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 10:04:44 2024

@author: rbj
"""
import os
import tkinter as tk
from tkinter import filedialog

REPLACE = "validation_"

def rename_files_in_subfolders(parent_directory):
    for dirpath, dirnames, filenames in os.walk(parent_directory):
        for filename in filenames:
            if REPLACE in filename:
                new_filename = filename.replace(REPLACE, "")
                old_file_path = os.path.join(dirpath, filename)
                new_file_path = os.path.join(dirpath, new_filename)
                os.rename(old_file_path, new_file_path)

def select_directory():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    directory = filedialog.askdirectory()  # Open the dialog to choose directory
    return directory

# Call the function to select directory and rename files
parent_directory = select_directory()
if parent_directory:
    rename_files_in_subfolders(parent_directory)

