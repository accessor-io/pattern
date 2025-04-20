#!/usr/bin/env python3
"""
Hyper-focused Bitcoin private key search for term 68
Using 0x7b0fd3348980cc58a (56.7% similarity) as a base
Target address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import logging
import json
import sys
from itertools import combinations
import random

# Constants
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"
TERM_67 = 0x730fc235c1942c1ae
HIGH_SIM_CANDIDATE = 0x7b0fd3348980cc58a  # 56.7% similarity
SOLUTION_JSON = "term68_solution.json"
SOLUTION_TXT = "term68_solution.txt"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("exact_match_search.log")
    ]
)
logger = logging.getLogger()

# Track statistics
stats = {
    "candidates_tested": 0,
    "start_time": time.time(),
    "best_similarity": 0.0,
    "best_candidate": None,
    "best_address": None,
}

def private_key_to_address(private_key: int) -> str:
    """Convert a private key integer to a Bitcoin address."""
    try:
        # Convert integer to 32-byte private key
        private_key_bytes = private_key.to_bytes(32, byteorder='big')
        
        # Create a signing key
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        
        # Get the verifying key
        vk = sk.get_verifying_key()
        
        # Get public key coordinates
        x_coord = vk.pubkey.point.x()
        y_coord = vk.pubkey.point.y()
        
        # Use uncompressed public key format
        public_key = b'\x04' + x_coord.to_bytes(32, byteorder='big') + y_coord.to_bytes(32, byteorder='big')
        
        # Hash the public key (SHA-256 and RIPEMD-160)
        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Add version byte
        versioned_hash = b'\x00' + ripemd160_hash
        
        # Double SHA-256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
        
        # Combine and encode
        binary_address = versioned_hash + checksum
        bitcoin_address = base58.b58encode(binary_address).decode('utf-8')
        
        return bitcoin_address
    except Exception as e:
        logger.error(f"Error converting private key to address: {e}")
        return None

def address_similarity(addr1, addr2):
    """Calculate similarity between two Bitcoin addresses."""
    if not addr1 or not addr2:
        return 0.0
    
    # Calculate character-by-character match
    char_matches = sum(1 for a, b in zip(addr1, addr2) if a == b)
    similarity = char_matches / max(len(addr1), len(addr2))
    
    return similarity

def has_too_many_consecutive_chars(value: int) -> bool:
    """Check if a value has too many consecutive identical hex characters."""
    hex_str = hex(value)[2:]
    current_char = hex_str[0]
    count = 1
    
    for char in hex_str[1:]:
        if char == current_char:
            count += 1
            if count >= 4:  # 4 or more consecutive identical characters
                return True
        else:
            current_char = char
            count = 1
    
    return False

def is_valid_candidate(value: int) -> bool:
    """Check if a value is a valid candidate."""
    # Must be greater than term 67
    if value <= TERM_67:
        return False
    
    # Must have exactly 68 bits
    if value.bit_length() != 68:
        return False
    
    # Must not have more than 3 consecutive identical hex characters
    if has_too_many_consecutive_chars(value):
        return False
    
    return True

def test_candidate(value: int) -> bool:
    """Test a candidate against the target address."""
    global stats
    
    stats["candidates_tested"] += 1
    
    if not is_valid_candidate(value):
        return False
    
    address = private_key_to_address(value)
    if not address:
        return False
    
    if stats["candidates_tested"] % 1000 == 0:
        elapsed = time.time() - stats["start_time"]
        logger.info(f"Tested {stats['candidates_tested']} candidates in {elapsed:.2f} seconds")
    
    # Calculate similarity for logging purposes
    similarity = address_similarity(address, TARGET_ADDRESS)
    if similarity > stats["best_similarity"]:
        stats["best_similarity"] = similarity
        stats["best_candidate"] = value
        stats["best_address"] = address
        logger.info(f"New best similarity: {similarity:.6f} for address {address} from {hex(value)}")
    
    # Check for exact match
    return address == TARGET_ADDRESS

def save_result(value=None):
    """Save the result to files."""
    if value is None:
        logger.info("No exact match found, saving best candidate as placeholder")
        
        if stats["best_candidate"]:
            result = {
                "private_key_int": stats["best_candidate"],
                "private_key_hex": hex(stats["best_candidate"]),
                "bitcoin_address": stats["best_address"],
                "target_address": TARGET_ADDRESS,
                "similarity": stats["best_similarity"],
                "timestamp": time.time(),
                "human_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "candidates_tested": stats["candidates_tested"],
                "status": "Best candidate (not exact match)"
            }
        else:
            result = {
                "private_key_int": None,
                "private_key_hex": None,
                "bitcoin_address": TARGET_ADDRESS,
                "timestamp": time.time(),
                "human_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "candidates_tested": stats["candidates_tested"],
                "status": "Not found"
            }
    else:
        logger.info(f"EXACT MATCH FOUND! Saving result: {hex(value)}")
        result = {
            "private_key_int": value,
            "private_key_hex": hex(value),
            "bitcoin_address": TARGET_ADDRESS,
            "timestamp": time.time(),
            "human_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "candidates_tested": stats["candidates_tested"],
            "status": "Exact match found"
        }

    # Save as JSON
    with open(SOLUTION_JSON, 'w') as f:
        json.dump(result, f, indent=2)

    # Save as plaintext
    with open(SOLUTION_TXT, 'w') as f:
        if value is None:
            f.write("Term 68 Solution - Best Candidate\n")
            if stats["best_candidate"]:
                f.write(f"Private Key: {hex(stats['best_candidate'])}\n")
                f.write(f"Generated Address: {stats['best_address']}\n")
                f.write(f"Target Address: {TARGET_ADDRESS}\n")
                f.write(f"Similarity: {stats['best_similarity']:.6f}\n")
            else:
                f.write("Private Key: Not found\n")
                f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S.%f', time.localtime())}\n")
        else:
            f.write("Term 68 Solution - EXACT MATCH FOUND!\n")
            f.write(f"Private Key: {hex(value)}\n")
            f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S.%f', time.localtime())}\n")

    logger.info(f"Solution saved to {SOLUTION_JSON} and {SOLUTION_TXT}")

def bit_flip_search(base_value, max_bits=8, max_candidates=1000000):
    """
    Try flipping combinations of bits in the base value.
    """
    tested = 0
    positions = list(range(base_value.bit_length()))
    
    logger.info(f"Starting bit flip search with base: {hex(base_value)}, max bits: {max_bits}")
    
    # Give higher priority to bits 0-20 (they have more impact on address)
    weighted_positions = positions.copy()
    for i in range(min(20, len(positions))):
        weighted_positions.extend([i] * 3)  # Add extra weight to first 20 bits
    
    for num_bits in range(1, max_bits + 1):
        logger.info(f"Trying {num_bits} bit flips...")
        
        # Try random combinations first
        max_random_tries = min(10000, max_candidates // (2 * max_bits))
        for _ in range(max_random_tries):
            if tested >= max_candidates:
                logger.info(f"Reached max candidates: {max_candidates}")
                return False
            
            # Select random positions with higher weight for lower bits
            pos_to_flip = random.sample(weighted_positions, num_bits)
            
            # Flip bits
            value = base_value
            for pos in pos_to_flip:
                value ^= (1 << pos)
            
            tested += 1
            
            # Test if valid and generates target address
            if is_valid_candidate(value) and test_candidate(value):
                logger.info(f"EXACT MATCH FOUND: {hex(value)}")
                save_result(value)
                return True
        
        # If num_bits is small enough, try all combinations systematically
        if num_bits <= 5:
            for pos_to_flip in combinations(positions, num_bits):
                if tested >= max_candidates:
                    logger.info(f"Reached max candidates: {max_candidates}")
                    return False
                
                # Flip bits
                value = base_value
                for pos in pos_to_flip:
                    value ^= (1 << pos)
                
                tested += 1
                
                # Test if valid and generates target address
                if is_valid_candidate(value) and test_candidate(value):
                    logger.info(f"EXACT MATCH FOUND: {hex(value)}")
                    save_result(value)
                    return True
    
    logger.info(f"Total bit-flip candidates tested: {tested}")
    return False

def pattern_search(base_value, max_candidates=100000):
    """
    Try applying different bit patterns and operations to the base value.
    """
    logger.info(f"Starting pattern search with base: {hex(base_value)}")
    
    # Calculate the difference between base and term 67
    diff = base_value - TERM_67
    logger.info(f"Difference from Term 67: {hex(diff)}")
    
    tested = 0
    patterns = [
        # XOR operations with various values
        lambda x: x ^ 0xFF,
        lambda x: x ^ 0xF0F0,
        lambda x: x ^ 0xFFFF,
        lambda x: x ^ 0xA5A5A5,
        
        # Shifting operations
        lambda x: (x << 1) & ((1 << 68) - 1),
        lambda x: (x << 2) & ((1 << 68) - 1),
        lambda x: (x << 4) & ((1 << 68) - 1),
        lambda x: x >> 1,
        lambda x: x >> 2,
        lambda x: x >> 4,
        
        # Rotations (preserving 68 bits)
        lambda x: ((x << 1) | (x >> 67)) & ((1 << 68) - 1),
        lambda x: ((x << 2) | (x >> 66)) & ((1 << 68) - 1),
        lambda x: ((x << 4) | (x >> 64)) & ((1 << 68) - 1),
        lambda x: ((x >> 1) | (x << 67)) & ((1 << 68) - 1),
        lambda x: ((x >> 2) | (x << 66)) & ((1 << 68) - 1),
        lambda x: ((x >> 4) | (x << 64)) & ((1 << 68) - 1),
        
        # Bit swapping operations
        lambda x: ((x & 0xFFFFFFFF) << 32) | ((x >> 32) & 0xFFFFFFFF),  # Swap 32-bit halves
        lambda x: ((x & 0xFFFF) << 48) | ((x & 0xFFFF0000) << 16) | ((x & 0xFFFF00000000) >> 16) | ((x & 0xFFFF000000000000) >> 48),  # Swap 16-bit chunks
        
        # Mathematical operations based on the difference
        lambda x: x + diff,
        lambda x: x - diff,
        lambda x: x + (diff * 2),
        lambda x: x - (diff * 2),
        lambda x: x ^ diff,
        lambda x: x | diff,
        lambda x: x & ~diff,
        
        # Nibble operations (4-bit chunks)
        lambda x: ((x & 0xF0F0F0F0F0F0F0F0) >> 4) | ((x & 0x0F0F0F0F0F0F0F0F) << 4),  # Swap adjacent nibbles
    ]
    
    # Apply patterns
    for pattern_func in patterns:
        if tested >= max_candidates:
            logger.info(f"Reached max candidates: {max_candidates}")
            break
        
        value = pattern_func(base_value)
        tested += 1
        
        if is_valid_candidate(value) and test_candidate(value):
            logger.info(f"EXACT MATCH FOUND: {hex(value)}")
            save_result(value)
            return True
    
    # Create variations with specific bit differences
    logger.info("Testing variations with specific bit differences...")
    
    # Get binary representation to analyze bit differences
    base_bin = bin(base_value)[2:].zfill(68)
    term67_bin = bin(TERM_67)[2:].zfill(68)
    
    # For each bit that differs, create a new candidate by toggling that bit
    for i in range(68):
        if tested >= max_candidates:
            break
        
        if base_bin[i] != term67_bin[i]:
            # Toggle this differing bit
            value = base_value ^ (1 << (67 - i))  # 67-i because binary string is indexed from left
            tested += 1
            
            if is_valid_candidate(value) and test_candidate(value):
                logger.info(f"EXACT MATCH FOUND: {hex(value)}")
                save_result(value)
                return True
    
    logger.info(f"Total pattern candidates tested: {tested}")
    return False

def exhaustive_search_around(base_value, radius=20000, max_candidates=1000000):
    """
    Perform an exhaustive search around the base value within the given radius.
    """
    logger.info(f"Starting exhaustive search around {hex(base_value)} ± {radius}")
    
    tested = 0
    for offset in range(-radius, radius + 1):
        if tested >= max_candidates:
            logger.info(f"Reached max candidates: {max_candidates}")
            return False
        
        value = base_value + offset
        tested += 1
        
        if is_valid_candidate(value) and test_candidate(value):
            logger.info(f"EXACT MATCH FOUND: {hex(value)}")
            save_result(value)
            return True
            
        if tested % 10000 == 0:
            logger.info(f"Tested {tested} candidates in exhaustive search")
    
    logger.info(f"Total exhaustive search candidates tested: {tested}")
    return False

def advanced_bit_pattern_search(base_value, max_candidates=100000):
    """
    Try more advanced bit manipulation patterns.
    """
    logger.info(f"Starting advanced bit pattern search with base: {hex(base_value)}")
    
    tested = 0
    
    # Test patterns where we swap groups of bits
    bit_length = base_value.bit_length()
    for chunk_size in [2, 4, 8]:
        num_chunks = bit_length // chunk_size
        
        for i in range(num_chunks):
            for j in range(i + 1, num_chunks):
                if tested >= max_candidates:
                    logger.info(f"Reached max candidates: {max_candidates}")
                    return False
                
                # Get positions
                i_pos = i * chunk_size
                j_pos = j * chunk_size
                
                # Extract chunks
                i_mask = ((1 << chunk_size) - 1) << i_pos
                j_mask = ((1 << chunk_size) - 1) << j_pos
                
                i_chunk = (base_value & i_mask) >> i_pos
                j_chunk = (base_value & j_mask) >> j_pos
                
                # Swap chunks
                value = base_value & ~(i_mask | j_mask)  # Clear both chunks
                value |= (i_chunk << j_pos) | (j_chunk << i_pos)  # Set swapped chunks
                
                tested += 1
                
                if is_valid_candidate(value) and test_candidate(value):
                    logger.info(f"EXACT MATCH FOUND: {hex(value)}")
                    save_result(value)
                    return True
    
    # Try substituting each byte with specific values
    for byte_pos in range(0, 8):
        position = byte_pos * 8
        
        # Values to try in each position
        values_to_try = [0x00, 0xFF, 0xAA, 0x55, 0xF0, 0x0F]
        
        for val in values_to_try:
            if tested >= max_candidates:
                logger.info(f"Reached max candidates: {max_candidates}")
                return False
            
            # Clear byte and set new value
            byte_mask = 0xFF << position
            value = (base_value & ~byte_mask) | (val << position)
            
            tested += 1
            
            if is_valid_candidate(value) and test_candidate(value):
                logger.info(f"EXACT MATCH FOUND: {hex(value)}")
                save_result(value)
                return True
    
    # Test specific relationships to term 67
    relations = [
        lambda x: TERM_67 + (x - TERM_67) * 2,
        lambda x: TERM_67 + (x - TERM_67) * 3,
        lambda x: TERM_67 + (x - TERM_67) // 2,
        lambda x: TERM_67 * 2 - x,
        lambda x: (x + TERM_67) // 2,
        lambda x: (x ^ TERM_67) + TERM_67,
        lambda x: (x | TERM_67) ^ TERM_67,
        lambda x: (x & TERM_67) | (x ^ TERM_67),
    ]
    
    for rel_func in relations:
        if tested >= max_candidates:
            logger.info(f"Reached max candidates: {max_candidates}")
            return False
        
        value = rel_func(base_value)
        tested += 1
        
        if is_valid_candidate(value) and test_candidate(value):
            logger.info(f"EXACT MATCH FOUND: {hex(value)}")
            save_result(value)
            return True
    
    logger.info(f"Total advanced bit pattern candidates tested: {tested}")
    return False

def main():
    start_time = time.time()
    logger.info("Starting hyper-focused search for exact Bitcoin private key (term 68)")
    logger.info(f"Target address: {TARGET_ADDRESS}")
    logger.info(f"Previous term (67): {hex(TERM_67)}")
    logger.info(f"Starting with high similarity candidate: {hex(HIGH_SIM_CANDIDATE)}")
    
    # Try all search methods
    logger.info("Starting bit flip search...")
    if bit_flip_search(HIGH_SIM_CANDIDATE, max_bits=8, max_candidates=1000000):
        logger.info("Found exact match!")
        logger.info(f"Total time: {time.time() - start_time:.2f} seconds")
        logger.info(f"Total candidates tested: {stats['candidates_tested']}")
        return 0
    
    logger.info("Starting pattern search...")
    if pattern_search(HIGH_SIM_CANDIDATE, max_candidates=100000):
        logger.info("Found exact match!")
        logger.info(f"Total time: {time.time() - start_time:.2f} seconds")
        logger.info(f"Total candidates tested: {stats['candidates_tested']}")
        return 0
    
    logger.info("Starting advanced bit pattern search...")
    if advanced_bit_pattern_search(HIGH_SIM_CANDIDATE, max_candidates=100000):
        logger.info("Found exact match!")
        logger.info(f"Total time: {time.time() - start_time:.2f} seconds")
        logger.info(f"Total candidates tested: {stats['candidates_tested']}")
        return 0
    
    logger.info("Starting exhaustive search around high similarity candidate...")
    if exhaustive_search_around(HIGH_SIM_CANDIDATE, radius=50000, max_candidates=1000000):
        logger.info("Found exact match!")
        logger.info(f"Total time: {time.time() - start_time:.2f} seconds")
        logger.info(f"Total candidates tested: {stats['candidates_tested']}")
        return 0
    
    # If no match found after all methods
    logger.info("No exact match found after all search methods.")
    logger.info(f"Total time: {time.time() - start_time:.2f} seconds")
    logger.info(f"Total candidates tested: {stats['candidates_tested']}")
    save_result(None)
    
    return 1

if __name__ == "__main__":
    sys.exit(main()) 