#!/usr/bin/env python3
"""
Comprehensive analysis of the Bitcoin puzzle chain patterns
"""

import hashlib
import json
import binascii
import base58
from typing import List, Tuple, Dict, Set
from collections import defaultdict

# The interesting difference value we found
KNOWN_DIFF = 0x4e5114d15126dfc4e0e9283275748a0667dd08abd95edfaa3f6e8165bebf1313

# Expected significant parts (from chain_demo.py)
EXPECTED_SIGNIFICANT = {
    1: "1", 2: "3", 3: "7", 4: "8", 5: "15", 6: "31", 7: "4c", 8: "e0",
    9: "1d3", 10: "202", 11: "483", 12: "a7b", 13: "1460", 14: "2930",
    15: "68f3", 16: "c936", 17: "1764f", 18: "3080d", 19: "5749f",
    20: "d2c55", 21: "1ba534", 22: "2de40f", 23: "556e52", 24: "dc2a04",
    25: "1fa5ee5", 26: "340326e", 27: "6ac3875", 28: "d916ce8",
    29: "17e2551e", 30: "3d94cd64", 31: "7d4fe747", 32: "b862a62e",
    33: "1a96ca8d8", 34: "34a65911d", 35: "4aed21170", 36: "9de820a7c",
    37: "1757756a93", 38: "22382facd0", 39: "4b5f8303e9", 40: "e9ae4933d6",
    41: "153869acc5b", 42: "2a221c58d8f", 43: "6bd3b27c591", 44: "e02b35a358f",
    45: "122fca143c05", 46: "2ec18388d544", 47: "6cd610b53cba", 48: "ade6d7ce3b9b",
    49: "174176b015f4d", 50: "22bd43c2e9354", 51: "75070a1a009d4", 52: "efae164cb9e3c",
    53: "180788e47e326c", 54: "236fb6d5ad1f43", 55: "6abe1f9b67e114", 56: "9d18b63ac4ffdf",
    57: "1eb25c90795d61c", 58: "2c675b852189a21", 59: "7496cbb87cab44f", 60: "fc07a1825367bbe",
    61: "13c96a3742f64906", 62: "363d541eb611abee", 63: "7cce5efdaccf6808", 64: "f7051f27b09112d4",
    65: "1a838b13505b26867"
}

def determine_L(n: int) -> int:
    """Determine the number of significant hex digits for index n."""
    if n <= 4:
        return 1
    elif n <= 8:
        return 2
    elif n <= 16:
        return 3
    elif n <= 32:
        return 4
    elif n <= 40:
        return 5
    elif n <= 48:
        return 6
    elif n <= 56:
        return 7
    elif n <= 64:
        return 8
    else:
        return 9

def chain_next_value(prev_value: int, n: int) -> Tuple[int, int, int]:
    """
    Compute the next value in the chain.
    Returns (X, S, L) where:
    - X is the full 256-bit hash value
    - S is the significant part (X mod 16^L)
    - L is the number of significant hex digits
    """
    L = determine_L(n)
    m = 16 ** L

    # Hash previous value concatenated with index
    input_bytes = prev_value.to_bytes(32, byteorder='big') + n.to_bytes(4, byteorder='big')
    h_bytes = hashlib.sha256(input_bytes).digest()
    X = int.from_bytes(h_bytes, byteorder='big')
    S = X % m

    return X, S, L

def analyze_chain(seed: int, max_depth: int = 65) -> Dict:
    """
    Analyze a chain starting from a seed up to max_depth.
    Returns detailed information about the chain.
    """
    chain_info = {
        'seed': hex(seed),
        'matches': [],
        'values': [],
        'total_matches': 0
    }

    current = seed
    for n in range(1, max_depth + 1):
        X, S, L = chain_next_value(current, n)
        significant = format(S, f'0{L}x')
        expected = EXPECTED_SIGNIFICANT.get(n, '')
        matches = significant == expected

        chain_info['values'].append({
            'index': n,
            'full_hash': hex(X),
            'significant': significant,
            'expected': expected,
            'matches': matches,
            'L': L
        })

        if matches:
            chain_info['matches'].append(n)
            chain_info['total_matches'] += 1

        current = X

    return chain_info

def analyze_seed_relationships(seeds: List[int]) -> List[Dict]:
    """Analyze relationships between seeds."""
    relationships = []
    
    for i, seed1 in enumerate(seeds):
        for seed2 in seeds[i+1:]:
            # Calculate various differences
            add_diff = (seed2 - seed1) % (2**256)
            xor_diff = seed1 ^ seed2
            and_result = seed1 & seed2
            or_result = seed1 | seed2
            
            # Count matching bits
            bit_diff = bin(xor_diff).count('1')
            
            rel = {
                'seed1': hex(seed1),
                'seed2': hex(seed2),
                'add_diff': hex(add_diff),
                'xor_diff': hex(xor_diff),
                'and_result': hex(and_result),
                'or_result': hex(or_result),
                'bit_differences': bit_diff,
                'matches_known_diff': add_diff == KNOWN_DIFF
            }
            relationships.append(rel)
            
            # If this matches our known difference, analyze further
            if add_diff == KNOWN_DIFF:
                print(f"\nFound matching difference pattern!")
                print(f"Seed 1: {hex(seed1)}")
                print(f"Seed 2: {hex(seed2)}")
                
                # Analyze both chains
                chain1 = analyze_chain(seed1)
                chain2 = analyze_chain(seed2)
                
                print("\nChain 1 matches:", chain1['matches'])
                print("Chain 2 matches:", chain2['matches'])
                
                # Find common successful indices
                common_matches = set(chain1['matches']) & set(chain2['matches'])
                print("Common successful indices:", sorted(common_matches))
                
                rel['chain_analysis'] = {
                    'chain1_matches': chain1['matches'],
                    'chain2_matches': chain2['matches'],
                    'common_matches': sorted(common_matches)
                }
    
    return relationships

def analyze_value_patterns(chain_info: Dict) -> Dict:
    """Analyze patterns in the chain values."""
    patterns = {
        'consecutive_matches': [],
        'match_gaps': [],
        'bit_patterns': defaultdict(int),
        'byte_patterns': defaultdict(int)
    }
    
    # Analyze consecutive matches
    current_streak = 0
    last_match = None
    for val in chain_info['values']:
        if val['matches']:
            current_streak += 1
            if last_match is not None:
                patterns['match_gaps'].append(val['index'] - last_match - 1)
            last_match = val['index']
        else:
            if current_streak > 1:
                patterns['consecutive_matches'].append(current_streak)
            current_streak = 0
    
    # Analyze bit and byte patterns in matching values
    for val in chain_info['values']:
        if val['matches']:
            try:
                # Convert hash to binary and look for repeating patterns
                hash_hex = val['full_hash'][2:] if val['full_hash'].startswith('0x') else val['full_hash']
                hash_hex = hash_hex.zfill(64)  # Ensure it's 32 bytes (64 hex chars)
                hash_int = int(hash_hex, 16)
                hash_bits = format(hash_int, '0256b')
                
                for i in range(len(hash_bits) - 7):
                    bit_pattern = hash_bits[i:i+8]
                    patterns['bit_patterns'][bit_pattern] += 1
                
                # Look for repeating byte patterns
                hash_bytes = bytes.fromhex(hash_hex)
                for i in range(len(hash_bytes) - 3):
                    byte_pattern = hash_bytes[i:i+4]
                    patterns['byte_patterns'][byte_pattern.hex()] += 1
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing hash value {val['full_hash']}: {e}")
                continue
    
    return patterns

def main():
    print("Starting comprehensive puzzle chain analysis...")
    
    # Read the puzzle file
    with open("../5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3k.vb", 'r') as f:
        lines = f.readlines()
    
    # Extract and decode private keys
    seeds = []
    for i in range(0, len(lines), 2):
        try:
            priv_key = lines[i].strip()
            if priv_key:
                raw = base58.b58decode(priv_key)[1:-4]  # Remove version and checksum
                seed = int.from_bytes(raw, 'big')
                seeds.append(seed)
        except Exception as e:
            print(f"Error decoding key: {e}")
    
    print(f"\nAnalyzing {len(seeds)} seeds...")
    
    # Analyze relationships between seeds
    relationships = analyze_seed_relationships(seeds)
    
    # Analyze each seed's chain
    chain_analyses = []
    for seed in seeds:
        chain_info = analyze_chain(seed)
        patterns = analyze_value_patterns(chain_info)
        
        analysis = {
            'seed': hex(seed),
            'chain_info': chain_info,
            'patterns': patterns
        }
        chain_analyses.append(analysis)
    
    # Save results
    results = {
        'relationships': relationships,
        'chain_analyses': chain_analyses,
        'known_diff': hex(KNOWN_DIFF)
    }
    
    with open('comprehensive_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nAnalysis complete! Results saved to comprehensive_analysis.json")
    
    # Print summary of findings
    print("\nSummary of findings:")
    matching_diffs = [r for r in relationships if r['matches_known_diff']]
    print(f"Found {len(matching_diffs)} pairs with the known difference pattern")
    
    # Find seeds with most matches
    best_chains = sorted(chain_analyses, key=lambda x: x['chain_info']['total_matches'], reverse=True)
    if best_chains:
        print(f"\nBest performing seed: {best_chains[0]['seed']}")
        print(f"Matches: {best_chains[0]['chain_info']['matches']}")

if __name__ == "__main__":
    main() 