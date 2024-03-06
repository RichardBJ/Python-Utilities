# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 17:56:28 2024

@author: rbj
"""

import pandas as pd

filename = 'example.csv'

# Read the CSV file
df = pd.read_csv(filename)



# Convert to Parquet and save
df.to_parquet(filename.replace(".csv", ".parquet"))