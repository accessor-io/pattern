#!/usr/bin/env python3

import sys
import os
import hashlib
import binascii
import re

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_keys_from_sequence():
    """Load all 160 keys from the verified Bitcoin sequence"""
    sequence_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               "hex_sequence_analysis", "verified_bitcoin_sequence.txt")
    
    keys = {}
    with open(sequence_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split('. ')
            if len(parts) != 2:
                continue
                
            index = int(parts[0])
            key_parts = parts[1].split(' - ')
            key = key_parts[0]
            
            keys[index] = key
            
    return keys

def convert_key_to_ascii(hex_str):
    """Convert a hex key to ASCII characters"""
    if not hex_str:
        return ""
        
    # Strip leading zeros
    hex_str = hex_str.lstrip('0')
    
    # Ensure even length for bytes conversion
    if len(hex_str) % 2 != 0:
        hex_str = "0" + hex_str
    
    try:
        # Convert to bytes
        key_bytes = bytes.fromhex(hex_str)
        # Convert bytes to ASCII, filtering out non-printable/non-ASCII
        ascii_str = ''.join(chr(b) for b in key_bytes if 32 <= b <= 126)
        return ascii_str
    except Exception as e:
        print(f"Error converting key to ASCII: {e}")
        return ""

def is_valid_bitcoin_address(address):
    """Basic validation of Bitcoin address format"""
    # Length check
    if len(address) < 25 or len(address) > 34:
        return False
    
    # Character set check (Base58)
    if not re.match(r'^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+$', address):
        return False
    
    # Common prefixes
    if not (address.startswith('1') or address.startswith('3') or address.startswith('bc1')):
        return False
        
    return True

def main():
    """Analyze all 160 keys in the sequence"""
    print("Loading all 160 keys from the Bitcoin sequence...")
    keys = load_keys_from_sequence()
    
    print(f"Loaded {len(keys)} keys from the sequence")
    
    # Extract ASCII characters from each key
    print("\nExtracting ASCII from keys:")
    all_ascii = ""
    ascii_by_key = {}
    
    for i in range(1, 161):
        if i in keys:
            key = keys[i]
            ascii_part = convert_key_to_ascii(key)
            ascii_by_key[i] = ascii_part
            all_ascii += ascii_part
            if ascii_part:
                print(f"Key {i}: {key} -> {ascii_part!r}")
    
    print("\nFull ASCII message from all 160 keys:")
    print(all_ascii)
    
    # Save the ASCII to a file
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "all_keys_ascii.txt"), "w") as f:
        f.write(all_ascii)
    
    # Focused steganographic analysis
    print("\n=== Advanced Steganographic Analysis ===")
    
    # Try the Nth character of the Nth key/ASCII (classic steganographic technique)
    print("\n1. Taking the Nth character of the Nth ASCII:")
    
    for offset in range(5):  # Try different offsets
        steg_result = ""
        
        for i in range(1, 161):
            if i in ascii_by_key and ascii_by_key[i]:
                # Get the i-th character of this key's ASCII, with an offset
                if len(ascii_by_key[i]) > 0:
                    char_pos = min((i - 1 + offset) % len(ascii_by_key[i]), len(ascii_by_key[i]) - 1)
                    steg_result += ascii_by_key[i][char_pos]
        
        print(f"Offset {offset}: {steg_result}")
        
        # Check if this forms a valid Bitcoin address
        if is_valid_bitcoin_address(steg_result):
            print(f"FOUND VALID BITCOIN ADDRESS (offset {offset}): {steg_result}")
    
    # Try taking the Nth character of the Nth key's ASCII
    print("\n2. Taking character at position N from ASCII of key N:")
    
    nth_char_of_nth_key = ""
    for i in range(1, 161):
        if i in ascii_by_key and ascii_by_key[i]:
            # Take the minimum to avoid index errors
            pos = min(i - 1, len(ascii_by_key[i]) - 1) if len(ascii_by_key[i]) > 0 else 0
            if len(ascii_by_key[i]) > 0:
                nth_char_of_nth_key += ascii_by_key[i][pos]
    
    print(f"Result: {nth_char_of_nth_key}")
    
    if is_valid_bitcoin_address(nth_char_of_nth_key):
        print(f"FOUND VALID BITCOIN ADDRESS: {nth_char_of_nth_key}")
    
    # Finally, check for specific sequence:
    # If we take the first character from key 1, second character from key 2, etc.
    print("\n3. Taking the Nth character from ASCII of key N (classic cipher):")
    
    nth_position = ""
    for i in range(1, 161):
        if i in ascii_by_key and ascii_by_key[i]:
            # If this ASCII part is long enough, take the Nth character
            if len(ascii_by_key[i]) >= i:
                nth_position += ascii_by_key[i][i-1]
            # Otherwise, wrap around
            elif len(ascii_by_key[i]) > 0:
                nth_position += ascii_by_key[i][(i-1) % len(ascii_by_key[i])]
    
    print(f"Result: {nth_position}")
    
    if is_valid_bitcoin_address(nth_position):
        print(f"FOUND VALID BITCOIN ADDRESS: {nth_position}")
        
    # Try with first character of each key's ASCII
    print("\n4. First character of each key with ASCII:")
    
    first_chars = ""
    for i in range(1, 161):
        if i in ascii_by_key and ascii_by_key[i] and len(ascii_by_key[i]) > 0:
            first_chars += ascii_by_key[i][0]
    
    print(f"Result: {first_chars}")
    
    if is_valid_bitcoin_address(first_chars):
        print(f"FOUND VALID BITCOIN ADDRESS: {first_chars}")
    
    # Look for Bitcoin address patterns in sliding windows
    for window_size in range(25, 35):  # Bitcoin addresses are 25-34 chars
        for i in range(len(all_ascii) - window_size):
            candidate = all_ascii[i:i+window_size]
            if is_valid_bitcoin_address(candidate):
                print(f"Found valid Bitcoin address in full ASCII at position {i}: {candidate}")
    
    # Scan through all possible combinations of characters from specific positions
    sliding_window_size = 30  # Typical Bitcoin address length
    for start_pos in range(len(all_ascii) - sliding_window_size):
        candidate = all_ascii[start_pos:start_pos+sliding_window_size]
        if candidate.startswith('1') and is_valid_bitcoin_address(candidate):
            print(f"Found valid Bitcoin address at position {start_pos}: {candidate}")

if __name__ == "__main__":
    main() 