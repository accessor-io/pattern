#!/usr/bin/env python3

import hashlib
import base58
import binascii

# The Bitcoin address we discovered
btc_address = "1CZqucvN1wZ4Gwq95dsNgj1xVjUcG9rEiQ"

print(f"Analyzing discovered Bitcoin address: {btc_address}")

# 1. Base58 decode the address
try:
    decoded = base58.b58decode(btc_address)
    print(f"\nBase58 decoded (hex): {decoded.hex()}")
    print(f"Length: {len(decoded)} bytes")
    
    # Check if this is a valid address structure (version + hash + checksum)
    if len(decoded) == 25:
        version = decoded[0]
        hash160 = decoded[1:21]
        checksum = decoded[21:25]
        
        print(f"\nVersion byte: {version} (0x{version:02x})")
        print(f"Hash160: {hash160.hex()}")
        print(f"Checksum: {checksum.hex()}")
        
        # Verify checksum
        hash_check = hashlib.sha256(hashlib.sha256(decoded[0:21]).digest()).digest()[:4]
        valid = hash_check == checksum
        print(f"Checksum valid: {valid}")
    
    # 2. Check for ASCII patterns in the hex representation
    hex_str = decoded.hex()
    potential_ascii = ""
    for i in range(0, len(hex_str), 2):
        if i + 2 <= len(hex_str):
            hex_byte = hex_str[i:i+2]
            byte_value = int(hex_byte, 16)
            if 32 <= byte_value <= 126:  # Printable ASCII range
                potential_ascii += chr(byte_value)
            else:
                potential_ascii += '.'
    
    print(f"\nPotential ASCII in hex: {potential_ascii}")
    
    # 3. Try different encodings/decodings
    try:
        hash160_ascii = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in hash160)
        print(f"Hash160 as ASCII: {hash160_ascii}")
    except:
        pass
    
    # 4. Check if the address can be interpreted as hexadecimal and decode
    address_without_1 = btc_address[1:]
    try:
        # Some puzzles encode messages by making them look like Bitcoin addresses
        print(f"\nAttempting to interpret address characters as clues:")
        print(f"Address without prefix '1': {address_without_1}")
        
        # Check for hex encoding
        if all(c in '0123456789ABCDEFabcdef' for c in address_without_1):
            try:
                hex_decoded = bytes.fromhex(address_without_1)
                hex_ascii = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in hex_decoded)
                print(f"As hex -> ASCII: {hex_ascii}")
            except:
                print("Not valid hex encoding")
    except:
        pass
    
    # 5. Look for reverse steganography - e.g., Nth character patterns
    print("\nChecking for character position patterns:")
    first_chars = ''.join([btc_address[i] for i in range(0, len(btc_address), 3)])
    print(f"Every 3rd char: {first_chars}")
    
    second_chars = ''.join([btc_address[i] for i in range(1, len(btc_address), 3)])
    print(f"Every 3rd char (offset 1): {second_chars}")
    
    third_chars = ''.join([btc_address[i] for i in range(2, len(btc_address), 3)])
    print(f"Every 3rd char (offset 2): {third_chars}")
    
    # 6. Numerical analysis
    print("\nNumerical analysis:")
    numerical_only = ''.join(c for c in btc_address if c.isdigit())
    print(f"Numerical digits only: {numerical_only}")
    
    alpha_only = ''.join(c for c in btc_address if c.isalpha())
    print(f"Alphabetical only: {alpha_only}")
    
except Exception as e:
    print(f"Error analyzing address: {e}")

print("\nPossible next steps:")
print("1. Look for patterns in the original key sequence")
print("2. Try deriving the private key for this address (if possible)")
print("3. Look for related addresses by changing one character")
print("4. Consider this address might be a clue to another puzzle") 