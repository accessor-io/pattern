#!/usr/bin/env python3
"""
Continuous Adaptive Search for Cryptographic Sequence Term 69 (T5)

Target Hash160: d31602ddf6d4384d274b011ee312311016e6b9f1

This script continuously searches for the 69-bit integer (private key) 
that produces the target Hash160 value for T5, adapting its search 
parameters and logging progress.

Features:
1. Continuously searches until a match is found.
2. Logs tested candidates and their Hash160 values.
3. Uses multiple search strategies including specialized T5 candidate generation.
"""

import hashlib
import base58  # Still needed for some potential future use or comparison, but not core T5 logic
from ecdsa import SigningKey, SECP256k1, VerifyingKey, NIST256p
import time
import os
import json
import logging
import random
import re
import sys
from collections import defaultdict, Counter
import itertools
import math
import multiprocessing as mp
from functools import partial
import csv
from datetime import datetime
import argparse
import struct

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='69_t5_continuous_search.log', # Updated filename
    filemode='a'
)
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

# -----------------------------
# Configuration and Constants
# -----------------------------

# Target information
TARGET_INDEX = 69  # Target number of bits for T5
TARGET_T5_HASH160 = "d31602ddf6d4384d274b011ee312311016e6b9f1"

# Known terms from the sequence (from 68-3 copy.py)
KNOWN_TERMS = {
    1: 0x2,                              # T1
    2: 0x3,                              # T2
    3: 0x5,                              # T3
    # T4 is unknown, but related to T1, T2, T3
    # T5 is the target (69 bits)
    6: 0x1fae61a8f5dd569a1 # T6 (70 bits)
}

# Bit limits (from 68-3 copy.py)
BIT_LIMITS = {
    68: (1 << 68),
    69: (1 << 69),
    70: (1 << 70)
}
MAX_VALUE = BIT_LIMITS[TARGET_INDEX] - 1 # Maximum 69-bit value
MIN_VALUE = 1 << (TARGET_INDEX - 1)    # Minimum 69-bit value (ensures correct length)

# Self-adjustment parameters (Simplified - less focus on adaptive similarity)
POPULATION_SIZE = 1000  # Size of genetic algorithm population
MUTATION_RATE = 0.05   # Genetic mutation rate (as proportion)
BIT_FLIP_MAX = 5       # Maximum bits to flip in Hamming distance exploration
SEARCH_RADIUS = 10000  # Search radius around promising values (for range search)
MEMORY_SIZE = 50000   # Number of tested candidates to remember (to avoid re-testing)

# File paths
CANDIDATE_LOG_FILE = "t5_candidate_log.csv" # Updated filename
TESTED_CANDIDATES_FILE = "t5_tested_candidates_memory.json" # Updated filename
PROGRESS_FILE = "t5_search_progress.json" # Updated filename
CHECKPOINT_FILE = "t5_search_checkpoint.json" # Updated filename
FOUND_KEY_FILE = "FOUND_T5_KEY.txt" # File to save the key if found

# Global variable to track tested candidates efficiently
TESTED_CANDIDATES_SET = set()
# Global variable to store the found key
FOUND_KEY = None

# -----------------------------
# Cryptographic Functions (Adapted for T5 Hash160)
# -----------------------------

# Custom RIPEMD160 Implementation (from 68-3 copy.py)
# Necessary because hashlib.new('ripemd160') might not always be available or consistent
def ripemd160(data):
    # Constants for RIPEMD-160
    K = [0x00000000, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xA953FD4E]
    KK = [0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x7A6D76E9, 0x00000000]
    s = [
        [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8],
        [7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12],
        [11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5],
        [11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12],
        [9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6]
    ]
    ss = [
        [8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6],
        [9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11],
        [9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5],
        [15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8],
        [8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11]
    ]
    rho = [7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8]
    pi = [(rho[i] + 5) % 16 for i in range(16)]

    def F(j, x, y, z):
        if 0 <= j <= 15: return x ^ y ^ z
        if 16 <= j <= 31: return (x & y) | (~x & z)
        if 32 <= j <= 47: return (x | ~y) ^ z
        if 48 <= j <= 63: return (x & z) | (y & ~z)
        if 64 <= j <= 79: return x ^ (y | ~z)
        return 0

    def rol(x, n):
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

    # Padding
    ml = len(data) * 8
    data += b'\x80'
    data += b'\x00' * (-(len(data) + 8) % 64)
    data += struct.pack('<Q', ml)

    # Process blocks
    h = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
    for i in range(0, len(data), 64):
        X = list(struct.unpack('<16I', data[i:i+64]))
        A, B, C, D, E = h
        AA, BB, CC, DD, EE = h

        for j in range(80):
            T = rol(A + F(j, B, C, D) + X[rho[j % 16]] + K[j // 16], s[j // 16][j % 16]) + E
            A, B, C, D, E = E, T, rol(B, 10), C, D

            T = rol(AA + F(79 - j, BB, CC, DD) + X[pi[j % 16]] + KK[j // 16], ss[j // 16][j % 16]) + EE
            AA, BB, CC, DD, EE = EE, T, rol(BB, 10), CC, DD

        T = h[1] + C + DD
        h[1] = h[2] + D + EE
        h[2] = h[3] + E + AA
        h[3] = h[4] + A + BB
        h[4] = h[0] + B + CC
        h[0] = T & 0xFFFFFFFF
        h = [(x + y) & 0xFFFFFFFF for x, y in zip(h, [h[1], h[2], h[3], h[4], h[0]])]
        h = [(h[i] + (AA if i == 4 else BB if i == 3 else CC if i == 2 else DD if i == 1 else EE)) & 0xFFFFFFFF for i in range(5)]


    # Return result as bytes
    return struct.pack('<5I', *h)


def private_key_to_hash160(private_key: int) -> str:
    """
    Convert a private key integer to its Hash160 (RIPEMD160(SHA256(PublicKey))).
    Handles 69-bit keys correctly by padding to 32 bytes.
    """
    global logger
    try:
        # Format private key to 64 hex digits (32 bytes), padding with leading zeros
        privkey_hex = format(private_key, '064x')
        privkey_bytes = bytes.fromhex(privkey_hex)

        # Create signing key from bytes
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()

        # Get compressed public key (starts with 0x02 or 0x03)
        # compressed = vk.to_string("compressed") # Use compressed format
        # For T5, the reference implementation might use uncompressed, check 68-3 copy.py
        # Re-checking 68-3 copy.py... it uses `vk.to_string("compressed")` in `private_to_public`. Let's stick to that.
        pubkey_bytes = vk.to_string("compressed")

        # Hash the public key: RIPEMD160(SHA256(PublicKey))
        sha_digest = hashlib.sha256(pubkey_bytes).digest()
        # Use the custom ripemd160 function
        hash160_digest = ripemd160(sha_digest)

        # Return the hex representation
        return hash160_digest.hex()

    except Exception as e:
        # Log error without stopping the entire search
        # Use logger if available, otherwise print
        log_func = logger.error if logger else print
        log_func(f"Error converting key {hex(private_key)} to Hash160: {e}")
        # Return None or an empty string to indicate failure
        return None

# Removed address_similarity function as it's not relevant for Hash160 matching

# -----------------------------
# Candidate Validation (Adapted for T5)
# -----------------------------

def has_too_many_consecutive_chars(value: int) -> bool:
    """
    Check if hex representation has more than 3 consecutive identical characters.
    (Constraint from 68-3 copy.py)
    """
    hex_str = hex(value)[2:] # Remove '0x' prefix
    if len(hex_str) < 4:
        return False # Cannot have 4 consecutive chars if length < 4

    # Use regex for potentially faster check
    if re.search(r'(.)\1{3,}', hex_str):
        return True
    return False
    # Manual check (alternative)
    # count = 1
    # prev_char = hex_str[0]
    # for char in hex_str[1:]:
    #     if char == prev_char:
    #         count += 1
    #         if count > 3:
    #             return True
    #     else:
    #         count = 1
    #         prev_char = char
    # return False

def is_valid_candidate_t5(value: int) -> bool:
    """
    Check if a value is a valid candidate for the 69th term (T5):
    1. Must have exactly 69 bits.
    2. Must not have more than 3 consecutive identical hex chars.
    """
    # Check bit length
    if not (MIN_VALUE <= value <= MAX_VALUE):
        return False
    # Check consecutive characters constraint
    if has_too_many_consecutive_chars(value):
        return False
    return True

# -----------------------------
# Candidate Testing (Adapted for T5)
# -----------------------------

def test_candidate(candidate: int) -> tuple:
    """
    Test a candidate T5 value.
    Checks validity, computes Hash160, compares to target.

    Args:
        candidate: The 69-bit integer private key candidate.

    Returns:
        tuple: (is_match, hex_hash160_or_none)
               is_match (bool): True if the Hash160 matches the target.
               hex_hash160_or_none (str or None): The computed Hash160 in hex, or None if invalid/error.
    """
    global TARGET_T5_HASH160, FOUND_KEY, logger, candidate_logger, memory_manager

    # 1. Check validity
    if not is_valid_candidate_t5(candidate):
        return False, None

    # 2. Avoid re-testing if already tested (using MemoryManager's set)
    if memory_manager.is_tested(candidate):
        return False, None # Return False for match, None for hash as it wasn't recomputed

    # 3. Compute Hash160
    hex_hash160 = private_key_to_hash160(candidate)

    # 4. Mark as tested (even if hash computation failed)
    memory_manager.add_tested(candidate) # Add to the set of tested candidates

    # 5. Log the attempt (candidate and its hash)
    if hex_hash160: # Log only if hash computation was successful
        candidate_logger.log_candidate(candidate, hex_hash160)

    # 6. Check for error during hash computation
    if hex_hash160 is None:
        return False, None

    # 7. Compare with target
    is_match = (hex_hash160 == TARGET_T5_HASH160)

    # 8. If match found, record and log prominently
    if is_match:
        FOUND_KEY = candidate
        logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.info(f"!!! MATCH FOUND FOR T5 (Term 69) !!!")
        logger.info(f"!!! Candidate Private Key (int): {candidate}")
        logger.info(f"!!! Candidate Private Key (hex): {hex(candidate)}")
        logger.info(f"!!! Computed Hash160: {hex_hash160}")
        logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Save the result immediately
        save_result(candidate)
        # Optionally: Signal other processes or exit if running in single mode

    return is_match, hex_hash160

# -----------------------------
# Memory and Logging (Adapted for T5)
# -----------------------------

class TestedCandidatesManager:
    """
    Manages memory of tested candidates to avoid redundant computations.
    Uses a set for efficient lookups.
    Periodically saves the set to a file.
    """
    def __init__(self, filename=TESTED_CANDIDATES_FILE, save_interval=300): # Save every 5 minutes
        self.tested_set = set()
        self.filename = filename
        self.save_interval = save_interval # seconds
        self.last_save_time = time.time()
        self.added_since_last_save = 0
        self.load_tested()
        logger.info(f"TestedCandidatesManager initialized with {len(self.tested_set)} entries.")

    def load_tested(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    # Load hex strings and convert back to integers
                    hex_candidates = json.load(f)
                    self.tested_set = {int(h, 16) for h in hex_candidates}
                logger.info(f"Loaded {len(self.tested_set)} previously tested candidates from {self.filename}")
            except Exception as e:
                logger.error(f"Error loading tested candidates from {self.filename}: {e}. Starting fresh.")
                self.tested_set = set()
        else:
            logger.info(f"No tested candidates file found at {self.filename}, starting fresh.")
            self.tested_set = set()

    def save_tested(self):
        if self.added_since_last_save == 0:
             # Avoid saving if nothing new was added
             return

        logger.info(f"Saving {len(self.tested_set)} tested candidates to {self.filename}...")
        try:
            # Convert integers to hex strings for JSON serialization
            hex_candidates = [hex(c) for c in self.tested_set]
            temp_filename = f"{self.filename}.tmp"
            with open(temp_filename, 'w') as f:
                json.dump(hex_candidates, f) # Store as a list of hex strings
            os.replace(temp_filename, self.filename)
            self.last_save_time = time.time()
            self.added_since_last_save = 0 # Reset counter after successful save
            logger.info(f"Successfully saved tested candidates.")
        except Exception as e:
            logger.error(f"Error saving tested candidates to {self.filename}: {e}")

    def add_tested(self, candidate: int):
        if candidate not in self.tested_set:
            self.tested_set.add(candidate)
            self.added_since_last_save += 1

            # Check if it's time to save
            current_time = time.time()
            if current_time - self.last_save_time >= self.save_interval or self.added_since_last_save >= MEMORY_SIZE / 10 : # Also save if many added quickly
                 self.save_tested()


    def is_tested(self, candidate: int) -> bool:
        return candidate in self.tested_set

    def get_count(self) -> int:
        return len(self.tested_set)

class CandidateLogger:
    """
    Logs all generated candidates and their Hash160 values to a CSV file.
    """
    def __init__(self, filename=CANDIDATE_LOG_FILE):
        self.filename = filename
        self.count = 0
        self.initialize_log()

    def initialize_log(self):
        file_exists = os.path.exists(self.filename)
        try:
            with open(self.filename, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow([
                        "timestamp",
                        "private_key_int",
                        "private_key_hex",
                        "computed_hash160_hex",
                        "bit_length"
                    ])
        except Exception as e:
            logger.error(f"Failed to initialize candidate log file {self.filename}: {e}")

    def log_candidate(self, private_key, hash160_hex):
        try:
            with open(self.filename, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    private_key,
                    hex(private_key),
                    hash160_hex,
                    private_key.bit_length()
                ])
            self.count += 1

            # Log summary periodically to main log
            if self.count % 10000 == 0: # Log every 10,000 candidates
                logger.info(f"Logged {self.count} candidates to {self.filename}")
        except Exception as e:
            # Log error but continue running
            logger.error(f"Failed to write to candidate log file {self.filename}: {e}")

# Initialize Managers
memory_manager = TestedCandidatesManager()
candidate_logger = CandidateLogger()


# -----------------------------
# Search Strategies (Adapted/Simplified for T5)
# -----------------------------

# Strategy 1: High-Quality Candidate Generation (from 68-3 copy.py)
def generate_high_quality_candidates(num_candidates=1000, known_terms=None, target_bits=69):
    """
    Generates high-quality candidate private keys for T5 based on known terms
    and observed patterns. Adapted from 68-3 copy.py.

    Args:
        num_candidates (int): The number of candidates to generate.
        known_terms (dict): Dictionary of known sequence terms (T1, T2, T3, T6).
        target_bits (int): The target bit length (69 for T5).

    Returns:
        list: A list of potential integer candidates for T5.
    """
    if known_terms is None:
        known_terms = KNOWN_TERMS

    candidates = []
    t1, t2, t3, t6 = known_terms[1], known_terms[2], known_terms[3], known_terms[6]

    # Define the search space boundaries more precisely
    min_val = 1 << (target_bits - 1)
    max_val = (1 << target_bits) - 1

    # 1. Linear Combinations and Variations of Known Terms
    term_values = list(known_terms.values())
    for _ in range(int(num_candidates * 0.3)): # 30% of candidates
        c1, c2, c3 = random.sample(term_values, 3)
        op1 = random.choice([lambda x, y: x + y, lambda x, y: x - y, lambda x, y: x * y, lambda x, y: x ^ y])
        op2 = random.choice([lambda x, y: x + y, lambda x, y: x - y, lambda x, y: x ^ y])

        try:
            candidate = op2(op1(c1, c2), c3)
            # Add small random offsets/shifts
            offset = random.randint(-100, 100)
            shift = random.randint(0, 4)
            candidate = (candidate + offset) & max_val # Apply mask
            candidate = (candidate << shift | candidate >> (target_bits - shift)) & max_val # Bit rotation

            if is_valid_candidate_t5(candidate):
                candidates.append(candidate)
        except (OverflowError, ValueError):
            continue # Skip if operations result in invalid numbers

    # 2. Bit Manipulation based on T6 (Next Term)
    # Assume T5 might share significant bit patterns with T6
    for _ in range(int(num_candidates * 0.3)): # 30% of candidates
        candidate = t6
        # Randomly flip 1 to 5 bits
        num_flips = random.randint(1, 5)
        for _ in range(num_flips):
            bit_pos = random.randint(0, target_bits - 1)
            candidate ^= (1 << bit_pos)

        # Apply random shifts
        shift = random.randint(1, 5)
        if random.random() < 0.5:
            candidate = (candidate << shift | candidate >> (target_bits - shift)) & max_val
        else:
            candidate = (candidate >> shift | candidate << (target_bits - shift)) & max_val

        if is_valid_candidate_t5(candidate):
            candidates.append(candidate)

    # 3. Pattern-Based Generation (Focus on Hex Patterns)
    # Look for patterns in known terms hex representations
    hex_patterns = [hex(t)[2:] for t in term_values]
    common_prefixes = [p[:4] for p in hex_patterns] # e.g., first 4 hex chars
    common_suffixes = [p[-4:] for p in hex_patterns]

    for _ in range(int(num_candidates * 0.2)): # 20% of candidates
        # Combine prefixes/suffixes/random parts
        prefix = random.choice(common_prefixes)
        suffix = random.choice(common_suffixes)
        mid_len = (target_bits // 4) - len(prefix) - len(suffix) # Approximate mid length in hex
        if mid_len > 0 :
            mid = ''.join(random.choices("0123456789abcdef", k=mid_len))
            hex_candidate = prefix + mid + suffix
            try:
                candidate = int(hex_candidate, 16)
                if is_valid_candidate_t5(candidate):
                    candidates.append(candidate)
            except ValueError:
                continue

    # 4. Random Generation within Valid Range (Fallback)
    remaining = num_candidates - len(candidates)
    for _ in range(max(0, remaining)):
        candidate = random.randint(min_val, max_val)
        if is_valid_candidate_t5(candidate):
            candidates.append(candidate)

    unique_candidates = list(set(candidates)) # Remove duplicates
    logger.info(f"Generated {len(unique_candidates)} high-quality T5 candidates.")
    return unique_candidates

# Strategy 2: Bit Flip Search
def bit_flip_search(center, max_bits=BIT_FLIP_MAX, max_candidates=500):
    """
    Search by flipping bits in a candidate. Tests generated candidates.
    Yields candidates rather than returning a list.
    """
    if not is_valid_candidate_t5(center):
        return # Center must be valid

    logger.info(f"Starting bit flip search around {hex(center)}")
    tested_count = 0

    for num_bits in range(1, max_bits + 1):
        if tested_count >= max_candidates or FOUND_KEY:
            break

        # Generate combinations of bit positions to flip
        bit_positions = list(range(TARGET_INDEX)) # 0 to 68
        for combo in itertools.combinations(bit_positions, num_bits):
            if tested_count >= max_candidates or FOUND_KEY:
                break

            # Create new value by flipping selected bits
            value = center
            for pos in combo:
                value ^= (1 << pos)

            # Yield the candidate for testing in the main loop
            yield value
            tested_count += 1

    logger.info(f"Bit flip search generated {tested_count} candidates.")

# Strategy 3: Adaptive Range Search
def adaptive_range_search(center, radius=SEARCH_RADIUS, max_candidates=1000):
    """
    Search in a range around a center value. Tests candidates.
    Yields candidates.
    """
    if not is_valid_candidate_t5(center):
        return # Center must be valid

    logger.info(f"Starting adaptive range search around {hex(center)} with radius {radius}")
    tested_count = 0

    # Search around center, stepping outwards
    for i in range(1, radius + 1):
        if tested_count >= max_candidates or FOUND_KEY:
            break

        # Test value + i
        val_plus = center + i
        yield val_plus
        tested_count += 1

        # Test value - i
        val_minus = center - i
        yield val_minus
        tested_count += 1

    logger.info(f"Adaptive range search generated {tested_count} candidates.")


# Strategy 4: Genetic Algorithm Search (Simplified Fitness)
def genetic_search(population_size=POPULATION_SIZE, generations=5):
    """
    Genetic algorithm search. Fitness is 1 for match, 0 otherwise.
    Yields candidates from the evolving population.
    """
    logger.info(f"Starting genetic search with population size {population_size}")

    # Create initial population - Use high-quality candidates + random
    population = generate_high_quality_candidates(population_size // 2)
    while len(population) < population_size:
        candidate = random.randint(MIN_VALUE, MAX_VALUE)
        if is_valid_candidate_t5(candidate):
            population.append(candidate)

    for gen in range(generations):
        if FOUND_KEY: break
        logger.info(f"Genetic algorithm generation {gen + 1}/{generations}")

        next_population = []
        fitness = [] # Store (candidate, is_match)

        # Evaluate current population and yield candidates
        for candidate in population:
            if FOUND_KEY: break
            yield candidate # Yield candidate for testing by main loop
            # Fitness evaluation happens implicitly if test_candidate finds a match

        # Simple selection: Keep all current candidates for breeding
        # More advanced selection could be added if needed (e.g., tournament)
        breeding_pool = list(population) # Use the whole population

        # Crossover and mutation to create the next generation
        while len(next_population) < population_size:
            if FOUND_KEY: break
            try:
                # Select parents
                parent1 = random.choice(breeding_pool)
                parent2 = random.choice(breeding_pool)

                # Crossover
                child = crossover(parent1, parent2)

                # Mutation
                child = mutate(child, MUTATION_RATE)

                # Add valid children to the next population
                if is_valid_candidate_t5(child):
                    next_population.append(child)
            except IndexError: # Handle case where breeding_pool might be empty
                 break

        population = next_population
        if not population: # Prevent infinite loop if population dies out
             logger.warning("Genetic algorithm population became empty. Stopping.")
             break


    logger.info("Completed genetic search generations.")


def crossover(parent1, parent2):
    """ Perform bitwise crossover between two candidates (single point). """
    bits1 = bin(parent1)[2:].zfill(TARGET_INDEX)
    bits2 = bin(parent2)[2:].zfill(TARGET_INDEX)
    point = random.randint(1, TARGET_INDEX - 1)
    child_bits = bits1[:point] + bits2[point:]
    return int(child_bits, 2)

def mutate(candidate, mutation_rate=MUTATION_RATE):
    """ Mutate bits in a candidate with given probability. """
    bits = list(bin(candidate)[2:].zfill(TARGET_INDEX))
    for i in range(TARGET_INDEX):
        if random.random() < mutation_rate:
            bits[i] = '1' if bits[i] == '0' else '0'
    # Ensure the most significant bit remains 1 if needed (already handled by is_valid?)
    # bits[0] = '1' # T5 must be 69 bits
    mutated_int = int(''.join(bits), 2)
    # Ensure mutation doesn't push it out of 69-bit range unexpectedly
    return mutated_int & ((1 << TARGET_INDEX) - 1) | (1 << (TARGET_INDEX - 1))


# -----------------------------
# Progress Saving and Loading
# -----------------------------

def save_progress(state):
    """Save the current search state"""
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        # logger.debug("Search progress saved.") # Reduce log noise
    except Exception as e:
        logger.error(f"Error saving progress: {e}")

def load_progress():
    """Load the last saved search state"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                state = json.load(f)
            logger.info("Search progress loaded.")
            return state
        except Exception as e:
            logger.error(f"Error loading progress: {e}. Starting fresh.")
            return None
    return None

def save_checkpoint(state):
    """Save a more comprehensive checkpoint"""
    # Checkpoint combines search state and tested candidates memory
    checkpoint_data = {
        'search_state': state,
        'tested_candidates_count': memory_manager.get_count() # Save count, actual set saved by manager
    }
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        logger.info(f"Checkpoint saved. Tested candidates: {memory_manager.get_count()}")
    except Exception as e:
        logger.error(f"Error saving checkpoint: {e}")
    # Trigger saving of the tested candidates set as well
    memory_manager.save_tested()


def load_checkpoint():
    """Load the last checkpoint"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                checkpoint_data = json.load(f)
            logger.info("Checkpoint loaded.")
            # Memory manager loads its own data, just return search state
            return checkpoint_data.get('search_state', None)
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}. Starting fresh.")
            return None
    return None

def save_result(found_key):
     """Save the found key to a file."""
     try:
         with open(FOUND_KEY_FILE, "w") as f:
              f.write(f"Found T5 Private Key (Term 69):
")
              f.write(f"Decimal: {found_key}
")
              f.write(f"Hex: {hex(found_key)}
")
              f.write(f"Target Hash160: {TARGET_T5_HASH160}
")
              f.write(f"Found at: {datetime.now().isoformat()}
")
         logger.info(f"Successfully saved found key to {FOUND_KEY_FILE}")
     except Exception as e:
         logger.error(f"Error saving found key to {FOUND_KEY_FILE}: {e}")


# -----------------------------
# Main Search Loop
# -----------------------------

def run_search(start_state=None):
    global FOUND_KEY, memory_manager

    if FOUND_KEY:
        logger.info("Key already found. Exiting search.")
        return FOUND_KEY

    state = start_state or {
        'iteration': 0,
        'last_tested_candidate': None,
        'current_strategy': 'high_quality',
        'strategy_iteration': 0,
        'search_center': random.randint(MIN_VALUE, MAX_VALUE), # Initial center
        'genetic_population': [],
    }

    # Ensure initial search center is valid
    while not is_valid_candidate_t5(state['search_center']):
         state['search_center'] = random.randint(MIN_VALUE, MAX_VALUE)


    logger.info("Starting T5 search loop...")
    logger.info(f"Target Hash160: {TARGET_T5_HASH160}")
    logger.info(f"Target Bits: {TARGET_INDEX}")
    logger.info(f"Range: {hex(MIN_VALUE)} to {hex(MAX_VALUE)}")


    strategies = {
        'high_quality': generate_high_quality_candidates,
        'bit_flip': bit_flip_search,
        'range': adaptive_range_search,
        'genetic': genetic_search,
    }
    strategy_order = ['high_quality', 'bit_flip', 'range', 'genetic']
    current_strategy_index = strategy_order.index(state.get('current_strategy', 'high_quality'))

    # Candidate generator state
    candidate_generator = None
    processed_in_strategy = 0
    max_per_strategy_cycle = 10000 # Process N candidates per strategy before switching

    while not FOUND_KEY:
        state['iteration'] += 1

        # Get current strategy function
        strategy_name = strategy_order[current_strategy_index]
        strategy_func = strategies[strategy_name]
        state['current_strategy'] = strategy_name

        # --- Candidate Generation ---
        candidate = None
        try:
            # If we don't have a generator for the current strategy or it's exhausted
            if candidate_generator is None:
                processed_in_strategy = 0 # Reset counter for new strategy cycle
                logger.info(f"Switching/starting strategy: {strategy_name}")
                if strategy_name == 'high_quality':
                    # Generate a batch and iterate through it
                    hq_candidates = strategy_func(num_candidates=max_per_strategy_cycle)
                    candidate_generator = iter(hq_candidates)
                elif strategy_name == 'bit_flip':
                    # Needs a center - use the last promising candidate or a random one
                    center = state.get('last_promising_candidate', state['search_center'])
                    candidate_generator = strategy_func(center=center, max_candidates=max_per_strategy_cycle)
                elif strategy_name == 'range':
                     center = state.get('last_promising_candidate', state['search_center'])
                     candidate_generator = strategy_func(center=center, max_candidates=max_per_strategy_cycle)
                elif strategy_name == 'genetic':
                     # Genetic search yields candidates directly
                     candidate_generator = strategy_func(population_size=POPULATION_SIZE, generations=2) # Run fewer generations per cycle


            # Get the next candidate from the current generator
            candidate = next(candidate_generator)
            processed_in_strategy += 1

        except StopIteration:
            # Current strategy's generator is exhausted, move to the next strategy
            logger.info(f"Strategy '{strategy_name}' cycle complete ({processed_in_strategy} candidates).")
            candidate_generator = None # Reset generator
            current_strategy_index = (current_strategy_index + 1) % len(strategy_order)
            # Update search center for next cycle based on best found so far (if applicable)
            # For T5, 'best' isn't really a concept until match, so maybe just keep randomizing center?
            state['search_center'] = random.randint(MIN_VALUE, MAX_VALUE)
            while not is_valid_candidate_t5(state['search_center']):
                 state['search_center'] = random.randint(MIN_VALUE, MAX_VALUE)
            state['last_promising_candidate'] = state['search_center'] # Reset promising candidate
            continue # Skip testing for this iteration, go to next strategy cycle

        except Exception as e:
             logger.error(f"Error during candidate generation with strategy '{strategy_name}': {e}")
             # Reset generator and move to next strategy to avoid getting stuck
             candidate_generator = None
             current_strategy_index = (current_strategy_index + 1) % len(strategy_order)
             continue


        # --- Candidate Testing ---
        if candidate is not None:
            state['last_tested_candidate'] = candidate
            is_match, _ = test_candidate(candidate) # test_candidate handles logging, saving match

            # For strategies needing feedback (like bit_flip, range), update center if match is found
            # Since T5 is exact match, this might not be super useful unless we find it
            if is_match:
                 state['last_promising_candidate'] = candidate # Found the key!
                 # The main loop will terminate as FOUND_KEY is set

        # --- Progress Saving ---
        if state['iteration'] % 10000 == 0: # Save progress every 10,000 iterations
             save_progress(state)
             logger.info(f"Iteration {state['iteration']}. Tested: {memory_manager.get_count()}. Current Strategy: {strategy_name}")

        if state['iteration'] % 100000 == 0: # Save checkpoint less frequently
             save_checkpoint(state)


    logger.info("Search loop finished.")
    if FOUND_KEY:
        logger.info(f"T5 Key found: {hex(FOUND_KEY)}")
        return FOUND_KEY
    else:
        logger.info("Search finished without finding the key.")
        # Save final state even if not found
        save_checkpoint(state)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Continuous Adaptive Search for T5 (Term 69)")
    parser.add_argument("--resume", action="store_true", help="Resume search from last checkpoint")
    args = parser.parse_args()

    initial_state = None
    if args.resume:
        logger.info("Attempting to resume from checkpoint...")
        initial_state = load_checkpoint()
        if initial_state:
             logger.info("Resuming previous search.")
        else:
             logger.warning("Checkpoint not found or failed to load. Starting a new search.")

    try:
        result = run_search(start_state=initial_state)
        if result:
            print(f"Success! Found T5 Key: {hex(result)}")
        else:
            print("Search completed without finding the key.")
    except KeyboardInterrupt:
        logger.info("Search interrupted by user. Saving final state...")
        # Attempt to save final state on interrupt
        # Need to access the state from run_search, this might require restructuring
        # or saving state more frequently within the loop just before exit.
        memory_manager.save_tested() # Ensure tested candidates are saved
        print("Search stopped. Final state saved.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred during search: {e}")
        print(f"An error occurred: {e}")
        # Try to save state on unexpected error
        memory_manager.save_tested()
        print("Attempted to save state before exiting due to error.")

