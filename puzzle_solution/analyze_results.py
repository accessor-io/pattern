#!/usr/bin/env python3
"""
Analyze and summarize the comprehensive analysis results
"""

import json
from collections import defaultdict
from typing import Dict, List, Set

def analyze_chain_patterns(chain_analyses: List[Dict]) -> Dict:
    """Analyze patterns across all chains."""
    patterns = {
        'match_frequencies': defaultdict(int),  # How often each index is matched
        'consecutive_matches': [],  # Lengths of consecutive match sequences
        'common_bit_patterns': defaultdict(int),  # Common bit patterns in matching values
        'common_byte_patterns': defaultdict(int),  # Common byte patterns in matching values
        'best_chains': []  # Chains with most matches
    }
    
    for analysis in chain_analyses:
        chain_info = analysis['chain_info']
        
        # Track match frequencies
        for match in chain_info['matches']:
            patterns['match_frequencies'][match] += 1
        
        # Track consecutive matches
        if 'patterns' in analysis:
            patterns['consecutive_matches'].extend(analysis['patterns']['consecutive_matches'])
            
            # Aggregate bit and byte patterns
            for bit_pattern, count in analysis['patterns']['bit_patterns'].items():
                patterns['common_bit_patterns'][bit_pattern] += count
            for byte_pattern, count in analysis['patterns']['byte_patterns'].items():
                patterns['common_byte_patterns'][byte_pattern] += count
        
        # Track best performing chains
        if len(chain_info['matches']) > 0:
            patterns['best_chains'].append({
                'seed': chain_info['seed'],
                'matches': chain_info['matches'],
                'total_matches': len(chain_info['matches'])
            })
    
    # Sort best chains by number of matches
    patterns['best_chains'].sort(key=lambda x: x['total_matches'], reverse=True)
    
    return patterns

def analyze_relationships(relationships: List[Dict]) -> Dict:
    """Analyze patterns in seed relationships."""
    patterns = {
        'diff_patterns': defaultdict(int),  # Common difference patterns
        'xor_patterns': defaultdict(int),  # Common XOR patterns
        'bit_diff_stats': {  # Statistics about bit differences
            'min': float('inf'),
            'max': 0,
            'avg': 0,
            'common': defaultdict(int)
        },
        'matching_diffs': []  # Pairs matching our known difference
    }
    
    total_bit_diffs = 0
    pair_count = len(relationships)
    
    for rel in relationships:
        # Track difference patterns
        patterns['diff_patterns'][rel['add_diff']] += 1
        patterns['xor_patterns'][rel['xor_diff']] += 1
        
        # Track bit difference statistics
        bit_diff = rel['bit_differences']
        patterns['bit_diff_stats']['min'] = min(patterns['bit_diff_stats']['min'], bit_diff)
        patterns['bit_diff_stats']['max'] = max(patterns['bit_diff_stats']['max'], bit_diff)
        total_bit_diffs += bit_diff
        patterns['bit_diff_stats']['common'][bit_diff] += 1
        
        # Track pairs matching our known difference
        if rel['matches_known_diff']:
            patterns['matching_diffs'].append({
                'seed1': rel['seed1'],
                'seed2': rel['seed2'],
                'chain_analysis': rel.get('chain_analysis', {})
            })
    
    if pair_count > 0:
        patterns['bit_diff_stats']['avg'] = total_bit_diffs / pair_count
    
    return patterns

def main():
    print("Analyzing comprehensive analysis results...")
    
    with open('comprehensive_analysis.json', 'r') as f:
        data = json.load(f)
    
    # Analyze chain patterns
    chain_patterns = analyze_chain_patterns(data['chain_analyses'])
    
    # Analyze relationships
    relationship_patterns = analyze_relationships(data['relationships'])
    
    print("\nSummary of Findings:")
    print("===================")
    
    print("\nBest Performing Seeds:")
    print("---------------------")
    for i, chain in enumerate(chain_patterns['best_chains'][:5], 1):
        print(f"{i}. Seed: {chain['seed']}")
        print(f"   Matches: {chain['matches']}")
        print(f"   Total matches: {chain['total_matches']}")
    
    print("\nMost Common Match Indices:")
    print("-------------------------")
    sorted_matches = sorted(chain_patterns['match_frequencies'].items(), 
                          key=lambda x: x[1], reverse=True)
    for index, freq in sorted_matches[:10]:
        print(f"Index {index}: {freq} times")
    
    print("\nConsecutive Match Statistics:")
    print("---------------------------")
    if chain_patterns['consecutive_matches']:
        max_consec = max(chain_patterns['consecutive_matches'])
        avg_consec = sum(chain_patterns['consecutive_matches']) / len(chain_patterns['consecutive_matches'])
        print(f"Maximum consecutive matches: {max_consec}")
        print(f"Average consecutive matches: {avg_consec:.2f}")
    
    print("\nBit Difference Statistics:")
    print("------------------------")
    stats = relationship_patterns['bit_diff_stats']
    print(f"Minimum bit differences: {stats['min']}")
    print(f"Maximum bit differences: {stats['max']}")
    print(f"Average bit differences: {stats['avg']:.2f}")
    
    print("\nMatching Difference Patterns:")
    print("--------------------------")
    matching_count = len(relationship_patterns['matching_diffs'])
    print(f"Found {matching_count} pairs matching the known difference pattern")
    for i, match in enumerate(relationship_patterns['matching_diffs'], 1):
        print(f"\nMatch {i}:")
        print(f"Seed 1: {match['seed1']}")
        print(f"Seed 2: {match['seed2']}")
        if 'chain_analysis' in match:
            print("Common successful indices:", match['chain_analysis'].get('common_matches', []))
    
    print("\nMost Common Byte Patterns:")
    print("------------------------")
    sorted_patterns = sorted(chain_patterns['common_byte_patterns'].items(),
                           key=lambda x: x[1], reverse=True)
    for pattern, count in sorted_patterns[:5]:
        print(f"Pattern {pattern}: {count} occurrences")

if __name__ == "__main__":
    main() 