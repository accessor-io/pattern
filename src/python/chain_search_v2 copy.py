#!/usr/bin/env python3
import hashlib
import math
import multiprocessing as mp
from functools import lru_cache
import itertools

def int_to_bytes(i, length):
    """Convert an integer i to a byte string of the given length (big-endian)."""
    return i.to_bytes(length, byteorder='big')

def determine_L(n):
    """Determine the number of significant hex digits L for chain element n."""
    return math.ceil(n / 4)

def chain_next_value(prev_value, n):
    """Compute the next chain value."""
    L = determine_L(n)
    m = 16 ** L
    input_bytes = prev_value.to_bytes(32, byteorder='big') + int_to_bytes(n, 4)
    h_bytes = hashlib.sha256(input_bytes).digest()
    X = int.from_bytes(h_bytes, byteorder='big')
    S = X % m
    return X, S, L

@lru_cache(maxsize=1024)
def chain_next_value_cached(prev_value, n):
    """Cached version of chain_next_value."""
    return chain_next_value(prev_value, n)

def analyze_sequence_pattern(value):
    """Analyze if a value follows the discovered sequence patterns."""
    binary = format(value, '028b')
    
    # Check bit distribution (based on analyze_hex_sequence.py)
    ones = binary.count('1')
    if not (6 <= ones <= 9):  # Relaxed constraint based on scaling
        return False
    
    # Check for required patterns (based on sequence analysis)
    required_patterns = ['110', '011', '101']
    if not any(pattern in binary for pattern in required_patterns):
        return False
    
    # Check leading zeros (based on known good seeds)
    leading_zeros = len(binary) - len(binary.lstrip('0'))
    if leading_zeros < 2 or leading_zeros > 20:
        return False
    
    return True

def generate_candidates(base_value):
    """Generate candidates using sequence analysis insights."""
    candidates = set()
    binary = format(base_value, '028b')
    
    # Generate variations based on bit patterns
    for i in range(len(binary) - 2):
        # Shift patterns
        shifted = (base_value << i) & ((1 << 28) - 1)
        candidates.add(shifted)
        
        # Rotate patterns
        rotated = ((base_value << i) | (base_value >> (28 - i))) & ((1 << 28) - 1)
        candidates.add(rotated)
        
        # XOR with key values
        for key in [67, 12, 247]:
            xored = base_value ^ key
            candidates.add(xored & ((1 << 28) - 1))
    
    # Apply polynomial transformations
    poly_value = ((base_value + 2) ** 4) & ((1 << 28) - 1)
    candidates.add(poly_value)
    
    return candidates

def verify_candidate(seed, max_index=6):
    """Verify a candidate seed against known patterns."""
    current = seed
    for n in range(1, max_index + 1):
        _, S, L = chain_next_value_cached(current, n)
        S_hex = format(S, 'x').zfill(L)
        expected = expected_significant.get(n)
        if expected is None or S_hex.lower() != expected.lower():
            return False
        current = _
    return True

def process_batch(args):
    """Process a batch of candidate seeds."""
    start, end = args
    local_best = None
    local_length = 0
    
    for base in range(start, end):
        if not analyze_sequence_pattern(base):
            continue
        
        candidates = generate_candidates(base)
        for candidate in candidates:
            if verify_candidate(candidate):
                valid_length = 0
                current = candidate
                
                # Check how far this candidate goes
                for n in range(1, 66):
                    _, S, L = chain_next_value_cached(current, n)
                    S_hex = format(S, 'x').zfill(L)
                    expected = expected_significant.get(n)
                    if S_hex.lower() != expected.lower():
                        break
                    valid_length = n
                    current = _
                
                if valid_length > local_length:
                    local_length = valid_length
                    local_best = candidate
    
    return local_best, local_length

def main():
    """Main search function."""
    print("Starting enhanced pattern-based search...")
    
    # Use multiple processes for parallel search
    num_processes = mp.cpu_count()
    print(f"Using {num_processes} CPU cores")
    
    # Create batches
    batch_size = 1000000
    batches = []
    for start in range(0, 1 << 28, batch_size):
        end = min(start + batch_size, 1 << 28)
        batches.append((start, end))
    
    # Run parallel search
    with mp.Pool(processes=num_processes) as pool:
        results = []
        for i, result in enumerate(pool.imap_unordered(process_batch, batches)):
            seed, length = result
            if seed is not None:
                results.append((seed, length))
            if i % 10 == 0:
                print(f"Processed {i}/{len(batches)} batches")
                if results:
                    best_so_far = max(results, key=lambda x: x[1])
                    print(f"Current best: Seed {best_so_far[0]:,} (length {best_so_far[1]})")
    
    # Print final results
    if results:
        best_seed, best_length = max(results, key=lambda x: x[1])
        print(f"\nBest seed found: {best_seed:,}")
        print(f"Valid length: {best_length}")
    else:
        print("\nNo valid seeds found")

if __name__ == '__main__':
    main() 