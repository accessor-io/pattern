#!/usr/bin/env python3

import numpy as np
from scipy.io import wavfile

# Generate a test sound with multiple frequencies
duration = 3  # seconds
sample_rate = 44100
t = np.linspace(0, duration, int(sample_rate * duration))

# Create a mix of frequencies
frequencies = [440, 880, 1760]  # A4, A5, A6
signal = np.zeros_like(t)
for freq in frequencies:
    signal += np.sin(2 * np.pi * freq * t)

# Normalize and amplify
signal = signal / len(frequencies)  # Normalize
signal = signal * 0.9  # Amplify to 90% of maximum

# Add a volume envelope
envelope = np.ones_like(signal)
attack = int(0.1 * sample_rate)  # 100ms attack
decay = int(0.1 * sample_rate)   # 100ms decay
envelope[:attack] = np.linspace(0, 1, attack)
envelope[-decay:] = np.linspace(1, 0, decay)
signal = signal * envelope

# Save as WAV file
wavfile.write('test_sound.wav', sample_rate, signal.astype(np.float32)) 