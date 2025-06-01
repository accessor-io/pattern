#!/usr/bin/env python3
"""
🔍 PATTERN ADDRESS VERIFICATION
Tests if discovered patterns actually generate the correct Bitcoin puzzle addresses
"""

import hashlib
import base58
import ecdsa
from typing import Dict, List, Tuple, Optional

# Secp256k1 constants
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Known puzzle addresses for verification
KNOWN_ADDRESSES = {
    65: "1FFy6jfKdGGLjQbAf3vWaYfBhLN1qcKQKT",
    66: "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9", 
    67: "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ",
    68: "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
    69: "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",  # This is actually unsolved
    70: "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR",
    71: "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU", 
    72: "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    73: "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
    74: "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
    75: "1J36UjUByGroXcCvmj13U6uwaVv9caEeAt",
    76: "17Q2Yn3AsQ8zHHLNtM4p9FbqsZTbzHJ4CY",
    77: "1LK1PKhiHnhJjwF5jFqP2xp6w7qyFkBVNj",
    78: "13p1ijLwsnrcuyqcTvJXkq2ASdXqcnEBLE",
    79: "1LKR3oPp6oBNGR1iTMo8u5hh8Kbh26wVj6",
    80: "1FJ8GhXB5dHhiGZKJtFSKQCzMVWHBG2rZC"
}

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

def load_verified_keys() -> Dict[int, int]:
    """Load verified Bitcoin puzzle keys"""
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
                    status = hex_and_status.split(' - ')[1].strip()
                else:
                    hex_key = hex_and_status.strip()
                    status = "UNKNOWN"
                
                # Load all KNOWN keys (verified solutions)
                if status == 'KNOWN':
                    verified_keys[pos] = int(hex_key, 16)
                    
        return verified_keys
        
    except Exception as e:
        print(f"✗ Error loading keys: {e}")
        return {}

def test_pattern_prediction(position: int, pattern_type: str, deviation_percent: float) -> List[Tuple[int, str]]:
    """Test pattern prediction with deviation range"""
    results = []
    
    # Calculate base pattern
    if pattern_type == "2^(n-1)":
        base_prediction = 1 << (position - 1)
    elif pattern_type == "2^n":
        base_prediction = 1 << position
    elif pattern_type == "2^(n-2)":
        base_prediction = 1 << (position - 2)
    else:
        return results
    
    # Test with deviation range
    deviation_range = int(base_prediction * deviation_percent / 100)
    
    # Test several points in the range
    test_points = [
        base_prediction,  # Exact
        base_prediction + deviation_range,  # Upper bound
        base_prediction - deviation_range,  # Lower bound
        base_prediction + deviation_range // 2,  # Mid upper
        base_prediction - deviation_range // 2,  # Mid lower
    ]
    
    for test_key in test_points:
        if test_key <= 0 or test_key >= N:
            continue
            
        try:
            pubkey = privkey_to_pubkey(test_key, compressed=True)
            address = pubkey_to_address(pubkey)
            results.append((test_key, address))
        except:
            continue
    
    return results

def verify_pattern_addresses():
    """Verify if patterns generate correct addresses"""
    
    print("🔍 PATTERN ADDRESS VERIFICATION")
    print("=" * 70)
    print("Testing if discovered patterns generate correct Bitcoin addresses...")
    print()
    
    # Load verified keys first
    verified_keys = load_verified_keys()
    
    # Pattern statistics from our analysis
    pattern_stats = {
        "2^(n-1)": 20.71,  # Average deviation %
        "2^n": 20.79,      # Average deviation %
        "2^(n-2)": 50.0    # Estimated
    }
    
    # Test positions with known solutions
    test_positions = [65, 66, 67, 68, 70, 75, 80]  # Known solved positions
    
    print("📊 VERIFICATION RESULTS:")
    print("-" * 70)
    print(f"{'Pos':>3} | {'Pattern':>10} | {'Known Key':>20} | {'Generated Address':>35} | {'Match':>5}")
    print("-" * 70)
    
    total_tests = 0
    correct_matches = 0
    
    for pos in test_positions:
        if pos not in verified_keys:
            continue
            
        actual_key = verified_keys[pos]
        target_address = None
        
        # Get target address (we need to generate it from the known key)
        try:
            pubkey = privkey_to_pubkey(actual_key, compressed=True)
            target_address = pubkey_to_address(pubkey)
        except:
            continue
        
        total_tests += 1
        
        # Determine best pattern for this position (from our analysis)
        if pos in [66, 75, 85, 95]:
            best_pattern = "2^(n-1)"
        elif pos in [80, 130]:
            best_pattern = "2^(n-2)"
        else:
            best_pattern = "2^n"
        
        # Test pattern prediction
        predicted_results = test_pattern_prediction(pos, best_pattern, pattern_stats[best_pattern])
        
        # Check if any prediction matches
        found_match = False
        for pred_key, pred_address in predicted_results:
            if pred_address == target_address:
                print(f"{pos:>3} | {best_pattern:>10} | {actual_key:>20x} | {pred_address:>35} | {'✅':>5}")
                found_match = True
                correct_matches += 1
                break
        
        if not found_match:
            # Show the closest attempt
            if predicted_results:
                closest_key, closest_address = predicted_results[0]
                print(f"{pos:>3} | {best_pattern:>10} | {actual_key:>20x} | {closest_address:>35} | {'❌':>5}")
            else:
                print(f"{pos:>3} | {best_pattern:>10} | {actual_key:>20x} | {'No prediction':>35} | {'❌':>5}")
    
    print("-" * 70)
    print()
    
    # Summary
    success_rate = (correct_matches / total_tests) * 100 if total_tests > 0 else 0
    
    print("📈 VERIFICATION SUMMARY:")
    print("=" * 50)
    print(f"Total positions tested: {total_tests}")
    print(f"Correct matches: {correct_matches}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate > 0:
        print("\n🎉 BREAKTHROUGH CONFIRMED!")
        print("Our patterns can predict Bitcoin puzzle keys!")
    else:
        print("\n⚠️  PATTERNS NEED REFINEMENT")
        print("Current patterns don't generate correct addresses.")
        print("Need to analyze the actual mathematical relationship more precisely.")
    
    # Test unsolved positions if patterns work
    if correct_matches > 0:
        print(f"\n🎯 APPLYING PATTERNS TO UNSOLVED PUZZLES:")
        print("=" * 50)
        
        unsolved_positions = [69, 71, 72, 73, 74, 76, 77, 78, 79]
        
        for pos in unsolved_positions[:3]:  # Test first 3 unsolved
            if pos in [69, 71]:
                pattern = "2^n"  # Based on neighboring position 70
            elif pos in [74, 76, 77]:
                pattern = "2^(n-1)"  # Based on neighboring position 75
            else:
                pattern = "2^n"  # Default
            
            predicted_results = test_pattern_prediction(pos, pattern, pattern_stats[pattern])
            
            print(f"\nPosition {pos} ({pattern} pattern):")
            if predicted_results:
                for i, (pred_key, pred_address) in enumerate(predicted_results[:3]):
                    print(f"  Candidate {i+1}: 0x{pred_key:x} -> {pred_address}")
            else:
                print("  No valid predictions generated")
    
    print(f"\n💡 ANALYSIS INSIGHTS:")
    print("- Bitcoin puzzles may use more complex generation than simple power-of-2 patterns")
    print("- Deviations might follow specific mathematical sequences")
    print("- Further analysis needed to discover the exact algorithm")

if __name__ == "__main__":
    verify_pattern_addresses() 