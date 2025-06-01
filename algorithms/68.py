#!/usr/bin/env python3
"""
This script continuously tries candidate–generation methods for index 68
until it finds a candidate private key whose corresponding Bitcoin address
matches the target address:
    1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ

It cycles through candidate variants, fixed primes, offset shifts, and now also
loops over multiple candidate prime offsets.
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import argparse
import itertools
import random

# -----------------------------
# Configuration and Constants
# -----------------------------

TARGET_INDEX = 68  # Candidate key must be exactly 68 bits.
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Known previous term for index 67.
PREV_TERM_67 = 0x730fc235c1942c1ae

# Adjust modulus to cover full 68-bit space
MODULUS = 1 << 68  # This ensures we can generate all possible 68-bit values

# Use a single prime offset value
PRIME_OFFSET = 0
# List of fixed primes to try.
FIXED_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

# Define the search space
BITS = 68
MIN_VALUE = PREV_TERM_67  # Start from previous term
MAX_VALUE = (1 << BITS) - 1  # Maximum 68-bit value

# Define step sizes for different ranges to cover the full space
STEP_SIZES = [
    # Small steps for fine detail
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    
    # Powers of 2 sequence with offsets
    *[(1 << i) for i in range(4, 67)],  # 2^4 to 2^66
    *[(1 << i) + (1 << (i-2)) for i in range(4, 67)],  # 2^i + 2^(i-2)
    
    # Large prime-based steps
    *[p * (1 << 32) for p in [131071, 524287, 8388607, 536870911]],  # Scaled Mersenne primes
    
    # Mixed steps combining powers
    *[(1 << i) + (1 << j) for i in range(32, 67, 4) for j in range(16, i, 4)],
    
    # Fibonacci-based large steps
    *[fib * (1 << 32) for fib in [6765, 10946, 17711, 28657, 46368, 75025]],
    
    # Hex pattern steps scaled up
    *[0x1234 << i for i in range(16, 64, 4)],
    *[0x12345 << i for i in range(16, 64, 4)],
    *[0x123456 << i for i in range(16, 64, 4)],
    
    # Maximum coverage steps
    *[(MAX_VALUE - (1 << i)) for i in range(0, 67, 4)],  # Steps near MAX_VALUE
    *[(MIN_VALUE + (1 << i)) for i in range(0, 67, 4)],  # Steps near MIN_VALUE
]

# Sort steps and remove duplicates
STEP_SIZES = sorted(list(set(STEP_SIZES)))

# Define base operations for generating candidates
BASE_OPS = {
    'add': lambda x, y: x + y,
    'mul': lambda x, y: x * y,
    'xor': lambda x, y: x ^ y,
    'or': lambda x, y: x | y,
    'and': lambda x, y: x & ((1 << 68) - 1),
    'shift_left': lambda x, y: (x << y) & ((1 << 68) - 1),
    'shift_right': lambda x, y: x >> y,
}

# Define values to combine with operations
BASE_VALUES = [
    # Powers of 2
    *[1 << i for i in range(1, 68)],
    # Prime numbers scaled up
    *[p << 32 for p in [131071, 524287, 8388607]],
    # Fibonacci numbers scaled up
    *[fib << 30 for fib in [6765, 10946, 17711, 28657]],
    # Interesting bit patterns
    *[int('1' * i, 2) for i in range(4, 69, 4)],  # Strings of 1s
    *[int('1' + '0' * i + '1', 2) for i in range(4, 65, 4)],  # 1s with zeros between
]

# Create candidate variants by combining operations and values
CANDIDATE_VARIANTS = []
for op_name, op_func in BASE_OPS.items():
    for val in BASE_VALUES:
        CANDIDATE_VARIANTS.append({
            "name": f"{op_name}_{hex(val)}",
            "type": "operation",
            "op": op_func,
            "value": val,
        })
        # Add compound operations
        for val2 in BASE_VALUES:
            if val2 > val:
                CANDIDATE_VARIANTS.append({
                    "name": f"{op_name}_{hex(val)}_{hex(val2)}",
                    "type": "compound",
                    "op1": op_func,
                    "op2": op_func,
                    "value1": val,
                    "value2": val2,
                })

# Add at the top with other constants
LAST_GENERATED = PREV_TERM_67  # Track the last generated value globally

# Constants from analysis
TERM_67 = 0x730fc235c1942c1ae
BITS = 68
MAX_VALUE = (1 << BITS) - 1

# Expanded growth patterns based on sequence analysis
GROWTH_PATTERNS = {
    'geometric': [
        # Much more geometric ratios
        {'ratio': r} for r in [
            *[1.1**i for i in range(1, 20)],  # Powers of 1.1
            *[1.2**i for i in range(1, 15)],  # Powers of 1.2
            *[1.5**i for i in range(1, 10)],  # Powers of 1.5
            *[2**i for i in range(1, 8)],     # Powers of 2
            1.618033988749895,  # Golden ratio
            2.718281828459045,  # e
            3.141592653589793,  # pi
            *[n/10 for n in range(11, 50)],  # 1.1 to 5.0 in 0.1 steps
        ]
    ],
    'polynomial': [
        # More polynomial combinations
        {'degree': d, 'coeff': c} 
        for d in range(2, 6)  # Degrees 2 through 5
        for c in [
            [1]*d,  # All ones
            [i+1 for i in range(d)],  # Increasing
            [d-i for i in range(d)],  # Decreasing
            [prime for prime in [2,3,5,7,11][:d]]  # Prime coefficients
        ]
    ],
    'bit_patterns': [
        # Comprehensive bit patterns
        {'shift': s, 'pattern': p, 'op': o}
        for s in range(1, 69)  # All possible shifts
        for p in [
            (1 << i) - 1 for i in range(4, 69, 4)  # Sequences of 1s
        ] + [
            (1 << i) | (1 << j)  # Two set bits
            for i in range(0, 68, 4)
            for j in range(i+4, 68, 4)
        ]
        for o in ['xor', 'or', 'and']  # Different bit operations
    ],
    'prime_based': [
        # Prime number patterns
        {'prime': p, 'shift': s, 'combine': c}
        for p in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]
        for s in range(0, 64, 4)  # Shifts by 4 bits
        for c in ['add', 'mul', 'xor']  # Combination methods
    ],
    'fibonacci': [
        # Extended Fibonacci-like sequences
        {'sequence': seq, 'mod': m}
        for seq in [
            [1,1,2,3,5,8,13,21,34,55],
            [2,1,3,4,7,11,18,29,47],
            [3,2,5,7,12,19,31,50],
            [1,2,4,8,16,32,64],
            [1,3,9,27,81],
        ]
        for m in [1, 2, 4, 8, 16]  # Modulus for sequence index
    ],
    'combined': [
        # Direct combined patterns instead of dynamic generation
        {
            'type': 'combined',
            'method': 'geo_prime',
            'ratio': 1.618033988749895,
            'prime_mult': p
        } for p in range(1, 11)
    ] + [
        {
            'type': 'combined',
            'method': 'fib_bit',
            'sequence': [1, 1, 2, 3, 5, 8, 13, 21],
            'shift': s
        } for s in range(4, 65, 4)
    ] + [
        {
            'type': 'combined',
            'method': 'poly_prime',
            'degree': d,
            'prime_mult': p
        } for d in range(2, 6) for p in range(1, 6)
    ] + [
        {
            'type': 'combined',
            'method': 'bit_fib',
            'pattern': (1 << i) - 1,
            'sequence': [1, 2, 4, 8, 16, 32]
        } for i in range(4, 69, 4)
    ]
}

# Add after the existing constants
ESTIMATE_VALUE = 0x12e7b5c4e1c670000

# Constants for 68-bit/17-hex-char values
MAX_68_BIT = (1 << 68) - 1  # 0xffffffffffffffff0
MIN_VALUE = PREV_TERM_67    # 0x730fc235c1942c1ae
MAX_VALUE = MAX_68_BIT

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

def generate_term_candidate(n: int, prev: int, prime: int, prime_offset: int,
                          variant: dict) -> int:
    """
    Generate candidate values ensuring no more than 3 consecutive identical characters
    in hex representation.
    """
    global LAST_GENERATED
    
    # Start from the largest known valid value
    base = max(LAST_GENERATED + 1, TERM_67 + 1)
    
    # Generate initial value based on variant type
    if variant['type'] == 'geometric':
        value = int(base * variant['ratio']) + prime
        
    elif variant['type'] == 'polynomial':
        value = base + (prime << variant['degree'])
        
    elif variant['type'] == 'bit_patterns':
        pattern = (prime << variant['shift']) | (prime << (variant['shift'] + 4))
        value = base ^ pattern
        
    elif variant['type'] == 'prime_based':
        value = base + (prime << variant['shift'])
        
    elif variant['type'] == 'fibonacci':
        seq = variant['sequence']
        idx = prime % len(seq)
        value = base + (seq[idx] << 4)
        
    elif variant['type'] == 'combined':
        if variant['method'] == 'geo_prime':
            value = int(base * variant['ratio']) + (prime << 4)
        elif variant['method'] == 'fib_bit':
            value = base + (variant['sequence'][prime % len(variant['sequence'])] << variant['shift'])
        elif variant['method'] == 'poly_prime':
            value = base + (prime << variant['degree'])
        elif variant['method'] == 'bit_fib':
            value = base ^ variant['pattern']
        else:
            raise ValueError(f"Unknown combined method: {variant['method']}")
    else:
        raise ValueError(f"Unknown variant type: {variant['type']}")
    
    # Ensure exactly 68 bits
    value &= MAX_VALUE
    if value.bit_length() < BITS:
        value |= (1 << (BITS-1))
    
    # Check for consecutive characters and modify if needed
    attempts = 0
    while has_too_many_consecutive_chars(value) and attempts < 10:
        # Modify the value to break consecutive patterns
        if attempts % 3 == 0:
            # XOR with prime pattern
            value ^= (prime << (attempts * 4))
        elif attempts % 3 == 1:
            # Add shifted prime
            value += (prime << (attempts * 4))
        else:
            # Mix bits
            value = ((value << 4) | (value >> 64)) & MAX_VALUE
        
        # Ensure still larger than previous
        if value <= LAST_GENERATED:
            value = LAST_GENERATED + prime + (1 << (attempts * 4))
        
        # Maintain bit length
        value &= MAX_VALUE
        if value.bit_length() < BITS:
            value |= (1 << (BITS-1))
            
        attempts += 1
    
    # Final validation
    if value <= LAST_GENERATED:
        value = LAST_GENERATED + prime + 1
        value &= MAX_VALUE
        value |= (1 << (BITS-1))
    
    LAST_GENERATED = value
    return value

# Create massive variant pool
CANDIDATE_VARIANTS = []
for pattern_type, patterns in GROWTH_PATTERNS.items():
    for pattern in patterns:
        CANDIDATE_VARIANTS.append({
            'name': f"{pattern_type}_{hash(str(pattern))}",
            'type': pattern_type,
            **pattern
        })

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
        ripemd_digest = hashlib.sha256(hashlib.sha256(pubkey).digest()).digest()[:20]
    versioned_payload = b'\x00' + ripemd_digest
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    address = base58.b58encode(versioned_payload + checksum).decode()
    return address

def format_candidate_output(candidate: int) -> str:
    """
    Format the candidate's 68-bit binary representation as:
      { first6bits.next5bits<remaining bits> }
    """
    bin_str = format(candidate, '068b')
    part1 = bin_str[:6]
    part2 = bin_str[6:11]
    part3 = bin_str[11:]
    return f"{{ {part1}.{part2}<{part3}> }}"

# -----------------------------
# Main Continuous Search Loop
# -----------------------------

def continuous_search():
    """
    Systematically explore the 68-bit space, tracking unique candidates and addresses.
    Only generates candidates larger than PREV_TERM_67.
    """
    prev = PREV_TERM_67
    attempt = 0
    seen_candidates = set()
    seen_addresses = set()
    
    # Calculate total combinations to try
    total_combinations = len(CANDIDATE_VARIANTS) * len(FIXED_PRIMES)
    print(f"Total combinations to try: {total_combinations}")
    print(f"Previous term: {hex(prev)} ({prev.bit_length()} bits)")
    
    # Track coverage statistics
    total_candidates = 0
    unique_candidates = 0
    unique_addresses = 0
    
    def print_stats():
        print("\nCoverage Statistics:")
        print(f"Total candidates generated: {total_candidates}")
        print(f"Unique candidates: {unique_candidates} ({unique_candidates/total_candidates*100:.2f}%)")
        print(f"Unique addresses: {unique_addresses}")
        print(f"Current candidate space coverage: {unique_candidates/(1<<68)*100:.8f}%")
    
    try:
        for variant in CANDIDATE_VARIANTS:
            for prime in FIXED_PRIMES:
                attempt += 1
                candidate = generate_term_candidate(
                    TARGET_INDEX, prev, prime, PRIME_OFFSET,
                    variant
                )
                
                total_candidates += 1
                
                # Always show the candidate and its comparison to prev
                print(f"\nCandidate {total_candidates}: {hex(candidate)} ({candidate.bit_length()} bits)")
                print(f"Difference from prev: +{hex(candidate - prev)}")
                print(f"Variant: {variant['name']}, Prime: {prime}")
                
                if candidate <= prev:
                    print("Error: Candidate not larger than previous term - skipping")
                    continue
                
                # Skip if we've seen this candidate before
                if candidate in seen_candidates:
                    print("Duplicate candidate - skipping")
                    continue
                
                seen_candidates.add(candidate)
                unique_candidates += 1
                
                if candidate.bit_length() != TARGET_INDEX:
                    print(f"Wrong bit length ({candidate.bit_length()}) - skipping")
                    continue
                
                try:
                    addr = private_key_to_address(candidate)
                    if addr not in seen_addresses:
                        seen_addresses.add(addr)
                        unique_addresses += 1
                        print(f"Address: {addr} (new)")
                    else:
                        print(f"Address: {addr} (duplicate)")
                    
                    if addr == TARGET_ADDRESS:
                        print("\n>>> MATCH FOUND! <<<")
                        print(f"Attempt: {attempt}")
                        print(f"Variant: {variant['name']}, Prime: {prime}")
                        print(f"Candidate (hex): {hex(candidate)}")
                        print(f"Formatted Candidate: {format_candidate_output(candidate)}")
                        print(f"Bitcoin Address: {addr}")
                        print_stats()
                        return candidate
                
                except Exception as e:
                    print(f"Error generating address: {e}")
                    continue
                
                if total_candidates % 100 == 0:
                    print_stats()
    
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
        print_stats()
        return None
    
    print("\nNo match found after trying all combinations.")
    print_stats()
    return None

def explore_around_estimate(estimate: int, range_bits: int = 8) -> None:
    """
    Explore values around the estimated candidate, focusing on 17-character hex values.
    """
    print(f"\nExploring around estimate: {hex(estimate)}")
    print(f"Bit length: {estimate.bit_length()} bits")
    print(f"Valid range:")
    print(f"  Min: {hex(MIN_VALUE)} ({len(hex(MIN_VALUE)[2:])} chars)")
    print(f"  Max: {hex(MAX_VALUE)} ({len(hex(MAX_VALUE)[2:])} chars)")
    
    seen_addresses = set()
    total_tested = 0
    
    # Generate variations that maintain 17 hex characters
    variations = []
    
    # 1. Modify each hex position
    hex_str = hex(estimate)[2:].zfill(17)  # Ensure 17 chars
    for pos in range(17):
        current_digit = int(hex_str[pos], 16)
        for new_digit in range(16):
            if new_digit != current_digit:
                # Calculate position value
                power = 16 ** (16 - pos)  # 17 chars, 0-based index
                diff = (new_digit - current_digit) * power
                new_val = estimate + diff
                if len(hex(new_val)[2:]) == 17:  # Ensure still 17 chars
                    variations.append(new_val)
    
    # 2. Small variations that maintain 17 chars
    for i in range(-0x1000, 0x1000):
        new_val = estimate + i
        if len(hex(new_val)[2:]) == 17:
            variations.append(new_val)
    
    # 3. Bit flips that maintain 17 chars
    for i in range(64, 68):  # Focus on high bits
        new_val = estimate ^ (1 << i)
        if len(hex(new_val)[2:]) == 17:
            variations.append(new_val)
    
    # 4. Pattern-based variations
    patterns = [
        0xF0F0F0F0,
        0x0F0F0F0F,
        0xFF00FF00,
        0x00FF00FF
    ]
    for pattern in patterns:
        for shift in range(0, 32, 4):
            new_val = estimate ^ (pattern << shift)
            if len(hex(new_val)[2:]) == 17:
                variations.append(new_val)
    
    # Remove duplicates and sort
    variations = sorted(set(variations))
    
    # Test each variation
    for candidate in variations:
        # Validate candidate
        if not (MIN_VALUE < candidate <= MAX_VALUE):
            continue
        if candidate.bit_length() != TARGET_INDEX:
            continue
        if has_too_many_consecutive_chars(candidate):
            continue
            
        total_tested += 1
        
        try:
            addr = private_key_to_address(candidate)
            if addr not in seen_addresses:
                seen_addresses.add(addr)
                print(f"\nTesting: {hex(candidate)} ({len(hex(candidate)[2:])} chars)")
                print(f"Difference from estimate: {hex(candidate - estimate)}")
                print(f"Address: {addr}")
                
                if addr == TARGET_ADDRESS:
                    print("\n>>> MATCH FOUND! <<<")
                    print(f"Candidate (hex): {hex(candidate)}")
                    print(f"Formatted: {format_candidate_output(candidate)}")
                    return candidate
                    
        except Exception as e:
            continue
            
        if total_tested % 1000 == 0:
            print(f"\nTested {total_tested} variations")
            print(f"Unique addresses found: {len(seen_addresses)}")
            print(f"Current candidate: {hex(candidate)} ({len(hex(candidate)[2:])} chars)")
    
    print(f"\nCompleted testing {total_tested} variations")
    print(f"Total unique addresses: {len(seen_addresses)}")
    return None

def targeted_position_search(best_candidate, target_address="1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"):
    """
    Advanced search that preserves matching positions between best candidates and target address.
    Focuses on systematically exploring combinations that only affect mismatched positions.
    
    Args:
        best_candidate: The private key that produced the highest similarity address
        target_address: The target Bitcoin address to match (default: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ)
    """
    print(f"\nStarting targeted position search with best candidate: {hex(best_candidate)}")
    
    # Calculate the best address we've found so far
    best_address = private_key_to_address(best_candidate)
    print(f"Best address so far: {best_address}")
    print(f"Target address:      {target_address}")
    
    # Identify matching positions between best and target address
    match_indices = []
    for i, (c1, c2) in enumerate(zip(best_address, target_address)):
        if c1 == c2:
            match_indices.append(i)
    
    matching_chars = ''.join([best_address[i] for i in match_indices])
    print(f"Matching positions: {match_indices}")
    print(f"Matching characters: {matching_chars}")
    
    # Store results of the bit influence testing
    bit_influence_map = {}
    
    # Phase 1: Build a map of which bits in the private key affect which positions in the address
    print("\nBuilding bit influence map...")
    for bit_pos in range(68):  # Assuming a 68-bit private key
        # Flip this bit in the best candidate
        test_candidate = best_candidate ^ (1 << bit_pos)
        test_address = private_key_to_address(test_candidate)
        
        # Find which positions changed in the address
        affected_positions = []
        for i, (orig, test) in enumerate(zip(best_address, test_address)):
            if orig != test:
                affected_positions.append(i)
        
        bit_influence_map[bit_pos] = affected_positions
        
        # Log progress for every 10 bits tested
        if bit_pos % 10 == 0:
            print(f"Tested bit position {bit_pos}/68")
    
    # Phase 2: Identify which bits we can safely modify (those that don't affect matching positions)
    safe_bits_to_modify = []
    for bit_pos, affected_pos in bit_influence_map.items():
        # If this bit doesn't affect any matching positions, it's safe to modify
        if not any(pos in match_indices for pos in affected_pos):
            safe_bits_to_modify.append(bit_pos)
    
    print(f"\nIdentified {len(safe_bits_to_modify)} safe bits to modify that don't affect matching positions")
    
    # Phase 3: Generate candidates by exploring combinations of safe bit modifications
    # Start with 1-bit changes, then 2-bit, etc.
    max_bits_to_combine = min(15, len(safe_bits_to_modify))  # Limit combinations to avoid explosion
    
    total_candidates_tested = 0
    best_similarity = address_similarity(best_address, target_address)
    
    print("\nGenerating and testing candidates...")
    
    # For very few bits, we can use combinations
    if len(safe_bits_to_modify) <= 20:
        for num_bits in range(1, max_bits_to_combine + 1):
            print(f"Testing {num_bits}-bit combinations...")
            
            # Generate all combinations of bits to flip
            for bit_combination in itertools.combinations(safe_bits_to_modify, num_bits):
                # Start with best candidate and flip the selected bits
                new_candidate = best_candidate
                for bit_pos in bit_combination:
                    new_candidate ^= (1 << bit_pos)
                
                # Test this candidate
                new_address = private_key_to_address(new_candidate)
                similarity = address_similarity(new_address, target_address)
                total_candidates_tested += 1
                
                # Check if we've found a better candidate or the exact match
                if new_address == target_address:
                    print(f"\n!!! MATCH FOUND !!! Private key: {hex(new_candidate)}")
                    return new_candidate
                elif similarity > best_similarity:
                    best_similarity = similarity
                    print(f"New best similarity: {best_similarity:.6f} with {hex(new_candidate)}")
                    best_candidate = new_candidate
                    best_address = new_address
                
                # Log progress for every 1000 candidates tested
                if total_candidates_tested % 1000 == 0:
                    print(f"Tested {total_candidates_tested} candidates, best similarity: {best_similarity:.6f}")
    else:
        # For many bits, use random sampling
        print("Too many bits to test all combinations. Using random sampling...")
        
        for num_bits in range(1, max_bits_to_combine + 1):
            print(f"Testing random {num_bits}-bit combinations...")
            
            # Test 1000 random combinations for each bit count
            for _ in range(1000):
                # Select random bits to flip
                bit_combination = random.sample(safe_bits_to_modify, num_bits)
                
                # Start with best candidate and flip the selected bits
                new_candidate = best_candidate
                for bit_pos in bit_combination:
                    new_candidate ^= (1 << bit_pos)
                
                # Test this candidate
                new_address = private_key_to_address(new_candidate)
                similarity = address_similarity(new_address, target_address)
                total_candidates_tested += 1
                
                # Check if we've found a better candidate or the exact match
                if new_address == target_address:
                    print(f"\n!!! MATCH FOUND !!! Private key: {hex(new_candidate)}")
                    return new_candidate
                elif similarity > best_similarity:
                    best_similarity = similarity
                    print(f"New best similarity: {best_similarity:.6f} with {hex(new_candidate)}")
                    best_candidate = new_candidate
                    best_address = new_address
                
                # Log progress for every 100 candidates tested
                if total_candidates_tested % 100 == 0:
                    print(f"Tested {total_candidates_tested} candidates, best similarity: {best_similarity:.6f}")
    
    # Phase 4: If no exact match found, try targeted bit patterns based on Bitcoin address structure
    print("\nTrying targeted bit patterns based on Bitcoin address structure...")
    
    # Focus on bits that influence the positions right after matching positions
    target_positions = []
    for i in range(len(target_address)):
        if i not in match_indices and (i-1 in match_indices or i+1 in match_indices):
            target_positions.append(i)
    
    print(f"Targeting positions next to matching ones: {target_positions}")
    
    # Find bits that influence these target positions
    target_bit_positions = set()
    for bit_pos, affected_pos in bit_influence_map.items():
        if any(pos in target_positions for pos in affected_pos):
            target_bit_positions.add(bit_pos)
    
    # Try combinations of these target bits
    max_target_bits = min(12, len(target_bit_positions))
    for num_bits in range(1, max_target_bits + 1):
        print(f"Testing {num_bits}-bit combinations of targeted bits...")
        
        if len(target_bit_positions) > 15:
            # Use random sampling for larger sets
            for _ in range(2000):
                bit_combination = random.sample(list(target_bit_positions), num_bits)
                
                # Start with best candidate and flip the selected bits
                new_candidate = best_candidate
                for bit_pos in bit_combination:
                    new_candidate ^= (1 << bit_pos)
                
                # Test this candidate
                new_address = private_key_to_address(new_candidate)
                similarity = address_similarity(new_address, target_address)
                total_candidates_tested += 1
                
                # Check results
                if new_address == target_address:
                    print(f"\n!!! MATCH FOUND !!! Private key: {hex(new_candidate)}")
                    return new_candidate
                elif similarity > best_similarity:
                    best_similarity = similarity
                    print(f"New best similarity: {best_similarity:.6f} with {hex(new_candidate)}")
                    best_candidate = new_candidate
                    best_address = new_address
        else:
            # Use combinations for smaller sets
            for bit_combination in itertools.combinations(target_bit_positions, num_bits):
                # Start with best candidate and flip the selected bits
                new_candidate = best_candidate
                for bit_pos in bit_combination:
                    new_candidate ^= (1 << bit_pos)
                
                # Test this candidate
                new_address = private_key_to_address(new_candidate)
                similarity = address_similarity(new_address, target_address)
                total_candidates_tested += 1
                
                # Check results
                if new_address == target_address:
                    print(f"\n!!! MATCH FOUND !!! Private key: {hex(new_candidate)}")
                    return new_candidate
                elif similarity > best_similarity:
                    best_similarity = similarity
                    print(f"New best similarity: {best_similarity:.6f} with {hex(new_candidate)}")
                    best_candidate = new_candidate
                    best_address = new_address
    
    print(f"\nCompleted targeted position search. Best similarity: {best_similarity:.6f}")
    print(f"Best candidate: {hex(best_candidate)}")
    print(f"Best address: {private_key_to_address(best_candidate)}")
    
    return best_candidate

# Add a new function to specifically analyze character correlations in the Bitcoin address
def analyze_address_character_correlations(target_address="1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"):
    """
    Analyze character correlations in Bitcoin addresses to understand patterns.
    This can help guide the bit manipulation strategy.
    """
    print(f"\nAnalyzing character correlations for target address: {target_address}")
    
    # We'll generate many candidates and analyze which private key patterns
    # tend to produce specific characters in the address
    total_samples = 10000
    char_position_data = {pos: {} for pos in range(len(target_address))}
    
    # Generate random 68-bit private keys
    for _ in range(total_samples):
        # Generate a random 68-bit key
        private_key = random.getrandbits(68)
        
        # Ensure it's exactly 68 bits
        mask = (1 << 68) - 1
        private_key &= mask
        
        # Generate the address
        address = private_key_to_address(private_key)
        
        # For each position, record the relationship between key bits and address chars
        for pos in range(min(len(address), len(target_address))):
            char = address[pos]
            if char not in char_position_data[pos]:
                char_position_data[pos][char] = []
            
            # Store the high-order bits of the private key (most significant 16 bits)
            high_bits = (private_key >> 52) & 0xFFFF
            char_position_data[pos][char].append(high_bits)
    
    # Analyze the data to find patterns
    position_insights = {}
    for pos in range(len(target_address)):
        target_char = target_address[pos]
        print(f"\nPosition {pos}, Target Character: {target_char}")
        
        if target_char in char_position_data[pos]:
            samples = char_position_data[pos][target_char]
            
            # Calculate frequency of this character at this position
            frequency = len(samples) / total_samples
            print(f"  Frequency: {frequency:.4f} ({len(samples)}/{total_samples})")
            
            # Analyze bit patterns in keys that produce this character
            if samples:
                # Check if certain bit patterns are common
                bit_counts = [0] * 16  # For the 16 high-order bits
                for key_bits in samples:
                    for bit_pos in range(16):
                        if key_bits & (1 << bit_pos):
                            bit_counts[bit_pos] += 1
                
                # Calculate bit probabilities
                bit_probs = [count / len(samples) for count in bit_counts]
                
                # Find bits with strong bias (far from 0.5)
                strong_bits = []
                for bit_pos, prob in enumerate(bit_probs):
                    bias = abs(prob - 0.5)
                    if bias > 0.1:  # Threshold for "strong" bias
                        strong_bits.append((bit_pos, prob))
                
                print(f"  Strongly biased bits: {strong_bits}")
                position_insights[pos] = {
                    'target_char': target_char,
                    'frequency': frequency,
                    'strong_bits': strong_bits
                }
            else:
                print("  No samples found for this character at this position")
        else:
            print("  No samples found for this character at this position")
    
    # Generate candidate patterns based on the analysis
    if position_insights:
        print("\nGenerating candidate patterns based on analysis:")
        
        # Create a template for the high-order bits based on the analysis
        template = 0
        mask = 0
        
        for pos, insights in position_insights.items():
            if 'strong_bits' in insights and insights['strong_bits']:
                for bit_pos, prob in insights['strong_bits']:
                    # Only set bits with very strong bias
                    if abs(prob - 0.5) > 0.2:
                        # Set this bit in the template according to its bias
                        if prob > 0.5:  # More likely to be 1
                            template |= (1 << (bit_pos + 52))  # Adjust for position in 68-bit key
                        # Note: if prob < 0.5, leave as 0
                        
                        # Set this bit in the mask
                        mask |= (1 << (bit_pos + 52))
        
        if mask:
            print(f"Bit template: {bin(template)[2:].zfill(68)}")
            print(f"Bit mask:     {bin(mask)[2:].zfill(68)}")
            
            # Generate 1000 candidates using this template
            candidates = []
            for _ in range(1000):
                # Start with the template
                candidate = template
                
                # Randomize non-masked bits
                for i in range(68):
                    if not (mask & (1 << i)):
                        if random.random() > 0.5:
                            candidate |= (1 << i)
                        else:
                            candidate &= ~(1 << i)
                
                candidates.append(candidate)
            
            # Test these candidates
            print("\nTesting generated candidates:")
            best_candidate = None
            best_similarity = 0
            
            for i, candidate in enumerate(candidates):
                address = private_key_to_address(candidate)
                similarity = address_similarity(address, target_address)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_candidate = candidate
                    print(f"New best similarity: {best_similarity:.6f} with {hex(candidate)}")
                    
                if i % 100 == 0:
                    print(f"Tested {i+1}/{len(candidates)} candidates")
            
            if best_candidate:
                print(f"\nBest candidate from character analysis: {hex(best_candidate)}")
                print(f"Best similarity: {best_similarity:.6f}")
                print(f"Address: {private_key_to_address(best_candidate)}")
                
                return best_candidate
    
    return None

def find_exact_address(target_address="1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"):
    """
    Comprehensive approach that combines multiple strategies to find the exact target address.
    """
    print(f"\n=== Launching comprehensive search for target address: {target_address} ===\n")
    
    # Step 1: Start with our best candidates
    best_candidates = [
        0x7940bc5919ad6e5f8,  # Produced 1MVcqyF7EnsNMBBiJSWkyK62zaYdtpZ3Yx (0.270000)
        0x7940be591d2d6edf8,  # Produced 1M57YfYarMvEKwFLGfUjVLBK3vp2hAZRvf (0.270000)
        0x970fddd8161fd29d0   # Produced 1MJeofVuSJ4Jhp6xCEifnGYp1VByCUXYQn (0.190588)
    ]
    
    # Try character correlation analysis first
    print("\nRunning character correlation analysis...")
    best_char_candidate = analyze_address_character_correlations(target_address)
    if best_char_candidate:
        best_candidates.append(best_char_candidate)
    
    # Step 2: Try targeted position search with each candidate
    best_overall_candidate = None
    best_overall_similarity = 0
    
    for candidate in best_candidates:
        print(f"\nTrying targeted position search with candidate: {hex(candidate)}")
        best_candidate = targeted_position_search(candidate, target_address)
        
        # Check if this produced a better result
        address = private_key_to_address(best_candidate)
        similarity = address_similarity(address, target_address)
        
        if similarity > best_overall_similarity:
            best_overall_similarity = similarity
            best_overall_candidate = best_candidate
        
        # If we found an exact match, return immediately
        if address == target_address:
            print(f"\n!!! EXACT MATCH FOUND !!! Private key: {hex(best_candidate)}")
            return best_candidate
    
    # If no exact match, return the best candidate we found
    print(f"\nBest candidate found: {hex(best_overall_candidate)}")
    print(f"Best similarity: {best_overall_similarity:.6f}")
    print(f"Address: {private_key_to_address(best_overall_candidate)}")
    
    return best_overall_candidate

# -----------------------------
# Main Execution
# -----------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bitcoin private key search for term 68")
    parser.add_argument("--find-exact", action="store_true", help="Run comprehensive search for exact address")
    parser.add_argument("--targeted-search", action="store_true", help="Run targeted position search")
    args = parser.parse_args()
    
    if args.find_exact:
        result = find_exact_address()
        if result:
            print(f"Found result: {hex(result)}")
            print(f"Address: {private_key_to_address(result)}")
    elif args.targeted_search:
        # Use our best candidate as starting point
        best_candidate = 0x7940bc5919ad6e5f8  # Change to your best candidate
        result = targeted_position_search(best_candidate)
        if result:
            print(f"Found result: {hex(result)}")
            print(f"Address: {private_key_to_address(result)}")
    else:
        continuous_search()
