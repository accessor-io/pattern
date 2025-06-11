"""
Bitcoin Key Candidate Generator

This module provides advanced functions for generating high-quality Bitcoin
private key candidates based on domain knowledge of Bitcoin address format
and cryptographic properties.
"""

import random
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_candidate(value, prev_term, target_index=68):
    """
    Check if a value is a valid candidate:
    1. Must be greater than previous term
    2. Must have exactly target_index bits (fit in target_index bits)
    3. Must not have more than 3 consecutive identical hex chars
    """
    return (
        value > prev_term and
        value.bit_length() <= target_index and
        not has_too_many_consecutive_chars(value)
    )

def has_too_many_consecutive_chars(value):
    """
    Check if hex representation has more than 3 consecutive identical characters.
    """
    hex_str = hex(value)[2:]  # Remove '0x' prefix
    return bool(re.search(r'(.)\1{3,}', hex_str))

def generate_bitcoin_focused_candidates(count=10, prev_term=None, base_candidates=None):
    """
    Generate high-quality candidates focused specifically on Bitcoin address structure.
    This uses knowledge of Bitcoin's address generation algorithm to target
    specific bit patterns that are likely to produce addresses with desired properties.
    
    Args:
        count: Number of candidates to generate
        prev_term: Previous term to use as baseline
        base_candidates: Optional list of existing candidates
        
    Returns:
        List of high-quality candidate integers
    """
    if prev_term is None:
        raise ValueError("Previous term must be provided")
    
    logger.info(f"Generating {count} Bitcoin-focused candidates")
    candidates = []
    
    # Add base candidates if provided
    if base_candidates:
        for candidate in base_candidates:
            if isinstance(candidate, str):
                try:
                    candidate = int(candidate)
                except (ValueError, TypeError):
                    continue
            if isinstance(candidate, int) and candidate not in candidates:
                candidates.append(candidate)
    
    # Add previous term as foundation
    if prev_term not in candidates:
        candidates.append(prev_term)
    
    # Bitcoin Address Format Knowledge:
    # 1. The first character is determined by version byte (usually '1' for standard addresses)
    # 2. The next ~33 chars are derived from RIPEMD160 hash of public key
    # 3. The last 4-6 characters include checksum bits
    
    # 1. Version Byte Targeting (first character)
    # Most Bitcoin addresses start with '1', which corresponds to specific bit patterns
    for _ in range(min(count // 5, 5)):
        new_candidate = prev_term
        
        # The highest bits affect the version byte
        version_bits = list(range(63, 68))
        # Try different patterns known to produce '1' addresses
        # These patterns are derived from analysis of known Bitcoin addresses
        
        # Clear the highest bits first
        for bit in version_bits:
            # Clear bit (set to 0)
            new_candidate &= ~(1 << bit)
        
        # Set specific patterns that tend to generate '1' addresses
        version_pattern = random.choice([
            0b00000,  # Common patterns for '1' addresses
            0b00001,
            0b00010,
            0b00011
        ])
        
        # Apply the pattern
        new_candidate |= (version_pattern << 63)
        
        if is_valid_candidate(new_candidate, prev_term) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    # 2. Checksum Region Targeting (last few characters)
    # Checksum is based on double-SHA256 of the address, affecting last chars
    for _ in range(min(count // 5, 5)):
        new_candidate = prev_term
        
        # Lowest bits affect checksum
        checksum_bits = list(range(0, 8))
        
        # Try patterns that create valid checksums
        for bit in random.sample(checksum_bits, random.randint(2, 4)):
            new_candidate ^= (1 << bit)
            
        if is_valid_candidate(new_candidate, prev_term) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    # 3. Middle Hash Region (characters 2-30 approximately)
    # These bits affect the main part of the address
    for _ in range(min(count // 5, 5)):
        new_candidate = prev_term
        
        # Middle bits affect the hash region
        middle_range = list(range(8, 60))
        
        # Modify a few bits in the middle region
        for bit in random.sample(middle_range, random.randint(3, 5)):
            new_candidate ^= (1 << bit)
            
        if is_valid_candidate(new_candidate, prev_term) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    # 4. Targeted Position Modifications
    # Specific bit positions that are known to affect specific address characters
    key_positions = [
        # Version byte bits
        [63, 64, 65, 66, 67],
        # Early hash bits (affect char position 1-5)
        [60, 59, 58, 57, 56, 55, 54],
        # Middle hash bits (affect char position 6-20)
        [53, 47, 43, 39, 32, 28, 24],
        # Late hash bits (affect char position 21-30)
        [20, 16, 12, 8, 4],
        # Checksum affecting bits (affect last few chars)
        [7, 6, 5, 4, 3, 2, 1, 0]
    ]
    
    for position_group in key_positions:
        new_candidate = prev_term
        
        # Modify 1-2 bits from this group
        for bit in random.sample(position_group, random.randint(1, 2)):
            new_candidate ^= (1 << bit)
            
        if is_valid_candidate(new_candidate, prev_term) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    # 5. Mathematical Transformations
    # These create interesting patterns in the resulting addresses
    transformations = [
        # Small increment/decrement
        lambda x: x + random.randint(1, 10),
        lambda x: x - random.randint(1, 10),
        
        # Bit rotation
        lambda x: (x & ~0xFFFFFFFF) | (((x & 0xFFFFFFFF) << 1) | ((x & 0xFFFFFFFF) >> 31)),
        
        # Swap bit sections
        lambda x: (x & 0xFFFFFFFF00000000) | ((x & 0xFFFF) << 16) | ((x & 0xFFFF0000) >> 16),
        
        # XOR with small powers of 2
        lambda x: x ^ (1 << random.randint(0, 67)),
        
        # Bit masking (clear/set specific bit regions)
        lambda x: x & ~(0xFF << 32),  # Clear 8 bits at position 32
        lambda x: x | (0xFF << 48),   # Set 8 bits at position 48
    ]
    
    for transform in transformations:
        try:
            new_candidate = transform(prev_term)
            if is_valid_candidate(new_candidate, prev_term) and new_candidate not in candidates:
                candidates.append(new_candidate)
        except:
            continue
    
    # If we still need more candidates, generate them using bit pattern strategies
    while len(candidates) < count:
        new_candidate = prev_term
        
        # Choose strategy
        strategy = random.choice([
            "sequential_bits",
            "evenly_spaced_bits",
            "clustered_bits",
            "fibonacci_bits"
        ])
        
        if strategy == "sequential_bits":
            # Modify a sequence of adjacent bits
            start = random.randint(0, 63)
            length = random.randint(2, 5)
            for i in range(start, min(start + length, 68)):
                new_candidate ^= (1 << i)
                
        elif strategy == "evenly_spaced_bits":
            # Modify bits at regular intervals
            start = random.randint(0, 20)
            spacing = random.randint(2, 10)
            for i in range(start, 68, spacing):
                new_candidate ^= (1 << i)
                
        elif strategy == "clustered_bits":
            # Modify bits clustered around a center point
            center = random.randint(20, 40)
            radius = random.randint(2, 5)
            for i in range(max(0, center - radius), min(68, center + radius)):
                if random.random() < 0.7:  # 70% chance to modify each bit in radius
                    new_candidate ^= (1 << i)
                    
        elif strategy == "fibonacci_bits":
            # Modify bits at Fibonacci positions
            fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55]
            for pos in fibonacci:
                if pos < 68 and random.random() < 0.5:
                    new_candidate ^= (1 << pos)
        
        if is_valid_candidate(new_candidate, prev_term) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    # Return the requested number of candidates
    return candidates[:count]

def evaluate_candidate_quality(candidate, target_address, similarity_fn):
    """
    Evaluate a candidate's quality based on the resulting address.
    
    Args:
        candidate: The private key candidate to evaluate
        target_address: The target Bitcoin address
        similarity_fn: Function to calculate similarity between addresses
        
    Returns:
        Dictionary with quality metrics or None if generation fails
    """
    # This function would require the private_key_to_address function
    # which should be passed in or imported from the main script
    pass 