#!/usr/bin/env python3
"""
Targeted search for position 68 based on sequence analysis prediction.
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import sys

# Target Bitcoin address
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Predicted value from sequence analysis
PREDICTION = 0xce2d691f719dbb6b0

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
        "human_time": time.strftime("%Y-%m-%d %H:%M:%S")
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
        
    print(f"Solution saved to term68_solution.json and term68_solution.txt")
    
    # Also print to screen
    print("\n=== PRIVATE KEY FOUND! ===")
    print(f"Term 68: {hex(private_key)}")
    print(f"Bitcoin Address: {TARGET_ADDRESS}")
    
    return result

def test_prediction_and_nearby():
    """Test the prediction and nearby values (±100)"""
    print(f"Testing prediction: {hex(PREDICTION)}")
    
    # Test exact prediction
    address = private_key_to_address(PREDICTION)
    if address == TARGET_ADDRESS:
        print(f"MATCH FOUND at exact prediction: {hex(PREDICTION)}")
        return PREDICTION
    
    print(f"Testing nearby values (±100)...")
    
    # Test nearby values
    for i in range(1, 101):
        # Check above
        test_value = PREDICTION + i
        address = private_key_to_address(test_value)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND at prediction +{i}: {hex(test_value)}")
            return test_value
            
        # Check below
        test_value = PREDICTION - i
        address = private_key_to_address(test_value)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND at prediction -{i}: {hex(test_value)}")
            return test_value
            
        if i % 10 == 0:
            print(f"Tested ±{i} from prediction")
    
    print("No match found in predicted value or nearby range")
    return None

if __name__ == "__main__":
    print("Starting targeted search for position 68 based on sequence analysis")
    start_time = time.time()
    
    result = test_prediction_and_nearby()
    
    if result:
        save_result(result)
    else:
        print("\nNo solution found.")
        
    print(f"Search completed in {time.time() - start_time:.2f} seconds") 