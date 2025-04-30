#!/usr/bin/env python3

import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solvers.archive.known_keys import KNOWN_KEYS, convert_significant_bits_to_ascii

print("Extracting hidden message from Bitcoin private keys...")
message = ""

# Process each key in order
for i in range(1, 67):  # Keys are from 1 to 66
    if i in KNOWN_KEYS:
        key = KNOWN_KEYS[i]
        ascii_part = convert_significant_bits_to_ascii(key)
        message += ascii_part
        print(f"Key {i}: {hex(key)[2:]} -> {ascii_part!r}")

print("\nFull message:")
print(message) 