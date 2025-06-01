#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive search for position 71 private key"""

import hashlib
import base58
import ecdsa
import time

def comprehensive_search_71():
    """Comprehensive search for the actual private key of position 71"""
    
    print("COMPREHENSIVE SEARCH FOR POSITION 71 PRIVATE KEY")
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
    
    # Search strategy: Check multiple ranges
    print("--- SEARCH STRATEGY ---")
    print("1. Check if key follows unexpected patterns")
    print("2. Search around known position 70 key")
    print("3. Search broader ranges")
    print()
    
    # Known position 70 from extended dataset
    pos_70_key = 0x349b84b6431a6c4ef1  # From our extended data
    print(f"Known position 70 key: 0x{pos_70_key:x}")
    
    # Strategy 1: Check if position 71 is close to position 70
    print("\n--- STRATEGY 1: Search around position 70 ---")
    start_time = time.time()
    
    search_start = pos_70_key
    search_range = 10000000000  # 10 billion
    step_size = 1000000  # 1 million step
    
    print(f"Searching from 0x{search_start:x} with range ±{search_range:,}")
    
    found_key = None
    tests_performed = 0
    
    for offset in range(-search_range, search_range + 1, step_size):
        candidate = search_start + offset
        if candidate <= 0:
            continue
            
        tests_performed += 1
        if tests_performed % 1000 == 0:
            elapsed = time.time() - start_time
            print(f"  Tested {tests_performed:,} keys in {elapsed:.1f}s (rate: {tests_performed/elapsed:.0f}/s)")
            
        address, hash160 = private_key_to_address(candidate, compressed=True)
        if address == target_address:
            found_key = candidate
            print(f"\nFOUND MATCH!")
            print(f"Private key: 0x{candidate:x}")
            print(f"Offset from pos 70: {offset:,}")
            break
    
    if not found_key:
        print("Not found around position 70")
        
        # Strategy 2: Check expected bit ranges
        print("\n--- STRATEGY 2: Check expected bit ranges ---")
        
        # Maybe the key is in the 70-bit range but not following expected patterns
        for bit_length in [70, 71, 69, 72, 68]:
            print(f"\nChecking {bit_length}-bit range...")
            
            if bit_length < 70:
                range_start = 2 ** (bit_length - 1)
                range_end = 2 ** bit_length
            else:
                range_start = 2 ** (bit_length - 1)
                range_end = 2 ** bit_length
            
            # Sample the range with strategic points
            test_points = [
                range_start,  # Start of range
                range_start + (range_end - range_start) // 4,  # 25%
                range_start + (range_end - range_start) // 2,  # 50%
                range_start + 3 * (range_end - range_start) // 4,  # 75%
                range_end - 1,  # End of range
            ]
            
            # Add some random-ish points
            for i in range(1, 20):
                fraction = i / 20.0
                point = int(range_start + fraction * (range_end - range_start))
                test_points.append(point)
            
            for candidate in test_points:
                tests_performed += 1
                address, hash160 = private_key_to_address(candidate, compressed=True)
                if address == target_address:
                    found_key = candidate
                    print(f"\nFOUND MATCH!")
                    print(f"Private key: 0x{candidate:x}")
                    print(f"Bit length: {bit_length}")
                    break
            
            if found_key:
                break
    
    if not found_key:
        # Strategy 3: More exhaustive search in smaller chunks
        print("\n--- STRATEGY 3: Exhaustive search in chunks ---")
        
        # Based on the pattern, position 71 should be close to 2^70 or 2^71
        bases = [2**70, 2**71]
        
        for base in bases:
            print(f"\nSearching around 2^{base.bit_length()-1}: 0x{base:x}")
            
            # Search in smaller chunks around the base
            chunk_size = 1000000000  # 1 billion
            step_size = 100000  # 100k step
            
            for chunk_offset in [-chunk_size, 0, chunk_size]:
                chunk_start = base + chunk_offset
                if chunk_start <= 0:
                    continue
                    
                print(f"  Searching chunk starting at 0x{chunk_start:x}")
                
                for offset in range(0, chunk_size, step_size):
                    candidate = chunk_start + offset
                    tests_performed += 1
                    
                    if tests_performed % 5000 == 0:
                        elapsed = time.time() - start_time
                        print(f"    Tested {tests_performed:,} total keys in {elapsed:.1f}s")
                    
                    address, hash160 = private_key_to_address(candidate, compressed=True)
                    if address == target_address:
                        found_key = candidate
                        print(f"\nFOUND MATCH!")
                        print(f"Private key: 0x{candidate:x}")
                        break
                
                if found_key:
                    break
            
            if found_key:
                break
    
    elapsed_total = time.time() - start_time
    print(f"\n--- SEARCH COMPLETE ---")
    print(f"Total keys tested: {tests_performed:,}")
    print(f"Total time: {elapsed_total:.1f} seconds")
    print(f"Search rate: {tests_performed/elapsed_total:.0f} keys/second")
    
    if found_key:
        print(f"\n" + "="*60)
        print("SUCCESS! POSITION 71 PRIVATE KEY FOUND!")
        print("="*60)
        print(f"Private key: 0x{found_key:x}")
        print(f"Decimal: {found_key:,}")
        
        # Analyze the pattern
        print(f"\n--- PATTERN ANALYSIS ---")
        
        # Compare to expected patterns
        base_2_70 = 2 ** 70
        base_2_71 = 2 ** 71
        
        diff_70 = found_key - base_2_70
        diff_71 = found_key - base_2_71
        percent_70 = (diff_70 / base_2_70) * 100
        percent_71 = (diff_71 / base_2_71) * 100
        
        print(f"2^70 base:  0x{base_2_70:x}")
        print(f"2^71 base:  0x{base_2_71:x}")
        print(f"Found key:  0x{found_key:x}")
        print()
        print(f"Difference from 2^70: {diff_70:,} ({percent_70:.3f}%)")
        print(f"Difference from 2^71: {diff_71:,} ({percent_71:.3f}%)")
        
        # Compare to position 70
        if pos_70_key:
            diff_from_70 = found_key - pos_70_key
            multiplier = found_key / pos_70_key
            print(f"\nComparison to position 70:")
            print(f"Position 70: 0x{pos_70_key:x}")
            print(f"Position 71: 0x{found_key:x}")
            print(f"Difference:  {diff_from_70:,}")
            print(f"Multiplier:  {multiplier:.6f}x")
        
        return found_key
    else:
        print(f"\nPrivate key not found after testing {tests_performed:,} candidates")
        print("The key might be in an unexpected range or the search needs optimization")
        return None

if __name__ == "__main__":
    result = comprehensive_search_71() 