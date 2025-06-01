#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick focused search for position 71 private key"""

import hashlib
import base58
import ecdsa
import time

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
        
        return address
    except:
        return None

def quick_search_71():
    """Quick focused search for position 71"""
    
    print("QUICK SEARCH FOR POSITION 71 PRIVATE KEY")
    print("=" * 50)
    
    target_address = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
    print(f"Target: {target_address}")
    print()
    
    # Test specific candidate ranges
    candidates = []
    
    # Range 1: Around 2^71 with 18% negative adjustment
    base_2_71 = 2 ** 71
    center1 = int(base_2_71 * 0.82)  # -18%
    candidates.append((center1 - 1000000000, center1 + 1000000000, "2^71 - 18%"))
    
    # Range 2: Around 2^70 with 15% positive adjustment  
    base_2_70 = 2 ** 70
    center2 = int(base_2_70 * 1.15)  # +15%
    candidates.append((center2 - 1000000000, center2 + 1000000000, "2^70 + 15%"))
    
    # Range 3: Around my prediction
    my_pred = 0x68f5c28f5c28f60000
    candidates.append((my_pred - 1000000000, my_pred + 1000000000, "My prediction"))
    
    # Range 4: Sequential from position 70
    pos_70 = 0x349b84b6431a6c4ef1
    candidates.append((pos_70 * 2 - 1000000000, pos_70 * 2 + 1000000000, "2 * pos70"))
    
    # Range 5: Some specific test points
    test_points = [
        base_2_71,  # Exact 2^71
        base_2_70,  # Exact 2^70
        int(base_2_71 * 0.8),   # 2^71 - 20%
        int(base_2_71 * 0.85),  # 2^71 - 15%
        int(base_2_70 * 1.2),   # 2^70 + 20%
        int(base_2_70 * 1.1),   # 2^70 + 10%
    ]
    
    for point in test_points:
        candidates.append((point - 100000000, point + 100000000, f"Around 0x{point:x}"))
    
    print("Testing candidates...")
    start_time = time.time()
    total_tested = 0
    
    for start_range, end_range, desc in candidates:
        print(f"\nSearching {desc}: 0x{start_range:x} to 0x{end_range:x}")
        
        step = 10000  # Test every 10,000th key for speed
        keys_in_range = 0
        
        for key in range(start_range, end_range, step):
            total_tested += 1
            keys_in_range += 1
            
            address = private_key_to_address(key, compressed=True)
            
            if address == target_address:
                elapsed = time.time() - start_time
                print(f"\n*** FOUND IT! ***")
                print(f"Private key: 0x{key:x}")
                print(f"Range: {desc}")
                print(f"Time: {elapsed:.1f}s, Tested: {total_tested:,} keys")
                
                # Verify
                verify = private_key_to_address(key, compressed=True)
                print(f"Verification: {verify}")
                print(f"Match: {'YES' if verify == target_address else 'NO'}")
                
                # Pattern analysis
                diff_70 = key - base_2_70
                diff_71 = key - base_2_71
                percent_70 = (diff_70 / base_2_70) * 100
                percent_71 = (diff_71 / base_2_71) * 100
                
                print(f"\nPattern Analysis:")
                print(f"2^70 difference: {percent_70:.3f}%")
                print(f"2^71 difference: {percent_71:.3f}%")
                
                if abs(percent_70) < abs(percent_71):
                    print(f"Follows 2^70 pattern with {percent_70:.3f}% adjustment")
                else:
                    print(f"Follows 2^71 pattern with {percent_71:.3f}% adjustment")
                
                return key
            
            # Progress
            if keys_in_range % 100000 == 0:
                elapsed = time.time() - start_time
                rate = total_tested / elapsed if elapsed > 0 else 0
                print(f"  Tested {keys_in_range:,} in range, {total_tested:,} total, {rate:.0f}/s")
        
        print(f"  Completed range: {keys_in_range:,} keys tested")
    
    elapsed = time.time() - start_time
    print(f"\nSearch complete: {total_tested:,} keys tested in {elapsed:.1f}s")
    print("Key not found in tested ranges")
    return None

if __name__ == "__main__":
    result = quick_search_71() 