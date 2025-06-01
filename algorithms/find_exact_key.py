#!/usr/bin/python3

import hashlib
import base58
import random
import itertools
import time
import logging
from collections import Counter
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("exact_key_search.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()

# Target information
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"
PREV_TERM_67 = 0x730fc235c1942c1ae
# Best candidates found so far
BEST_CANDIDATES = [
    0x7940bc5919ad6e5f8,  # Produced 1MVcqyF7EnsNMBBiJSWkyK62zaYdtpZ3Yx (0.270000)
    0x7940be591d2d6edf8,  # Produced 1M57YfYarMvEKwFLGfUjVLBK3vp2hAZRvf (0.270000)
    0x970fddd8161fd29d0   # Produced 1MJeofVuSJ4Jhp6xCEifnGYp1VByCUXYQn (0.190588)
]

# Constants for candidate generation
MIN_VALUE = PREV_TERM_67
MAX_VALUE = (1 << 68) - 1  # Maximum 68-bit value

def private_key_to_address(private_key: int) -> str:
    """Convert a private key integer to a Bitcoin address."""
    # Ensure the key is properly formatted (68 bits)
    private_key &= MAX_VALUE
    
    # Convert to bytes with proper encoding (big-endian)
    key_bytes = private_key.to_bytes(34, byteorder='big')
    
    # Calculate SHA-256 hash
    sha256_hash = hashlib.sha256(key_bytes).digest()
    
    # Calculate RIPEMD-160 hash
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    
    # Add version byte (0x00 for mainnet)
    versioned_hash = b'\x00' + ripemd160_hash
    
    # Calculate checksum (first 4 bytes of double SHA-256)
    checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
    
    # Combine versioned hash and checksum
    binary_address = versioned_hash + checksum
    
    # Convert to Base58
    address = base58.b58encode(binary_address).decode('utf-8')
    
    return address

def address_similarity(addr1, addr2):
    """
    Compute similarity between two Bitcoin addresses
    Higher score = more similar (max 1.0)
    
    Enhanced to better capture meaningful patterns
    """
    # If addresses are exactly the same (match found)
    if addr1 == addr2:
        return 1.0
    
    # Get similarity based on exact character matches at each position
    common_prefix = 0
    for i in range(min(len(addr1), len(addr2))):
        if addr1[i] == addr2[i]:
            common_prefix += 1
        else:
            break
    
    # Calculate prefix-based similarity (heavily weight prefix matches)
    prefix_similarity = common_prefix / max(len(addr1), len(addr2))
    
    # Enhanced positional matching - give more weight to matches at key positions
    # First 4 characters are critical in Bitcoin addresses
    positional_matches = 0
    positional_weights = []
    
    # Create position weights that emphasize the beginning of the address
    for i in range(min(len(addr1), len(addr2))):
        if i < 5:  # First 5 characters are most important
            weight = 2.0
        elif 5 <= i < 10:  # Next 5 are important too
            weight = 1.5
        else:  # Rest have normal weight
            weight = 1.0
        positional_weights.append(weight)
    
    # Calculate weighted positional match score
    weighted_match_score = 0
    total_weight = sum(positional_weights)
    
    for i, (c1, c2) in enumerate(zip(addr1, addr2)):
        if c1 == c2:
            weighted_match_score += positional_weights[i]
    
    positional_similarity = weighted_match_score / total_weight
    
    # Calculate character-based similarity
    matching_chars = sum(1 for a, b in zip(addr1, addr2) if a == b)
    char_similarity = matching_chars / max(len(addr1), len(addr2))
    
    # Count character frequency similarity
    addr1_freq = Counter(addr1)
    addr2_freq = Counter(addr2)
    total_chars = sum(addr1_freq.values())
    
    freq_similarity = 0
    for c in set(addr1_freq.keys()).union(addr2_freq.keys()):
        freq1 = addr1_freq.get(c, 0) / total_chars
        freq2 = addr2_freq.get(c, 0) / total_chars
        freq_similarity += min(freq1, freq2)
    
    # Weight the similarity components with increased emphasis on positional similarity
    similarity = (0.4 * prefix_similarity) + (0.4 * positional_similarity) + (0.15 * char_similarity) + (0.05 * freq_similarity)
    
    # Scale similarity to ensure higher values
    scaled_similarity = similarity * 2.0
    
    # Ensure max value is 1.0
    return min(1.0, scaled_similarity)

def save_result(key_value):
    """Save the found key to both a JSON file and a text file."""
    if key_value is None:
        return
        
    hex_value = hex(key_value)
    address = private_key_to_address(key_value)
    
    # Save as text
    with open("term68_solution.txt", "w") as f:
        f.write(f"Bitcoin Private Key (Term 68):\n")
        f.write(f"Decimal: {key_value}\n")
        f.write(f"Hex: {hex_value}\n")
        f.write(f"Bit Length: {key_value.bit_length()}\n")
        f.write(f"Address: {address}\n")
    
    logger.info(f"Result saved to term68_solution.txt")
    logger.info(f"Found matching private key: {hex_value}")
    logger.info(f"Address: {address}")

def build_influence_map(candidate, target_address=TARGET_ADDRESS):
    """
    Build a map showing which bits in the private key affect which positions in the address.
    
    Returns:
        dict: Mapping of bit positions to lists of affected address character positions
    """
    logger.info("Building bit influence map...")
    
    # Get the original address for this candidate
    orig_address = private_key_to_address(candidate)
    
    influence_map = {}
    for bit_pos in range(68):  # For a 68-bit key
        # Flip this bit
        modified = candidate ^ (1 << bit_pos)
        mod_address = private_key_to_address(modified)
        
        # Find which address positions were affected
        affected_positions = []
        for i, (orig_char, mod_char) in enumerate(zip(orig_address, mod_address)):
            if orig_char != mod_char:
                affected_positions.append(i)
        
        influence_map[bit_pos] = affected_positions
        
        # Log progress
        if bit_pos % 10 == 0:
            logger.info(f"Analyzed bit position {bit_pos}/68")
    
    # Show a summary of the influence map
    influence_density = {}
    for pos in range(len(target_address)):
        affecting_bits = []
        for bit_pos, affected in influence_map.items():
            if pos in affected:
                affecting_bits.append(bit_pos)
        influence_density[pos] = affecting_bits
        logger.info(f"Address position {pos} ('{target_address[pos]}') is affected by {len(affecting_bits)} bits")
    
    return influence_map, influence_density

def targeted_search(candidate):
    """
    Execute a highly targeted search based on preserving matching positions.
    """
    start_time = time.time()
    
    # Get the address for this candidate
    address = private_key_to_address(candidate)
    original_similarity = address_similarity(address, TARGET_ADDRESS)
    
    logger.info(f"Starting targeted search with candidate: {hex(candidate)}")
    logger.info(f"Current address: {address}")
    logger.info(f"Target address:  {TARGET_ADDRESS}")
    logger.info(f"Current similarity: {original_similarity:.6f}")
    
    # Find matching positions
    matching_positions = []
    for i, (a, b) in enumerate(zip(address, TARGET_ADDRESS)):
        if a == b:
            matching_positions.append(i)
            
    logger.info(f"Matching positions: {matching_positions}")
    logger.info(f"Matching characters: {''.join([address[i] for i in matching_positions])}")
    
    # Build the influence map
    influence_map, influence_density = build_influence_map(candidate)
    
    # Find bits that affect matching positions
    matching_bits = set()
    for pos in matching_positions:
        for bit_pos, affected in influence_map.items():
            if pos in affected:
                matching_bits.add(bit_pos)
    
    logger.info(f"Found {len(matching_bits)} bits that affect matching positions")
    
    # Find bits that don't affect matching positions
    safe_bits = set(range(68)) - matching_bits
    logger.info(f"Found {len(safe_bits)} bits that can be safely modified")
    
    # Try combinations of bit flips, starting with fewer bits
    max_bits = min(15, len(safe_bits))  # Limit for computational feasibility
    
    total_tested = 0
    best_candidate = candidate
    best_similarity = original_similarity
    best_address = address
    
    safe_bits_list = sorted(list(safe_bits))
    
    # For small numbers of bits, try all combinations
    if len(safe_bits_list) <= 23:  # Feasible for full combinations
        for num_bits in range(1, max_bits + 1):
            logger.info(f"Testing all {num_bits}-bit combinations...")
            
            for bit_combo in itertools.combinations(safe_bits_list, num_bits):
                # Apply the bit flips
                new_candidate = candidate
                for bit in bit_combo:
                    new_candidate ^= (1 << bit)
                
                # Test this candidate
                new_address = private_key_to_address(new_candidate)
                total_tested += 1
                
                # Check for exact match
                if new_address == TARGET_ADDRESS:
                    logger.info(f"EXACT MATCH FOUND! Key: {hex(new_candidate)}")
                    save_result(new_candidate)
                    return new_candidate
                
                # Calculate similarity
                similarity = address_similarity(new_address, TARGET_ADDRESS)
                
                # Check if this is better
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_candidate = new_candidate
                    best_address = new_address
                    logger.info(f"New best: {best_similarity:.6f} with {hex(best_candidate)}")
                    logger.info(f"Address: {best_address}")
                
                # Log progress
                if total_tested % 1000 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"Tested {total_tested} candidates in {elapsed:.2f}s")
    else:
        # Use random sampling for larger bit sets
        for num_bits in range(1, max_bits + 1):
            logger.info(f"Randomly sampling {num_bits}-bit combinations...")
            
            # Try 5000 random combinations for each bit count
            for _ in range(5000):
                # Select random bits to flip
                bit_combo = random.sample(safe_bits_list, num_bits)
                
                # Apply the bit flips
                new_candidate = candidate
                for bit in bit_combo:
                    new_candidate ^= (1 << bit)
                
                # Test this candidate
                new_address = private_key_to_address(new_candidate)
                total_tested += 1
                
                # Check for exact match
                if new_address == TARGET_ADDRESS:
                    logger.info(f"EXACT MATCH FOUND! Key: {hex(new_candidate)}")
                    save_result(new_candidate)
                    return new_candidate
                
                # Calculate similarity
                similarity = address_similarity(new_address, TARGET_ADDRESS)
                
                # Check if this is better
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_candidate = new_candidate
                    best_address = new_address
                    logger.info(f"New best: {best_similarity:.6f} with {hex(best_candidate)}")
                    logger.info(f"Address: {best_address}")
                
                # Log progress
                if total_tested % 1000 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"Tested {total_tested} candidates in {elapsed:.2f}s")
    
    # After exhaustive testing, try more advanced methods
    
    # Try targeting "adjacent" bits - bits that affect positions next to matching positions
    logger.info("Targeting bits affecting positions adjacent to matching positions...")
    
    # Find position pairs where one matches and one doesn't
    adjacent_positions = []
    for i in range(len(TARGET_ADDRESS) - 1):
        if i in matching_positions and i+1 not in matching_positions:
            adjacent_positions.append(i+1)
        elif i not in matching_positions and i+1 in matching_positions:
            adjacent_positions.append(i)
    
    logger.info(f"Found {len(adjacent_positions)} positions adjacent to matches")
    
    # Find bits that affect these adjacent positions
    adjacent_bits = set()
    for pos in adjacent_positions:
        for bit_pos, affected in influence_map.items():
            if pos in affected and bit_pos not in matching_bits:
                adjacent_bits.add(bit_pos)
    
    logger.info(f"Found {len(adjacent_bits)} bits that affect adjacent positions")
    
    # Try combinations of these adjacent bits
    adjacent_bits_list = sorted(list(adjacent_bits))
    max_adj_bits = min(12, len(adjacent_bits_list))
    
    for num_bits in range(1, max_adj_bits + 1):
        logger.info(f"Testing combinations of {num_bits} adjacent-affecting bits...")
        
        # Use random sampling if there are too many combinations
        if len(adjacent_bits_list) > 15:
            for _ in range(3000):
                # Select random bits to flip
                bit_combo = random.sample(adjacent_bits_list, num_bits)
                
                # Apply the bit flips
                new_candidate = best_candidate  # Start from our current best
                for bit in bit_combo:
                    new_candidate ^= (1 << bit)
                
                # Test this candidate
                new_address = private_key_to_address(new_candidate)
                total_tested += 1
                
                # Check for exact match
                if new_address == TARGET_ADDRESS:
                    logger.info(f"EXACT MATCH FOUND! Key: {hex(new_candidate)}")
                    save_result(new_candidate)
                    return new_candidate
                
                # Calculate similarity
                similarity = address_similarity(new_address, TARGET_ADDRESS)
                
                # Check if this is better
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_candidate = new_candidate
                    best_address = new_address
                    logger.info(f"New best: {best_similarity:.6f} with {hex(best_candidate)}")
                    logger.info(f"Address: {best_address}")
        else:
            for bit_combo in itertools.combinations(adjacent_bits_list, num_bits):
                # Apply the bit flips
                new_candidate = best_candidate  # Start from our current best
                for bit in bit_combo:
                    new_candidate ^= (1 << bit)
                
                # Test this candidate
                new_address = private_key_to_address(new_candidate)
                total_tested += 1
                
                # Check for exact match
                if new_address == TARGET_ADDRESS:
                    logger.info(f"EXACT MATCH FOUND! Key: {hex(new_candidate)}")
                    save_result(new_candidate)
                    return new_candidate
                
                # Calculate similarity
                similarity = address_similarity(new_address, TARGET_ADDRESS)
                
                # Check if this is better
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_candidate = new_candidate
                    best_address = new_address
                    logger.info(f"New best: {best_similarity:.6f} with {hex(best_candidate)}")
                    logger.info(f"Address: {best_address}")
    
    # Final pass: try guided random walks from our best candidate
    logger.info("Performing guided random walks from best candidate...")
    
    for _ in range(10000):
        # Start from our best candidate
        new_candidate = best_candidate
        
        # Flip 1-5 random bits that don't affect matching positions
        num_bits = random.randint(1, 5)
        bits_to_flip = random.sample(safe_bits_list, num_bits)
        
        for bit in bits_to_flip:
            new_candidate ^= (1 << bit)
        
        # Test this candidate
        new_address = private_key_to_address(new_candidate)
        total_tested += 1
        
        # Check for exact match
        if new_address == TARGET_ADDRESS:
            logger.info(f"EXACT MATCH FOUND! Key: {hex(new_candidate)}")
            save_result(new_candidate)
            return new_candidate
        
        # Calculate similarity
        similarity = address_similarity(new_address, TARGET_ADDRESS)
        
        # Check if this is better
        if similarity > best_similarity:
            best_similarity = similarity
            best_candidate = new_candidate
            best_address = new_address
            logger.info(f"New best: {best_similarity:.6f} with {hex(best_candidate)}")
            logger.info(f"Address: {best_address}")
    
    # Final result summary
    elapsed = time.time() - start_time
    logger.info(f"\nSearch completed in {elapsed:.2f} seconds")
    logger.info(f"Tested {total_tested} candidates")
    logger.info(f"Best similarity: {best_similarity:.6f}")
    logger.info(f"Best candidate: {hex(best_candidate)}")
    logger.info(f"Best address: {best_address}")
    
    return best_candidate

def main():
    """Run the targeted search for each of our best candidates."""
    logger.info(f"Starting exact address search for {TARGET_ADDRESS}")
    logger.info(f"Previous term (67): {hex(PREV_TERM_67)}")
    
    best_overall = None
    best_overall_similarity = 0
    
    # Try each of our best candidates
    for i, candidate in enumerate(BEST_CANDIDATES):
        logger.info(f"\n===== Testing candidate {i+1}/{len(BEST_CANDIDATES)}: {hex(candidate)} =====")
        address = private_key_to_address(candidate)
        similarity = address_similarity(address, TARGET_ADDRESS)
        logger.info(f"Initial similarity: {similarity:.6f}")
        
        # Run the targeted search
        best_candidate = targeted_search(candidate)
        
        # Check if this result is better than our overall best
        best_address = private_key_to_address(best_candidate)
        best_similarity = address_similarity(best_address, TARGET_ADDRESS)
        
        if best_similarity > best_overall_similarity:
            best_overall_similarity = best_similarity
            best_overall = best_candidate
        
        # If we found an exact match, we're done
        if best_address == TARGET_ADDRESS:
            logger.info("Found exact match!")
            save_result(best_candidate)
            return best_candidate
    
    # No exact match found, return our best overall candidate
    logger.info(f"\nBest overall candidate: {hex(best_overall)}")
    logger.info(f"Best overall similarity: {best_overall_similarity:.6f}")
    logger.info(f"Best overall address: {private_key_to_address(best_overall)}")
    
    # Save this result
    save_result(best_overall)
    
    return best_overall

if __name__ == "__main__":
    # Increase recursion limit for combinations
    sys.setrecursionlimit(10000)
    
    # Run the main search
    result = main()
    
    if result is not None:
        print("\nBest result:")
        print(f"Private key: {hex(result)}")
        print(f"Address: {private_key_to_address(result)}")
        print(f"Similarity: {address_similarity(private_key_to_address(result), TARGET_ADDRESS):.6f}")
    else:
        print("\nNo result found.") 