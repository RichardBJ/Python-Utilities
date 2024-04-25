import re

def calibrate(raw, YZ, AD, YCF, YAG, ADCMAX):
    return list(map(lambda x: (x - YZ) * AD / (YCF * YAG * (ADCMAX + 1)), raw))


with open('nat_006.EDR', 'rb') as my_file:
    # Read the data file in its entirety and get the head and data contents.
    data = my_file.read()
    header = data[:2049].decode('ASCII')
    contents = data[2049:]

    # Convert the contents from bytes to integers.
    parsed = list(contents)

    # Find the conversion parameters from the header.
    YZn = re.findall(r'(?<=YZ\d=)\-?\d+\.?\d*',header)
    AD = re.findall(r'(?<=AD=)\-?\d+\.?\d*',header)
    YCFn = re.findall(r'(?<=YCF\d=)\-?\d+\.?\d*',header)
    YAGn = re.findall(r'(?<=YAG\d=)\-?\d+\.?\d*',header)
    ADCMAX = re.findall(r'(?<=ADCMAX=)\-?\d+\.?\d*',header)

    # How many signals are there?
    num_signals = len(YZn)
    
    # Separate signals
    split = [parsed[i::num_signals] for i in range(num_signals)]
        
    # Convert signals to adjusted readings
    calibrated = [calibrate(split[i], float(YZn[i]), float(AD[0]), float(YCFn[i]), float(YAGn[i]), float(ADCMAX[0])) for i in range(num_signals)]

print(header)
print('YZn:', YZn)
print('AD:', AD)
print('YCFn:', YCFn)
print('YAGn:', YAGn)
print('ADCMAX:', ADCMAX)
input('Press ENTER to continue')
print(calibrated[0][:100])

import matplotlib.pyplot as plt

MAGIC_NUM = 100000
plt.plot(range(MAGIC_NUM), calibrated[0][:MAGIC_NUM])
plt.ylim(-1, 5)
plt.show()
