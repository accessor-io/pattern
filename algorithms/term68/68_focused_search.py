#!/usr/bin/env python3
"""
Focused Bitcoin key search for index 68, guided by constraints from existing analysis.
Target address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ

This script implements specialized search strategies:
1. Min/max boundary exploration
2. Pattern-based value generation
3. Systematic bit-level search
4. Key constraint validation
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import os
import json
import logging
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='68_focused_search.log',
    filemode='a'
)
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

# -----------------------------
# Configuration and Constants
# -----------------------------

TARGET_INDEX = 68  # Candidate key must be exactly 68 bits
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Known previous term for index 67 (mandatory minimum value)
PREV_TERM_67 = 0x730fc235c1942c1ae

# Estimated target value from previous search
ESTIMATE_VALUE = 0x12e7b5c4e1c670000

# Defined 68-bit boundaries
MIN_VALUE = PREV_TERM_67  # Absolute minimum is previous term
MAX_VALUE = (1 << 68) - 1  # Maximum 68-bit value 

# Load predicted 68th term values from line_68s.txt
def load_predictions():
    predictions = []
    try:
        with open('line_68s.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        # Convert hex string to integer
                        value = int(line, 16)
                        # Only include values that are exactly 68 bits and > PREV_TERM_67
                        if value.bit_length() == TARGET_INDEX and value > PREV_TERM_67:
                            predictions.append(value)
                    except ValueError:
                        continue
    except FileNotFoundError:
        logger.warning("predictions file line_68s.txt not found")
    
    # Sort and remove duplicates
    predictions = sorted(set(predictions))
    logger.info(f"Loaded {len(predictions)} valid predictions")
    return predictions

# -----------------------------
# Helper Functions
# -----------------------------

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

def has_too_many_consecutive_chars(value: int) -> bool:
    """
    Check if hex representation has more than 3 consecutive identical characters.
    """
    hex_str = hex(value)[2:]  # Remove '0x' prefix
    count = 1
    prev_char = hex_str[0]
    
    for char in hex_str[1:]:
        if char == prev_char:
            count += 1
            if count > 3:
                return True
        else:
            count = 1
            prev_char = char
    return False

def is_valid_candidate(value: int) -> bool:
    """
    Check if a value is a valid candidate for the 68th term:
    1. Must be > PREV_TERM_67
    2. Must be exactly 68 bits
    3. Must not have more than 3 consecutive identical hex chars
    """
    return (
        value > PREV_TERM_67 and 
        value.bit_length() == TARGET_INDEX and
        not has_too_many_consecutive_chars(value)
    )

# -----------------------------
# Search Strategies
# -----------------------------

def search_predictions(predictions):
    """
    Search through the list of predicted values.
    """
    logger.info(f"Starting search through {len(predictions)} predictions")
    tested = 0
    current_batch = 0
    batch_size = 1000
    total_batches = (len(predictions) + batch_size - 1) // batch_size
    
    for i, candidate in enumerate(predictions):
        if i % batch_size == 0:
            current_batch += 1
            logger.info(f"Processing batch {current_batch}/{total_batches} ({i}/{len(predictions)})")
        
        if not is_valid_candidate(candidate):
            continue
            
        tested += 1
        try:
            addr = private_key_to_address(candidate)
            if addr == TARGET_ADDRESS:
                logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                save_result(candidate)
                return candidate
                
            if tested % 100 == 0:
                logger.info(f"Tested {tested} candidates, current: {hex(candidate)}")
        except Exception as e:
            logger.error(f"Error processing {hex(candidate)}: {e}")
    
    logger.info(f"Completed testing {tested} predictions without finding a match")
    return None

def systematic_bit_search():
    """
    Systematically flip bits in promising regions to explore the space.
    """
    base_candidates = [
        PREV_TERM_67 + 1,                         # Just above minimum
        (PREV_TERM_67 + MAX_VALUE) // 2,          # Midpoint of range
        ESTIMATE_VALUE,                           # Previous estimate
        MAX_VALUE - 1000,                         # Near maximum
    ]
    
    logger.info("Starting systematic bit search")
    tested = 0
    
    for base in base_candidates:
        logger.info(f"Exploring bit variations around {hex(base)}")
        
        # Try flipping each bit individually
        for bit in range(68):
            candidate = base ^ (1 << bit)
            
            if not is_valid_candidate(candidate):
                continue
                
            tested += 1
            try:
                addr = private_key_to_address(candidate)
                if addr == TARGET_ADDRESS:
                    logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                    save_result(candidate)
                    return candidate
            except Exception:
                continue
                
            # Try combinations of bit flips (pairs)
            for bit2 in range(bit+1, 68):
                candidate = base ^ (1 << bit) ^ (1 << bit2)
                
                if not is_valid_candidate(candidate):
                    continue
                    
                tested += 1
                try:
                    addr = private_key_to_address(candidate)
                    if addr == TARGET_ADDRESS:
                        logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                        save_result(candidate)
                        return candidate
                except Exception:
                    continue
                    
                if tested % 1000 == 0:
                    logger.info(f"Tested {tested} bit combinations")
    
    logger.info(f"Completed testing {tested} bit variations without finding a match")
    return None

def focused_range_search():
    """
    Search through focused ranges based on patterns observed in previous terms.
    """
    # Define ranges to check based on observed patterns and analysis
    ranges = [
        # Near the previous term
        (PREV_TERM_67, PREV_TERM_67 + 0x1000),
        
        # Around predicted min value from extract_min_max.py
        (0x8747dd8c268dd31c4 - 0x1000, 0x8747dd8c268dd31c4 + 0x1000),
        
        # Around predicted max value from extract_min_max.py
        (0xd7db28ca2b3a33c0c - 0x1000, 0xd7db28ca2b3a33c0c + 0x1000),
        
        # Around bit-shifted value of previous term
        (0x7a40be591dad6edc8 - 0x1000, 0x7a40be591dad6edc8 + 0x1000),
        
        # Around estimate value
        (ESTIMATE_VALUE - 0x1000, ESTIMATE_VALUE + 0x1000),
        
        # Special pattern regions (derived from file analysis)
        (0x12e7b5c4e1c67, 0x12e7b5c4e1c67 + 0x1000),
        (0x730fc235c1950000, 0x730fc235c1960000),
    ]
    
    logger.info("Starting focused range search")
    tested = 0
    
    for start, end in ranges:
        range_size = end - start
        logger.info(f"Searching range {hex(start)} to {hex(end)} ({range_size} values)")
        
        # Use step size to sample the range rather than exhaustive search
        step = max(1, range_size // 10000)
        
        for candidate in range(start, end, step):
            if not is_valid_candidate(candidate):
                continue
                
            tested += 1
            try:
                addr = private_key_to_address(candidate)
                if addr == TARGET_ADDRESS:
                    logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                    save_result(candidate)
                    return candidate
                    
                if tested % 1000 == 0:
                    logger.info(f"Tested {tested} focused candidates, current: {hex(candidate)}")
            except Exception as e:
                logger.error(f"Error processing {hex(candidate)}: {e}")
    
    logger.info(f"Completed testing {tested} focused values without finding a match")
    return None

def pattern_based_generation(limit=10000):
    """
    Generate candidates based on mathematical patterns and transformations.
    """
    candidates = []
    
    # Pattern 1: Linear growth with different offsets
    for i in range(1, 100):
        candidate = PREV_TERM_67 + (i * 1000)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # Pattern 2: Geometric growth
    multipliers = [1.1, 1.2, 1.5, 2, 3]
    for mult in multipliers:
        value = int(PREV_TERM_67 * mult)
        if is_valid_candidate(value):
            candidates.append(value)
    
    # Pattern 3: Bit shifted values
    for shift in range(1, 20):
        value = PREV_TERM_67 + (PREV_TERM_67 >> shift)
        if is_valid_candidate(value):
            candidates.append(value)
    
    # Pattern 4: XOR with constants
    constants = [0x12345, 0xabcdef, 0x777777, 0xffffff]
    for const in constants:
        value = PREV_TERM_67 ^ const
        if is_valid_candidate(value):
            candidates.append(value)
    
    # Ensure we don't exceed limit and we don't have duplicates
    candidates = sorted(set(candidates))[:limit]
    
    logger.info(f"Generated {len(candidates)} pattern-based candidates")
    tested = 0
    
    for candidate in candidates:
        tested += 1
        try:
            addr = private_key_to_address(candidate)
            if addr == TARGET_ADDRESS:
                logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                save_result(candidate)
                return candidate
                
            if tested % 100 == 0:
                logger.info(f"Tested {tested} pattern-based candidates, current: {hex(candidate)}")
        except Exception as e:
            logger.error(f"Error processing {hex(candidate)}: {e}")
    
    logger.info(f"Completed testing {tested} pattern-based candidates without finding a match")
    return None

# -----------------------------
# Result Management
# -----------------------------

def save_result(result):
    """
    Save the result to a file.
    """
    result_data = {
        "term_index": 68,
        "private_key_hex": hex(result),
        "private_key_int": result,
        "bitcoin_address": TARGET_ADDRESS,
        "found_timestamp": time.time(),
        "previous_term_67": hex(PREV_TERM_67),
    }
    
    with open("term68_solution.json", "w") as f:
        json.dump(result_data, f, indent=2)
    
    # Also save as plain text
    with open("term68_solution.txt", "w") as f:
        f.write(f"Term 68 Solution\n")
        f.write(f"Private Key (hex): {hex(result)}\n")
        f.write(f"Private Key (int): {result}\n")
        f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
        f.write(f"Previous Term (67): {hex(PREV_TERM_67)}\n")
    
    logger.info(f"Solution saved to term68_solution.json and term68_solution.txt")

# -----------------------------
# Main Search Controller
# -----------------------------

def main():
    logger.info("=== Starting focused search for Term 68 ===")
    logger.info(f"Target Address: {TARGET_ADDRESS}")
    logger.info(f"Previous Term (67): {hex(PREV_TERM_67)}")
    logger.info(f"Search Range: {hex(MIN_VALUE)} to {hex(MAX_VALUE)}")
    logger.info(f"Estimated Value: {hex(ESTIMATE_VALUE)}")
    
    # Load predictions
    predictions = load_predictions()
    
    # Step 1: Search predicted values
    logger.info("Strategy 1: Search through predicted values")
    result = search_predictions(predictions)
    if result:
        return result
    
    # Step 2: Try pattern-based generation
    logger.info("Strategy 2: Pattern-based candidate generation")
    result = pattern_based_generation()
    if result:
        return result
    
    # Step 3: Try systematic bit search
    logger.info("Strategy 3: Systematic bit-level search")
    result = systematic_bit_search()
    if result:
        return result
    
    # Step 4: Try focused range search
    logger.info("Strategy 4: Focused range search")
    result = focused_range_search()
    if result:
        return result
    
    logger.info("All search strategies completed without finding a match")
    return None

if __name__ == "__main__":
    start_time = time.time()
    result = main()
    duration = time.time() - start_time
    
    if result:
        print(f"\n=== MATCH FOUND! ===")
        print(f"Term 68: {hex(result)}")
        print(f"Bitcoin Address: {TARGET_ADDRESS}")
        print(f"Search duration: {duration:.2f} seconds")
    else:
        print(f"\nNo match found after {duration:.2f} seconds") 