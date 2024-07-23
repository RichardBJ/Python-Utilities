#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 17:30:38 2024

@author: rbj
"""

import shutil
import os

# specify your source and destination directories
source_dir = '/Users/rbj/Library/CloudStorage/OneDrive-TheUniversityofLiverpool/Data/seanb/2024_06_17/combo'
destination_dir = '/Users/rbj/Library/CloudStorage/OneDrive-TheUniversityofLiverpool/Data/COPY FOR GAN'

# get list of all files in directory
files_wanted = os.listdir(destination_dir)
files_to_copy = []

for file in files_wanted:
    files_to_copy.append(file.replace(".png",".parquet"))


for file_name in files_to_copy:
    source_file_path = os.path.join(source_dir, file_name)
    destination_file_path = os.path.join(destination_dir, file_name)

    # check if file exists in the source directory
    if os.path.exists(source_file_path):
        shutil.copy2(source_file_path, destination_file_path)
        print(f'Copied {file_name} from {source_dir} to {destination_dir}')
    else:
        print(f'{file_name} does not exist in {source_dir}')
