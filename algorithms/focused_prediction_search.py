#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused search around my original prediction for position 71"""

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

def focused_search_around_prediction():
    """Focused search around my original prediction"""
    
    print("FOCUSED SEARCH AROUND MY PREDICTION FOR POSITION 71")
    print("=" * 60)
    
    target_address = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
    my_prediction = 0x68f5c28f5c28f60000
    
    print(f"Target address: {target_address}")
    print(f"My prediction:  0x{my_prediction:x}")
    print(f"My prediction:  {my_prediction:,}")
    print()
    
    # Create focused search ranges around my prediction
    search_ranges = [
        # Very close to my prediction (±1M)
        (my_prediction - 1000000, my_prediction + 1000000, 1, "Very close (±1M, step=1)"),
        
        # Close to my prediction (±10M)
        (my_prediction - 10000000, my_prediction + 10000000, 100, "Close (±10M, step=100)"),
        
        # Nearby my prediction (±100M)
        (my_prediction - 100000000, my_prediction + 100000000, 1000, "Nearby (±100M, step=1k)"),
        
        # Around my prediction (±1B)
        (my_prediction - 1000000000, my_prediction + 1000000000, 10000, "Around (±1B, step=10k)"),
        
        # Broader area (±10B)
        (my_prediction - 10000000000, my_prediction + 10000000000, 100000, "Broader (±10B, step=100k)"),
    ]
    
    print("Search ranges around my prediction:")
    for i, (start, end, step, desc) in enumerate(search_ranges):
        keys_to_test = (end - start) // step
        print(f"  {i+1}. {desc}")
        print(f"     Range: 0x{start:x} to 0x{end:x}")
        print(f"     Keys to test: {keys_to_test:,}")
    print()
    
    start_time = time.time()
    total_tested = 0
    
    for range_idx, (start_range, end_range, step, desc) in enumerate(search_ranges):
        print(f"\nSearching range {range_idx + 1}: {desc}")
        print(f"Range: 0x{start_range:x} to 0x{end_range:x}, step={step}")
        
        range_tested = 0
        
        for key in range(start_range, end_range, step):
            total_tested += 1
            range_tested += 1
            
            address = private_key_to_address(key, compressed=True)
            
            if address == target_address:
                elapsed = time.time() - start_time
                print(f"\n🎉 FOUND THE KEY! 🎉")
                print(f"Private key: 0x{key:x}")
                print(f"Private key: {key:,}")
                print(f"Found in range: {desc}")
                print(f"Search time: {elapsed:.2f} seconds")
                print(f"Total keys tested: {total_tested:,}")
                
                # Verify the result
                verify = private_key_to_address(key, compressed=True)
                print(f"\nVerification:")
                print(f"Generated address: {verify}")
                print(f"Target address:    {target_address}")
                print(f"Match: {'✅ YES' if verify == target_address else '❌ NO'}")
                
                # Analyze how close my prediction was
                prediction_diff = key - my_prediction
                prediction_error = abs(prediction_diff) / key * 100
                
                print(f"\nPrediction Analysis:")
                print(f"My prediction:     0x{my_prediction:x}")
                print(f"Actual key:        0x{key:x}")
                print(f"Difference:        {prediction_diff:,}")
                print(f"Relative error:    {prediction_error:.6f}%")
                print(f"Accuracy:          {100 - prediction_error:.6f}%")
                
                if abs(prediction_diff) < 1000000:
                    print("🎯 INCREDIBLE! Within 1 million of my prediction!")
                elif abs(prediction_diff) < 10000000:
                    print("🎯 AMAZING! Within 10 million of my prediction!")
                elif abs(prediction_diff) < 100000000:
                    print("🎯 EXCELLENT! Within 100 million of my prediction!")
                else:
                    print("📊 Good prediction in the right general area!")
                
                # Pattern analysis
                base_2_70 = 2 ** 70
                base_2_71 = 2 ** 71
                
                diff_70 = key - base_2_70
                diff_71 = key - base_2_71
                percent_70 = (diff_70 / base_2_70) * 100
                percent_71 = (diff_71 / base_2_71) * 100
                
                print(f"\nBitcoin Puzzle Pattern Analysis:")
                print(f"2^70 base:         0x{base_2_70:x}")
                print(f"2^71 base:         0x{base_2_71:x}")
                print(f"Actual key:        0x{key:x}")
                print(f"Diff from 2^70:    {percent_70:.3f}%")
                print(f"Diff from 2^71:    {percent_71:.3f}%")
                
                if abs(percent_70) < abs(percent_71):
                    print(f"✅ Position 71 follows 2^(n-1) = 2^70 pattern with {percent_70:.3f}% adjustment")
                else:
                    print(f"✅ Position 71 follows 2^n = 2^71 pattern with {percent_71:.3f}% adjustment")
                
                return key
            
            # Progress reporting
            if range_tested % 10000 == 0:
                elapsed = time.time() - start_time
                rate = total_tested / elapsed if elapsed > 0 else 0
                progress = (key - start_range) / (end_range - start_range) * 100
                print(f"  Progress: {progress:.1f}% | Tested: {range_tested:,} | Total: {total_tested:,} | Rate: {rate:.0f}/s | Current: 0x{key:x}")
        
        elapsed = time.time() - start_time
        print(f"Completed range {range_idx + 1}: {range_tested:,} keys tested in {elapsed:.1f}s")
    
    elapsed_total = time.time() - start_time
    print(f"\n--- SEARCH COMPLETE ---")
    print(f"Total time: {elapsed_total:.1f} seconds")
    print(f"Total keys tested: {total_tested:,}")
    print(f"Average rate: {total_tested/elapsed_total:.0f} keys/second")
    print("❌ Key not found in prediction area")
    
    return None

if __name__ == "__main__":
    result = focused_search_around_prediction() 