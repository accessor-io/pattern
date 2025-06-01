#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Highly targeted search for position 71 private key using pattern analysis"""

import hashlib
import base58
import ecdsa
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

def private_key_to_address(private_key_int, compressed=True):
    """Convert private key to Bitcoin address - optimized version"""
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

def search_range(start_key, end_key, target_address, worker_id=0):
    """Search a specific range for the target address"""
    keys_tested = 0
    step = 1000  # Test every 1000th key for speed
    
    for key in range(start_key, end_key, step):
        keys_tested += 1
        address = private_key_to_address(key, compressed=True)
        
        if address == target_address:
            return key, keys_tested
        
        # Progress reporting
        if keys_tested % 100000 == 0:
            print(f"Worker {worker_id}: Tested {keys_tested:,} keys, current: 0x{key:x}")
    
    return None, keys_tested

def targeted_search_71():
    """Highly targeted search for position 71 based on our pattern analysis"""
    
    print("TARGETED SEARCH FOR POSITION 71 PRIVATE KEY")
    print("=" * 60)
    
    target_address = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
    print(f"Target address: {target_address}")
    print()
    
    # Known position 70 key from our extended dataset
    pos_70_key = 0x349b84b6431a6c4ef1
    
    print("--- PATTERN-BASED SEARCH STRATEGY ---")
    print("Based on our pattern analysis:")
    print("- Position 70 follows 2^70 pattern with ~17.8% negative adjustment")
    print("- Position 71 likely follows 2^71 pattern with similar adjustment")
    print("- OR could follow 2^70 pattern like neighboring positions")
    print()
    
    # Calculate search ranges based on patterns
    base_2_70 = 2 ** 70
    base_2_71 = 2 ** 71
    
    search_ranges = []
    
    # Range 1: Around 2^71 with -15% to -25% adjustment (based on pattern)
    range1_center = int(base_2_71 * 0.82)  # -18% adjustment
    range1_size = int(base_2_71 * 0.05)    # ±5% around center
    search_ranges.append((
        range1_center - range1_size,
        range1_center + range1_size,
        "2^71 with ~18% negative adjustment"
    ))
    
    # Range 2: Around 2^70 with positive adjustment (alternative pattern)
    range2_center = int(base_2_70 * 1.15)  # +15% adjustment
    range2_size = int(base_2_70 * 0.05)    # ±5% around center
    search_ranges.append((
        range2_center - range2_size,
        range2_center + range2_size,
        "2^70 with ~15% positive adjustment"
    ))
    
    # Range 3: Close to position 70 (sequential pattern)
    range3_center = pos_70_key * 2  # Double the previous key
    range3_size = pos_70_key // 2   # Large range around it
    search_ranges.append((
        range3_center - range3_size,
        range3_center + range3_size,
        "Sequential: ~2x position 70"
    ))
    
    # Range 4: My original prediction area (more thorough)
    my_prediction = 0x68f5c28f5c28f60000
    range4_size = int(my_prediction * 0.1)  # ±10% around my prediction
    search_ranges.append((
        my_prediction - range4_size,
        my_prediction + range4_size,
        "Around my original prediction"
    ))
    
    # Range 5: Broader 2^71 search
    range5_start = int(base_2_71 * 0.7)   # 30% below
    range5_end = int(base_2_71 * 1.3)     # 30% above
    search_ranges.append((
        range5_start,
        range5_end,
        "Broad 2^71 range (70%-130%)"
    ))
    
    print("Search ranges:")
    total_keys_to_test = 0
    for i, (start, end, desc) in enumerate(search_ranges):
        range_size = (end - start) // 1000  # We test every 1000th key
        total_keys_to_test += range_size
        print(f"  {i+1}. {desc}")
        print(f"     Range: 0x{start:x} to 0x{end:x}")
        print(f"     Keys to test: {range_size:,}")
    
    print(f"\nTotal keys to test: {total_keys_to_test:,}")
    print()
    
    # Use multiprocessing for parallel search
    num_workers = min(8, multiprocessing.cpu_count())
    print(f"Using {num_workers} worker processes")
    
    start_time = time.time()
    found_key = None
    total_tested = 0
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        
        # Submit search tasks for each range
        for range_idx, (range_start, range_end, range_desc) in enumerate(search_ranges):
            # Split each range across workers
            range_size = range_end - range_start
            chunk_size = range_size // num_workers
            
            for worker_id in range(num_workers):
                chunk_start = range_start + worker_id * chunk_size
                chunk_end = chunk_start + chunk_size
                if worker_id == num_workers - 1:  # Last worker gets remainder
                    chunk_end = range_end
                
                future = executor.submit(
                    search_range, 
                    chunk_start, 
                    chunk_end, 
                    target_address, 
                    f"{range_idx+1}.{worker_id+1}"
                )
                futures.append((future, range_desc, chunk_start, chunk_end))
        
        print(f"Submitted {len(futures)} search tasks")
        print("Searching...")
        
        # Process results as they complete
        for future, range_desc, chunk_start, chunk_end in as_completed(futures):
            try:
                result, keys_tested = future.result()
                total_tested += keys_tested
                
                if result is not None:
                    found_key = result
                    print(f"\n*** FOUND KEY! ***")
                    print(f"Range: {range_desc}")
                    print(f"Private key: 0x{found_key:x}")
                    
                    # Cancel remaining tasks
                    for f, _, _, _ in futures:
                        f.cancel()
                    break
                else:
                    elapsed = time.time() - start_time
                    rate = total_tested / elapsed if elapsed > 0 else 0
                    print(f"Completed range {range_desc}: {keys_tested:,} keys tested")
                    print(f"Total progress: {total_tested:,} keys, {rate:.0f} keys/sec")
            
            except Exception as e:
                print(f"Error in search task: {e}")
    
    elapsed_total = time.time() - start_time
    
    print(f"\n--- SEARCH COMPLETE ---")
    print(f"Total time: {elapsed_total:.1f} seconds") 
    print(f"Total keys tested: {total_tested:,}")
    print(f"Average rate: {total_tested/elapsed_total:.0f} keys/second")
    
    if found_key:
        print(f"\n" + "="*60)
        print("SUCCESS! POSITION 71 PRIVATE KEY FOUND!")
        print("="*60)
        print(f"Private key: 0x{found_key:x}")
        print(f"Decimal: {found_key:,}")
        
        # Verify the key
        verify_address = private_key_to_address(found_key, compressed=True)
        print(f"Generated address: {verify_address}")
        print(f"Matches target: {'YES' if verify_address == target_address else 'NO'}")
        
        # Pattern analysis
        print(f"\n--- PATTERN ANALYSIS ---")
        base_2_70 = 2 ** 70
        base_2_71 = 2 ** 71
        
        diff_70 = found_key - base_2_70
        diff_71 = found_key - base_2_71
        percent_70 = (diff_70 / base_2_70) * 100
        percent_71 = (diff_71 / base_2_71) * 100
        
        print(f"Found key:  0x{found_key:x}")
        print(f"2^70 base:  0x{base_2_70:x}")
        print(f"2^71 base:  0x{base_2_71:x}")
        print()
        print(f"Difference from 2^70: {diff_70:,} ({percent_70:.3f}%)")
        print(f"Difference from 2^71: {diff_71:,} ({percent_71:.3f}%)")
        
        # Determine pattern
        if abs(percent_70) < abs(percent_71):
            print(f"\nPATTERN: Position 71 follows 2^(n-1) = 2^70 pattern")
            print(f"Adjustment: {percent_70:.3f}% of 2^70")
        else:
            print(f"\nPATTERN: Position 71 follows 2^n = 2^71 pattern")
            print(f"Adjustment: {percent_71:.3f}% of 2^71")
        
        # Compare to my prediction
        my_prediction = 0x68f5c28f5c28f60000
        prediction_diff = found_key - my_prediction
        prediction_error = abs(prediction_diff) / found_key * 100
        
        print(f"\n--- MY PREDICTION ANALYSIS ---")
        print(f"My prediction:   0x{my_prediction:x}")
        print(f"Actual key:      0x{found_key:x}")
        print(f"Difference:      {prediction_diff:,}")
        print(f"Relative error:  {prediction_error:.3f}%")
        
        return found_key
    else:
        print(f"\nPrivate key not found in {total_tested:,} tests")
        print("Consider expanding search ranges or refining pattern analysis")
        return None

if __name__ == "__main__":
    result = targeted_search_71() 