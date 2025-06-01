#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find the actual private key for position 71 and analyze the pattern"""

import hashlib
import base58
import ecdsa

def find_key_for_address_71():
    """Find the actual private key for Bitcoin address 1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"""
    
    print("FINDING ACTUAL PRIVATE KEY FOR POSITION 71")
    print("=" * 60)
    
    target_address = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
    target_hash160 = "f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8"
    
    print(f"Target address: {target_address}")
    print(f"Target hash160: {target_hash160}")
    print()
    
    def private_key_to_address(private_key_int, compressed=True):
        """Convert private key to Bitcoin address"""
        try:
            private_key_bytes = private_key_int.to_bytes(32, 'big')
            sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
            vk = sk.get_verifying_key()
            
            if compressed:
                x = vk.pubkey.point.x()
                y = vk.pubkey.point.y()
                if y % 2 == 0:
                    public_key = b'\x02' + x.to_bytes(32, 'big')
                else:
                    public_key = b'\x03' + x.to_bytes(32, 'big')
            else:
                public_key = b'\x04' + vk.to_string()
            
            sha256_hash = hashlib.sha256(public_key).digest()
            ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
            versioned_payload = b'\x00' + ripemd160_hash
            checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
            full_payload = versioned_payload + checksum
            address = base58.b58encode(full_payload).decode()
            
            return address, ripemd160_hash.hex()
        except:
            return None, None
    
    # Search parameters for position 71
    print("--- SEARCH PARAMETERS ---")
    position = 71
    
    # Position 71 should be in the range 2^70 to 2^71
    min_range = 2 ** 70
    max_range = 2 ** 71
    
    print(f"Position {position} expected range:")
    print(f"Min (2^70): 0x{min_range:x}")
    print(f"Max (2^71): 0x{max_range:x}")
    print()
    
    # My prediction for comparison
    my_prediction = 0x68f5c28f5c28f60000
    print(f"My prediction: 0x{my_prediction:x}")
    print()
    
    # Start search from known pattern bases
    base_2_70 = 2 ** 70
    base_2_71 = 2 ** 71
    
    print("--- SEARCHING FOR ACTUAL KEY ---")
    print("Testing pattern-based candidates...")
    
    # Test various pattern adjustments
    test_candidates = []
    
    # 2^70 pattern with various adjustments
    for adj_percent in range(-50, 51, 1):  # -50% to +50% in 1% steps
        adjustment = int(base_2_70 * adj_percent / 100)
        candidate = base_2_70 + adjustment
        if min_range <= candidate <= max_range:
            test_candidates.append(("2^70 + {}%".format(adj_percent), candidate))
    
    # 2^71 pattern with various adjustments  
    for adj_percent in range(-50, 51, 1):  # -50% to +50% in 1% steps
        adjustment = int(base_2_71 * adj_percent / 100)
        candidate = base_2_71 + adjustment
        if min_range <= candidate <= max_range:
            test_candidates.append(("2^71 + {}%".format(adj_percent), candidate))
    
    # Test specific bit patterns
    for bit_offset in range(0, 64):
        # Set specific bits
        candidate1 = base_2_70 | (1 << bit_offset)
        candidate2 = base_2_71 | (1 << bit_offset)
        if min_range <= candidate1 <= max_range:
            test_candidates.append(("2^70 | (1<<{})".format(bit_offset), candidate1))
        if min_range <= candidate2 <= max_range:
            test_candidates.append(("2^71 | (1<<{})".format(bit_offset), candidate2))
    
    print(f"Testing {len(test_candidates)} candidates...")
    
    found_key = None
    found_pattern = None
    
    for i, (pattern_desc, candidate) in enumerate(test_candidates):
        if i % 1000 == 0:
            print(f"  Tested {i}/{len(test_candidates)} candidates...")
            
        address, hash160 = private_key_to_address(candidate, compressed=True)
        if address == target_address:
            found_key = candidate
            found_pattern = pattern_desc
            print(f"\nFOUND MATCH!")
            print(f"Pattern: {pattern_desc}")
            print(f"Private key: 0x{candidate:x}")
            break
    
    if not found_key:
        # More exhaustive search around key bases
        print("\nPattern search failed. Trying exhaustive search around bases...")
        
        search_bases = [base_2_70, base_2_71, my_prediction]
        search_range = 100000000  # ±100M around each base
        
        for base_name, search_base in [("2^70", base_2_70), ("2^71", base_2_71), ("My prediction", my_prediction)]:
            print(f"\nSearching around {base_name}: 0x{search_base:x}")
            
            for offset in range(-search_range, search_range + 1, 1000000):  # 1M step
                candidate = search_base + offset
                if candidate <= 0 or candidate > max_range:
                    continue
                    
                address, hash160 = private_key_to_address(candidate, compressed=True)
                if address == target_address:
                    found_key = candidate
                    found_pattern = f"{base_name} + {offset:,}"
                    print(f"\nFOUND MATCH!")
                    print(f"Pattern: {found_pattern}")
                    print(f"Private key: 0x{candidate:x}")
                    break
            
            if found_key:
                break
    
    if found_key:
        print("\n" + "="*60)
        print("SUCCESS! ACTUAL POSITION 71 KEY FOUND")
        print("="*60)
        print(f"Actual private key: 0x{found_key:x}")
        print(f"Pattern: {found_pattern}")
        print()
        
        # Analyze the pattern
        print("--- PATTERN ANALYSIS ---")
        
        # Compare to powers of 2
        diff_2_70 = found_key - base_2_70
        diff_2_71 = found_key - base_2_71
        percent_2_70 = (diff_2_70 / base_2_70) * 100
        percent_2_71 = (diff_2_71 / base_2_71) * 100
        
        print(f"Actual key:      0x{found_key:x}")
        print(f"2^70 base:       0x{base_2_70:x}")
        print(f"2^71 base:       0x{base_2_71:x}")
        print()
        print(f"Difference from 2^70: {diff_2_70:,} ({percent_2_70:.3f}%)")
        print(f"Difference from 2^71: {diff_2_71:,} ({percent_2_71:.3f}%)")
        print()
        
        # Determine which pattern it follows
        if abs(percent_2_70) < abs(percent_2_71):
            print(f"PATTERN: Position 71 follows 2^(n-1) = 2^70 pattern")
            print(f"Adjustment: {percent_2_70:.3f}% of base")
        else:
            print(f"PATTERN: Position 71 follows 2^n = 2^71 pattern") 
            print(f"Adjustment: {percent_2_71:.3f}% of base")
        
        # Compare to my prediction
        prediction_diff = found_key - my_prediction
        prediction_error = abs(prediction_diff) / found_key * 100
        
        print(f"\n--- MY PREDICTION ANALYSIS ---")
        print(f"My prediction:   0x{my_prediction:x}")
        print(f"Actual key:      0x{found_key:x}")
        print(f"Difference:      {prediction_diff:,}")
        print(f"Relative error:  {prediction_error:.3f}%")
        
        return found_key, found_pattern
    else:
        print("\nKey not found in search range!")
        return None, None

if __name__ == "__main__":
    actual_key, pattern = find_key_for_address_71() 