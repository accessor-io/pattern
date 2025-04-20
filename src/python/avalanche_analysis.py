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
    """
    Determine the number of significant hex digits L for chain element n.
    Here we use the rule: L = ceil(n / 4)
    This rule reproduces the known lengths for n=1..65.
    """
    return math.ceil(n / 4)

def chain_next_value(prev_value, n):
    """
    Given the previous 256-bit integer `prev_value` and the chain index n,
    compute the next 256-bit integer Xₙ by hashing (prev_value || n).
    
    Then the "significant" part is defined as:
         Sₙ = Xₙ mod (16^L)
    where L = determine_L(n).
    Returns (X, S, L).
    """
    L = determine_L(n)
    m = 16 ** L
    input_bytes = prev_value.to_bytes(32, byteorder='big') + int_to_bytes(n, 4)
    h_bytes = hashlib.sha256(input_bytes).digest()
    X = int.from_bytes(h_bytes, byteorder='big')
    S = X % m
    print(f"chain_next_value: prev_value={prev_value}, n={n}, input_bytes={input_bytes.hex()}, h_bytes={h_bytes.hex()}, X={X}, S={S}, L={L}")
    return X, S, L

def format_256bit(X):
    """Return a 64-character hexadecimal string for a 256-bit integer X."""
    return format(X, '064x')

# Expected significant parts for indices 1 through 65.
expected_significant = {
    1: "1",
    2: "3",
    3: "7",
    4: "8",
    5: "15",
    6: "31",
    7: "4c",
    8: "e0",
    9: "1d3",
    10: "202",
    11: "483",
    12: "a7b",
    13: "1460",
    14: "2930",
    15: "68f3",
    16: "c936",
    17: "1764f",
    18: "3080d",
    19: "5749f",
    20: "d2c55",
    21: "1ba534",
    22: "2de40f",
    23: "556e52",
    24: "dc2a04",
    25: "1fa5ee5",
    26: "340326e",
    27: "6ac3875",
    28: "d916ce8",
    29: "17e2551e",
    30: "3d94cd64",
    31: "7d4fe747",
    32: "b862a62e",
    33: "1a96ca8d8",
    34: "34a65911d",
    35: "4aed21170",
    36: "9de820a7c",
    37: "1757756a93",
    38: "22382facd0",
    39: "4b5f8303e9",
    40: "e9ae4933d6",
    41: "153869acc5b",
    42: "2a221c58d8f",
    43: "6bd3b27c591",
    44: "e02b35a358f",
    45: "122fca143c05",
    46: "2ec18388d544",
    47: "6cd610b53cba",
    48: "ade6d7ce3b9b",
    49: "174176b015f4d",
    50: "22bd43c2e9354",
    51: "75070a1a009d4",
    52: "efae164cb9e3c",
    53: "180788e47e326c",
    54: "236fb6d5ad1f43",
    55: "6abe1f9b67e114",
    56: "9d18b63ac4ffdf",
    57: "1eb25c90795d61c",
    58: "2c675b852189a21",
    59: "7496cbb87cab44f",
    60: "fc07a1825367bbe",
    61: "13c96a3742f64906",
    62: "363d541eb611abee",
    63: "7cce5efdaccf6808",
    64: "f7051f27b09112d4",
    65: "1a838b13505b26867"
}

def generate_chain(seed, chain_length):
    """
    Generate and print the chain of values starting from a given seed.
    """
    current_value = seed
    for n in range(1, chain_length + 1):
        current_value, S, L = chain_next_value(current_value, n)
        full_hex = format_256bit(current_value)
        significant_str = full_hex[-L:]
        print(f"Index {n:2d}: {full_hex[:-L]}[{significant_str}]   Expected: {expected_significant.get(n, 'N/A')}")
    return current_value

def verify_candidate(seed, max_index=65):
    """
    Verify candidate seed by iterating through each index from 1 to max_index.
    For each index, if the computed significant part does not match the expected value,
    log the failure and return False.
    If all indices match, return True.
    """
    current_value = seed
    for n in range(1, max_index + 1):
        current_value, S, L = chain_next_value(current_value, n)
        S_hex = format(S, 'x').zfill(L)
        expected = expected_significant.get(n)
        print(f"Index {n}: computed significant = {S_hex} (expected: {expected})")
        if expected is None or S_hex.lower() != expected.lower():
            print(f"Seed {seed} rejected at index {n}.")
            return False
    return True

def analyze_candidate_chain(seed, max_index=65):
    """
    Analyze a candidate seed's chain in detail, showing the full hash values
    and how the significant parts are derived.
    """
    current_value = seed
    chain_data = []
    
    print(f"\n🔍 Detailed Analysis of Seed {seed}")
    print(f"Initial seed (X₀): {format_256bit(seed)}")
    
    for n in range(1, max_index + 1):
        X, S, L = chain_next_value(current_value, n)
        S_hex = format(S, 'x').zfill(L)
        expected = expected_significant.get(n)
        matches = S_hex.lower() == expected.lower()
        
        chain_data.append({
            'index': n,
            'full_hash': X,
            'significant': S_hex,
            'expected': expected,
            'L': L,
            'matches': matches
        })
        
        if not matches:
            break
            
        current_value = X
    
    return chain_data

@lru_cache(maxsize=1024)
def chain_next_value_cached(prev_value, n):
    """Cached version of chain_next_value for frequently accessed values."""
    return chain_next_value(prev_value, n)

def quick_reject_check(seed):
    """
    Quick check of first few indices to reject obviously bad seeds.
    Uses bit manipulation for faster checks.
    """
    current = seed
    # Check first index (must produce "1")
    _, S, _ = chain_next_value_cached(current, 1)
    if S != 1:  # First index must be exactly 1
        print(f"quick_reject_check: Seed {seed} rejected at index 1 with S={S}")
        return False
    
    # Check second index (must produce "3")
    _, S, _ = chain_next_value_cached(current, 2)
    if S != 3:  # Second index must be exactly 3
        print(f"quick_reject_check: Seed {seed} rejected at index 2 with S={S}")
        return False
    
    return True

def process_batch(args):
    """
    Process a batch of seeds in parallel.
    Returns the best seed and its valid length in this batch.
    """
    start, end, max_index = args
    local_best_seed = None
    local_best_length = 0
    
    for seed in range(start, end):
        # Quick rejection test first
        if not quick_reject_check(seed):
            continue
            
        current_value = seed
        valid_length = 0
        
        # Now check remaining indices
        for n in range(3, max_index + 1):
            _, S, L = chain_next_value_cached(current_value, n)
            S_hex = format(S, 'x').zfill(L)
            expected = expected_significant.get(n)
            
            if S_hex.lower() != expected.lower():
                print(f"process_batch: Seed {seed} rejected at index {n} with S={S_hex} (expected: {expected})")
                break
            valid_length = n
            current_value = _
        
        if valid_length > local_best_length:
            local_best_length = valid_length
            local_best_seed = seed
            print(f"process_batch: New local best seed {seed} with valid length {valid_length}")
    
    return local_best_seed, local_best_length

def parallel_candidate_search(candidate_min, candidate_max, max_index=65, batch_size=100000):
    """
    Parallel implementation of the candidate search using multiple processes.
    """
    num_processes = mp.cpu_count()  # Use all available CPU cores
    print(f"Using {num_processes} CPU cores for parallel search")
    
    # Create batches
    batches = []
    for start in range(candidate_min, candidate_max, batch_size):
        end = min(start + batch_size, candidate_max)
        batches.append((start, end, max_index))
    
    # Create process pool and run search
    with mp.Pool(processes=num_processes) as pool:
        results = []
        for i, result in enumerate(pool.imap_unordered(process_batch, batches)):
            seed, length = result
            if seed is not None:
                results.append((seed, length))
            if i % 10 == 0:  # Progress update every 10 batches
                print(f"Processed {i}/{len(batches)} batches")
                if results:
                    best_so_far = max(results, key=lambda x: x[1])
                    print(f"Current best: Seed {best_so_far[0]:,} (length {best_so_far[1]})")
    
    # Find the overall best result
    if results:
        best_seed, best_length = max(results, key=lambda x: x[1])
        return best_seed, best_length
    return None, 0

def analyze_hash_pattern(seed, length=5):
    """
    Analyze the hash pattern for a given seed, showing how each value
    is derived from the previous one.
    """
    current_value = seed
    print(f"\n🔍 Hash Chain Analysis for Seed {seed:,}")
    print(f"Initial seed (X₀): {format_256bit(seed)}")
    
    for n in range(1, length + 1):
        input_bytes = current_value.to_bytes(32, byteorder='big') + int_to_bytes(n, 4)
        h_bytes = hashlib.sha256(input_bytes).digest()
        X = int.from_bytes(h_bytes, byteorder='big')
        L = determine_L(n)
        m = 16 ** L
        S = X % m
        S_hex = format(S, 'x').zfill(L)
        expected = expected_significant.get(n)
        
        print(f"\nIndex {n}:")
        print(f"  Input bytes: {input_bytes.hex()}")
        print(f"  Full hash (X_{n}): {format_256bit(X)}")
        print(f"  L = {L} (using {L} hex digits)")
        print(f"  Modulus = 16^{L} = {m}")
        print(f"  Significant (S_{n}): {S_hex}")
        print(f"  Expected: {expected}")
        print(f"  {'✓' if S_hex.lower() == expected.lower() else '❌'} Match status")
        
        current_value = X
    return current_value

def search_region(center_seed, radius, max_index=65):
    """
    Search a specific region around a promising seed.
    """
    start_seed = max(0, center_seed - radius)
    end_seed = center_seed + radius
    
    print(f"\n🎯 Searching region around seed {center_seed:,}")
    print(f"Range: {start_seed:,} to {end_seed:,}")
    
    best_seed = None
    best_length = 0
    
    for seed in range(start_seed, end_seed + 1):
        current_value = seed
        valid_length = 0
        
        for n in range(1, max_index + 1):
            _, S, L = chain_next_value(current_value, n)
            S_hex = format(S, 'x').zfill(L)
            expected = expected_significant.get(n)
            
            if S_hex.lower() != expected.lower():
                print(f"search_region: Seed {seed} rejected at index {n} with S={S_hex} (expected: {expected})")
                break
            valid_length = n
            current_value = _
        
        if valid_length > best_length:
            best_length = valid_length
            best_seed = seed
            print(f"\n🔥 New best in region: Seed {seed:,} reached index {valid_length}")
    
    return best_seed, best_length

def analyze_bit_patterns(seed):
    """
    Analyze the bit patterns of a seed and its hash chain.
    """
    current_value = seed
    print(f"\n🔬 Bit Pattern Analysis for Seed {seed:,}")
    print(f"Seed bits: {bin(seed)[2:].zfill(28)}")
    
    for n in range(1, 7):  # Analyze up to index 6
        X, S, L = chain_next_value(current_value, n)
        S_hex = format(S, 'x').zfill(L)
        expected = expected_significant.get(n)
        matches = S_hex.lower() == expected.lower()
        
        print(f"\nIndex {n}:")
        print(f"  Full hash bits: {bin(X)[2:].zfill(256)}")
        print(f"  Significant hex: {S_hex}")
        print(f"  Expected hex: {expected}")
        print(f"  {'✓' if matches else '❌'} Match status")
        
        current_value = X
    return current_value

def analyze_bit_count(value):
    """Analyze if a value has properties matching the bit pattern requirements"""
    binary = format(value, '028b')
    ones = binary.count('1')
    
    # Check bit count (scaled from 67/256 for 28-bit space)
    if not (6 <= ones <= 9):
        print(f"analyze_bit_count: Value {value} rejected due to bit count {ones}")
        return False
    
    # Check for required patterns
    required_patterns = ['110', '011', '101']
    if not any(pattern in binary for pattern in required_patterns):
        print(f"analyze_bit_count: Value {value} rejected due to missing required patterns")
        return False
    
    # Check leading zeros
    leading_zeros = len(binary) - len(binary.lstrip('0'))
    if leading_zeros < 2 or leading_zeros > 20:
        print(f"analyze_bit_count: Value {value} rejected due to leading zeros {leading_zeros}")
        return False
    
    return True

def apply_transformations(seed):
    """Apply the discovered transformations to generate candidate seeds"""
    candidates = set()
    
    # Right move transformation
    right_move = ((seed + 2) ** 4) ^ 67
    candidates.add(right_move & ((1 << 28) - 1))
    print(f"apply_transformations: Right move transformation of seed {seed} resulted in {right_move & ((1 << 28) - 1)}")
    
    # Down move transformation
    down_move = seed
    for key in [67, 12, 247]:
        down_move = (down_move ^ key) * 2
    candidates.add(down_move & ((1 << 28) - 1))
    print(f"apply_transformations: Down move transformation of seed {seed} resulted in {down_move & ((1 << 28) - 1)}")
    
    # Block-based transformations
    for block in range(5):
        if block % 3 == 0:
            base = ((seed >> 3) | (seed << 29)) & 0xffffffff
        elif block % 3 == 1:
            base = ((seed >> 5) | (seed << 27)) & 0xffffffff
        else:
            base = ((seed >> 7) | (seed << 25)) & 0xffffffff
        
        # Apply position-specific transformations
        transforms = [0x1234, 0x2345, 0x3456, 0x4567]
        for t in transforms:
            candidate = (base * t + block) & ((1 << 28) - 1)
            candidates.add(candidate)
            print(f"apply_transformations: Block-based transformation of seed {seed} with block {block} and transform {t} resulted in {candidate}")
    
    return candidates

def analyze_avalanche_effect(value):
    """Analyze avalanche effect in hash chain"""
    scores = []
    current = value
    for n in range(1, 7):  # Check first 6 indices
        X1, _, _ = chain_next_value(current, n)
        # Flip one bit and compare
        flipped = current ^ 1
        X2, _, _ = chain_next_value(flipped, n)
        # Count differing bits
        diff_bits = bin(X1 ^ X2).count('1')
        scores.append(diff_bits / 256)  # Normalize to [0,1]
        print(f"analyze_avalanche_effect: Value {value} at index {n} has avalanche score {diff_bits / 256}")
        current = X1
    return sum(scores) / len(scores)  # Average avalanche effect

def analyze_entropy(value):
    """Calculate entropy of hash chain values"""
    current = value
    entropies = []
    for n in range(1, 7):
        X, _, _ = chain_next_value(current, n)
        # Convert to bytes and calculate byte frequency
        bytes_str = X.to_bytes(32, byteorder='big')
        freq = {}
        for byte in bytes_str:
            freq[byte] = freq.get(byte, 0) + 1
        # Calculate entropy
        entropy = 0
        for count in freq.values():
            p = count / 32
            entropy -= p * math.log2(p)
        entropies.append(entropy)
        print(f"analyze_entropy: Value {value} at index {n} has entropy {entropy}")
        current = X
    return sum(entropies) / len(entropies)

def find_strong_bit_positions(candidates):
    """Find bit positions that are strongly biased"""
    bit_counts = [0] * 28  # For 28-bit numbers
    total = len(candidates)
    
    for candidate in candidates:
        binary = format(candidate, '028b')
        for i, bit in enumerate(binary):
            if bit == '1':
                bit_counts[i] += 1
    
    # Find strongly biased positions (>80% same value)
    strong_ones = []
    strong_zeros = []
    for i, count in enumerate(bit_counts):
        prob = count / total
        if prob > 0.8:
            strong_ones.append(i)
        elif prob < 0.2:
            strong_zeros.append(i)
    
    print(f"find_strong_bit_positions: Strong ones at positions {strong_ones}, strong zeros at positions {strong_zeros}")
    return strong_ones, strong_zeros

def enhanced_pattern_based_quick_check(seed):
    """Enhanced quick check using advanced pattern analysis"""
    # Check bit count
    if not analyze_bit_count(seed):
        return False
    
    # Check avalanche effect (should be close to 0.5 for good diffusion)
    avalanche = analyze_avalanche_effect(seed)
    if not (0.45 <= avalanche <= 0.55):
        print(f"enhanced_pattern_based_quick_check: Seed {seed} rejected due to avalanche effect {avalanche}")
        return False
    
    # Check entropy (should be high for good randomness)
    entropy = analyze_entropy(seed)
    if entropy < 4.5:  # Typical good entropy for SHA-256
        print(f"enhanced_pattern_based_quick_check: Seed {seed} rejected due to entropy {entropy}")
        return False
    
    # Basic pattern checks
    current = seed
    expected_pattern = [1, 3, 7, 8, 15, 31]
    for n, expected in enumerate(expected_pattern, 1):
        _, S, L = chain_next_value_cached(current, n)
        if S != expected:
            print(f"enhanced_pattern_based_quick_check: Seed {seed} rejected at index {n} with S={S} (expected: {expected})")
            return False
        current = _
    
    # Apply transformations and check candidates
    candidates = apply_transformations(seed)
    strong_ones, strong_zeros = find_strong_bit_positions(candidates)
    
    # Verify candidate bits match strong positions
    seed_binary = format(seed, '028b')
    for pos in strong_ones:
        if seed_binary[pos] != '1':
            print(f"enhanced_pattern_based_quick_check: Seed {seed} rejected due to strong one position {pos}")
            return False
    for pos in strong_zeros:
        if seed_binary[pos] != '0':
            print(f"enhanced_pattern_based_quick_check: Seed {seed} rejected due to strong zero position {pos}")
            return False
    
    return True

def generate_candidate_seeds():
    """Generate candidate seeds using sequence analysis insights"""
    candidates = set()
    
    # Base patterns with known good properties
    base_patterns = [
        0b0000111110111000,  # 1976
        0b0000000001000011,  # 67
        0b0000000000001100,  # 12
        0b0000000011110111   # 247
    ]
    
    # Generate variations of base patterns
    for pattern in base_patterns:
        binary = format(pattern, '028b')
        
        # Generate shifted versions
        for shift in range(24):
            shifted = (pattern << shift) & ((1 << 28) - 1)
            if analyze_bit_count(shifted):
                candidates.add(shifted)
                print(f"generate_candidate_seeds: Shifted version of pattern {pattern} resulted in {shifted}")
        
        # Generate rotated versions
        for rot in range(24):
            rotated = ((pattern << rot) | (pattern >> (28 - rot))) & ((1 << 28) - 1)
            if analyze_bit_count(rotated):
                candidates.add(rotated)
                print(f"generate_candidate_seeds: Rotated version of pattern {pattern} resulted in {rotated}")
        
        # Generate XOR variations
        for key in [67, 12, 247]:
            xored = pattern ^ key
            if analyze_bit_count(xored):
                candidates.add(xored & ((1 << 28) - 1))
                print(f"generate_candidate_seeds: XOR version of pattern {pattern} with key {key} resulted in {xored & ((1 << 28) - 1)}")
    
    # Add polynomial transformations
    base_candidates = candidates.copy()
    for candidate in base_candidates:
        poly = ((candidate + 2) ** 4) & ((1 << 28) - 1)
        if analyze_bit_count(poly):
            candidates.add(poly)
            print(f"generate_candidate_seeds: Polynomial transformation of candidate {candidate} resulted in {poly}")
    
    return sorted(list(candidates))

def optimized_parallel_search(max_index=65, batch_size=1000):
    """Pattern-optimized parallel search with advanced analysis"""
    num_processes = mp.cpu_count()
    print(f"Using {num_processes} CPU cores for optimized search")
    
    # Generate candidates using enhanced pattern analysis
    candidates = set()
    
    # Add candidates based on known patterns
    base_patterns = [
        0b0000111110111000,  # 1976
        0b0000000001000011,  # 67
        0b0000000000001100,  # 12
        0b0000000011110111   # 247
    ]
    
    # Add candidates from bit pattern analysis
    for pattern in base_patterns:
        for shift in range(24):
            candidate = pattern << shift
            if candidate < 2**28:
                # Apply advanced filtering
                if enhanced_pattern_based_quick_check(candidate):
                    candidates.add(candidate)
                    print(f"optimized_parallel_search: Added candidate {candidate} from pattern {pattern} with shift {shift}")
                    # Generate related candidates
                    for related in apply_transformations(candidate):
                        if enhanced_pattern_based_quick_check(related):
                            candidates.add(related)
                            print(f"optimized_parallel_search: Added related candidate {related} from candidate {candidate}")
    
    candidates = sorted(list(candidates))
    print(f"Generated {len(candidates):,} pattern-based candidates")
    
    # Create batches of candidates
    batches = []
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i + batch_size]
        batches.append((batch, max_index))
    
    def process_pattern_batch(args):
        batch, max_index = args
        local_best_seed = None
        local_best_length = 0
        
        for seed in batch:
            # Use pattern-based quick check
            if not enhanced_pattern_based_quick_check(seed):
                continue
                
            current_value = seed
            valid_length = 0
            
            for n in range(1, max_index + 1):
                _, S, L = chain_next_value_cached(current_value, n)
                S_hex = format(S, 'x').zfill(L)
                expected = expected_significant.get(n)
                
                if S_hex.lower() != expected.lower():
                    print(f"process_pattern_batch: Seed {seed} rejected at index {n} with S={S_hex} (expected: {expected})")
                    break
                valid_length = n
                current_value = _
            
            if valid_length > local_best_length:
                local_best_length = valid_length
                local_best_seed = seed
                print(f"process_pattern_batch: New local best seed {seed} with valid length {valid_length}")
        
        return local_best_seed, local_best_length
    
    # Run parallel search
    with mp.Pool(processes=num_processes) as pool:
        results = []
        for i, result in enumerate(pool.imap_unordered(process_pattern_batch, batches)):
            seed, length = result
            if seed is not None:
                results.append((seed, length))
            if i % 10 == 0:
                print(f"Processed {i}/{len(batches)} batches")
                if results:
                    best_so_far = max(results, key=lambda x: x[1])
                    print(f"Current best: Seed {best_so_far[0]:,} (length {best_so_far[1]})")
    
    if results:
        best_seed, best_length = max(results, key=lambda x: x[1])
        return best_seed, best_length
    return None, 0

if __name__ == '__main__':
    print("Starting pattern-optimized search...")
    
    # Run optimized search
    best_seed, best_length = optimized_parallel_search(max_index=65)
    
    if best_seed is not None:
        print(f"\n🎉 Best seed found: {best_seed:,}")
        print(f"Valid length: {best_length}")
        print("\nGenerating chain for verification:")
        generate_chain(best_seed, best_length + 1)
    else:
        print("\n❌ No valid seed found")