#!/usr/bin/env python3
import pandas as pd
import hashlib, glob

def extract_hashtags(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    hashtags = [line.split()[0] for line in lines if line.strip()]
    return hashtags

# Use the function
original_hashtags = extract_hashtags("raw.md5")
new_hashtags = pd.read_csv("hashtags.csv")["MD5"]

original_hashtags = [hashtag.strip().lower() for hashtag in original_hashtags]
new_hashtags = [hashtag.strip().lower() for hashtag in new_hashtags]


for hashtag in new_hashtags:
	print (hashtag)


for hashtag in original_hashtags:
    found = True if hashtag in new_hashtags else False
    print(f"{hashtag} found  = {found}")
    