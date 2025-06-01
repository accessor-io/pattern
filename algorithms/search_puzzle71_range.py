#!/usr/bin/env python3
"""
Search Puzzle 71 Range
=====================
Iterate through variations of the predicted key
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
from concurrent.futures import ProcessPoolExecutor
import time

# Starting points (variations of our predicted key)
START_KEYS = [
    0x402f1c8d9d44b99800,  # Original prediction
    0x402f1c8d9d44b99000,  # Rounded down
    0x402f1c8d9d44b99fff,  # Rounded up
    0x402f1c8d9d44b90000,  # Further down
    0x402f1c8d9d44ba0000,  # Further up
    0x402f1c8d9d44000000,  # Major variation
    0x402f1c8d9d45000000,  # Major variation up
]

CHUNK_SIZE = 1000000  # 1 million keys per chunk
TARGET_ADDRESS = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
TARGET_RIPEMD160 = "f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8"

def private_key_to_address(private_key: int) -> tuple[str, str]:
    """Convert private key to Bitcoin address and RIPEMD160"""
    try:
        # Convert to public key
        privkey_hex = format(private_key, '064x')
        privkey_bytes = bytes.fromhex(privkey_hex)
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Compressed public key
        if y % 2 == 0:
            pubkey_bytes = b'\x02' + x.to_bytes(32, 'big')
        else:
            pubkey_bytes = b'\x03' + x.to_bytes(32, 'big')
        
        # Hash160 (SHA256 + RIPEMD160)
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        ripemd160_hex = ripemd160_hash.hex()
        
        # Add version byte and checksum
        versioned_payload = b'\x00' + ripemd160_hash
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        address_bytes = versioned_payload + checksum
        
        # Base58 encode
        address = base58.b58encode(address_bytes).decode()
        return address, ripemd160_hex
    except Exception:
        return None, None

def check_range(start: int, count: int, direction: int = 1) -> tuple[int, str, str]:
    """Check a range of private keys"""
    for i in range(count):
        key = start + (i * direction)  # Direction can be 1 or -1
        addr, ripemd = private_key_to_address(key)
        if addr is None:  # Skip invalid keys
            continue
        if ripemd == TARGET_RIPEMD160:
            return key, addr, ripemd
        if i % 100000 == 0:  # Reduced progress output frequency
            print(f"Checked {'up' if direction > 0 else 'down'} to: 0x{key:x} from start: 0x{start:x}")
    return None, None, None

def main():
    print(f"\nSearching for Bitcoin Puzzle #71 private key")
    print(f"==========================================")
    print(f"Target Address: {TARGET_ADDRESS}")
    print(f"Target RIPEMD160: {TARGET_RIPEMD160}")
    print("\nTrying multiple starting points:")
    for key in START_KEYS:
        print(f"0x{key:x}")
    
    start_time = time.time()
    
    # Use multiple processes to speed up search
    with ProcessPoolExecutor() as executor:
        futures = []
        for start_key in START_KEYS:
            # 2 processes per starting point - one up, one down
            futures.append(executor.submit(check_range, start_key, CHUNK_SIZE, 1))
            futures.append(executor.submit(check_range, start_key, CHUNK_SIZE, -1))
        
        # Check results as they complete
        for future in futures:
            key, addr, ripemd = future.result()
            if key:
                elapsed = time.time() - start_time
                print(f"\n✅ FOUND THE KEY!")
                print(f"Private Key (hex): 0x{key:x}")
                print(f"Generated Address: {addr}")
                print(f"RIPEMD160: {ripemd}")
                print(f"Time taken: {elapsed:.2f} seconds")
                return
    
    print("\n❌ Key not found in these ranges.")

if __name__ == "__main__":
    main() 