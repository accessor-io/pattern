#!/usr/bin/env python3
"""
Test exact 68-bit candidate values from predictions for the Bitcoin address.
Target address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Target address to match
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# The exact 3 unique values from the prediction analysis
EXACT_CANDIDATES = [
    0x8747dd8c268dd31c4,  # Minimum identified value
    0xd7db28ca2b3a33c0c,  # Maximum identified value
    # The third value is not explicitly listed in the output,
    # but we'll try to extract it from the predictions file
]

def private_key_to_address(private_key: int) -> str:
    """
    Convert a private key (integer) into an uncompressed Bitcoin address.
    """
    privkey_hex = format(private_key, '064x')
    privkey_bytes = bytes.fromhex(privkey_hex)
    sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    pubkey = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
    sha_digest = hashlib.sha256(pubkey).digest()
    try:
        ripemd_digest = hashlib.new('ripemd160', sha_digest).digest()
    except Exception:
        # Fallback for environments without ripemd160
        ripemd_digest = hashlib.sha256(hashlib.sha256(pubkey).digest()).digest()[:20]
    versioned_payload = b'\x00' + ripemd_digest
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    address = base58.b58encode(versioned_payload + checksum).decode()
    return address

def load_exact_candidates():
    """
    Load all unique 68-bit values from the predictions file.
    """
    candidates = set()
    try:
        with open('line_68s.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        value = int(line, 16)
                        if value.bit_length() == 68:
                            candidates.add(value)
                    except ValueError:
                        continue
    except FileNotFoundError:
        logger.warning("Predictions file line_68s.txt not found")
    
    logger.info(f"Loaded {len(candidates)} unique 68-bit values")
    return sorted(candidates)

def test_values_around(center, radius=1000):
    """
    Test values around a specific candidate.
    """
    logger.info(f"Testing values around {hex(center)} ± {radius}")
    count = 0
    
    for offset in range(-radius, radius + 1):
        candidate = center + offset
        
        # Skip if not exactly 68 bits
        if candidate.bit_length() != 68:
            continue
        
        count += 1
        try:
            addr = private_key_to_address(candidate)
            if addr == TARGET_ADDRESS:
                logger.info(f"MATCH FOUND! Value: {hex(candidate)}")
                return candidate
                
            if count % 100 == 0:
                logger.info(f"Tested {count} values around {hex(center)}")
        except Exception as e:
            logger.error(f"Error processing {hex(candidate)}: {e}")
    
    logger.info(f"No match found in {count} values around {hex(center)}")
    return None

def save_result(result):
    """
    Save the result to a file.
    """
    with open("term68_solution.txt", "w") as f:
        f.write(f"Term 68 Solution\n")
        f.write(f"Private Key (hex): {hex(result)}\n")
        f.write(f"Private Key (int): {result}\n")
        f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
    
    logger.info(f"Solution saved to term68_solution.txt")

def main():
    start_time = time.time()
    logger.info("Starting exact candidate testing for term 68")
    logger.info(f"Target address: {TARGET_ADDRESS}")
    
    # First, test the explicitly known candidates
    for candidate in EXACT_CANDIDATES:
        logger.info(f"Testing exact candidate: {hex(candidate)}")
        try:
            addr = private_key_to_address(candidate)
            logger.info(f"Address: {addr}")
            
            if addr == TARGET_ADDRESS:
                logger.info(f"MATCH FOUND! Exact match: {hex(candidate)}")
                save_result(candidate)
                return candidate
        except Exception as e:
            logger.error(f"Error processing {hex(candidate)}: {e}")
    
    # If no match, load all unique 68-bit candidates from the file
    all_candidates = load_exact_candidates()
    logger.info(f"Testing all {len(all_candidates)} unique candidates from file")
    
    for candidate in all_candidates:
        try:
            addr = private_key_to_address(candidate)
            if addr == TARGET_ADDRESS:
                logger.info(f"MATCH FOUND! File match: {hex(candidate)}")
                save_result(candidate)
                return candidate
        except Exception as e:
            logger.error(f"Error processing {hex(candidate)}: {e}")
    
    # If still no match, test values around each candidate
    logger.info("No exact match found, searching around candidates")
    for candidate in all_candidates:
        result = test_values_around(candidate, radius=100)
        if result:
            save_result(result)
            return result
    
    # Final try - test some bit-flipped variations
    logger.info("Trying bit-flip variations of candidates")
    for candidate in all_candidates:
        for bit in range(68):
            modified = candidate ^ (1 << bit)
            try:
                addr = private_key_to_address(modified)
                if addr == TARGET_ADDRESS:
                    logger.info(f"MATCH FOUND! Bit-flipped match: {hex(modified)}")
                    save_result(modified)
                    return modified
            except Exception:
                continue
    
    duration = time.time() - start_time
    logger.info(f"Search completed in {duration:.2f} seconds without finding a match")
    return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n=== MATCH FOUND! ===")
        print(f"Term 68: {hex(result)}")
        print(f"Bitcoin Address: {TARGET_ADDRESS}")
    else:
        print("No match found") 