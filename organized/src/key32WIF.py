#!/usr/bin/env python3

import sys
import hashlib
import base58

def private_key_to_wif(private_key_hex, compressed=True):
    # Validate private key
    if len(private_key_hex) != 64:
        raise ValueError("Private key must be 32 bytes (64 hex characters)")
    
    try:
        # Convert to bytes
        private_key_bytes = bytes.fromhex(private_key_hex)
    except ValueError:
        raise ValueError("Invalid hex string")

    # Add version byte (0x80 for mainnet)
    version_key = b'\x80' + private_key_bytes
    
    # Add compression flag if needed
    if compressed:
        version_key += b'\x01'
    
    # Double SHA256 for checksum
    double_sha256 = hashlib.sha256(hashlib.sha256(version_key).digest()).digest()
    
    # First 4 bytes of double SHA256 as checksum
    checksum = double_sha256[:4]
    
    # Concatenate everything and base58 encode
    wif = base58.b58encode(version_key + checksum).decode('utf-8')
    
    return wif

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <private_key_hex>")
        sys.exit(1)
        
    private_key = sys.argv[1]
    
    try:
        wif_compressed = private_key_to_wif(private_key, compressed=True)
        wif_uncompressed = private_key_to_wif(private_key, compressed=False)
        print(f"WIF (Compressed): {wif_compressed}")
        print(f"WIF (Uncompressed): {wif_uncompressed}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()