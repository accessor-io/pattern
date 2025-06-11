#!/usr/bin/python3

import hashlib
from typing import List, Dict
import numpy as np
from collections import defaultdict

def analyze_hash_chains(hex_sequence: List[str]) -> dict:
    """
    Analyze sequence for hash chain properties
    - Hash preimage patterns
    - Chain relationships
    - Merkle tree properties
    """
    results = []
    for i, hex_str in enumerate(hex_sequence):
        # Generate various hashes
        sha256_hash = hashlib.sha256(bytes.fromhex(hex_str)).hexdigest()
        double_sha256 = hashlib.sha256(bytes.fromhex(sha256_hash)).hexdigest()
        ripemd160 = hashlib.new('ripemd160', bytes.fromhex(hex_str)).hexdigest()
        
        # Check for potential preimage relationships with next value
        next_hex = hex_sequence[i+1] if i < len(hex_sequence)-1 else None
        preimage_relation = check_preimage_relation(hex_str, next_hex) if next_hex else None
        
        result = {
            'sha256': sha256_hash,
            'double_sha256': double_sha256,
            'ripemd160': ripemd160,
            'preimage_relation': preimage_relation
        }
        results.append(result)
    
    return {
        'hash_chains': results,
        'chain_properties': analyze_chain_properties(hex_sequence)
    }

def check_preimage_relation(current: str, next_value: str) -> dict:
    """Check if there's a preimage relationship between values"""
    # Try different hash functions
    hash_functions = {
        'sha256': hashlib.sha256,
        'double_sha256': lambda x: hashlib.sha256(hashlib.sha256(x).digest()),
        'ripemd160': lambda x: hashlib.new('ripemd160', x)
    }
    
    relations = {}
    for name, func in hash_functions.items():
        try:
            current_hash = func(bytes.fromhex(current)).hexdigest()
            if current_hash == next_value:
                relations[name] = True
            else:
                relations[name] = False
        except:
            relations[name] = False
    
    return relations

def analyze_chain_properties(hex_sequence: List[str]) -> dict:
    """Analyze properties of the sequence as a hash chain"""
    # Build Merkle tree levels
    current_level = hex_sequence
    merkle_levels = [current_level]
    
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level)-1, 2):
            combined = current_level[i] + current_level[i+1]
            next_hash = hashlib.sha256(bytes.fromhex(combined)).hexdigest()
            next_level.append(next_hash)
        if len(current_level) % 2 == 1:
            next_level.append(current_level[-1])
        current_level = next_level
        merkle_levels.append(current_level)
    
    # Analyze bit patterns in hashes
    hash_patterns = defaultdict(int)
    for hex_str in hex_sequence:
        binary = bin(int(hex_str, 16))[2:].zfill(256)
        pattern = binary[:8]  # Look at first byte pattern
        hash_patterns[pattern] += 1
    
    return {
        'merkle_levels': len(merkle_levels),
        'merkle_root': merkle_levels[-1][0],
        'common_patterns': dict(sorted(hash_patterns.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)[:5])  # Top 5 patterns
    }

def main():
    """Main analysis function"""
    with open('../data/32bHex.txt', 'r') as f:
        hex_strings = [line.strip() for line in f if line.strip()]
    
    analysis = analyze_hash_chains(hex_strings)
    
    # Write results
    with open('../output/hash_chains/hash_analysis.txt', 'w') as f:
        f.write("Hash Chain Analysis\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("Individual Hash Properties:\n")
        f.write("-" * 40 + "\n")
        for i, result in enumerate(analysis['hash_chains']):
            f.write(f"\nValue {i+1}:\n")
            f.write(f"SHA256: {result['sha256']}\n")
            f.write(f"Double SHA256: {result['double_sha256']}\n")
            f.write(f"RIPEMD160: {result['ripemd160']}\n")
            if result['preimage_relation']:
                f.write("Preimage relations:\n")
                for hash_type, is_preimage in result['preimage_relation'].items():
                    f.write(f"  {hash_type}: {is_preimage}\n")
            f.write("\n")
        
        f.write("\nChain Properties:\n")
        f.write("-" * 40 + "\n")
        chain_props = analysis['chain_properties']
        f.write(f"Merkle tree levels: {chain_props['merkle_levels']}\n")
        f.write(f"Merkle root: {chain_props['merkle_root']}\n")
        f.write("\nCommon bit patterns:\n")
        for pattern, count in chain_props['common_patterns'].items():
            f.write(f"Pattern {pattern}: {count} occurrences\n")

if __name__ == "__main__":
    main() 