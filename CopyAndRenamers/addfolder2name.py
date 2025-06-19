#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 09:54:02 2024

@author: rbj
Adds two levels of the foldername to the filenames in a range of folders
"""

import os
import tkinter as tk
from tkinter import filedialog

def rename_files_in_subfolders(parent_directory):
    for dirpath, dirnames, filenames in os.walk(parent_directory):
        # Split the dirpath into a list of folders
        folders = dirpath.split(os.sep)
        # If there are at least two folders (the parent and the current one)
        if len(folders) >= 2:
            # Get the last two folder names
            parent_folder_name = folders[-2]
            folder_name = folders[-1]
            for filename in filenames:
                if "parquet" in filename:
                    new_filename = f"{parent_folder_name}_{folder_name}_{filename}"
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