#!/usr/bin/env python3
import hashlib
import base58
from ecdsa import SigningKey, SECP256k1

def private_key_to_address(private_key_int, compressed=True):
    """Convert private key integer to Bitcoin address"""
    try:
        # Convert to 32-byte private key
        private_key_bytes = private_key_int.to_bytes(32, 'big')
        
        # Generate signing key
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Generate public key
        if compressed:
            x = vk.pubkey.point.x()
            y = vk.pubkey.point.y()
            if y % 2 == 0:
                public_key = b'\x02' + x.to_bytes(32, 'big')
            else:
                public_key = b'\x03' + x.to_bytes(32, 'big')
        else:
            public_key = b'\x04' + vk.to_string()
        
        # Hash public key: SHA256 then RIPEMD160
        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Add version byte (0x00 for mainnet)
        versioned_payload = b'\x00' + ripemd160_hash
        
        # Calculate checksum (first 4 bytes of double SHA256)
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        
        # Combine and encode with Base58
        full_payload = versioned_payload + checksum
        address = base58.b58encode(full_payload).decode()
        
        return address, ripemd160_hash.hex(), public_key.hex()
        
    except Exception as e:
        print(f"Error converting private key: {e}")
        return None, None, None

def main():
    # Private key from user
    private_key_hex = "0x45848500718449031"
    
    # Remove 0x prefix if present and convert to integer
    if private_key_hex.startswith('0x'):
        private_key_hex = private_key_hex[2:]
    
    private_key_int = int(private_key_hex, 16)
    
    print("Bitcoin Address Conversion")
    print("=" * 50)
    print(f"Private Key (hex): {private_key_hex}")
    print(f"Private Key (int): {private_key_int}")
    print(f"Private Key (32-byte hex): {private_key_int:064x}")
    print()
    
    # Convert to compressed address
    address_compressed, hash160_compressed, pubkey_compressed = private_key_to_address(private_key_int, compressed=True)
    
    if address_compressed:
        print("COMPRESSED ADDRESS:")
        print(f"  Address:    {address_compressed}")
        print(f"  Hash160:    {hash160_compressed}")
        print(f"  Public Key: {pubkey_compressed}")
        print()
    
    # Convert to uncompressed address
    address_uncompressed, hash160_uncompressed, pubkey_uncompressed = private_key_to_address(private_key_int, compressed=False)
    
    if address_uncompressed:
        print("UNCOMPRESSED ADDRESS:")
        print(f"  Address:    {address_uncompressed}")
        print(f"  Hash160:    {hash160_uncompressed}")
        print(f"  Public Key: {pubkey_uncompressed}")
        print()
    
    # Additional info
    print("ADDITIONAL INFO:")
    print(f"  Private key is in range: {1 <= private_key_int < 2**256}")
    print(f"  Private key bit length: {private_key_int.bit_length()}")
    
    # Check if this matches any known puzzle
    puzzle_ranges = {
        1: (1, 1),
        2: (2, 3),
        3: (4, 7),
        4: (8, 15),
        5: (16, 31),
        10: (2**9, 2**10-1),
        20: (2**19, 2**20-1),
        30: (2**29, 2**30-1),
        40: (2**39, 2**40-1),
        50: (2**49, 2**50-1),
        60: (2**59, 2**60-1),
        70: (2**69, 2**70-1),
        71: (2**70, 2**71-1),
    }
    
    for puzzle_num, (min_val, max_val) in puzzle_ranges.items():
        if min_val <= private_key_int <= max_val:
            print(f"  This key is in Bitcoin Puzzle #{puzzle_num} range!")
            break
    else:
        print(f"  This key is not in any standard Bitcoin puzzle range.")

if __name__ == "__main__":
    main() 