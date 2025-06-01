#!/usr/bin/env python3
import hashlib
import base58
import re

# Suffixes from the user's screenshot
suffixes = [
    '6abe1f9b67e114',
    '9d18b63ac4ffdf', 
    '1eb25c90795d61c',
    '2c675b852189a21',
    '7496cbb87cab44f',
    '0fc07a1825367bbe',
    '13c96a3742f64906',
    '363d541eb611abee',
    '7cce5efdaccf6808',
    'f7051f27b09112d4',
    '1a838b13505b26867',
    '2832ed74f2b5e35ee',
    '730fc235c1942c1ae',
    'bebb3940cd0fc1491',
    '101d83275fb2bc7e0c',
    '349b84b6431a6c4ef1'
]

def address_to_hash160(address):
    """Convert Bitcoin address to hash160"""
    try:
        # Decode base58check
        decoded = base58.b58decode_check(address)
        # Skip version byte (first byte)
        hash160 = decoded[1:]
        return hash160.hex()
    except Exception as e:
        print(f"Error decoding address {address}: {e}")
        return None

def main():
    print("Comparing suffixes with hash160s from derived addresses...")
    print("=" * 60)
    
    matches = []
    addresses = []
    
    # Read the file and extract addresses
    try:
        with open('data/raw/key_generator_output_10_20250528.txt', 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            # Look for "Derived Address: " lines
            match = re.search(r'Derived Address: ([123mn][A-HJ-NP-Za-km-z1-9]{25,34})', line)
            if match:
                address = match.group(1)
                addresses.append(address)
                
    except FileNotFoundError:
        print("Error: File 'data/raw/key_generator_output_10_20250528.txt' not found")
        return
        
    print(f"Found {len(addresses)} derived addresses")
    print()
    
    # Compare each address's hash160 with suffixes
    for i, address in enumerate(addresses):
        hash160 = address_to_hash160(address)
        if hash160:
            print(f"Address {i+1}: {address}")
            print(f"Hash160: {hash160}")
            
            # Check if hash160 ends with any suffix
            for suffix in suffixes:
                if hash160.endswith(suffix):
                    matches.append((i+1, address, hash160, suffix))
                    print(f"*** MATCH! Ends with suffix: {suffix} ***")
                    
            # Check if any suffix is contained in hash160
            for suffix in suffixes:
                if suffix in hash160:
                    print(f"  Contains suffix: {suffix}")
                    
            print()
    
    print("=" * 60)
    print("SUMMARY OF MATCHES:")
    if matches:
        for index, address, hash160, suffix in matches:
            print(f"Index {index}: {address}")
            print(f"  Hash160: {hash160}")
            print(f"  Suffix:  {suffix}")
            print()
    else:
        print("No exact matches found where hash160 ends with provided suffixes.")
        print()
        print("Trying alternative approach: Check if suffixes match beginning of hash160...")
        
        for i, address in enumerate(addresses):
            hash160 = address_to_hash160(address)
            if hash160:
                for suffix in suffixes:
                    if hash160.startswith(suffix):
                        print(f"Index {i+1}: {address} - Hash160 STARTS with {suffix}")
                        
        print()
        print("Trying: Check if suffixes are substrings of hash160...")
        substring_matches = []
        for i, address in enumerate(addresses):
            hash160 = address_to_hash160(address)
            if hash160:
                for suffix in suffixes:
                    if suffix in hash160:
                        substring_matches.append((i+1, address, hash160, suffix))
                        
        if substring_matches:
            print("Substring matches found:")
            for index, address, hash160, suffix in substring_matches:
                print(f"Index {index}: {address}")
                print(f"  Hash160: {hash160}")
                print(f"  Contains: {suffix}")
                print()

if __name__ == "__main__":
    main() 