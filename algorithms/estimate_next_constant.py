#!/usr/bin/env python3
"""Estimate the next constant by analyzing the growth pattern"""

import math
import hashlib
import base58
import ecdsa

# Secp256k1 constants
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def sha256(data):
    return hashlib.sha256(data).digest()

def ripemd160(data):
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(data):
    return ripemd160(sha256(data))

def base58_encode(data):
    versioned = b'\x00' + data
    checksum = sha256(sha256(versioned))[:4]
    return base58.b58encode(versioned + checksum).decode()

def privkey_to_pubkey(privkey_int, compressed=True):
    sk = ecdsa.SigningKey.from_secret_exponent(privkey_int, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    point = vk.pubkey.point
    
    if compressed:
        x = point.x()
        y = point.y()
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        return prefix + x.to_bytes(32, 'big')
    else:
        x = point.x()
        y = point.y()
        return b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')

def pubkey_to_address(pubkey_bytes):
    h160 = hash160(pubkey_bytes)
    return base58_encode(h160)

def analyze_growth_patterns():
    """Analyze the growth patterns of differences between consecutive positions"""
    
    print("🔍 ANALYZING GROWTH PATTERNS TO ESTIMATE NEXT CONSTANT")
    print("=" * 70)
    
    # Load verified keys
    verified_keys = {}
    try:
        with open('verified_bitcoin_sequence.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or not line[0].isdigit():
                    continue
                parts = line.split('.', 1)
                if len(parts) != 2:
                    continue
                pos = int(parts[0])
                hex_and_status = parts[1].strip()
                if ' - ' in hex_and_status:
                    hex_key = hex_and_status.split(' - ')[0].strip()
                else:
                    hex_key = hex_and_status.strip()
                
                # Only load verified positions (up to 68)
                if pos <= 68 and 'KNOWN' in hex_and_status:
                    verified_keys[pos] = int(hex_key, 16)
                    
        print(f"✓ Loaded {len(verified_keys)} verified keys")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Calculate differences (constants) between consecutive positions
    differences = {}
    ratios = {}
    
    print(f"\n--- Calculating Differences (Constants) ---")
    for pos in range(2, 69):  # Up to position 68
        if pos in verified_keys and pos-1 in verified_keys:
            diff = verified_keys[pos] - verified_keys[pos-1]
            differences[pos] = diff
            
            if pos > 2 and differences.get(pos-1):
                ratio = diff / differences[pos-1]
                ratios[pos] = ratio
            
            print(f"Position {pos-1} → {pos}: {diff:,}")
    
    print(f"\n--- Analyzing Growth Ratios ---")
    for pos in sorted(ratios.keys()):
        print(f"Position {pos}: ratio = {ratios[pos]:.3f}")
    
    # Analyze different growth patterns
    print(f"\n--- Growth Pattern Analysis ---")
    
    # 1. Recent trend analysis (last 10 positions)
    recent_diffs = [differences[i] for i in range(59, 69) if i in differences]
    recent_ratios = [ratios[i] for i in range(60, 69) if i in ratios]
    
    if recent_diffs and recent_ratios:
        avg_recent_ratio = sum(recent_ratios) / len(recent_ratios)
        median_recent_ratio = sorted(recent_ratios)[len(recent_ratios)//2]
        last_diff = recent_diffs[-1]
        
        print(f"Recent differences (59-68): {[f'{d:,}' for d in recent_diffs[-5:]]}")
        print(f"Recent ratios (60-68): {[f'{r:.3f}' for r in recent_ratios[-5:]]}")
        print(f"Average recent ratio: {avg_recent_ratio:.3f}")
        print(f"Median recent ratio: {median_recent_ratio:.3f}")
        print(f"Last difference (67→68): {last_diff:,}")
        
        # Estimate next difference using different methods
        estimates = {}
        
        # Method 1: Average ratio
        estimates['avg_ratio'] = int(last_diff * avg_recent_ratio)
        
        # Method 2: Median ratio
        estimates['median_ratio'] = int(last_diff * median_recent_ratio)
        
        # Method 3: Last ratio
        if recent_ratios:
            estimates['last_ratio'] = int(last_diff * recent_ratios[-1])
        
        # Method 4: Exponential trend (if consistent growth)
        if len(recent_ratios) >= 3:
            # Fit exponential growth
            ratio_trend = sum(recent_ratios[-3:]) / 3
            estimates['trend_ratio'] = int(last_diff * ratio_trend)
        
        # Method 5: Powers of 2 analysis (based on our Phase 2 findings)
        # Look for closest power of 2 patterns in recent differences
        power_estimates = []
        for shift in range(60, 75):
            power_of_2 = 1 << shift
            if abs(power_of_2 - last_diff) < power_of_2 * 0.5:  # Within 50%
                next_power = 1 << (shift + 1)
                power_estimates.append(next_power)
                print(f"Pattern: diff ~2^{shift}, next could be ~2^{shift+1} = {next_power:,}")
        
        if power_estimates:
            estimates['power_of_2'] = power_estimates[0]  # Take first estimate
        
        print(f"\n--- ESTIMATES FOR POSITION 69 DIFFERENCE ---")
        for method, estimate in estimates.items():
            print(f"{method:15}: {estimate:,}")
        
        # Calculate consensus estimate
        estimate_values = list(estimates.values())
        consensus = int(sum(estimate_values) / len(estimate_values))
        estimates['consensus'] = consensus
        
        print(f"{'consensus':15}: {consensus:,}")
        
        return estimates, verified_keys[68]
    
    return None, None

def test_estimates():
    """Test the estimated constants against the actual puzzle 69 address"""
    
    estimates, base_key = analyze_growth_patterns()
    
    if not estimates or not base_key:
        print("Could not generate estimates")
        return
    
    target_address = "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG"  # Puzzle 69
    
    print(f"\n--- TESTING ESTIMATES AGAINST PUZZLE 69 ---")
    print(f"Base key (pos 68): 0x{base_key:x}")
    print(f"Target address: {target_address}")
    print()
    
    for method, estimated_diff in estimates.items():
        predicted_key = (base_key + estimated_diff) % N
        
        try:
            pubkey_compressed = privkey_to_pubkey(predicted_key, compressed=True)
            predicted_address = pubkey_to_address(pubkey_compressed)
            
            match = "🎉 MATCH!" if predicted_address == target_address else "❌ No match"
            
            print(f"{method:15}: diff = {estimated_diff:,}")
            print(f"                 key = 0x{predicted_key:x}")
            print(f"                 addr = {predicted_address}")
            print(f"                 {match}")
            print()
            
            if predicted_address == target_address:
                print(f"🚀 BREAKTHROUGH! Found the pattern for position 69!")
                print(f"   Method: {method}")
                print(f"   Estimated difference: {estimated_diff:,}")
                print(f"   Private key: 0x{predicted_key:x}")
                return True
                
        except Exception as e:
            print(f"{method:15}: Error - {e}")
            continue
    
    # If no exact matches, try variations around the consensus
    print(f"--- TESTING VARIATIONS AROUND CONSENSUS ---")
    consensus = estimates.get('consensus', 0)
    
    # Try adjustments around the consensus estimate
    adjustments = [0, 1, -1, 2, -2, 5, -5, 10, -10, 100, -100, 1000, -1000, 10000, -10000]
    
    for adj in adjustments:
        test_diff = consensus + adj
        predicted_key = (base_key + test_diff) % N
        
        try:
            pubkey_compressed = privkey_to_pubkey(predicted_key, compressed=True)
            predicted_address = pubkey_to_address(pubkey_compressed)
            
            if predicted_address == target_address:
                print(f"🎉 MATCH FOUND!")
                print(f"   Consensus + {adj:,} = {test_diff:,}")
                print(f"   Private key: 0x{predicted_key:x}")
                print(f"   Address: {predicted_address}")
                return True
                
        except Exception:
            continue
    
    print(f"❌ No matches found with estimated constants")
    print(f"💡 The pattern for position 69 may be more complex than linear growth")
    return False

def detailed_trend_analysis():
    """Perform detailed trend analysis on the differences"""
    
    print(f"\n--- DETAILED TREND ANALYSIS ---")
    
    # Load data again for detailed analysis
    verified_keys = {}
    with open('verified_bitcoin_sequence.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            parts = line.split('.', 1)
            if len(parts) != 2:
                continue
            pos = int(parts[0])
            hex_and_status = parts[1].strip()
            if ' - ' in hex_and_status:
                hex_key = hex_and_status.split(' - ')[0].strip()
            else:
                hex_key = hex_and_status.strip()
            
            if pos <= 68 and 'KNOWN' in hex_and_status:
                verified_keys[pos] = int(hex_key, 16)
    
    # Calculate all differences
    diffs = []
    positions = []
    for pos in range(2, 69):
        if pos in verified_keys and pos-1 in verified_keys:
            diff = verified_keys[pos] - verified_keys[pos-1]
            diffs.append(diff)
            positions.append(pos)
    
    print(f"Total differences calculated: {len(diffs)}")
    
    # Analyze segments
    segments = {
        'early': (2, 10),
        'mid': (11, 30),
        'late': (31, 50),
        'recent': (51, 68)
    }
    
    for segment_name, (start, end) in segments.items():
        segment_diffs = [diffs[i] for i, pos in enumerate(positions) if start <= pos <= end]
        if segment_diffs:
            avg_diff = sum(segment_diffs) / len(segment_diffs)
            print(f"{segment_name:10} (pos {start:2}-{end:2}): avg = {avg_diff:,.0f}, count = {len(segment_diffs)}")
    
    # Growth acceleration analysis
    print(f"\nGrowth acceleration analysis:")
    for i in range(len(diffs)-1):
        if i >= len(diffs)-5:  # Last 5 differences
            growth = diffs[i+1] / diffs[i] if diffs[i] > 0 else 0
            print(f"Position {positions[i+1]:2}: {diffs[i]:12,} → {diffs[i+1]:12,} (×{growth:.3f})")

if __name__ == "__main__":
    test_estimates()
    detailed_trend_analysis() 