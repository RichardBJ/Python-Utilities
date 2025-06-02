#!/usr/bin/env python3
#!/usr/bin/env python3
import csv, sys
from matplotlib import pyplot as plt
import numpy as np

a=[2]*150

a=np.asscalar(np.asarray(a))
print(a)

file="/Users/richardbarrett-jolley/Downloads/cts_data_0.csv"
seq=448
limit=10000000
start = 0
length = 102

raw = -1
idl = 2


import csv
x=[]
y=[]
i=0
j=0
firstline=True

print('Parsing data...')

with open(file) as infile:
    reader = csv.reader(infile)
    for row in reader:

        if firstline == True:
            # Don't read first line if header exists
            firstline = False
            continue

        elif i > limit:
            # Stop if past limit
            break

        else:
            # Add current and channels to respective lists
            i += 1
            x.append(float(row[raw]))
            y.append(float(row[idl]))

        if i % 10000 == 0:
            # Progress update every 10000 iterations
            print(f'Progress: {i}/{limit}', end='\r')
            sys.stdout.flush()

print("\n")
maxx=np.max(x)
maxy=np.max(y)
miny=np.min(y)
minx=np.min(y)
maxer=max([maxx,maxy])
miner=max([minx,miny])


print("original global max and mins", maxer,miner)

x=x-miner
x=x/(maxer)-0.5
pts = range(start, start+length)
labs = (np.asarray(y) / 2) + 1.5
xax = pts

plt.plot(xax, x[pts])
plt.plot(xax, labs[pts])
plt.hlines(0, start, start+length)
#plt.ylim([-1.1, 2.1])
plt.axis('on')
plt.show()
print('finished')