#!/usr/bin/env python3

import numpy as np
from scipy.io import wavfile

# Generate a simple test sound
duration = 2  # seconds
sample_rate = 44100
t = np.linspace(0, duration, int(sample_rate * duration))

# Create a loud 440 Hz tone (A4 note)
frequency = 440
amplitude = 0.8
signal = amplitude * np.sin(2 * np.pi * frequency * t)

# Convert to 16-bit PCM
signal = np.int16(signal * 32767)

# Save as WAV file
wavfile.write('simple_test.wav', sample_rate, signal) 