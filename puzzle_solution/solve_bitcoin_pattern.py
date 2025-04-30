#!/usr/bin/env python3

import sys
import os
import hashlib
import base58
import binascii

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solvers.archive.known_keys import KNOWN_KEYS

# Try to assemble keys into something meaningful
print("=== Bitcoin-Specific Pattern Analysis ===\n")

# Function to convert a private key to a Bitcoin address (simplified)
def privkey_to_address(private_key):
    try:
        # Convert to hex
        private_key_bytes = private_key.to_bytes(32, byteorder='big')
        
        # Get public key using a placeholder approach (this is simplified)
        # In real Bitcoin implementation, this uses elliptic curve multiplication
        # Here we're just hashing as placeholder 
        sha = hashlib.sha256(private_key_bytes).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha)
        public_key_hash = ripemd160.digest()
        
        # Add version byte (0x00 for mainnet)
        versioned_payload = b'\x00' + public_key_hash
        
        # Double SHA-256 to get checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        
        # Combine and Base58 encode
        binary_address = versioned_payload + checksum
        address = base58.b58encode(binary_address)
        
        return address.decode('utf-8')
    except Exception as e:
        return f"Error: {str(e)}"

# Approach 1: Check if the keys form a valid seed phrase when combined
keys_hex = [hex(KNOWN_KEYS[i])[2:] for i in range(1, 67) if i in KNOWN_KEYS]

print("Approach 1: Examining if keys form seed phrases")
chunks = [keys_hex[i:i+12] for i in range(0, len(keys_hex), 12)]
for i, chunk in enumerate(chunks):
    print(f"Potential seed phrase {i+1}: {' '.join(chunk)}")
print()

# Approach 2: Check if adjacent keys represent private/public key pairs
print("Approach 2: Looking for private/public key pairs")
for i in range(1, 66):
    if i in KNOWN_KEYS and i+1 in KNOWN_KEYS:
        print(f"Keys {i} & {i+1}: {hex(KNOWN_KEYS[i])} -> {hex(KNOWN_KEYS[i+1])}")
print()

# Approach 3: Concatenate specific keys based on a pattern
print("Approach 3: Concatenating keys with ASCII values spelling something meaningful")
# Convert each key's hex value to a string, then check for letter patterns

# First, filter for keys with ASCII representations
ascii_keys = {}
for i in range(1, 67):
    if i in KNOWN_KEYS:
        key = KNOWN_KEYS[i]
        hex_str = hex(key)[2:].lstrip('0')
        if len(hex_str) % 2 != 0:
            hex_str = "0" + hex_str
        try:
            key_bytes = bytes.fromhex(hex_str)
            ascii_str = ''.join(chr(b) for b in key_bytes if 32 <= b <= 126)
            if ascii_str:
                ascii_keys[i] = ascii_str
        except:
            pass

print("Keys with ASCII values:")
for idx, val in ascii_keys.items():
    print(f"Key {idx}: {val}")

# Check if the indices spell something when put together
indices = list(ascii_keys.keys())
indices_hex = ''.join([hex(i)[2:] for i in indices])
print(f"\nIndices as hex: {indices_hex}")
try:
    if len(indices_hex) % 2 != 0:
        indices_hex = "0" + indices_hex
    indices_bytes = bytes.fromhex(indices_hex)
    indices_ascii = ''.join(chr(b) for b in indices_bytes if 32 <= b <= 126)
    print(f"Indices as ASCII: {indices_ascii}")
except Exception as e:
    print(f"Error in hex conversion: {e}")

# Approach 4: Try all keys as potential private keys to get Bitcoin addresses
print("\nApproach 4: Generate Bitcoin addresses from each key")
for i in range(1, 67):
    if i in KNOWN_KEYS:
        key = KNOWN_KEYS[i]
        if key < 2**256:  # Valid range for Bitcoin private keys
            addr = privkey_to_address(key)
            print(f"Key {i} ({hex(key)}) -> Address: {addr}")

# Approach 5: Check if the keys, when sorted, reveal a pattern
print("\nApproach 5: Sorted keys analysis")
sorted_keys = sorted([(i, KNOWN_KEYS[i]) for i in range(1, 67) if i in KNOWN_KEYS], key=lambda x: x[1])
print("Keys sorted by value:")
for idx, (original_idx, key) in enumerate(sorted_keys):
    print(f"Position {idx+1}: Key {original_idx} = {hex(key)}")

# Additional analysis: Look for Bitcoin-specific constants
print("\nChecking for Bitcoin constants in the keys:")
bitcoin_constants = {
    "SECP256K1 P": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    "SECP256K1 N": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
    "Hash160 Size": 0x14,
    "P2PKH version": 0x00,
    "P2SH version": 0x05,
    "WIF version": 0x80,
    "SIGHASH_ALL": 0x01,
    "SIGHASH_NONE": 0x02,
    "SIGHASH_SINGLE": 0x03,
}

for name, constant in bitcoin_constants.items():
    for i in range(1, 67):
        if i in KNOWN_KEYS and KNOWN_KEYS[i] == constant:
            print(f"Key {i} matches {name}: {hex(constant)}") 