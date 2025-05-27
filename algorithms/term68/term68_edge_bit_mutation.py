#!/usr/bin/env python3
"""
Edge-focused search for position 68 with proper zero-padding.
Focusing on the highest and lowest order bits in our prediction.
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

# Predicted value from scrypt analysis
PREDICTION = 0xce2d691f719dbb6b0

# Variations we want to test (add/subtract to prediction)
OFFSETS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 32, 64, 128]

def verify_padding(private_key):
    """Verify and print the properly padded hex representation"""
    hex_str = hex(private_key)[2:]  # Remove '0x' prefix
    padded_hex = hex_str.zfill(64)  # Pad to 64 characters
    
    if len(padded_hex) != 64:
        print(f"WARNING: Padding resulted in incorrect length: {len(padded_hex)}")
    
    return padded_hex

def private_key_to_address(private_key):
    """
    Convert a private key (integer) to a compressed Bitcoin address.
    Ensures proper 32-byte padding of the private key.
    """
    try:
        # Convert to properly padded hex string (64 characters)
        privkey_hex = format(private_key, '064x')
        
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
        "prediction": hex(PREDICTION),
        "difference": private_key - PREDICTION
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

def test_candidate(candidate):
    """Test a candidate and return True if it matches the target address"""
    address = private_key_to_address(candidate)
    return address == TARGET_ADDRESS

def generate_edge_bit_mutations(value):
    """Generate candidates by flipping bits at the edges (highest and lowest order)"""
    candidates = []
    
    # Convert to binary with padding to ensure 256 bits
    bin_value = format(value, '0256b')
    bin_list = list(bin_value)
    
    # Flip each bit at the high end (first 16 bits)
    for i in range(16):
        mutated = bin_list.copy()
        mutated[i] = '1' if mutated[i] == '0' else '0'
        candidates.append(int(''.join(mutated), 2))
    
    # Flip each bit at the low end (last 16 bits)
    for i in range(240, 256):
        mutated = bin_list.copy()
        mutated[i] = '1' if mutated[i] == '0' else '0'
        candidates.append(int(''.join(mutated), 2))
    
    # Also try offsetting by powers of 2
    for offset in OFFSETS:
        candidates.append(value + offset)
        candidates.append(value - offset)
    
    # Try offsetting individual bytes
    bytes_value = value.to_bytes(32, byteorder='big')
    
    # Modify the first few bytes
    for i in range(3):  # First 3 bytes
        if bytes_value[i] == 0:
            continue
            
        for adj in [1, 2, 4, 8, 16, 32, 64, 128]:
            if bytes_value[i] + adj <= 255:
                new_bytes = bytearray(bytes_value)
                new_bytes[i] = bytes_value[i] + adj
                candidates.append(int.from_bytes(new_bytes, byteorder='big'))
            
            if bytes_value[i] >= adj:
                new_bytes = bytearray(bytes_value)
                new_bytes[i] = bytes_value[i] - adj
                candidates.append(int.from_bytes(new_bytes, byteorder='big'))
    
    # Modify the last few bytes
    for i in range(29, 32):  # Last 3 bytes
        if bytes_value[i] == 0:
            continue
            
        for adj in [1, 2, 4, 8, 16, 32, 64, 128]:
            if bytes_value[i] + adj <= 255:
                new_bytes = bytearray(bytes_value)
                new_bytes[i] = bytes_value[i] + adj
                candidates.append(int.from_bytes(new_bytes, byteorder='big'))
            
            if bytes_value[i] >= adj:
                new_bytes = bytearray(bytes_value)
                new_bytes[i] = bytes_value[i] - adj
                candidates.append(int.from_bytes(new_bytes, byteorder='big'))
    
    # Remove duplicates
    candidates = list(set(candidates))
    
    return candidates

def handle_edge_case_patterns():
    """Try some common edge case patterns and transformations"""
    candidates = []
    
    # Check the exact prediction first
    if test_candidate(PREDICTION):
        return PREDICTION
    
    # Generate edge bit mutations
    candidates.extend(generate_edge_bit_mutations(PREDICTION))
    
    # Try combining PREDICTION with various constants
    for c in [1, 2, 4, 8, 16, 32, 64, 128, 256, 65536]:
        candidates.append(PREDICTION ^ c)  # XOR with constant
        candidates.append(PREDICTION | c)  # OR with constant
        candidates.append(PREDICTION & ~c)  # AND with inverted constant
    
    # Try bit shift transformations (which particularly affect the edge bits)
    for shift in range(1, 8):
        candidates.append(PREDICTION << shift)  # Shift left
        candidates.append(PREDICTION >> shift)  # Shift right
        
        # Circular shifts (preserving n bits)
        n = 68  # Assumed bit length of our terms
        mask = (1 << n) - 1
        candidates.append(((PREDICTION << shift) | (PREDICTION >> (n - shift))) & mask)
        candidates.append(((PREDICTION >> shift) | (PREDICTION << (n - shift))) & mask)
    
    # Remove duplicates
    candidates = list(set(candidates))
    
    # Test the candidates
    print(f"Testing {len(candidates)} edge-case candidates...")
    for i, candidate in enumerate(candidates):
        if i % 100 == 0:
            print(f"Tested {i}/{len(candidates)} edge candidates")
        
        if test_candidate(candidate):
            print(f"MATCH FOUND! Edge case: {hex(candidate)}")
            return candidate
    
    return None

def try_byte_swapping():
    """Try swapping adjacent bytes in the prediction"""
    print("Trying byte swapping candidates...")
    bytes_value = PREDICTION.to_bytes(32, byteorder='big')
    
    candidates = []
    
    # Try swapping adjacent bytes
    for i in range(len(bytes_value) - 1):
        new_bytes = bytearray(bytes_value)
        new_bytes[i], new_bytes[i+1] = new_bytes[i+1], new_bytes[i]
        candidates.append(int.from_bytes(new_bytes, byteorder='big'))
    
    # Test the candidates
    for i, candidate in enumerate(candidates):
        print(f"Testing byte-swap candidate {i+1}/{len(candidates)}: {hex(candidate)}")
        
        if test_candidate(candidate):
            print(f"MATCH FOUND with byte swap: {hex(candidate)}")
            return candidate
    
    print("No match found with byte swapping")
    return None

def main():
    """Main execution function focusing on edge bit mutations"""
    print(f"Starting edge-focused search for position 68")
    start_time = time.time()
    
    # Start with the exact prediction
    print(f"Testing exact prediction: {hex(PREDICTION)}")
    print(f"Padded to 64 chars: {verify_padding(PREDICTION)}")
    
    if test_candidate(PREDICTION):
        print("MATCH FOUND at exact prediction!")
        save_result(PREDICTION)
        return PREDICTION
    
    # Try edge bit mutations and other pattern transformations
    result = handle_edge_case_patterns()
    if result:
        save_result(result)
        print(f"Search completed in {time.time() - start_time:.2f} seconds")
        return result
    
    # Try byte swapping
    result = try_byte_swapping()
    if result:
        save_result(result)
        print(f"Search completed in {time.time() - start_time:.2f} seconds")
        return result
    
    print(f"No solution found after trying all edge cases")
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