#!/usr/bin/env python3
"""
Adaptive Bitcoin key search for index 68, using multiple search strategies
and machine learning-inspired techniques to find the private key.
Target address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ

This script implements multiple advanced search strategies:
1. Advanced pattern recognition
2. Genetic algorithm approach
3. Machine learning-inspired transformation space exploration 
4. Multi-dimensional search paths
5. Statistical analysis-based candidate generation
6. Ultra-focused proximity search with tiny step size
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
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

# Configure logging
logger = logging.getLogger("bitcoin_search")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Add file handler
file_handler = logging.FileHandler("key_search.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# -----------------------------
# Constants
# -----------------------------

# Target Bitcoin address
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Sequence-specific constants
TARGET_INDEX = 68  # We are looking for the 68th term in the sequence
PREV_TERM_66 = 0x2832ed74f2b5e35ee  # Known value for position 66
PREV_TERM_67 = 0x730fc235c1942c1ae  # Known value for position 67

# Search range boundaries
MIN_VALUE = PREV_TERM_67  # Start from the previous term
MAX_VALUE = (1 << 68) - 1  # Maximum 68-bit value

# Values discovered from previous analyses
MIN_PREDICTED = 0x8747dd8c268dd31c4
MAX_PREDICTED = 0xd7db28ca2b3a33c0c
ESTIMATE_VALUE = 0x12e7b5c4e1c670000
BIT_SHIFTED_VALUE = 0x7a40be591dad6edc8

# Common mathematical constants (potential factors in the sequence)
GOLDEN_RATIO = 1.618033988749895
EULER = 2.718281828459045
PI = 3.141592653589793

# Multiprocessing settings
CPU_COUNT = mp.cpu_count()
CHUNK_SIZE = 1000

# Pattern recognition settings
MAX_PATTERNS = 100
PATTERN_COMPLEXITY = 5  # Max complexity of patterns to detect

# -----------------------------
# Data Loading Functions
# -----------------------------

def load_predictions():
    """
    Load predicted 68th term values from line_68s.txt
    Returns a list of valid predictions
    """
    predictions = []
    try:
        with open('line_68s.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        # Convert hex string to integer
                        value = int(line, 16)
                        if value > PREV_TERM_67:
                            predictions.append(value)
                    except ValueError:
                        continue
        
        # Remove duplicates and sort
        predictions = sorted(set(predictions))
        valid_predictions = [p for p in predictions if p.bit_length() == TARGET_INDEX]
        logger.info(f"Loaded {len(predictions)} total predictions, {len(valid_predictions)} valid 68-bit predictions")
        return valid_predictions
    except FileNotFoundError:
        logger.warning("Predictions file line_68s.txt not found")
        return []

def load_previous_terms():
    """
    Load previous terms from sequence files if available
    Returns a dictionary with position as key and the actual value as integer
    """
    terms = {}
    
    # Define known values in case files can't be loaded
    known_values = {
        66: 0x2832ed74f2b5e35ee,
        67: 0x730fc235c1942c1ae
    }
    
    try:
        # Try to load term 67 values
        with open('line_67s.txt', 'r') as f:
            term_67_values = []
            for line in f:
                line = line.strip()
                if line:
                    try:
                        value = int(line, 16)
                        term_67_values.append(value)
                    except ValueError:
                        continue
            
            if term_67_values:
                # Use the first value for simplicity
                terms[67] = term_67_values[0]
                logger.info(f"Loaded value for term 67: {hex(terms[67])}")
            else:
                terms[67] = known_values[67]
                logger.info(f"Using default value for term 67: {hex(terms[67])}")
    except FileNotFoundError:
        terms[67] = known_values[67]
        logger.info(f"Using default value for term 67: {hex(terms[67])}")
    
    # Also add term 66
    terms[66] = known_values[66]
    logger.info(f"Using value for term 66: {hex(terms[66])}")
    
    return terms

# -----------------------------
# Cryptographic Helper Functions
# -----------------------------

def private_key_to_address(private_key: int) -> str:
    """
    Convert a private key (integer) into a compressed Bitcoin address.
    """
    try:
        privkey_hex = format(private_key, '064x')
        privkey_bytes = bytes.fromhex(privkey_hex)
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Generate compressed public key
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Compressed public key format: 0x02/0x03 + x coordinate
        # 0x02 if y is even, 0x03 if y is odd
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        pubkey = prefix + x.to_bytes(32, 'big')
        
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
    except Exception as e:
        logger.error(f"Error in private_key_to_address: {e}")
        return None

# -----------------------------
# Candidate Validation Functions
# -----------------------------

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

def calculate_candidate_score(candidate: int, prev_terms: dict) -> float:
    """
    Calculate a score for a candidate based on pattern matching.
    Higher score means a better candidate.
    """
    score = 0.0
    
    # Check if the candidate has exactly 68 bits
    if candidate.bit_length() == TARGET_INDEX:
        score += 1.0
    else:
        return 0.0  # Reject if not 68 bits
    
    # Check if candidate is greater than the previous term
    if candidate > PREV_TERM_67:
        score += 1.0
    else:
        return 0.0  # Reject if not > prev term
    
    # Check for consecutive hex chars
    if has_too_many_consecutive_chars(candidate):
        return 0.0  # Reject if has too many consecutive chars
    
    # Reward proximity to predictions
    proximity_to_min = 1.0 - min(1.0, abs(candidate - MIN_PREDICTED) / MIN_PREDICTED)
    proximity_to_max = 1.0 - min(1.0, abs(candidate - MAX_PREDICTED) / MAX_PREDICTED)
    score += max(proximity_to_min, proximity_to_max)
    
    # Reward values that follow mathematical relationships with term 67
    ratio_to_prev = candidate / PREV_TERM_67
    
    # Check proximity to common mathematical constants
    golden_ratio_score = max(0, 1.0 - abs(ratio_to_prev - GOLDEN_RATIO))
    euler_score = max(0, 1.0 - abs(ratio_to_prev - EULER))
    pi_score = max(0, 1.0 - abs(ratio_to_prev - PI))
    
    # Combine mathematical pattern scores
    math_score = max(golden_ratio_score, euler_score, pi_score)
    score += math_score
    
    # Reward bit pattern similarities
    prev_bits = bin(PREV_TERM_67)[2:].zfill(68)
    candidate_bits = bin(candidate)[2:].zfill(68)
    bit_similarity = sum(p == c for p, c in zip(prev_bits, candidate_bits)) / 68.0
    
    # We want some similarity but not too much
    if 0.3 <= bit_similarity <= 0.7:
        score += 1.0
    
    return score

# -----------------------------
# Advanced Pattern Recognition
# -----------------------------

def detect_patterns(previous_terms: dict) -> list:
    """
    Detect potential patterns in the sequence to guide the search.
    Returns a list of pattern functions that can generate candidates.
    """
    patterns = []
    term_67_values = previous_terms.get(67, [PREV_TERM_67])
    
    # Pattern 1: Linear growth
    def linear_pattern(x, a):
        return PREV_TERM_67 + a * x
    
    # Pattern 2: Geometric growth
    def geometric_pattern(x, r):
        return int(PREV_TERM_67 * (r ** x))
    
    # Pattern 3: Bit shift pattern
    def bit_shift_pattern(x, shift):
        return PREV_TERM_67 + (PREV_TERM_67 >> shift)
    
    # Pattern 4: XOR pattern with a constant
    def xor_pattern(x, const):
        return PREV_TERM_67 ^ const
    
    # Pattern 5: Addition with bit reversal
    def bit_reversal_pattern(x):
        bits = bin(PREV_TERM_67)[2:].zfill(68)
        reversed_bits = bits[::-1]
        reversed_value = int(reversed_bits, 2)
        return PREV_TERM_67 + reversed_value
    
    # Pattern 6: Fibonacci-like (based on term_67 and a multiple of it)
    def fibonacci_like_pattern(x, mult):
        prev = PREV_TERM_67
        prev_prev = int(prev / mult)
        return prev + prev_prev
    
    # Add basic patterns with various parameters
    for a in [1, 10, 100, 1000, 10000, 100000]:
        patterns.append(lambda x, a=a: linear_pattern(x, a))
    
    for r in [1.1, 1.2, 1.5, 1.618, 2, 3, 4]:
        patterns.append(lambda x, r=r: geometric_pattern(x, r))
    
    for shift in range(1, 10):
        patterns.append(lambda x, shift=shift: bit_shift_pattern(x, shift))
    
    for const in [0x1, 0xF, 0xFF, 0xFFF, 0xFFFF, 0x12345, 0xABCDEF]:
        patterns.append(lambda x, const=const: xor_pattern(x, const))
    
    patterns.append(lambda x: bit_reversal_pattern(x))
    
    for mult in [1.5, 1.618, 2, 3, 4]:
        patterns.append(lambda x, mult=mult: fibonacci_like_pattern(x, mult))
    
    logger.info(f"Generated {len(patterns)} pattern functions")
    return patterns

def generate_pattern_candidates(patterns: list, count: int = 1000) -> list:
    """
    Generate candidates based on detected patterns.
    """
    candidates = []
    
    for pattern_func in patterns:
        try:
            for i in range(1, 10):  # Try different inputs
                candidate = pattern_func(i)
                if isinstance(candidate, float):
                    candidate = int(candidate)
                
                if is_valid_candidate(candidate):
                    candidates.append(candidate)
                
                if len(candidates) >= count:
                    break
        except Exception as e:
            logger.warning(f"Error in pattern function: {e}")
    
    return list(set(candidates))[:count]

# -----------------------------
# Genetic Algorithm Approach
# -----------------------------

def create_initial_population(size=100):
    """
    Create initial population for genetic algorithm
    """
    population = []
    
    # Add some predefined values
    initial_values = [
        PREV_TERM_67 + 1,
        MIN_PREDICTED,
        MAX_PREDICTED,
        ESTIMATE_VALUE,
        BIT_SHIFTED_VALUE
    ]
    
    population.extend(initial_values)
    
    # Add random variations
    while len(population) < size:
        # Choose a base value
        base = random.choice(initial_values)
        
        # Apply random mutation
        mutation_type = random.randint(1, 4)
        
        if mutation_type == 1:  # Bit flip
            bit_pos = random.randint(0, 67)
            new_value = base ^ (1 << bit_pos)
        elif mutation_type == 2:  # Add random number
            new_value = base + random.randint(1, 1000000)
        elif mutation_type == 3:  # XOR with random value
            new_value = base ^ random.randint(1, 0xFFFF)
        else:  # Bit shift
            shift = random.randint(1, 10)
            new_value = base + (base >> shift)
        
        if is_valid_candidate(new_value):
            population.append(new_value)
    
    # Return unique valid candidates
    return list(set(p for p in population if is_valid_candidate(p)))

def crossover(parent1, parent2):
    """
    Perform crossover operation between two parents
    """
    # Convert to binary strings with leading zeros
    p1_bits = bin(parent1)[2:].zfill(68)
    p2_bits = bin(parent2)[2:].zfill(68)
    
    # Choose random crossover point
    crossover_point = random.randint(1, 67)
    
    # Create child
    child_bits = p1_bits[:crossover_point] + p2_bits[crossover_point:]
    child = int(child_bits, 2)
    
    return child

def mutate(candidate, mutation_rate=0.05):
    """
    Mutate a candidate by flipping bits with a certain probability
    """
    bits = list(bin(candidate)[2:].zfill(68))
    
    for i in range(len(bits)):
        if random.random() < mutation_rate:
            bits[i] = '1' if bits[i] == '0' else '0'
    
    mutated = int(''.join(bits), 2)
    return mutated

def genetic_algorithm_search(prev_terms, population_size=100, generations=10):
    """
    Perform genetic algorithm search
    """
    logger.info(f"Starting genetic algorithm search with population size {population_size}")
    
    # Create initial population
    population = create_initial_population(population_size)
    
    total_tested = 0
    best_score = 0
    best_candidate = None
    
    for generation in range(generations):
        logger.info(f"Generation {generation+1}/{generations}, population: {len(population)}")
        
        # Evaluate fitness
        fitness_scores = []
        for candidate in population:
            score = calculate_candidate_score(candidate, prev_terms)
            fitness_scores.append((candidate, score))
            
            # Test the candidate
            try:
                addr = private_key_to_address(candidate)
                total_tested += 1
                
                if addr == TARGET_ADDRESS:
                    logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                    save_result(candidate)
                    return candidate
                
                if score > best_score:
                    best_score = score
                    best_candidate = candidate
            except Exception as e:
                logger.error(f"Error testing {hex(candidate)}: {e}")
        
        # Sort by fitness
        fitness_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top performers
        top_performers = [fs[0] for fs in fitness_scores[:population_size//2]]
        
        # Create new population
        new_population = top_performers.copy()
        
        # Add new offspring
        while len(new_population) < population_size:
            parent1 = random.choice(top_performers)
            parent2 = random.choice(top_performers)
            
            child = crossover(parent1, parent2)
            child = mutate(child)
            
            if is_valid_candidate(child):
                new_population.append(child)
        
        population = list(set(new_population))
        
        if total_tested % 100 == 0:
            logger.info(f"Tested {total_tested} candidates, best score: {best_score}, best candidate: {hex(best_candidate)}")
    
    logger.info(f"Completed genetic algorithm search, tested {total_tested} candidates")
    return None

# -----------------------------
# Statistical Analysis and Candidate Generation
# -----------------------------

def analyze_bit_patterns(prev_terms):
    """
    Analyze bit patterns in previous terms to guide search
    """
    term_67_values = prev_terms.get(67, [PREV_TERM_67])
    # Ensure we create enough stats slots for the maximum bit length
    max_bits = max(val.bit_length() for val in term_67_values)
    bit_stats = [{'0': 0, '1': 0} for _ in range(max_bits)]
    
    for value in term_67_values:
        bits = bin(value)[2:].zfill(max_bits)
        for i, bit in enumerate(bits):
            bit_stats[i][bit] += 1
    
    # Calculate probability of each bit being 1
    bit_probs = []
    for pos in range(max_bits):
        total = bit_stats[pos]['0'] + bit_stats[pos]['1']
        if total > 0:
            prob_1 = bit_stats[pos]['1'] / total
        else:
            prob_1 = 0.5  # Default to 50% if no data
        bit_probs.append(prob_1)
    
    return bit_probs

def generate_statistical_candidates(bit_probs, count=1000):
    """
    Generate candidates based on bit probabilities
    """
    candidates = []
    
    while len(candidates) < count:
        # Generate candidate based on bit probabilities
        bits = []
        for prob in bit_probs:
            if random.random() < prob:
                bits.append('1')
            else:
                bits.append('0')
        
        candidate = int(''.join(bits), 2)
        
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    return list(set(candidates))

# -----------------------------
# Multi-dimensional Search
# -----------------------------

def search_bit_dimension(start_value, bit_positions, max_candidates=1000):
    """
    Search along specific bit dimensions (flipping combinations of bits)
    """
    candidates = []
    
    # Generate all combinations of bit positions
    for r in range(1, min(5, len(bit_positions) + 1)):
        for combo in itertools.combinations(bit_positions, r):
            # Create a mask that has 1s at the selected positions
            mask = sum(1 << pos for pos in combo)
            
            # Flip those bits
            candidate = start_value ^ mask
            
            if is_valid_candidate(candidate):
                candidates.append(candidate)
            
            if len(candidates) >= max_candidates:
                break
    
    return candidates

def multi_dimensional_search(prev_terms, base_candidates, max_candidates=5000):
    """
    Conduct search along multiple dimensions based on bit positions
    """
    logger.info("Starting multi-dimensional search")
    
    # Identify important bit positions
    bit_probs = analyze_bit_patterns(prev_terms)
    important_bits = [i for i, prob in enumerate(bit_probs) if 0.3 <= prob <= 0.7]
    
    logger.info(f"Identified {len(important_bits)} important bit positions")
    
    candidates = []
    tested = 0
    
    # Search around each base candidate
    for base in base_candidates:
        logger.info(f"Searching around base {hex(base)}")
        
        # Get candidates from bit dimension search
        bit_candidates = search_bit_dimension(base, important_bits, max_candidates//len(base_candidates))
        
        for candidate in bit_candidates:
            tested += 1
            try:
                addr = private_key_to_address(candidate)
                if addr == TARGET_ADDRESS:
                    logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                    save_result(candidate)
                    return candidate
                
                if tested % 100 == 0:
                    logger.info(f"Tested {tested} multi-dimensional candidates")
            except Exception as e:
                logger.error(f"Error testing {hex(candidate)}: {e}")
    
    logger.info(f"Completed multi-dimensional search, tested {tested} candidates")
    return None

# -----------------------------
# Mathematical Transformations
# -----------------------------

def apply_mathematical_transformations(base_value, count=100):
    """
    Apply various mathematical transformations to generate candidates
    """
    candidates = []
    transformations = [
        # Linear transforms
        lambda x: x + 1,
        lambda x: x + 0x100,
        lambda x: x + 0x10000,
        
        # Multiplicative transforms
        lambda x: int(x * 1.5),
        lambda x: int(x * GOLDEN_RATIO),
        lambda x: int(x * PI),
        lambda x: int(x * EULER),
        
        # Bit operations
        lambda x: x ^ 0xFFFF,
        lambda x: x ^ 0xFFFFFFFF,
        lambda x: x | 0xFF,
        lambda x: x & ~0xFF,
        
        # Shifts
        lambda x: x << 1,
        lambda x: x << 2,
        lambda x: x >> 1,
        lambda x: x >> 2,
        
        # Combinations
        lambda x: (x << 1) ^ 0xF0F0,
        lambda x: (x >> 2) | 0xF0F0,
        lambda x: (x + 0x1000) ^ 0xAAAA,
    ]
    
    for transform in transformations:
        try:
            candidate = transform(base_value)
            if is_valid_candidate(candidate):
                candidates.append(candidate)
            
            if len(candidates) >= count:
                break
        except Exception:
            continue
    
    return list(set(candidates))

def mathematical_transformation_search(base_candidates, max_candidates=5000):
    """
    Search using mathematical transformations on base candidates
    """
    logger.info("Starting mathematical transformation search")
    
    candidates = []
    tested = 0
    
    # Apply transformations to each base candidate
    for base in base_candidates:
        transformed = apply_mathematical_transformations(base)
        candidates.extend(transformed)
    
    # Remove duplicates
    candidates = list(set(candidates))
    logger.info(f"Generated {len(candidates)} candidates via mathematical transformations")
    
    # Test candidates
    for candidate in candidates[:max_candidates]:
        tested += 1
        try:
            addr = private_key_to_address(candidate)
            if addr == TARGET_ADDRESS:
                logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                save_result(candidate)
                return candidate
            
            if tested % 100 == 0:
                logger.info(f"Tested {tested} transformation candidates")
        except Exception as e:
            logger.error(f"Error testing {hex(candidate)}: {e}")
    
    logger.info(f"Completed transformation search, tested {tested} candidates")
    return None

# -----------------------------
# Prediction Validation
# -----------------------------

def search_predictions(predictions):
    """
    Search through predicted values
    """
    logger.info(f"Starting search through {len(predictions)} predictions")
    tested = 0
    
    for candidate in predictions:
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
                logger.info(f"Tested {tested} predictions, current: {hex(candidate)}")
        except Exception as e:
            logger.error(f"Error processing {hex(candidate)}: {e}")
    
    logger.info(f"Completed testing {tested} predictions without finding a match")
    return None

# -----------------------------
# Optimization-based Search
# -----------------------------

def hill_climbing_search(start_value, iterations=1000, step_size=0.1):
    """
    Perform hill climbing search starting from a value
    """
    logger.info(f"Starting hill climbing search from {hex(start_value)}")
    
    current_value = start_value
    current_score = calculate_candidate_score(current_value, {67: [PREV_TERM_67]})
    
    best_value = current_value
    best_score = current_score
    
    tested = 0
    
    for i in range(iterations):
        # Generate neighbors by flipping random bits
        neighbors = []
        for _ in range(5):  # Generate 5 neighbors
            bit_pos = random.randint(0, 67)
            neighbor = current_value ^ (1 << bit_pos)
            
            if is_valid_candidate(neighbor):
                neighbors.append(neighbor)
        
        if not neighbors:
            continue
        
        # Evaluate neighbors
        best_neighbor = None
        best_neighbor_score = 0
        
        for neighbor in neighbors:
            score = calculate_candidate_score(neighbor, {67: [PREV_TERM_67]})
            
            tested += 1
            try:
                addr = private_key_to_address(neighbor)
                if addr == TARGET_ADDRESS:
                    logger.info(f"MATCH FOUND! Candidate: {hex(neighbor)}")
                    save_result(neighbor)
                    return neighbor
            except Exception:
                continue
            
            if score > best_neighbor_score:
                best_neighbor = neighbor
                best_neighbor_score = score
        
        # Move to best neighbor if better than current
        if best_neighbor_score > current_score:
            current_value = best_neighbor
            current_score = best_neighbor_score
            
            if current_score > best_score:
                best_value = current_value
                best_score = current_score
                logger.info(f"New best: {hex(best_value)} with score {best_score}")
        else:
            # Random restart to avoid local optima
            if random.random() < 0.1:
                bit_pos = random.randint(0, 67)
                current_value = current_value ^ (1 << bit_pos)
                current_score = calculate_candidate_score(current_value, {67: [PREV_TERM_67]})
        
        if tested % 100 == 0:
            logger.info(f"Tested {tested} candidates in hill climbing, best score: {best_score}")
    
    logger.info(f"Completed hill climbing search, tested {tested} candidates")
    return None

# -----------------------------
# Search around Specific Values
# -----------------------------

def search_range(start, end, step=1):
    """
    Search a range of values
    """
    tested = 0
    
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
                logger.info(f"Tested {tested} range candidates, current: {hex(candidate)}")
        except Exception as e:
            logger.error(f"Error processing {hex(candidate)}: {e}")
    
    logger.info(f"Completed testing {tested} range candidates without finding a match")
    return None

def focused_range_search():
    """
    Search through focused ranges based on all analysis
    """
    # Define ranges to check based on observed patterns and analysis
    ranges = [
        # Near the previous term
        (PREV_TERM_67, PREV_TERM_67 + 0x10000, 16),
        
        # Around MIN_PREDICTED
        (MIN_PREDICTED - 0x10000, MIN_PREDICTED + 0x10000, 16),
        
        # Around MAX_PREDICTED
        (MAX_PREDICTED - 0x10000, MAX_PREDICTED + 0x10000, 16),
        
        # Around BIT_SHIFTED_VALUE
        (BIT_SHIFTED_VALUE - 0x10000, BIT_SHIFTED_VALUE + 0x10000, 16),
        
        # Special ranges based on mathematical constants
        (int(PREV_TERM_67 * GOLDEN_RATIO) - 0x1000, int(PREV_TERM_67 * GOLDEN_RATIO) + 0x1000, 8),
        (int(PREV_TERM_67 * PI) - 0x1000, int(PREV_TERM_67 * PI) + 0x1000, 8),
        (int(PREV_TERM_67 * EULER) - 0x1000, int(PREV_TERM_67 * EULER) + 0x1000, 8),
        
        # Power of 2 multiples
        (PREV_TERM_67 * 2 - 0x1000, PREV_TERM_67 * 2 + 0x1000, 8),
        (PREV_TERM_67 * 4 - 0x1000, PREV_TERM_67 * 4 + 0x1000, 8),
        
        # Special bit patterns
        (PREV_TERM_67 ^ 0xFFFFFF, (PREV_TERM_67 ^ 0xFFFFFF) + 0x1000, 8),
        (PREV_TERM_67 | 0xFFFFFF, (PREV_TERM_67 | 0xFFFFFF) + 0x1000, 8),
        (PREV_TERM_67 & ~0xFFFFFF, (PREV_TERM_67 & ~0xFFFFFF) + 0x1000, 8),
    ]
    
    logger.info("Starting focused range search")
    
    for start, end, step in ranges:
        logger.info(f"Searching range {hex(start)} to {hex(end)} with step {step}")
        result = search_range(start, end, step)
        if result:
            return result
    
    return None

# -----------------------------
# Proximity-based Search
# -----------------------------

def search_nearby_values(base_value, range_size=10000, step=1):
    """
    Search values that are very close to a base value (both above and below).
    This is useful when we suspect the key is very close to a known value.
    
    Args:
        base_value: The central value to search around
        range_size: How far to search in both directions
        step: Step size for the search
    """
    logger.info(f"Starting proximity search around {hex(base_value)} with range ±{range_size}")
    
    # Search above the base value
    for offset in range(0, range_size, step):
        candidate = base_value + offset
        if is_valid_candidate(candidate):
            try:
                addr = private_key_to_address(candidate)
                if addr == TARGET_ADDRESS:
                    logger.info(f"MATCH FOUND! Candidate: {hex(candidate)} (offset +{offset})")
                    save_result(candidate)
                    return candidate
                
                if offset % 1000 == 0:
                    logger.info(f"Tested up to +{offset} from base")
            except Exception as e:
                logger.error(f"Error testing {hex(candidate)}: {e}")
    
    # Search below the base value (but not below PREV_TERM_67)
    for offset in range(1, range_size, step):
        candidate = base_value - offset
        if candidate <= PREV_TERM_67:
            continue
            
        if is_valid_candidate(candidate):
            try:
                addr = private_key_to_address(candidate)
                if addr == TARGET_ADDRESS:
                    logger.info(f"MATCH FOUND! Candidate: {hex(candidate)} (offset -{offset})")
                    save_result(candidate)
                    return candidate
                
                if offset % 1000 == 0:
                    logger.info(f"Tested down to -{offset} from base")
            except Exception as e:
                logger.error(f"Error testing {hex(candidate)}: {e}")
    
    logger.info(f"Completed proximity search without finding a match")
    return None

# -----------------------------
# Direct Key Testing Function
# -----------------------------

def direct_key_search(base_value, range_size=100000, step=1):
    """
    Perform a direct search around a base value with small step sizes.
    This is a brute force approach within a limited range.
    
    Args:
        base_value: The integer value to search around
        range_size: How far to search in each direction
        step: Step size for the search
    
    Returns:
        The private key value if found, None otherwise
    """
    logger.info(f"Starting direct key search around {hex(base_value)}")
    logger.info(f"Search range: ±{range_size} with step {step}")
    
    # First test the exact base value
    address = private_key_to_address(base_value)
    if address == TARGET_ADDRESS:
        logger.info(f"Found match at exact base value: {hex(base_value)}")
        return base_value
    
    # Try above the base value
    for i in range(step, range_size + 1, step):
        if i % 10000 == 0:
            logger.info(f"Testing: +{i} from base")
        
        test_value = base_value + i
        try:
            address = private_key_to_address(test_value)
            if address == TARGET_ADDRESS:
                logger.info(f"Found match at +{i} from base: {hex(test_value)}")
                return test_value
        except Exception as e:
            logger.error(f"Error testing +{i}: {str(e)}")
    
    # Try below the base value
    for i in range(step, range_size + 1, step):
        if i % 10000 == 0:
            logger.info(f"Testing: -{i} from base")
        
        test_value = base_value - i
        # Don't test negative values
        if test_value <= 0:
            break
            
        try:
            address = private_key_to_address(test_value)
            if address == TARGET_ADDRESS:
                logger.info(f"Found match at -{i} from base: {hex(test_value)}")
                return test_value
        except Exception as e:
            logger.error(f"Error testing -{i}: {str(e)}")
    
    logger.info(f"No match found in range ±{range_size} from {hex(base_value)}")
    return None

def ultra_focused_search(base_value, offset_range=1000, step=1):
    """
    Perform an ultra-focused search with a very small step size
    around a given base value.
    
    Args:
        base_value: The integer value to search around
        offset_range: How far to search in each direction
        step: Step size for the search (default is 1 for incremental search)
    
    Returns:
        The private key value if found, None otherwise
    """
    logger.info(f"Starting ultra-focused search around {hex(base_value)}")
    logger.info(f"Search range: ±{offset_range} with step {step}")
    
    # Test the exact base value first
    address = private_key_to_address(base_value)
    if address == TARGET_ADDRESS:
        logger.info(f"Found match at exact base value: {hex(base_value)}")
        return base_value
    
    # Test small offsets around the base value
    for offset in range(1, offset_range + 1, step):
        # Test base + offset
        try:
            value_plus = base_value + offset
            address = private_key_to_address(value_plus)
            if address == TARGET_ADDRESS:
                logger.info(f"Found match at +{offset} from base: {hex(value_plus)}")
                return value_plus
        except Exception as e:
            logger.error(f"Error testing +{offset}: {str(e)}")
        
        # Test base - offset
        try:
            value_minus = base_value - offset
            if value_minus > 0:  # Don't test negative values
                address = private_key_to_address(value_minus)
                if address == TARGET_ADDRESS:
                    logger.info(f"Found match at -{offset} from base: {hex(value_minus)}")
                    return value_minus
        except Exception as e:
            logger.error(f"Error testing -{offset}: {str(e)}")
        
        # Log progress every 100 iterations
        if offset % 100 == 0:
            logger.info(f"Tested offsets: ±{offset}")
    
    logger.info(f"No match found in ultra-focused search ±{offset_range} from {hex(base_value)}")
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
# Main Search Orchestration
# -----------------------------

def main():
    """Main execution function that combines multiple search strategies"""
    logger.info(f"Starting adaptive search for Term 68")
    
    # Load known values and predictions
    prev_terms = load_previous_terms()
    predictions = load_predictions()
    
    logger.info(f"Target address: {TARGET_ADDRESS}")
    logger.info(f"Previous term (67): {hex(prev_terms[67])}")
    logger.info(f"Search range: {hex(prev_terms[67])} to {hex(0xfffffffffffffffff)}")
    
    # Initialize direct search candidates with term 67 and nearby values
    direct_search_candidates = [
        prev_terms[67],                             # Exact Term 67
        prev_terms[67] + 1,                         # Term 67 + 1
        prev_terms[67] - 1,                         # Term 67 - 1
        
        # Adjacent terms +/- small offsets
        prev_terms[67] + 0x1a,                      # Small offset based on previous patterns
        prev_terms[67] - 0x1a,
        prev_terms[67] + 0x67,                      # Position number as offset
        prev_terms[67] - 0x67,
        prev_terms[67] + 0x68,                      # Target position as offset
        prev_terms[67] - 0x68,
        
        # Common growth patterns
        int(prev_terms[67] * 1.1),                  # Geometric growth at various rates
        int(prev_terms[67] * 1.2),
        int(prev_terms[67] * 1.3),
        int(prev_terms[67] * 1.4),
        int(prev_terms[67] * 1.5),
        int(prev_terms[67] * 1.6),
        
        # Fibonacci-like patterns (xor with previous terms)
        prev_terms[67] ^ prev_terms[66],            # XOR with previous term
        (prev_terms[67] ^ prev_terms[66]) + prev_terms[67], # XOR combined with addition
        
        # Bit-shifted values
        prev_terms[67] << 1,                        # Left shift by 1
        prev_terms[67] >> 1,                        # Right shift by 1
        (prev_terms[67] << 1) ^ prev_terms[67],     # Shift and XOR
        
        # Patterns observed in crypto functions
        (prev_terms[67] << 8) ^ (prev_terms[67] >> 56), # Rotation patterns
        ((prev_terms[67] << 1) | (prev_terms[67] >> 63)) & 0xFFFFFFFFFFFFFFFF,
        
        # Predictions if available
        min(predictions) if predictions else None,
        max(predictions) if predictions else None
    ]
    
    # Filter out None values and keep unique candidates
    direct_search_candidates = [x for x in direct_search_candidates if x is not None]
    direct_search_candidates = list(set(direct_search_candidates))
    
    logger.info(f"Generated {len(direct_search_candidates)} direct search candidates")
    
    # Log the direct search candidates for reference
    for i, candidate in enumerate(direct_search_candidates):
        logger.info(f"Candidate {i+1}: {hex(candidate)}")
    
    # First try ultra-focused searches with step size of 1
    logger.info("Starting ultra-focused search with tiny steps")
    for candidate in direct_search_candidates:
        result = ultra_focused_search(candidate, offset_range=25000, step=1)
        if result:
            save_result(result)
            return result
    
    # Try larger ranges for promising candidates
    logger.info("Expanding search to larger ranges")
    priority_candidates = [
        prev_terms[67],                  # Term 67
        int(prev_terms[67] * 1.1),       # 10% growth
        int(prev_terms[67] * 1.2),       # 20% growth
        prev_terms[67] ^ prev_terms[66], # XOR pattern
    ]
    
    for candidate in priority_candidates:
        result = direct_key_search(candidate, range_size=1000000, step=1)
        if result:
            save_result(result)
            return result
    
    # Try proximity-based searches
    logger.info("Starting proximity-based searches")
    for base_value in prev_terms.values():
        result = search_nearby_values(base_value, range_size=10000, step=10)
        if result:
            save_result(result)
            return result
    
    # Try pattern-based approach
    logger.info("Starting pattern recognition search")
    patterns = detect_patterns(prev_terms)
    pattern_candidates = generate_pattern_candidates(patterns)
    result = search_predictions(pattern_candidates)
    if result:
        save_result(result)
        return result
    
    # Try statistical analysis approach
    logger.info("Starting statistical analysis")
    bit_stats = analyze_bit_patterns(prev_terms)
    stat_candidates = generate_statistical_candidates(bit_stats)
    result = search_predictions(stat_candidates)
    if result:
        save_result(result)
        return result
    
    logger.info("All search strategies completed without finding the key")
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