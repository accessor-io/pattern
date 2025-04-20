#!/usr/bin/env python3
"""
Term 68 Exact Calculator

This script calculates the exact value of Term 68 using the formula:
Term_68 = (Term_67 * 271) + 68

It then tests if this value generates the target Bitcoin address.
If not, it implements a refined search around the calculated value.

Based on sequence formula from gpt_version.py
"""

import hashlib
import base58
import json
import time
import logging
from ecdsa import SigningKey, SECP256k1

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('term68_exact_calculator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Target information
TARGET_INDEX = 68
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"
PREV_TERM_67 = 0x730fc235c1942c1ae  # Term 67 value
TERM_68_FORMULA = {
    'type': 'C',
    'prime': 271,
    'offset': 68
}

def private_key_to_address(private_key: int) -> str:
    """
    Convert a private key integer to a Bitcoin address
    Includes robust error handling for RIPEMD160 issues
    """
    try:
        # Format private key to 64 hex digits (32 bytes)
        privkey_hex = format(private_key, '064x')
        privkey_bytes = bytes.fromhex(privkey_hex)
        
        # Create signing key
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Get public key coordinates
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Create uncompressed public key (04 + x + y)
        pubkey = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
        
        # Hash public key
        sha_digest = hashlib.sha256(pubkey).digest()
        
        try:
            # Try RIPEMD-160 hash
            ripemd_digest = hashlib.new('ripemd160', sha_digest).digest()
        except (Exception, ValueError) as e:
            # Fallback if RIPEMD-160 is not available
            logger.warning(f"RIPEMD160 not available: {e}. Using SHA256 fallback.")
            ripemd_digest = hashlib.sha256(hashlib.sha256(pubkey).digest()).digest()[:20]
        
        # Add version byte and checksum
        versioned_payload = b'\x00' + ripemd_digest
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        
        # Encode result in Base58
        address = base58.b58encode(versioned_payload + checksum).decode()
        return address
    except Exception as e:
        logger.error(f"Error in private_key_to_address: {e}")
        return None

def calculate_exact_term_68():
    """
    Calculate the exact value of Term 68 using the formula from gpt_version.py:
    Term_68 = (Term_67 * 271) + 68
    """
    term_67 = PREV_TERM_67
    prime = TERM_68_FORMULA['prime']
    offset = TERM_68_FORMULA['offset']
    
    # Type C formula: T(n) = (T(n-1) * prime) + offset
    term_68_full = (term_67 * prime) + offset
    
    logger.info(f"Term 67 (hex): {hex(term_67)}")
    logger.info(f"Formula: Term_68 = (Term_67 * {prime}) + {offset}")
    logger.info(f"Full Term 68 (decimal): {term_68_full}")
    logger.info(f"Full Term 68 (hex): {hex(term_68_full)}")
    logger.info(f"Full Term 68 bits: {term_68_full.bit_length()}")
    
    # Since the sequence specifies exactly 68 bits, let's also create a 68-bit version
    # by taking the least significant 68 bits
    mask_68_bits = (1 << 68) - 1
    term_68_truncated = term_68_full & mask_68_bits
    
    logger.info(f"Truncated Term 68 (decimal): {term_68_truncated}")
    logger.info(f"Truncated Term 68 (hex): {hex(term_68_truncated)}")
    logger.info(f"Truncated Term 68 bits: {term_68_truncated.bit_length()}")
    
    return term_68_full, term_68_truncated

def has_too_many_consecutive_chars(value: int) -> bool:
    """
    Check if hex representation has more than 3 consecutive identical characters.
    """
    hex_str = hex(value)[2:]  # Remove '0x' prefix
    
    # Use regex for better performance
    import re
    if re.search(r'(.)\1{3,}', hex_str):
        return True
    
    return False

def is_valid_candidate(value: int) -> bool:
    """
    Check if a value is a valid candidate for the 68th term:
    1. Must be greater than previous term
    2. Must have exactly 68 bits (fit in 68 bits)
    3. Must not have more than 3 consecutive identical hex chars
    """
    return (
        value > PREV_TERM_67 and
        value.bit_length() <= TARGET_INDEX and
        not has_too_many_consecutive_chars(value)
    )

def test_term_68_value(value):
    """
    Test if the Term 68 value generates the target Bitcoin address
    """
    logger.info(f"Testing Term 68 value: {hex(value)}")
    
    # Validate candidate
    if not is_valid_candidate(value):
        logger.warning(f"Candidate {hex(value)} is not valid")
        return False
    
    # Generate address
    address = private_key_to_address(value)
    if not address:
        logger.warning("Failed to generate address")
        return False
    
    logger.info(f"Generated address: {address}")
    logger.info(f"Target address:    {TARGET_ADDRESS}")
    
    # Check for match
    is_match = (address == TARGET_ADDRESS)
    if is_match:
        logger.info("!!! EXACT MATCH FOUND !!!")
        save_result(value)
    else:
        logger.info("No match")
        
        # Show character-by-character comparison
        match_chars = 0
        for i, (a, b) in enumerate(zip(address, TARGET_ADDRESS)):
            if a == b:
                match_chars += 1
                
        logger.info(f"Character match: {match_chars}/{len(TARGET_ADDRESS)} ({match_chars/len(TARGET_ADDRESS)*100:.2f}%)")
    
    return is_match

def search_around_term_68(center, radius=1000):
    """
    Search around the calculated Term 68 value within a specified radius
    """
    logger.info(f"Searching around {hex(center)} with radius {radius}")
    
    for offset in range(-radius, radius+1):
        if offset == 0:  # Skip, we already tested the exact value
            continue
            
        candidate = center + offset
        if is_valid_candidate(candidate):
            address = private_key_to_address(candidate)
            if not address:
                continue
                
            logger.info(f"Offset {offset}: Generated {address} from {hex(candidate)}")
            
            if address == TARGET_ADDRESS:
                logger.info(f"!!! MATCH FOUND at offset {offset} !!!")
                save_result(candidate)
                return True
    
    logger.info(f"No match found within radius {radius}")
    return False

def perform_bit_flips(center, max_bits=5):
    """
    Try flipping up to max_bits bits in the center value
    """
    logger.info(f"Performing bit flips (up to {max_bits} bits) on {hex(center)}")
    
    # Get binary representation
    bits = bin(center)[2:].zfill(68)
    bit_positions = list(range(len(bits)))
    
    # Try flipping 1-max_bits bits
    import itertools
    for num_bits in range(1, max_bits+1):
        logger.info(f"Trying {num_bits}-bit flips")
        
        # Get all combinations of bit positions to flip
        for positions in itertools.combinations(bit_positions, num_bits):
            # Create a new candidate by flipping bits at positions
            candidate = center
            for pos in positions:
                candidate ^= (1 << pos)
                
            if is_valid_candidate(candidate):
                address = private_key_to_address(candidate)
                if not address:
                    continue
                    
                logger.info(f"Flipped bits {positions}: Generated {address} from {hex(candidate)}")
                
                if address == TARGET_ADDRESS:
                    logger.info(f"!!! MATCH FOUND by flipping bits {positions} !!!")
                    save_result(candidate)
                    return True
    
    logger.info("No match found by bit flipping")
    return False

def save_result(value):
    """
    Save the found solution to files
    """
    result = {
        "term": 68,
        "private_key_int": value,
        "private_key_hex": hex(value),
        "address": private_key_to_address(value),
        "timestamp": time.time()
    }
    
    # Save as JSON
    with open("term68_solution.json", "w") as f:
        json.dump(result, f, indent=4)
    
    # Save as plain text
    with open("term68_solution.txt", "w") as f:
        f.write(f"Term 68 Solution\n")
        f.write(f"---------------\n")
        f.write(f"Value (int): {value}\n")
        f.write(f"Value (hex): {hex(value)}\n")
        f.write(f"Address: {result['address']}\n")
    
    logger.info(f"Solution saved to term68_solution.json and term68_solution.txt")
    return result

def main():
    """
    Main function to calculate and test Term 68
    """
    logger.info("Starting Term 68 Exact Calculator")
    
    try:
        # Calculate the exact Term 68 value (both full and truncated)
        term_68_full, term_68_truncated = calculate_exact_term_68()
        
        # Test the full value first
        logger.info("Testing full Term 68 value...")
        full_match = test_term_68_value(term_68_full)
        
        if not full_match:
            # If the full value doesn't match, try the truncated 68-bit value
            logger.info("Testing truncated 68-bit Term 68 value...")
            truncated_match = test_term_68_value(term_68_truncated)
            
            if not truncated_match:
                # Try searching around both values
                logger.info("Exact match not found. Searching nearby values...")
                
                # Check if truncated value is valid before proceeding
                if is_valid_candidate(term_68_truncated):
                    # Try bit flips on truncated value
                    logger.info("Trying bit flips on truncated value...")
                    bit_flip_match = perform_bit_flips(term_68_truncated, max_bits=5)
                    
                    if not bit_flip_match:
                        # Try values within a radius of truncated value
                        logger.info("Trying nearby values around truncated value...")
                        radius_match = search_around_term_68(term_68_truncated, radius=1000)
                        
                        if not radius_match:
                            logger.info("No match found around truncated value. Trying broader searches...")
                            
                            # Try with a larger radius
                            logger.info("Trying larger radius around truncated value...")
                            radius_match = search_around_term_68(term_68_truncated, radius=10000)
                            
                            if not radius_match:
                                logger.info("No match found. Please try additional search strategies.")
                else:
                    logger.warning("Truncated Term 68 value is not a valid candidate.")
                    logger.info("Please try additional search strategies.")
                    
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    
    logger.info("Term 68 Exact Calculator completed")

if __name__ == "__main__":
    main()
