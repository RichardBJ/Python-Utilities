#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 17:37:17 2024

@author: rbj
"""

import os

# specify your source and destination directories
A = '/Users/rbj/Library/CloudStorage/OneDrive-TheUniversityofLiverpool/Data/seanb/2024_06_17/combo'
B = '/Users/rbj/Library/CloudStorage/OneDrive-TheUniversityofLiverpool/Data/COPY FOR GAN'

# get list of all files in directories
A_files = os.listdir(A)
B_files = os.listdir(B)
file_extension="parquet"

# filter files by extension and check if they exist in directory B
files_in_A_not_in_B = [file for file in A_files if file.endswith(file_extension) and file not in B_files]

files_in_A_not_in_B.sort()


# print the files
for file_name in files_in_A_not_in_B:
    print(file_name)