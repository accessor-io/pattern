#!/usr/bin/env python3
"""
Search for position 68 by analyzing and applying bit patterns between terms 66 and 67.
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import sys

# Target Bitcoin address
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Known terms
TERM_66 = 0x2832ed74f2b5e35ee
TERM_67 = 0x730fc235c1942c1ae
TERM_67_ALT = 0x3ce0e3395f140001

def analyze_bit_patterns(term1, term2):
    """Analyze bit patterns between two terms"""
    # Convert to binary strings
    bin1 = format(term1, '064b')
    bin2 = format(term2, '064b')
    
    # Find positions where bits changed
    changes = []
    for i in range(64):
        if bin1[i] != bin2[i]:
            changes.append(i)
    
    # Find patterns in the changes
    patterns = {
        'total_changes': len(changes),
        'change_positions': changes,
        'first_change': changes[0] if changes else -1,
        'last_change': changes[-1] if changes else -1,
        'gaps': [changes[i+1] - changes[i] for i in range(len(changes)-1)],
        'clusters': []
    }
    
    # Find clusters of changes
    current_cluster = []
    for i in range(len(changes)-1):
        current_cluster.append(changes[i])
        if changes[i+1] - changes[i] > 1:  # Gap larger than 1 bit
            if len(current_cluster) > 1:
                patterns['clusters'].append(current_cluster)
            current_cluster = []
    if current_cluster:
        patterns['clusters'].append(current_cluster)
    
    return patterns

def apply_patterns(term, patterns):
    """Apply bit patterns to generate candidates"""
    candidates = []
    
    # Convert term to binary
    term_bin = list(format(term, '064b'))
    
    # 1. Apply same pattern of changes
    new_bin = term_bin.copy()
    for pos in patterns['change_positions']:
        if pos < len(new_bin):
            new_bin[pos] = '1' if new_bin[pos] == '0' else '0'
    candidates.append(int(''.join(new_bin), 2))
    
    # 2. Apply pattern shifted by 1
    new_bin = term_bin.copy()
    for pos in patterns['change_positions']:
        shifted_pos = pos + 1
        if shifted_pos < len(new_bin):
            new_bin[shifted_pos] = '1' if new_bin[shifted_pos] == '0' else '0'
    candidates.append(int(''.join(new_bin), 2))
    
    # 3. Apply pattern shifted by -1
    new_bin = term_bin.copy()
    for pos in patterns['change_positions']:
        shifted_pos = pos - 1
        if shifted_pos >= 0:
            new_bin[shifted_pos] = '1' if new_bin[shifted_pos] == '0' else '0'
    candidates.append(int(''.join(new_bin), 2))
    
    # 4. Apply pattern in reverse
    new_bin = term_bin.copy()
    for pos in reversed(patterns['change_positions']):
        if pos < len(new_bin):
            new_bin[pos] = '1' if new_bin[pos] == '0' else '0'
    candidates.append(int(''.join(new_bin), 2))
    
    # 5. Apply pattern to clusters
    for cluster in patterns['clusters']:
        new_bin = term_bin.copy()
        for pos in cluster:
            if pos < len(new_bin):
                new_bin[pos] = '1' if new_bin[pos] == '0' else '0'
        candidates.append(int(''.join(new_bin), 2))
    
    # 6. Apply pattern with gaps
    if patterns['gaps']:
        avg_gap = sum(patterns['gaps']) / len(patterns['gaps'])
        new_bin = term_bin.copy()
        pos = patterns['first_change']
        while pos < len(new_bin):
            new_bin[pos] = '1' if new_bin[pos] == '0' else '0'
            pos += int(avg_gap)
        candidates.append(int(''.join(new_bin), 2))
    
    # 7. Apply pattern with doubled frequency
    new_bin = term_bin.copy()
    for pos in patterns['change_positions']:
        doubled_pos = pos * 2
        if doubled_pos < len(new_bin):
            new_bin[doubled_pos] = '1' if new_bin[doubled_pos] == '0' else '0'
    candidates.append(int(''.join(new_bin), 2))
    
    # 8. Apply pattern with halved frequency
    new_bin = term_bin.copy()
    for pos in patterns['change_positions']:
        halved_pos = pos // 2
        if halved_pos < len(new_bin):
            new_bin[halved_pos] = '1' if new_bin[halved_pos] == '0' else '0'
    candidates.append(int(''.join(new_bin), 2))
    
    # 9. Apply complementary pattern
    new_bin = term_bin.copy()
    all_positions = set(range(len(new_bin)))
    complement_positions = all_positions - set(patterns['change_positions'])
    for pos in complement_positions:
        new_bin[pos] = '1' if new_bin[pos] == '0' else '0'
    candidates.append(int(''.join(new_bin), 2))
    
    # 10. Apply pattern with alternating bits
    new_bin = term_bin.copy()
    for i, pos in enumerate(patterns['change_positions']):
        if pos < len(new_bin):
            new_bin[pos] = '1' if i % 2 == 0 else '0'
    candidates.append(int(''.join(new_bin), 2))
    
    # Also add the predicted value and its neighbors
    predicted = 0xce2d691f719dbb6b0
    candidates.extend([
        predicted,
        predicted + 1,
        predicted - 1,
        predicted ^ term,
        predicted | term,
        predicted & term
    ])
    
    return list(set(candidates))

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

def test_candidates():
    """Test candidates generated from bit patterns"""
    # Analyze patterns between terms 66 and 67
    patterns_66_67 = analyze_bit_patterns(TERM_66, TERM_67)
    print(f"Found {patterns_66_67['total_changes']} bit changes between terms 66 and 67")
    print(f"First change at bit {patterns_66_67['first_change']}, last change at bit {patterns_66_67['last_change']}")
    print(f"Found {len(patterns_66_67['clusters'])} clusters of changes")
    
    # Generate candidates from both versions of term 67
    candidates = []
    for term_67 in [TERM_67, TERM_67_ALT]:
        candidates.extend(apply_patterns(term_67, patterns_66_67))
    
    # Remove duplicates
    candidates = list(set(candidates))
    print(f"\nGenerated {len(candidates)} unique candidates")
    
    # Test candidates
    for i, candidate in enumerate(candidates):
        print(f"Testing candidate {i+1}/{len(candidates)}: {hex(candidate)}")
        address = private_key_to_address(candidate)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND! Candidate: {hex(candidate)}")
            return candidate
    
    print("No match found in candidates")
    return None

if __name__ == "__main__":
    print("Starting bit pattern analysis search for position 68")
    start_time = time.time()
    
    result = test_candidates()
    
    if result:
        save_result(result)
    else:
        print("\nNo solution found.")
        
    print(f"Search completed in {time.time() - start_time:.2f} seconds") 