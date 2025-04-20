#!/usr/bin/env python3

import sys
import hashlib
import ecdsa
import base58

def private_key_to_addresses(private_key_hex):
    # Validate private key
    if len(private_key_hex) != 64:
        raise ValueError("Private key must be 32 bytes (64 hex characters)")
    
    try:
        private_key_bytes = bytes.fromhex(private_key_hex)
    except ValueError:
        raise ValueError("Invalid hex string")

    # Create signing key
    signing_key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
    verifying_key = signing_key.get_verifying_key()
    
    # Get public key points
    public_key_bytes = verifying_key.to_string()
    public_key_hex = public_key_bytes.hex()
    
    # Uncompressed public key (04 + x + y)
    uncompressed_public_key = "04" + public_key_hex
    
    # Compressed public key (02 or 03 + x)
    if int(public_key_hex[-2:], 16) % 2 == 0:
        compressed_public_key = "02" + public_key_hex[:64]
    else:
        compressed_public_key = "03" + public_key_hex[:64]
    
    # Generate addresses
    uncompressed_address = public_key_to_address(uncompressed_public_key)
    compressed_address = public_key_to_address(compressed_public_key)
    
    return {
        'uncompressed': uncompressed_address,
        'compressed': compressed_address
    }

def public_key_to_address(public_key_hex):
    # SHA256 of public key
    sha256_hash = hashlib.sha256(bytes.fromhex(public_key_hex)).digest()
    
    # RIPEMD160 of SHA256
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    
    # Add version byte (0x00 for mainnet)
    version_ripemd160_hash = b'\x00' + ripemd160_hash
    
    # Double SHA256 for checksum
    double_sha256 = hashlib.sha256(hashlib.sha256(version_ripemd160_hash).digest()).digest()
    
    # First 4 bytes of double SHA256 as checksum
    checksum = double_sha256[:4]
    
    # Concatenate version + ripemd160 hash + checksum
    binary_address = version_ripemd160_hash + checksum
    
    # Base58 encode
    address = base58.b58encode(binary_address).decode('utf-8')
    
    return address

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <private_key_hex>")
        sys.exit(1)
        
    private_key = sys.argv[1]
    
    try:
        addresses = private_key_to_addresses(private_key)
        print(f"Uncompressed Address: {addresses['uncompressed']}")
        print(f"Compressed Address: {addresses['compressed']}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()