# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
from scipy import signal

# Define the parameters for the square wave
amplitude = 1
frequency1 = 3
frequency2 = 3.5

time = np.linspace(0, 1, 500, endpoint=False)

# Generate the square waves
square_wave1 = amplitude * signal.square(2 * np.pi * frequency1 * time)
square_wave2 = amplitude * signal.square(2 * np.pi * frequency2 * time)
square_wave3 = np.roll(square_wave1,50)

# Create a DataFrame
df = pd.DataFrame({
    'Time': time,
    'SquareWave1': square_wave1,
    'SquareWave2': square_wave2,
    'SquareWave3': square_wave3
})
# Save the DataFrame as a Parquet file
df.to_parquet('square_wave.parquet')
