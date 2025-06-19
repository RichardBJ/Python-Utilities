#!/usr/bin/env python3
#!/usr/bin/env python3
import pandas as pd
import os
# I think this joins horizontally

# Define the folder path where the CSV files are located
folder_path = "/Users/richardbarrett-jolley/Library/CloudStorage/OneDrive-TheUniversityofLiverpool/Data/seanb/2024_02_23/output"

# Initialize an empty list to store dataframes
dfs = []

# Iterate over each file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        fsize = os.path.getsize(file_path)
        if fsize > 1000:
            df = pd.read_csv(file_path)
            nc = df.shape[1]
            if nc == 2:
                dfs.append(df["Channel 0"])

# Combine all dataframes into one
combined_df = pd.concat(dfs, axis=1, ignore_index=True)

# Print the combined dataframe
print(combined_df.head())
print(combined_df.info())
combined_filename = os.path.join(folder_path, "combined.csv")
combined_df.to_csv(combined_filename, index=False)

