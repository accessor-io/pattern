#!/usr/bin/env python3

import sys
import os
import binascii

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solvers.archive.known_keys import KNOWN_KEYS

def convert_key_to_ascii(key: int) -> str:
    """Convert the key to an ASCII string with improved filtering."""
    # Get the hex representation without '0x' prefix
    hex_str = hex(key)[2:].lstrip('0')
    if not hex_str:
        hex_str = "0"
    # Ensure even length for bytes conversion
    if len(hex_str) % 2 != 0:
        hex_str = "0" + hex_str
    
    try:
        # Convert to bytes
        key_bytes = bytes.fromhex(hex_str)
        # Convert bytes to ASCII, filtering out non-printable/non-ASCII
        ascii_str = ''.join(chr(b) for b in key_bytes if 32 <= b <= 126)
        return ascii_str
    except:
        return ""

# Try different approaches
print("=== Analyzing Bitcoin private keys for hidden messages ===\n")

# Approach 1: Direct ASCII conversion of each key
print("Approach 1: Direct ASCII from each key")
message1 = ""
for i in range(1, 67):
    if i in KNOWN_KEYS:
        key = KNOWN_KEYS[i]
        ascii_part = convert_key_to_ascii(key)
        if ascii_part:
            message1 += ascii_part
            print(f"Key {i}: {hex(key)[2:]} -> {ascii_part!r}")

print("\nDirect ASCII message:")
print(message1)
print()

# Approach 2: Concatenate all hex values first, then convert to ASCII
print("\nApproach 2: Concatenated hex to ASCII")
all_hex = ""
for i in range(1, 67):
    if i in KNOWN_KEYS:
        hex_val = hex(KNOWN_KEYS[i])[2:].lstrip('0')
        all_hex += hex_val

# Ensure even length
if len(all_hex) % 2 != 0:
    all_hex = "0" + all_hex

try:
    # Convert to bytes and then ASCII
    full_bytes = bytes.fromhex(all_hex)
    message2 = ''.join(chr(b) for b in full_bytes if 32 <= b <= 126)
    print("Concatenated hex ASCII message:")
    print(message2)
except Exception as e:
    print(f"Error in hex conversion: {e}")

# Approach 3: XOR adjacent keys
print("\nApproach 3: XOR of adjacent keys")
message3 = ""
for i in range(1, 66):  # Up to 65 to get pairs
    if i in KNOWN_KEYS and i+1 in KNOWN_KEYS:
        xor_result = KNOWN_KEYS[i] ^ KNOWN_KEYS[i+1]
        ascii_part = convert_key_to_ascii(xor_result)
        if ascii_part:
            message3 += ascii_part
            print(f"XOR Keys {i}&{i+1}: {hex(xor_result)[2:]} -> {ascii_part!r}")

print("\nXOR ASCII message:")
print(message3) 