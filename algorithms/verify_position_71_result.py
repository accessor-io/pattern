#!/usr/bin/env python3
"""
Verify Position 71 Result
=========================
Verify that the found private key generates the correct Bitcoin address
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1

# Our predicted private key
FOUND_PRIVATE_KEY = 0x40760c9d7ecaf1f800
EXPECTED_ADDRESS = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

def private_key_to_address(private_key: int) -> str:
    """Convert private key to Bitcoin address"""
    # Convert to public key
    privkey_hex = format(private_key, '064x')
    privkey_bytes = bytes.fromhex(privkey_hex)
    sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    
    # Compressed public key (Position 71 uses compressed format)
    if y % 2 == 0:
        pubkey_bytes = b'\x02' + x.to_bytes(32, 'big')
    else:
        pubkey_bytes = b'\x03' + x.to_bytes(32, 'big')
    
    # Hash160 (SHA256 + RIPEMD160)
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    
    # Add version byte and checksum
    versioned_payload = b'\x00' + ripemd160_hash
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    address_bytes = versioned_payload + checksum
    
    # Base58 encode
    address = base58.b58encode(address_bytes).decode()
    return address

def main():
    print(f"\nVerifying private key for Bitcoin Puzzle #71")
    print(f"=============================================")
    print(f"Private Key (hex): {format(FOUND_PRIVATE_KEY, '016x')}")
    print(f"Expected Address: {EXPECTED_ADDRESS}")
    
    generated_address = private_key_to_address(FOUND_PRIVATE_KEY)
    print(f"Generated Address: {generated_address}")
    
    if generated_address == EXPECTED_ADDRESS:
        print("\n✅ SUCCESS! The private key generates the correct Bitcoin address!")
    else:
        print("\n❌ FAILURE! The private key does not generate the expected address.")

if __name__ == "__main__":
    main() 