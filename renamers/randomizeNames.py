# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 10:16:07 2024

@author: rbj
"""
import os
import tkinter as tk
from tkinter import filedialog
import random

def prepend_random_integer(folder_path):
    # Get the list of files in the folder
    files = os.listdir(folder_path)
    num_files = len(files)

    # Shuffle a list of indices
    shuffled_indices = list(range(1, num_files + 1))
    random.shuffle(shuffled_indices)

    # Pair shuffled indices with filenames
    new_filenames = [f"{index}_{filename}" for index, filename in zip(shuffled_indices, files)]

    # Rename files
    for filename, new_filename in zip(files, new_filenames):
        old_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(folder_path, new_filename)
        os.rename(old_file_path, new_file_path)

def select_directory():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory()  # Open the dialog to choose a directory
    return folder_path

# Call the function to select a directory and prepend random integers to filenames
selected_folder = select_directory()
if selected_folder:
    prepend_random_integer(selected_folder)
    print("Random integers prepended to filenames successfully!")
else:
    print("No folder selected. Exiting.")
