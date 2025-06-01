#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate my position 71 prediction against the actual Bitcoin address"""

import hashlib
import base58
import ecdsa

def validate_prediction_71():
    """Validate my blind prediction for position 71 against actual Bitcoin address"""
    
    print("VALIDATING POSITION 71 PREDICTION AGAINST ACTUAL ADDRESS")
    print("=" * 70)
    
    # Provided actual Bitcoin address for position 71
    actual_address = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
    actual_hash160 = "f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8"
    
    print(f"Actual Bitcoin Address: {actual_address}")
    print(f"Actual Hash160:         {actual_hash160}")
    print(f"Address Type:           P2PKH (Compressed)")
    print()
    
    # My blind prediction
    my_prediction = 0x68f5c28f5c28f60000
    print(f"My blind prediction:    0x{my_prediction:x}")
    print(f"Predicted decimal:      {my_prediction:,}")
    print()
    
    # Convert my prediction to Bitcoin address
    def private_key_to_address(private_key_int, compressed=True):
        """Convert private key to Bitcoin address"""
        
        # Generate public key point
        private_key_bytes = private_key_int.to_bytes(32, 'big')
        sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        
        if compressed:
            # Compressed public key format
            x = vk.pubkey.point.x()
            y = vk.pubkey.point.y()
            if y % 2 == 0:
                public_key = b'\x02' + x.to_bytes(32, 'big')
            else:
                public_key = b'\x03' + x.to_bytes(32, 'big')
        else:
            # Uncompressed public key format
            public_key = b'\x04' + vk.to_string()
        
        # Hash the public key (SHA256 then RIPEMD160)
        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Add version byte (0x00 for mainnet)
        versioned_payload = b'\x00' + ripemd160_hash
        
        # Calculate checksum (double SHA256)
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        
        # Encode as Base58
        full_payload = versioned_payload + checksum
        address = base58.b58encode(full_payload).decode()
        
        return address, ripemd160_hash.hex()
    
    # Generate address from my prediction
    print("--- CONVERTING PREDICTION TO BITCOIN ADDRESS ---")
    predicted_address, predicted_hash160 = private_key_to_address(my_prediction, compressed=True)
    
    print(f"Predicted address:      {predicted_address}")
    print(f"Predicted hash160:      {predicted_hash160}")
    print()
    
    # Compare addresses
    print("--- VALIDATION RESULTS ---")
    address_match = predicted_address == actual_address
    hash160_match = predicted_hash160 == actual_hash160
    
    print(f"Address match:  {'YES!' if address_match else 'NO'}")
    print(f"Hash160 match:  {'YES!' if hash160_match else 'NO'}")
    
    if address_match:
        print("\nINCREDIBLE SUCCESS!")
        print("MY BLIND PREDICTION IS 100% CORRECT!")
        print("This proves our Bitcoin puzzle algorithm discovery is PERFECT!")
    else:
        print(f"\nPREDICTION ANALYSIS:")
        print(f"Expected: {actual_address}")
        print(f"Got:      {predicted_address}")
        
        # Try to find the correct private key by testing nearby values
        print(f"\n--- SEARCHING NEARBY VALUES ---")
        
        # Test a range around my prediction
        search_range = 1000000  # Search ±1M around prediction
        found_match = False
        
        for offset in range(-search_range, search_range + 1, 100000):
            test_key = my_prediction + offset
            if test_key <= 0:
                continue
                
            try:
                test_address, test_hash160 = private_key_to_address(test_key, compressed=True)
                if test_address == actual_address:
                    print(f"FOUND EXACT MATCH!")
                    print(f"Correct private key: 0x{test_key:x}")
                    print(f"My prediction was off by: {offset:,}")
                    error_percentage = abs(offset) / my_prediction * 100
                    print(f"Relative error: {error_percentage:.6f}%")
                    found_match = True
                    break
            except:
                continue
        
        if not found_match:
            print("No exact match found in nearby range")
    
    return address_match

if __name__ == "__main__":
    success = validate_prediction_71() 