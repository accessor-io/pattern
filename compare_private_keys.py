#!/usr/bin/env python3
import hashlib
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

def main():
    print("Comparing suffixes with private keys from generator output...")
    print("=" * 60)
    
    private_keys = []
    target_addresses = []
    
    # Read the file and extract private keys and target addresses
    try:
        with open('data/raw/key_generator_output_10_20250528.txt', 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            # Look for private key lines
            hex_match = re.search(r'Known Private Key \(Hex\): ([0-9a-fA-F]+)', line)
            if hex_match:
                private_key_hex = hex_match.group(1)
                private_keys.append(private_key_hex)
                
            # Look for target address lines  
            target_match = re.search(r'Target: ([123mn][A-HJ-NP-Za-km-z1-9]{25,34})', line)
            if target_match:
                target_address = target_match.group(1)
                target_addresses.append(target_address)
                
    except FileNotFoundError:
        print("Error: File 'data/raw/key_generator_output_10_20250528.txt' not found")
        return
        
    print(f"Found {len(private_keys)} private keys")
    print(f"Found {len(target_addresses)} target addresses")
    print()
    
    # Check if suffixes match the end of private keys
    print("Checking if suffixes match end of private keys...")
    matches = []
    
    for i, pk_hex in enumerate(private_keys):
        print(f"Private Key {i+1}: {pk_hex}")
        
        for suffix in suffixes:
            if pk_hex.endswith(suffix):
                matches.append((i+1, pk_hex, suffix))
                print(f"*** MATCH! Ends with suffix: {suffix} ***")
                
        # Also check if suffix is contained anywhere in private key
        for suffix in suffixes:
            if suffix in pk_hex and not pk_hex.endswith(suffix):
                print(f"  Contains suffix: {suffix}")
        print()
    
    # Check if suffixes match hashes of private keys
    print("=" * 60)
    print("Checking if suffixes match SHA256 of private keys...")
    
    for i, pk_hex in enumerate(private_keys):
        # Hash the private key as hex string
        sha256_str = hashlib.sha256(pk_hex.encode()).hexdigest()
        # Hash the private key as bytes
        sha256_bytes = hashlib.sha256(bytes.fromhex(pk_hex)).hexdigest()
        
        print(f"Private Key {i+1}: {pk_hex}")
        print(f"  SHA256(as string): {sha256_str}")
        print(f"  SHA256(as bytes):  {sha256_bytes}")
        
        # Check if any suffix matches end of hash
        for suffix in suffixes:
            if sha256_str.endswith(suffix):
                print(f"  *** SHA256(string) ends with: {suffix} ***")
            if sha256_bytes.endswith(suffix):
                print(f"  *** SHA256(bytes) ends with: {suffix} ***")
        print()
    
    # Check target addresses
    print("=" * 60)
    print("Checking target addresses...")
    
    for i, addr in enumerate(target_addresses):
        print(f"Target Address {i+1}: {addr}")
        
        # Hash the address
        sha256_addr = hashlib.sha256(addr.encode()).hexdigest()
        print(f"  SHA256: {sha256_addr}")
        
        # Check if any suffix matches
        for suffix in suffixes:
            if sha256_addr.endswith(suffix):
                print(f"  *** SHA256 ends with: {suffix} ***")
        print()
    
    print("=" * 60)
    print("SUMMARY:")
    if matches:
        print("Private key matches:")
        for index, pk_hex, suffix in matches:
            print(f"  Key {index}: {pk_hex} ends with {suffix}")
    else:
        print("No matches found between suffixes and private keys.")

if __name__ == "__main__":
    main() 