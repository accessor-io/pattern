#!/usr/bin/env python3

import numpy as np
from scipy.io import wavfile

# Generate a simple beep
sample_rate = 44100
duration = 0.5  # seconds
t = np.linspace(0, duration, int(sample_rate * duration))

# Create a 440 Hz sine wave
frequency = 440
amplitude = 0.8
signal = amplitude * np.sin(2 * np.pi * frequency * t)

# Convert to 16-bit PCM
signal = np.int16(signal * 32767)

# Save as WAV file
wavfile.write('beep.wav', sample_rate, signal)

print("Generated beep.wav - please try playing this file") 