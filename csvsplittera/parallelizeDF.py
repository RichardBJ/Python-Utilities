#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 12:18:00 2024

@author: rbj

Requires you already opened your PD dataframe
with "read_parquet for example". THEN you select this script and f9
NOTE we will crop any column less than the full length!!

"""
import pandas as pd
import math
DROPTIME = True
num_current_columns = 30 #Target since may be cropped
newLen = int(math.floor(len(df)/num_current_columns))
print(newLen)

# Create a new DataFrame with the desired columns
new_columns = ['Time']
new_df = pd.DataFrame(columns=new_columns)

# Populate the Time column with the original Time values
new_df['Time'] = df.loc[0:newLen,'Time']
print(new_df.info())

# Populate the Voltage columns with the corresponding Voltage values, reset to start at Time zero
for i, j in enumerate(range(0,len(df)-(newLen-1),newLen)):
    new_df[f'Current_{i}'] = df.loc[j:j+newLen-1,'Noisy Current'].reset_index(drop=True)
print(new_df.info())

if DROPTIME:
    new_df.drop("Time",axis=1, inplace=True)
new_df.to_parquet(file_path.replace(".parquet","_para.parquet"))
