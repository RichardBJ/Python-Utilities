#!/usr/bin/env python3
import hashlib, glob
import pandas as pd

files = glob.glob(r"**/*.gz", recursive=True)

table={}
for row, file in enumerate(files):
    print(file)
    table[row]=[file,hashlib.md5(open(file,'rb').
                            read()).hexdigest()]
							
tabledf=pd.DataFrame.from_dict(table, 
        orient='index',columns=['File', 'MD5'])
tabledf.head()

tabledf.to_csv("hashtags.csv",mode="a")