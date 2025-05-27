#!/usr/bin/env python3
"""
Ultra-focused search for position 68 based on scrypt and balloon hash analyses.
Target value range: 0xce2d691f719dbb6b0 ± small variations
Target address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import sys

# Target Bitcoin address
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Predicted value from scrypt analysis
SCRYPT_PREDICTION = 0xce2d691f719dbb6b0

# Predicted value from balloon hash analysis (slightly different)
BALLOON_PREDICTION = 0xce2d691f719dbb6b2

# Alternate value seen in some places
ALT_PREDICTION = 0xce2d691f719dbb6af

def private_key_to_address(private_key):
    """Convert a private key (integer) to a compressed Bitcoin address."""
    try:
        # Convert integer to bytes
        privkey_hex = format(private_key, '064x')
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
    
    result = {
        "term_index": 68,
        "private_key_hex": hex(private_key),
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
        f.write(f"Private Key (int): {private_key}\n")
        f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
        f.write(f"Difference from prediction: {result['difference']}\n")
        
    print(f"Solution saved to term68_solution.json and term68_solution.txt")
    
    # Also print to screen
    print("\n=== PRIVATE KEY FOUND! ===")
    print(f"Term 68: {hex(private_key)}")
    print(f"Bitcoin Address: {TARGET_ADDRESS}")
    print(f"Difference from prediction: {result['difference']}")
    
    return result

def micro_bit_adjust_search(base_value, max_flips=5):
    """
    Try flipping combinations of up to 'max_flips' bits in the predicted value.
    """
    import itertools
    
    # Convert to binary for bit manipulation
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
        # All possible bit positions (focusing on the more volatile higher bits)
        # Positions are 0-indexed from the left in the binary representation
        bit_positions = list(range(64))  # All positions
        
        # All combinations of 'num_bits' positions
        for positions in itertools.combinations(bit_positions, num_bits):
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

def micro_adjust_search(base_value, range_size=1000):
    """
    Perform a search with tiny step size around the base value.
    Increasing the range_size parameter will try more candidates further from the base.
    """
    print(f"Performing micro-adjust search around {hex(base_value)}...")
    
    # First check the exact base value (again)
    address = private_key_to_address(base_value)
    if address == TARGET_ADDRESS:
        print(f"MATCH FOUND at exact value: {hex(base_value)}")
        return base_value
    
    # Search above the base value
    for i in range(1, range_size + 1):
        # Try base + i
        candidate = base_value + i
        address = private_key_to_address(candidate)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND at {hex(candidate)} (+{i} from base)")
            return candidate
        
        # Try base + polynomial values
        candidate = base_value + (i * i)  # Adding i²
        address = private_key_to_address(candidate)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND at {hex(candidate)} (+{i*i} from base)")
            return candidate
        
        # Log progress occasionally
        if i % 100 == 0:
            print(f"Tested up to +{i} from base")
    
    # Search below the base value
    for i in range(1, range_size + 1):
        # Try base - i
        candidate = base_value - i
        address = private_key_to_address(candidate)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND at {hex(candidate)} (-{i} from base)")
            return candidate
        
        # Try base - polynomial values
        candidate = base_value - (i * i)  # Subtracting i²
        address = private_key_to_address(candidate)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND at {hex(candidate)} (-{i*i} from base)")
            return candidate
        
        # Log progress occasionally
        if i % 100 == 0:
            print(f"Tested up to -{i} from base")
    
    print(f"No match found within ±{range_size} from {hex(base_value)}")
    return None

def byte_adjust_search(base_value):
    """
    Perform adjustments at the byte level, based on byte-change patterns
    observed in the sequence.
    """
    print(f"Performing byte-level adjustments on {hex(base_value)}...")
    
    # Convert to bytes
    base_bytes = base_value.to_bytes(32, byteorder='big')
    candidates = []
    
    # Modify individual bytes with small offsets
    for i in range(len(base_bytes)):
        # Skip all-zero bytes
        if base_bytes[i] == 0:
            continue
            
        # Try several small adjustments to this byte
        for adj in [-2, -1, 1, 2, 4, 8, 16, 32, 64, 128]:
            new_bytes = bytearray(base_bytes)
            
            # Skip if adjustment would overflow/underflow byte
            if 0 <= base_bytes[i] + adj <= 255:
                new_bytes[i] = base_bytes[i] + adj
                candidate = int.from_bytes(new_bytes, byteorder='big')
                candidates.append(candidate)
    
    # Test candidates
    print(f"Testing {len(candidates)} byte-adjusted candidates...")
    for i, candidate in enumerate(candidates):
        address = private_key_to_address(candidate)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND with byte adjustment: {hex(candidate)}")
            return candidate
            
        if (i + 1) % 100 == 0:
            print(f"Tested {i+1}/{len(candidates)} byte-adjusted candidates")
    
    print("No match found with byte adjustments")
    return None

def main():
    """Main execution function with multiple search strategies"""
    print(f"Starting ultra-focused search for position 68")
    start_time = time.time()
    
    # Base values to search around
    base_values = [
        SCRYPT_PREDICTION,     # Predicted value from scrypt analysis
        BALLOON_PREDICTION,    # Predicted value from balloon hash analysis
        ALT_PREDICTION         # Alternative prediction
    ]
    
    # Try bit adjustments on each base value
    for base in base_values:
        # Strategy 1: Try flipping small numbers of bits
        print(f"\nTrying micro bit adjustments on {hex(base)}")
        result = micro_bit_adjust_search(base, max_flips=3)
        if result:
            save_result(result)
            print(f"Search completed in {time.time() - start_time:.2f} seconds")
            return result
    
    # Strategy 2: Try tiny increments/decrements
    for base in base_values:
        print(f"\nTrying micro adjustments on {hex(base)}")
        result = micro_adjust_search(base, range_size=500)
        if result:
            save_result(result)
            print(f"Search completed in {time.time() - start_time:.2f} seconds")
            return result
    
    # Strategy 3: Try byte-level adjustments
    for base in base_values:
        print(f"\nTrying byte-level adjustments on {hex(base)}")
        result = byte_adjust_search(base)
        if result:
            save_result(result)
            print(f"Search completed in {time.time() - start_time:.2f} seconds")
            return result
    
    # Strategy 4: Try a very fine-grained search with even tinier steps
    print("\nTrying ultra-fine search on predicted value")
    for i in range(-50, 51):
        candidate = SCRYPT_PREDICTION + i
        address = private_key_to_address(candidate)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND at offset {i}: {hex(candidate)}")
            save_result(candidate)
            print(f"Search completed in {time.time() - start_time:.2f} seconds")
            return candidate
    
    print(f"No solution found after trying all strategies")
    print(f"Search completed in {time.time() - start_time:.2f} seconds")
    return None

if __name__ == "__main__":
    try:
        result = main()
        if result:
            print(f"\n=== RESULT FOUND ===")
            print(f"Term 68: {hex(result)}")
            print(f"Bitcoin Address: {TARGET_ADDRESS}")
        else:
            print("\nNo match found.")
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}") 