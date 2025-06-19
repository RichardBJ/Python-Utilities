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
PLOT = False
OLD = False
DECIMATE = 20

root = tkinter.Tk()
root.withdraw()
'''
currdir = os.getcwd()
headerFile = filedialog.askopenfilename(initialdir=currdir, title="Select .edh file", filetypes = (("elements data header","*.edh"),("all files","*.*")))
if len(headerFile) > 0:
    print ("You chose: %s" % headerFile)
    # Create a new filename by replacing the extension
    out_file = os.path.splitext(headerFile)[0] + '.csv'
'''

def process_file(headerFilename, decimate=1):
	oversamplingActive = False
	out_file = os.path.splitext(headerFilename)[0] + '.csv'
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
				#But also a voltage channel!
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
			
	#RBJ change
	col_dat = dat.reshape(-1,channelNum)[::decimate, :]

	L = len(dat)
	singleChanLen = int(L/channelNum)

	t = np.arange(0, singleChanLen)/Fs
	print(f'data length = {len(col_dat)}, time length = {len(t)}')
	if CONVERT & (not OLD):
		np.savetxt(out_file, col_dat, delimiter=',', fmt = '%.5f')

	#get ready to receive the data, start with time
	data_dict = {'t': t}

	if PLOT:
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
	elif CONVERT:
		for i in range(channelNum):
			data_dict[channelList[i]] = dat[range(i, L-channelNum+1+i, channelNum*decimate)]


	if CONVERT & OLD:
		# Write the data to a CSV file
		with open(out_file, 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(list(data_dict.keys()))  # Write the header
			writer.writerows(zip(*data_dict.values()))  # Write the data
		# Write the data to a CSV file
		with open("new_dat.csv", 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(list(data_dict.keys()))  # Write the header
			writer.writerows(col_dat)  # Write the data

	plt.show()
	
for dirpath, dirnames, filenames in os.walk("P:/Nanion"):
    for filename in filenames:
        # check if the file is a .csv file
        if filename.endswith('.edh'):
            # create full file path
            file_path = os.path.join(dirpath, filename)
            
            # process the file
            process_file(file_path,decimate=DECIMATE)