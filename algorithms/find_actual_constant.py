#!/usr/bin/env python3
"""
🔍 CONSTANT HUNTER - Find the exact mathematical constant
Focus on extracting the precise relationship between position and key
"""

import hashlib
import base58
import ecdsa
import math
from typing import Dict, List, Tuple, Optional

# Secp256k1 constants
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Known solutions
KNOWN_KEYS = {
    64: 0xf7051f27b09112d4,
    65: 0x1a838b13505b26867,
    66: 0x2832ed74f2b5e35ee,
    67: 0x730fc235c1942c1ae,
    68: 0xbebb3940cd0fc1491,
    70: 0x349b84b6431a6c4ef1,
    75: 0x4c5ce114686a1336e07,
    80: 0xea1a5c66dcc11b5ad180,
}

# Target addresses for verification
TARGET_ADDRESSES = {
    69: "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
    71: "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU", 
    72: "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
}

def privkey_to_address(private_key):
    """Convert private key to Bitcoin address"""
    try:
        sk = ecdsa.SigningKey.from_secret_exponent(private_key, curve=ecdsa.SECP256k1)
        vk = sk.verifying_key
        point = vk.pubkey.point
        
        x = point.x()
        y = point.y()
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        pubkey = prefix + x.to_bytes(32, 'big')
        
        # Hash160
        h = hashlib.sha256(pubkey).digest()
        h = hashlib.new('ripemd160', h).digest()
        
        # Add version byte and checksum
        versioned = b'\x00' + h
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        return base58.b58encode(versioned + checksum).decode()
    except:
        return None

def extract_constants():
    """Extract mathematical constants from known keys"""
    print("🔍 EXTRACTING MATHEMATICAL CONSTANTS")
    print("=" * 60)
    
    positions = sorted(KNOWN_KEYS.keys())
    
    # Method 1: Ratio analysis between consecutive keys
    print("📊 RATIO ANALYSIS:")
    ratios = []
    for i in range(len(positions) - 1):
        pos1, pos2 = positions[i], positions[i + 1]
        key1, key2 = KNOWN_KEYS[pos1], KNOWN_KEYS[pos2]
        
        ratio = key2 / key1
        ratios.append(ratio)
        
        print(f"  {pos1}→{pos2}: ratio = {ratio:.6f}")
    
    avg_ratio = sum(ratios) / len(ratios)
    print(f"  Average ratio: {avg_ratio:.6f}")
    print()
    
    # Method 2: Position-to-key constant analysis
    print("📊 POSITION-TO-KEY CONSTANT ANALYSIS:")
    constants = []
    for pos in positions:
        key = KNOWN_KEYS[pos]
        
        # Try different constant relationships
        c1 = key / (1 << (pos - 1))  # key / 2^(n-1)
        c2 = key / (1 << pos)        # key / 2^n
        c3 = key / (pos ** 2)        # key / n^2
        c4 = key / (pos ** 3)        # key / n^3
        c5 = key / math.sqrt(pos)    # key / sqrt(n)
        
        constants.append({
            'pos': pos,
            'key': key,
            'c1': c1,
            'c2': c2,
            'c3': c3,
            'c4': c4,
            'c5': c5
        })
        
        print(f"  Pos {pos:>2}: k/2^(n-1)={c1:.6f}, k/2^n={c2:.6f}, k/n^2={c3:.2e}, k/n^3={c4:.2e}")
    
    print()
    
    # Method 3: Look for consistent multipliers
    print("📊 CONSISTENT MULTIPLIER ANALYSIS:")
    
    # Check if k = 2^(n-1) * constant
    multipliers_n_minus_1 = []
    for pos in positions:
        key = KNOWN_KEYS[pos]
        base = 1 << (pos - 1)
        multiplier = key / base
        multipliers_n_minus_1.append(multiplier)
        print(f"  Pos {pos:>2}: {key:>20x} = 2^{pos-1} * {multiplier:.8f}")
    
    avg_mult_n_minus_1 = sum(multipliers_n_minus_1) / len(multipliers_n_minus_1)
    print(f"  Average multiplier: {avg_mult_n_minus_1:.8f}")
    print()
    
    # Check if k = 2^n * constant
    print("📊 2^n MULTIPLIER ANALYSIS:")
    multipliers_n = []
    for pos in positions:
        key = KNOWN_KEYS[pos]
        base = 1 << pos
        multiplier = key / base
        multipliers_n.append(multiplier)
        print(f"  Pos {pos:>2}: {key:>20x} = 2^{pos} * {multiplier:.8f}")
    
    avg_mult_n = sum(multipliers_n) / len(multipliers_n)
    print(f"  Average multiplier: {avg_mult_n:.8f}")
    print()
    
    return avg_mult_n_minus_1, avg_mult_n

def test_constant_predictions(const_n_minus_1, const_n):
    """Test predictions using extracted constants"""
    print("🎯 TESTING CONSTANT-BASED PREDICTIONS")
    print("=" * 60)
    
    # Test both constant types
    for test_pos in [69, 71, 72]:
        if test_pos not in TARGET_ADDRESSES:
            continue
            
        target_address = TARGET_ADDRESSES[test_pos]
        
        print(f"Position {test_pos}:")
        print(f"  Target: {target_address}")
        
        # Method 1: k = 2^(n-1) * constant
        pred_key_1 = int((1 << (test_pos - 1)) * const_n_minus_1)
        pred_addr_1 = privkey_to_address(pred_key_1)
        match_1 = "✅" if pred_addr_1 == target_address else "❌"
        
        print(f"  2^(n-1) method: 0x{pred_key_1:x}")
        print(f"  Predicted addr: {pred_addr_1}")
        print(f"  Match: {match_1}")
        
        # Method 2: k = 2^n * constant
        pred_key_2 = int((1 << test_pos) * const_n)
        pred_addr_2 = privkey_to_address(pred_key_2)
        match_2 = "✅" if pred_addr_2 == target_address else "❌"
        
        print(f"  2^n method:     0x{pred_key_2:x}")
        print(f"  Predicted addr: {pred_addr_2}")
        print(f"  Match: {match_2}")
        print()

def refined_constant_search():
    """More refined constant search with position-dependent analysis"""
    print("🔬 REFINED CONSTANT SEARCH")
    print("=" * 60)
    
    positions = sorted(KNOWN_KEYS.keys())
    
    # Look for position-dependent constants
    print("Position-dependent constant analysis:")
    
    for i, pos in enumerate(positions):
        key = KNOWN_KEYS[pos]
        
        # Try various position-dependent formulas
        formulas = [
            ("k = 2^(n-1) * (1 + n/100)", (1 << (pos-1)) * (1 + pos/100)),
            ("k = 2^(n-1) * (1 + n/1000)", (1 << (pos-1)) * (1 + pos/1000)),
            ("k = 2^(n-1) * sqrt(n)", (1 << (pos-1)) * math.sqrt(pos)),
            ("k = 2^(n-1) * log(n)", (1 << (pos-1)) * math.log(pos)),
            ("k = 2^(n-1) * (1 + 1/n)", (1 << (pos-1)) * (1 + 1/pos)),
            ("k = 2^(n-1) * φ", (1 << (pos-1)) * ((1 + math.sqrt(5))/2)),
            ("k = 2^(n-1) * π/2", (1 << (pos-1)) * (math.pi/2)),
            ("k = 2^(n-1) * e/2", (1 << (pos-1)) * (math.e/2)),
        ]
        
        print(f"\nPosition {pos}:")
        print(f"  Actual: 0x{key:x}")
        
        for formula_name, predicted in formulas:
            predicted = int(predicted)
            error = abs(key - predicted) / key * 100
            
            if error < 50:  # Only show reasonable matches
                print(f"  {formula_name}: 0x{predicted:x} (error: {error:.1f}%)")

def hunt_for_the_constant():
    """Main constant hunting function"""
    print("🎯 HUNTING FOR THE BITCOIN PUZZLE CONSTANT")
    print("=" * 80)
    print("Focusing on extracting the exact mathematical relationship...")
    print()
    
    # Extract basic constants
    const_n_minus_1, const_n = extract_constants()
    
    # Test predictions
    test_constant_predictions(const_n_minus_1, const_n)
    
    # Refined search
    refined_constant_search()
    
    print("=" * 80)
    print("🎯 CONSTANT EXTRACTION COMPLETE")
    print()
    print(f"💡 KEY FINDINGS:")
    print(f"- Average 2^(n-1) multiplier: {const_n_minus_1:.8f}")
    print(f"- Average 2^n multiplier: {const_n:.8f}")
    print(f"- Keys show position-dependent variations")
    print(f"- The relationship is NOT a simple constant!")
    print(f"- Each position may have a unique formula")

if __name__ == "__main__":
    hunt_for_the_constant() 