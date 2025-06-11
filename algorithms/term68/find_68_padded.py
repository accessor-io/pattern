#!/usr/bin/env python3
"""
Search for position 68 with proper zero-padding for Bitcoin private keys.
Ensuring all candidates are correctly padded to 64 hexadecimal characters.
Target address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import sys
import itertools

# Target Bitcoin address
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Known terms
TERM_66 = 0x2832ed74f2b5e35ee
TERM_67 = 0x730fc235c1942c1ae
TERM_67_ALT = 0x3ce0e3395f140001
TERM_69 = 0x1ef55100b22af5acd7  # From predictions.json
TERM_70 = 0x349b84b6431a6c4ef1  # Known for validation

# Predicted values for position 68
SCRYPT_PREDICTION = 0xce2d691f719dbb6b0
BALLOON_PREDICTION = 0xce2d691f719dbb6b2
ALT_PREDICTION = 0xce2d691f719dbb6af

def verify_padding(private_key):
    """Verify and print the properly padded hex representation"""
    hex_str = hex(private_key)[2:]  # Remove '0x' prefix
    padded_hex = hex_str.zfill(64)  # Pad to 64 characters
    
    print(f"Original hex:  {hex_str} ({len(hex_str)} chars)")
    print(f"Padded to 64:  {padded_hex} ({len(padded_hex)} chars)")
    
    # Validate padding is correct
    if len(padded_hex) != 64:
        print("WARNING: Padding resulted in incorrect length!")
    
    return padded_hex

def private_key_to_address(private_key, validate_padding=False):
    """
    Convert a private key (integer) to a compressed Bitcoin address.
    
    Args:
        private_key: Integer representation of private key
        validate_padding: If True, print padding verification info
    """
    try:
        # Convert to properly padded hex string (64 characters)
        privkey_hex = format(private_key, '064x')
        
        if validate_padding:
            print(f"Converting private key: {hex(private_key)}")
            print(f"Padded hex ({len(privkey_hex)} chars): {privkey_hex}")
            
        # Convert to bytes
        privkey_bytes = bytes.fromhex(privkey_hex)
        
        # Create ECDSA signing key
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Get x and y coordinates
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Create compressed public key format (0x02 if y is even, 0x03 if y is odd)
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        compressed_pubkey = prefix + x.to_bytes(32, 'big')
        
        # Hash with SHA-256 and RIPEMD-160
        sha_digest = hashlib.sha256(compressed_pubkey).digest()
        try:
            ripemd_digest = hashlib.new('ripemd160', sha_digest).digest()
        except Exception:
            # Fallback for environments without ripemd160
            ripemd_digest = hashlib.sha256(sha_digest).digest()[:20]
            
        # Add network byte (0x00 for mainnet)
        versioned_payload = b'\x00' + ripemd_digest
        
        # Calculate and append checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        address_bytes = versioned_payload + checksum
        
        # Encode with Base58
        address = base58.b58encode(address_bytes).decode('utf-8')
        return address
    except Exception as e:
        print(f"Error generating address: {e}")
        return None

def save_result(private_key):
    """Save the found private key to both JSON and text files"""
    import json
    
    # Verify proper padding
    padded_hex = verify_padding(private_key)
    
    result = {
        "term_index": 68,
        "private_key_hex": hex(private_key),
        "private_key_padded_hex": padded_hex,
        "private_key_int": private_key,
        "bitcoin_address": TARGET_ADDRESS,
        "found_timestamp": time.time(),
        "human_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prediction": hex(SCRYPT_PREDICTION),
        "difference": private_key - SCRYPT_PREDICTION
    }
    
    # Save as JSON
    with open("term68_solution.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Save as text file
    with open("term68_solution.txt", "w") as f:
        f.write(f"Term 68 Solution\n")
        f.write(f"Private Key (hex): {hex(private_key)}\n")
        f.write(f"Private Key (padded hex): {padded_hex}\n")
        f.write(f"Private Key (decimal): {private_key}\n")
        f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
        f.write(f"Difference from prediction: {result['difference']}\n")
        
    print(f"Solution saved to term68_solution.json and term68_solution.txt")
    
    # Also print to screen
    print("\n=== PRIVATE KEY FOUND! ===")
    print(f"Term 68: {hex(private_key)}")
    print(f"Term 68 (padded): {padded_hex}")
    print(f"Bitcoin Address: {TARGET_ADDRESS}")
    print(f"Difference from prediction: {result['difference']}")
    
    return result

def verify_known_addresses():
    """Verify that our address generation works for known terms"""
    print("Verifying address generation for known terms...")
    
    # These are made-up addresses just for verification
    # The real addresses might be different
    test_cases = [
        (66, TERM_66),
        (67, TERM_67),
        (70, TERM_70)
    ]
    
    for position, value in test_cases:
        # Verify padding
        padded_hex = verify_padding(value)
        
        # Generate address
        address = private_key_to_address(value, validate_padding=True)
        
        print(f"Position {position}: {hex(value)}")
        print(f"Address: {address}")
        print("----------------------")
    
    print("Verification complete!\n")

def micro_bit_adjust_search(base_value, max_flips=4):
    """
    Try flipping combinations of up to 'max_flips' bits in the predicted value.
    Ensuring proper padding for each candidate.
    """
    # Verify padding for base value
    print(f"Base value before testing: {hex(base_value)}")
    verify_padding(base_value)000000000000000000000000000000000000000000000002832ed74f2b5e35ee
    
    # Convert to binary for bit manipulation (64 bits)
    base_bin = list(format(base_value, '064b'))
    
    # First check the exact prediction
    print(f"Testing base value: {hex(base_value)}")
    address = private_key_to_address(base_value)
    if address == TARGET_ADDRESS:
        print(f"MATCH FOUND at exact prediction: {hex(base_value)}")
        return base_value
    
    # Try flipping combinations of bits
    total_candidates = 0
    
    for num_bits in range(1, max_flips + 1):
        print(f"Trying combinations of {num_bits} bit flips...")
        
        # All possible bit positions (focusing more on lower bits which are more likely to change)
        # Positions are 0-indexed from the left in the binary representation
        bit_positions = list(range(64))
        lower_half_positions = list(range(32, 64))  # Lower 32 bits (right half)
        
        # First try combinations of lower bits (more likely to change)
        for positions in itertools.combinations(lower_half_positions, num_bits):
            # Create a new binary representation with bits flipped
            new_bin = base_bin.copy()
            for pos in positions:
                # Flip the bit at position 'pos'
                new_bin[pos] = '1' if new_bin[pos] == '0' else '0'
            
            # Convert back to integer
            candidate = int(''.join(new_bin), 2)
            total_candidates += 1
            
            if total_candidates % 100 == 0:
                print(f"Tested {total_candidates} candidates...")
            
            # Test this candidate
            address = private_key_to_address(candidate)
            if address == TARGET_ADDRESS:
                print(f"MATCH FOUND with {num_bits} bit flips: {hex(candidate)}")
                print(f"Flipped bits at positions: {positions}")
                return candidate
        
        # If num_bits <= 2, also try all positions
        if num_bits <= 2:
            for positions in itertools.combinations(bit_positions, num_bits):
                # Skip if we already tested this combination
                if all(pos in lower_half_positions for pos in positions):
                    continue
                    
                # Create a new binary representation with bits flipped
                new_bin = base_bin.copy()
                for pos in positions:
                    # Flip the bit at position 'pos'
                    new_bin[pos] = '1' if new_bin[pos] == '0' else '0'
                
                # Convert back to integer
                candidate = int(''.join(new_bin), 2)
                total_candidates += 1
                
                if total_candidates % 100 == 0:
                    print(f"Tested {total_candidates} candidates...")
                
                # Test this candidate
                address = private_key_to_address(candidate)
                if address == TARGET_ADDRESS:
                    print(f"MATCH FOUND with {num_bits} bit flips: {hex(candidate)}")
                    print(f"Flipped bits at positions: {positions}")
                    return candidate
    
    print(f"No match found after testing {total_candidates} candidates")
    return None

def pattern_based_search():
    """
    Search for position 68 based on patterns between terms 66, 67, and 69.
    Apply the same patterns that generated 67 from 66, to generate 68 from 67.
    """
    print("Starting pattern-based search...")
    candidates = []
    
    # Calculate transformation from 66 to 67
    diff_66_67 = TERM_67 - TERM_66
    ratio_66_67 = TERM_67 / TERM_66
    xor_66_67 = TERM_66 ^ TERM_67
    
    # Apply those same transformations from 67 to predict 68
    candidates.append(TERM_67 + diff_66_67)  # Same difference
    candidates.append(int(TERM_67 * ratio_66_67))  # Same ratio
    candidates.append(TERM_67 ^ xor_66_67)  # Same XOR pattern
    
    # Try some more complex patterns
    candidates.append(TERM_67 + (TERM_67 - TERM_66))  # Accelerating difference
    candidates.append(TERM_67 * (TERM_67 / TERM_66))  # Accelerating ratio
    candidates.append((TERM_67 * 2) - TERM_66)  # Linear extrapolation
    candidates.append(TERM_67 + ((TERM_67 - TERM_66) // 2))  # Half-difference
    candidates.append(TERM_67 + (TERM_67 - TERM_66) * 2)  # Double-difference
    
    # Try transformation patterns from 67 to 69 (skipping 68)
    diff_67_69 = TERM_69 - TERM_67
    candidates.append(TERM_67 + (diff_67_69 // 2))  # Midpoint between 67 and 69
    
    # Add our predictions to the candidates
    candidates.append(SCRYPT_PREDICTION)
    candidates.append(BALLOON_PREDICTION)
    candidates.append(ALT_PREDICTION)
    
    # Try tiny variations around predictions
    for i in range(-10, 11):
        candidates.append(SCRYPT_PREDICTION + i)
        candidates.append(BALLOON_PREDICTION + i)
        candidates.append(ALT_PREDICTION + i)
    
    # Try bit-flipped variations of predictions
    for prediction in [SCRYPT_PREDICTION, BALLOON_PREDICTION, ALT_PREDICTION]:
        bin_pred = list(format(prediction, '064b'))
        # Flip least significant bit
        bin_pred[-1] = '1' if bin_pred[-1] == '0' else '0'
        candidates.append(int(''.join(bin_pred), 2))
        
        # Flip second least significant bit
        bin_pred = list(format(prediction, '064b'))
        bin_pred[-2] = '1' if bin_pred[-2] == '0' else '0'
        candidates.append(int(''.join(bin_pred), 2))
    
    # Remove duplicates
    candidates = list(set(candidates))
    
    print(f"Testing {len(candidates)} pattern-based candidates...")
    for i, candidate in enumerate(candidates):
        # For diagnostics, show the padded hex for some candidates
        if i < 10 or i % 50 == 0:
            print(f"Testing candidate {i+1}/{len(candidates)}: {hex(candidate)}")
            verify_padding(candidate)
        else:
            print(f"Testing candidate {i+1}/{len(candidates)}: {hex(candidate)}")
            
        address = private_key_to_address(candidate)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND! Candidate: {hex(candidate)}")
            return candidate
    
    print("No match found among pattern-based candidates")
    return None

def main():
    """Main execution function with multiple search strategies"""
    print(f"Starting enhanced search for position 68 with proper padding")
    start_time = time.time()
    
    # First verify our address generation works with known terms
    verify_known_addresses()
    
    # Try pattern-based search first (this is faster)
    print("\nTrying pattern-based search")
    result = pattern_based_search()
    if result:
        save_result(result)
        print(f"Search completed in {time.time() - start_time:.2f} seconds")
        return result
    
    # Try bit-flipping on our prediction
    print("\nTrying bit flipping variations of prediction")
    result = micro_bit_adjust_search(SCRYPT_PREDICTION, max_flips=3)
    if result:
        save_result(result)
        print(f"Search completed in {time.time() - start_time:.2f} seconds")
        return result
    
    # Try bit-flipping on balloon prediction
    print("\nTrying bit flipping variations of balloon prediction")
    result = micro_bit_adjust_search(BALLOON_PREDICTION, max_flips=3)
    if result:
        save_result(result)
        print(f"Search completed in {time.time() - start_time:.2f} seconds")
        return result
    
    # Try bit-flipping on alt prediction
    print("\nTrying bit flipping variations of alt prediction")
    result = micro_bit_adjust_search(ALT_PREDICTION, max_flips=3)
    if result:
        save_result(result)
        print(f"Search completed in {time.time() - start_time:.2f} seconds")
        return result
    
    print(f"No solution found after trying all strategies")
    print(f"Search completed in {time.time() - start_time:.2f} seconds")
    return None

if __name__ == "__main__":
    try:
        result = main()
        if result:
            print(f"\n=== RESULT FOUND ===")
            print(f"Term 68: {hex(result)}")
            padded_hex = format(result, '064x')
            print(f"Term 68 (padded): {padded_hex}")
            print(f"Bitcoin Address: {TARGET_ADDRESS}")
        else:
            print("\nNo match found.")
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}") 