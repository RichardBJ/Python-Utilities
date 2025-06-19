#!/usr/bin/env python3
#!/usr/bin/env python3
#   Copyright (C) 2020 Filippo Cona
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   EDAmat is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with EDAmat.  If not, see <https://urldefense.com/v3/__http://www.gnu.org/licenses/>.

import numpy as np
import matplotlib.pyplot as plt
import tkinter
from tkinter import filedialog
import os
import glob
import csv

CONVERT = True

root = tkinter.Tk()
root.withdraw()

currdir = os.getcwd()
headerFilename = filedialog.askopenfilename(initialdir=currdir, title="Select .edh file", filetypes = (("elements data header","*.edh"),("all files","*.*")))
if len(headerFilename) > 0:
    print ("You chose: %s" % headerFilename)
    # Create a new filename by replacing the extension
    out_file = os.path.splitext(filename)[0] + '.csv'

oversamplingActive = False

with open(headerFilename) as fp:
    line = fp.readline()
    while line:
        parts = line.split(": ")
        if line.startswith("Channel"):
            currentChannelNum = int(parts[1])
            channelNum = currentChannelNum+1
            print("channels: " + str(channelNum))

        elif line.startswith("Range"):
            parts = parts[1].split(" ")
            currentRange = int(parts[0])
            currentUnit = parts[1].rstrip('\n')
            print("range: " + str(currentRange) + " " + currentUnit)

        elif "(SR" in line:
            parts = parts[1].split(" ")
            samplingRate = float(parts[0])
            samplingRateUnit = parts[1].rstrip('\n')
            if ")" in samplingRateUnit:
                samplingRateUnit = samplingRateUnit[:-1]
            print("sampling rate: " + str(samplingRate) + " " + samplingRateUnit)

        elif line.startswith("Oversampling"):
            if "enabled" in parts[1]:
                parts = parts[0].split("x")
                oversamplingActive = True
                oversamplingFactor = int(parts[1])
                print("final sampling rate: " + str(samplingRate*oversamplingFactor) + " " + samplingRateUnit)

        elif line.startswith("Active channels"):
            parts = parts[1].split(" ")
            currentChannelNum = len(parts);
            print("active current channels: " + str(currentChannelNum))
            channelNum = currentChannelNum+1
            channelList = parts
            channelList.append('Vc')

        line = fp.readline()

if samplingRateUnit == "Hz":
    lowSrCoeff = 1000000.0/1024.0
    xlabel = "s"

elif samplingRateUnit == "kHz":
    lowSrCoeff = 1000.0/1024.0
    xlabel = "ms"

elif samplingRateUnit == "MHz":
    lowSrCoeff = 1.0/1024.0
    xlabel = "us"

if samplingRate in [1.25, 5, 10, 20, 40]:
    Fs = lowSrCoeff*samplingRate

else:
    Fs = samplingRate

if oversamplingActive:
    Fs *= oversamplingFactor

print("real sampling rate: " + str(Fs) + " " + samplingRateUnit)
yLabels = []
for i in range(currentChannelNum):
    yLabels.append(currentUnit)

yLabels.append("mV")

datList = glob.glob(headerFilename[:-4] + "_*.dat")

dat = []

for dataFilename in datList:
    with open(dataFilename, 'rb') as f:
        dat = np.append(dat, np.fromfile(f, dtype=np.float32))

L = len(dat)
singleChanLen = int(L/channelNum)

t = np.arange(0, singleChanLen)/Fs

#get ready to receive the data, start with time
data_dict = {'t': t}

# uncomment following lines to plot
with open(out_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.write

plt.style.use('bmh')
plt.figure(figsize=(8, 5))
for i in range(channelNum):
    plt.subplot(channelNum, 1, i+1)
    plt.plot(t, dat[range(i, L-channelNum+1+i, channelNum)], lw=.5, label=channelList[i])
    plt.ylabel(yLabels[i])
    plt.xlabel(xlabel)
    plt.legend(loc="upper right")
    if CONVERT:
        # Add the data to the dictionary
        data_dict[channelList[i]] = dat[range(i, L-channelNum+1+i, channelNum)]

if CONVERT:
    # Write the data to a CSV file
    with open(out_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data_dict.keys())
        writer.writeheader()  # Write the header
        writer.writerows([dict(zip(data_dict, v)) for v in zip(*data_dict.values())])



plt.show()
