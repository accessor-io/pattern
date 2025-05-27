#!/usr/bin/env python3
"""
Focused search for position 68 in the sequence.
Previous terms:
66: 0x2832ed74f2b5e35ee
67: 0x730fc235c1942c1ae
Target address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import logging
import sys
import random
from typing import Optional, List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("position_68_search.log")
    ]
)
logger = logging.getLogger("position_68")

# Constants
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"
POSITION_66 = 0x2832ed74f2b5e35ee
POSITION_67 = 0x730fc235c1942c1ae

# Mathematical constants
GOLDEN_RATIO = 1.618033988749895
EULER = 2.718281828459045
PI = 3.141592653589793

# Search ranges
MIN_PREDICTED = 0x8747dd8c268dd31c4
MAX_PREDICTED = 0xd7db28ca2b3a33c0c
ESTIMATE_VALUE = 0x12e7b5c4e1c670000
BIT_SHIFTED_VALUE = 0x7a40be591dad6edc8

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

def is_valid_candidate(value: int) -> bool:
    """
    Check if a value is a valid candidate for the 68th term:
    1. Must be > POSITION_67
    2. Must be exactly 68 bits
    3. Must not have more than 3 consecutive identical hex chars
    """
    # Ensure value is greater than previous term
    if value <= POSITION_67:
        return False
    
    # Check bit length
    if value.bit_length() != 68:
        return False
    
    # Check for too many consecutive identical hex chars
    hex_str = format(value, 'x')
    count = 1
    prev_char = hex_str[0]
    
    for char in hex_str[1:]:
        if char == prev_char:
            count += 1
            if count > 3:
                return False
        else:
            count = 1
            prev_char = char
            
    return True

def analyze_transition_66_to_67() -> Dict:
    """Analyze the transition from position 66 to 67."""
    # Convert to binary for bit analysis
    bin66 = format(POSITION_66, 'b').zfill(68)  # Using 68 bits since we're looking for position 68
    bin67 = format(POSITION_67, 'b').zfill(68)
    
    # Count bit changes
    bit_changes = sum(1 for i in range(68) if bin66[i] != bin67[i])
    
    # Calculate XOR
    xor_result = POSITION_66 ^ POSITION_67
    
    # Calculate ratio
    ratio = POSITION_67 / POSITION_66
    
    # Calculate difference
    diff = POSITION_67 - POSITION_66
    
    # Find first and last different bits
    first_diff = next((i for i in range(68) if bin66[i] != bin67[i]), -1)
    last_diff = next((i for i in range(67, -1, -1) if bin66[i] != bin67[i]), -1)
    
    analysis = {
        'bit_changes': bit_changes,
        'xor_result': xor_result,
        'ratio': ratio,
        'difference': diff,
        'bit_changes_ratio': bit_changes / 68,
        'first_different_bit': first_diff,
        'last_different_bit': last_diff
    }
    
    logger.info(f"Analysis of transition 66->67:")
    logger.info(f"Bit changes: {bit_changes} ({bit_changes/68*100:.2f}%)")
    logger.info(f"XOR result: 0x{xor_result:x}")
    logger.info(f"Ratio: {ratio:.6f}")
    logger.info(f"Difference: 0x{diff:x}")
    logger.info(f"First different bit: {first_diff}")
    logger.info(f"Last different bit: {last_diff}")
    
    return analysis

def generate_candidates() -> List[int]:
    """Generate candidate values for position 68 based on analysis."""
    candidates = []
    analysis = analyze_transition_66_to_67()
    
    # 1. Simple incremental patterns
    candidates.append(POSITION_67 + 1)
    candidates.append(POSITION_67 + 2)
    candidates.append(POSITION_67 + 3)
    
    # 2. Apply the same XOR pattern
    xor_candidate = POSITION_67 ^ analysis['xor_result']
    candidates.append(xor_candidate)
    
    # 3. Apply the same ratio
    ratio_candidate = int(POSITION_67 * analysis['ratio'])
    candidates.append(ratio_candidate)
    
    # 4. Add the same difference
    diff_candidate = POSITION_67 + analysis['difference']
    candidates.append(diff_candidate)
    
    # 5. Bit shift patterns
    for shift in range(1, 5):
        candidates.append(POSITION_67 << shift)
        candidates.append(POSITION_67 >> shift)
    
    # 6. XOR with position number
    candidates.append(POSITION_67 ^ 68)
    
    # 7. Add position number
    candidates.append(POSITION_67 + 68)
    
    # 8. Multiply by common factors
    for factor in [1.1, 1.2, 1.5, 1.618, 2]:
        candidates.append(int(POSITION_67 * factor))
    
    # 9. Bit rotation patterns
    for i in range(1, 9):
        rotated = ((POSITION_67 << i) | (POSITION_67 >> (64-i))) & 0xFFFFFFFFFFFFFFFF
        candidates.append(rotated)
    
    # 10. Various XOR operations
    for const in [0x1, 0xF, 0xFF, 0xFFF, 0xFFFF, 0x12345, 0xABCDEF]:
        candidates.append(POSITION_67 ^ const)
    
    # 11. XOR with previous value
    candidates.append(POSITION_67 ^ POSITION_66)
    
    # 12. Add various patterns
    for num in [0x100, 0x1000, 0x10000, 0x100000]:
        candidates.append(POSITION_67 + num)
    
    # 13. Predictions from other analysis
    candidates.append(MIN_PREDICTED)
    candidates.append(MAX_PREDICTED)
    candidates.append(ESTIMATE_VALUE)
    candidates.append(BIT_SHIFTED_VALUE)
    
    # 14. Fibonacci-like patterns
    candidates.append(POSITION_67 + POSITION_66)
    candidates.append(POSITION_67 * 2 - POSITION_66)
    
    # Filter and deduplicate candidates
    valid_candidates = []
    for candidate in candidates:
        if is_valid_candidate(candidate):
            valid_candidates.append(candidate)
    
    return list(set(valid_candidates))

def search_candidates(candidates: List[int]) -> Optional[int]:
    """Search through candidates to find the correct value."""
    logger.info(f"Searching through {len(candidates)} candidates")
    
    for i, candidate in enumerate(candidates):
        if i % 10 == 0:
            logger.info(f"Testing candidate {i}/{len(candidates)}: 0x{candidate:x}")
        
        address = private_key_to_address(candidate)
        if address == TARGET_ADDRESS:
            logger.info(f"FOUND MATCH! Position 68: 0x{candidate:x}")
            return candidate
    
    return None

def search_proximity(base_value, range_size=10000, step=1):
    """Search values very close to a base value."""
    logger.info(f"Starting proximity search around 0x{base_value:x} (±{range_size})")
    
    # Test the exact base value first
    address = private_key_to_address(base_value)
    if address == TARGET_ADDRESS:
        logger.info(f"FOUND MATCH at exact base: 0x{base_value:x}")
        return base_value
    
    # Search above the base value
    for offset in range(1, range_size + 1, step):
        if offset % 1000 == 0:
            logger.info(f"Testing offset +{offset}")
            
        test_value = base_value + offset
        try:
            address = private_key_to_address(test_value)
            if address == TARGET_ADDRESS:
                logger.info(f"FOUND MATCH at offset +{offset}: 0x{test_value:x}")
                return test_value
        except Exception as e:
            logger.error(f"Error at offset +{offset}: {e}")
    
    # Search below the base value
    for offset in range(1, range_size + 1, step):
        if offset % 1000 == 0:
            logger.info(f"Testing offset -{offset}")
            
        test_value = base_value - offset
        if test_value <= 0:
            break
            
        try:
            address = private_key_to_address(test_value)
            if address == TARGET_ADDRESS:
                logger.info(f"FOUND MATCH at offset -{offset}: 0x{test_value:x}")
                return test_value
        except Exception as e:
            logger.error(f"Error at offset -{offset}: {e}")
    
    return None

def save_result(value: int) -> None:
    """Save the found value to a file."""
    result = {
        "position": 68,
        "value_hex": hex(value),
        "value_decimal": value,
        "previous_position_67": hex(POSITION_67),
        "bitcoin_address": TARGET_ADDRESS,
        "found_timestamp": time.time()
    }
    
    with open("position_68_result.json", "w") as f:
        import json
        json.dump(result, f, indent=2)
    
    # Also save as plain text
    with open("position_68_result.txt", "w") as f:
        f.write(f"Position 68 FOUND\n")
        f.write(f"Value (hex): {hex(value)}\n")
        f.write(f"Value (decimal): {value}\n")
        f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
        f.write(f"Previous term (67): {hex(POSITION_67)}\n")
    
    logger.info(f"Result saved to position_68_result.json and position_68_result.txt")

def main():
    """Main execution function."""
    logger.info("Starting focused search for position 68")
    start_time = time.time()
    
    # Step 1: Test common increments (very close values)
    logger.info("Step 1: Testing common increments")
    for i in range(1, 100):
        test_value = POSITION_67 + i
        address = private_key_to_address(test_value)
        if address == TARGET_ADDRESS:
            logger.info(f"FOUND MATCH with increment {i}: 0x{test_value:x}")
            save_result(test_value)
            return test_value
    
    # Step 2: Generate and test pattern-based candidates
    logger.info("Step 2: Testing pattern-based candidates")
    candidates = generate_candidates()
    logger.info(f"Generated {len(candidates)} candidates")
    result = search_candidates(candidates)
    if result:
        save_result(result)
        logger.info(f"Search completed successfully in {time.time() - start_time:.2f} seconds")
        return result
    
    # Step 3: Focused proximity search around key values
    logger.info("Step 3: Running proximity searches")
    priority_values = [
        POSITION_67 + 1,                  # Most common increment
        POSITION_67 ^ 68,                 # XOR with position
        int(POSITION_67 * GOLDEN_RATIO),  # Golden ratio increase
        POSITION_67 * 2,                  # Double
        MIN_PREDICTED,                    # Min predicted value
        MAX_PREDICTED                     # Max predicted value
    ]
    
    for base_value in priority_values:
        result = search_proximity(base_value, range_size=10000, step=1)
        if result:
            save_result(result)
            logger.info(f"Search completed successfully in {time.time() - start_time:.2f} seconds")
            return result
    
    # Step 4: Target specific potential values 
    for i in range(1, 1000):
        # Try some specific values based on patterns in the sequence
        test_value = POSITION_67 + i * 68  # Multiples of position number
        address = private_key_to_address(test_value)
        if address == TARGET_ADDRESS:
            logger.info(f"FOUND MATCH with pattern 67 + {i}*68: 0x{test_value:x}")
            save_result(test_value)
            return test_value
            
        if i % 100 == 0:
            logger.info(f"Tested up to pattern 67 + {i}*68")
    
    logger.info(f"No match found after {time.time() - start_time:.2f} seconds")
    return None

if __name__ == "__main__":
    try:
        result = main()
        if result:
            print(f"\n=== POSITION 68 FOUND ===")
            print(f"Value: 0x{result:x}")
            print(f"Address: {TARGET_ADDRESS}")
        else:
            print("\nNo match found in the search space.")
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nError: {e}") 