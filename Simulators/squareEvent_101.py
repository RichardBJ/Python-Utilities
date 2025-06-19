#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np


# Define the parameters for the square wave
amplitude = 1
frequency1 = 3
frequency2 = 3.5

time = np.linspace(0, 1, 500, endpoint=False)

# Generate the square waves
start = 50
endp = 100
square_wave1 = [1 if start < i < endp else 0 for i in range(500)]
start = 100
endp = 150
square_wave2 = [1 if start < i < endp else 0 for i in range(500)]
start = 150
endp = 160
square_wave3 = [1 if start < i < endp else 0 for i in range(500)]


# Create a DataFrame
df = pd.DataFrame({
    'Time': time,
    'SquareWave1': square_wave1,
    'SquareWave2': square_wave2,
    'SquareWave3': square_wave3
})
# Save the DataFrame as a Parquet file
df.to_parquet('square_wave2.parquet')
