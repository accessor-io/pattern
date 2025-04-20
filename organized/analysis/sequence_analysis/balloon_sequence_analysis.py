"""
Sequence Analysis using Memory-Hard Function Patterns
Inspired by Balloon Hashing and sequential memory-hard functions

This approach examines whether the sequence follows patterns similar to 
memory-hard cryptographic functions like those described in the paper:
'Balloon Hashing: A Memory-Hard Function Providing Provable Protection Against Sequential Attacks'
"""

import math
import numpy as np
from typing import List, Dict, Tuple, Optional, Callable
import matplotlib.pyplot as plt
import os

# Ensure output directory exists
os.makedirs('sequence_analysis_results', exist_ok=True)

class SequenceAnalyzer:
    def __init__(self):
        # Known sequence values (positions 1-67)
        self.sequence = [
            0x1, 0x3, 0x7, 0x8, 0x15, 0x31, 0x4c, 0xe0, 0x1d3, 0x202, 
            0x483, 0xa7b, 0x1460, 0x2930, 0x68f3, 0xc936, 0x1764f, 0x3080d, 
            0x5749f, 0xd2c55, 0x1ba534, 0x2de40f, 0x556e52, 0xdc2a04, 
            0x1fa5ee5, 0x340326e, 0x6ac3875, 0xd916ce8, 0x17e2551e, 0x3d94cd64, 
            0x7d4fe747, 0xb862a62e, 0x1a96ca8d8, 0x34a65911d, 0x4aed21170, 
            0x9de820a7c, 0x1757756a93, 0x22382facd0, 0x4b5f8303e9, 0xe9ae4933d6, 
            0x153869acc5b, 0x2a221c58d8f, 0x6bd3b27c591, 0xe02b35a358f, 
            0x122fca143c05, 0x2ec18388d544, 0x6cd610b53cba, 0xade6d7ce3b9b, 
            0x174176b015f4d, 0x22bd43c2e9354, 0x75070a1a009d4, 0xefae164cb9e3c, 
            0x180788e47e326c, 0x236fb6d5ad1f43, 0x6abe1f9b67e114, 0x9d18b63ac4ffdf, 
            0x1eb25c90795d61c, 0x2c675b852189a21, 0x7496cbb87cab44f, 0xfc07a1825367bbe, 
            0x13c96a3742f64906, 0x363d541eb611abee, 0x7cce5efdaccf6808, 0xf7051f27b09112d4, 
            0x1a838b13505b26867, 0x2832ed74f2b5e35ee, 0x730fc235c1942c1ae
        ]
        
        # Additional known values
        self.extended_sequence = {
            70: 0x349b84b6431a6c4ef1,
            75: 0x4c5ce114686a1336e07,
            80: 0xea1a5c66dcc11b5ad180,
            85: 0x11720c4f018d51b8cebba8,
            90: 0x2ce00bb2136a445c71e85bf,
            95: 0x527a792b183c7f64a0e8b1f4,
            100: 0xaf55fc59c335c8ec67ed24826,
            105: 0x16f14fc2054cd87ee6396b33df3,
            110: 0x35c0d7234df7deb0f20cf7062444,
            115: 0x60f4d11574f5deee49961d9609ac6,
            120: 0xb10f22572c497a836ea187f2e1fc23,
            125: 0x1c533b6bb7f0804e09960225e44877ac,
            130: 0x33e7665705359f04f28b88cf897c603c9
        }
        
        # Add extended sequence values to main sequence
        for pos, val in self.extended_sequence.items():
            while len(self.sequence) < pos:
                self.sequence.append(None)
            self.sequence[pos-1] = val
    
    def analyze_growth_pattern(self) -> Dict:
        """
        Analyze growth patterns in the sequence, looking for evidence of
        memory-hard function characteristics
        """
        print("Analyzing growth patterns...")
        
        # Calculate consecutive ratios
        ratios = []
        for i in range(1, len(self.sequence)):
            if self.sequence[i] is not None and self.sequence[i-1] is not None:
                ratio = self.sequence[i] / self.sequence[i-1]
                ratios.append(ratio)
                print(f"Position {i+1}/{i}: ratio = {ratio:.4f}")
        
        # Analyze ratios
        avg_ratio = sum(ratios) / len(ratios)
        min_ratio = min(ratios)
        max_ratio = max(ratios)
        std_ratio = np.std(ratios)
        
        # Plot ratios
        plt.figure(figsize=(12, 6))
        plt.plot(range(2, len(ratios)+2), ratios, marker='o')
        plt.axhline(y=avg_ratio, color='r', linestyle='--', label=f'Average: {avg_ratio:.4f}')
        plt.title('Growth Ratio Between Consecutive Elements')
        plt.xlabel('Position')
        plt.ylabel('Ratio (a[n]/a[n-1])')
        plt.grid(True)
        plt.legend()
        plt.savefig('sequence_analysis_results/growth_ratios.png')
        
        # Calculate bit growth
        bit_growth = []
        for i in range(1, len(self.sequence)):
            if self.sequence[i] is not None and self.sequence[i-1] is not None:
                bits1 = self.sequence[i-1].bit_length()
                bits2 = self.sequence[i].bit_length()
                growth = bits2 - bits1
                bit_growth.append(growth)
                print(f"Position {i+1}/{i}: bit growth = {growth}")
        
        # Plot bit growth
        plt.figure(figsize=(12, 6))
        plt.plot(range(2, len(bit_growth)+2), bit_growth, marker='o', color='g')
        plt.title('Bit Growth Between Consecutive Elements')
        plt.xlabel('Position')
        plt.ylabel('Bit Growth')
        plt.grid(True)
        plt.savefig('sequence_analysis_results/bit_growth.png')
        
        return {
            'average_ratio': avg_ratio,
            'min_ratio': min_ratio,
            'max_ratio': max_ratio,
            'std_ratio': std_ratio,
            'ratios': ratios,
            'bit_growth': bit_growth
        }
    
    def analyze_bit_operations(self) -> Dict:
        """
        Analyze bit-level operations that might explain the pattern,
        particularly operations common in memory-hard functions
        """
        print("\nAnalyzing bit operations...")
        
        # Test various bit operations between consecutive terms
        operations = {
            'XOR': lambda a, b: a ^ b,
            'AND': lambda a, b: a & b,
            'OR': lambda a, b: a | b,
            'XOR_shifted_1': lambda a, b: a ^ (b << 1),
            'XOR_shifted_2': lambda a, b: a ^ (b << 2),
            'XOR_shifted_4': lambda a, b: a ^ (b << 4),
            'XOR_shifted_8': lambda a, b: a ^ (b << 8),
            'ADD': lambda a, b: a + b,
            'SUB': lambda a, b: max(0, a - b),
            'MUL': lambda a, b: a * b,
            'DIV': lambda a, b: a // b if b != 0 else 0,
            'ROT_ADD': lambda a, b: (a << 1 | a >> 63) + b if a.bit_length() <= 64 else a + b,
            'ROT_XOR': lambda a, b: (a << 1 | a >> 63) ^ b if a.bit_length() <= 64 else a ^ b,
        }
        
        # Results for each operation
        results = {op: [] for op in operations}
        
        # Test if any operations between consecutive terms match another term in the sequence
        for i in range(len(self.sequence)-2):
            if self.sequence[i] is None or self.sequence[i+1] is None:
                continue
                
            a, b = self.sequence[i], self.sequence[i+1]
            
            for op_name, op_func in operations.items():
                try:
                    result = op_func(a, b)
                    match_indices = []
                    
                    # Check if result matches any other value in sequence
                    for j, val in enumerate(self.sequence):
                        if val is not None and val == result:
                            match_indices.append(j+1)  # 1-indexed position
                    
                    if match_indices:
                        results[op_name].append({
                            'positions': (i+1, i+2),  # 1-indexed positions
                            'values': (a, b),
                            'result': result,
                            'matches': match_indices
                        })
                        print(f"Operation {op_name} on positions {i+1},{i+2} matches positions {match_indices}")
                except Exception as e:
                    # Skip operations that cause errors (e.g., overflow)
                    continue
        
        # Count total matches for each operation
        match_counts = {op: len(results[op]) for op in operations}
        print("\nOperation match counts:")
        for op, count in sorted(match_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{op}: {count} matches")
        
        return {
            'operations': results,
            'match_counts': match_counts
        }
    
    def analyze_balloon_patterns(self) -> Dict:
        """
        Look for patterns that resemble Balloon Hashing algorithm
        from the paper, which consists of:
        1. Initialize array with hash function
        2. Mix elements by accessing previous elements
        3. Perform random walks to access elements
        """
        print("\nAnalyzing patterns resembling Balloon Hashing...")
        
        # Function to test if a sequence follows the general form:
        # a[n] = f(a[n-1], a[g(n-1)])
        # where g(n-1) is a function that returns an index < n-1
        def test_balloon_pattern(f: Callable, max_index: int = 20) -> List[Dict]:
            results = []
            
            # For each position, try to find a pattern
            for n in range(3, min(max_index, len(self.sequence))):
                if self.sequence[n] is None or self.sequence[n-1] is None:
                    continue
                    
                current = self.sequence[n]
                prev = self.sequence[n-1]
                
                # Try different indices for the second term
                for j in range(1, n-1):
                    if self.sequence[j] is None:
                        continue
                        
                    prev_random = self.sequence[j]
                    
                    try:
                        # Apply the function
                        expected = f(prev, prev_random)
                        
                        # Check if it matches
                        if abs((expected - current) / current) < 0.001:  # Allow for small differences
                            results.append({
                                'position': n+1,  # 1-indexed
                                'formula': f"a[{n+1}] = f(a[{n}], a[{j+1}])",
                                'values': (prev, prev_random, current),
                                'error': abs((expected - current) / current)
                            })
                            print(f"Position {n+1}: Found potential pattern using positions {n} and {j+1}")
                    except Exception:
                        # Skip operations that cause errors
                        continue
            
            return results
        
        # Test various combination functions
        patterns = {
            'xor_then_add': test_balloon_pattern(lambda a, b: a ^ b + a),
            'xor_then_shift': test_balloon_pattern(lambda a, b: (a ^ b) << 1),
            'add_then_xor': test_balloon_pattern(lambda a, b: (a + b) ^ a),
            'interleave': test_balloon_pattern(lambda a, b: (a << 32) | (b & 0xFFFFFFFF) if a.bit_length() <= 64 and b.bit_length() <= 64 else a ^ b),
            'hash_mix': test_balloon_pattern(lambda a, b: ((a << 1) | (a >> 63)) ^ ((b << 5) | (b >> 59)) if a.bit_length() <= 64 and b.bit_length() <= 64 else a ^ b)
        }
        
        # Count patterns found for each function
        count_by_function = {func: len(patterns[func]) for func in patterns}
        
        # Find positions with the most matches
        position_matches = {}
        for func, results in patterns.items():
            for result in results:
                pos = result['position']
                position_matches[pos] = position_matches.get(pos, 0) + 1
        
        top_positions = sorted(position_matches.items(), key=lambda x: x[1], reverse=True)[:5]
        print("\nPositions with most pattern matches:")
        for pos, count in top_positions:
            print(f"Position {pos}: {count} matches")
        
        return {
            'patterns': patterns,
            'count_by_function': count_by_function,
            'top_positions': top_positions
        }
    
    def simulate_memory_hard_function(self, seed: int = 0x1, steps: int = 67) -> List[int]:
        """
        Simulate a memory-hard function similar to those in the papers
        to see if it produces a similar sequence
        """
        print(f"\nSimulating memory-hard function with seed {hex(seed)}...")
        
        # Constant multipliers used in hash functions
        C1 = 0x5851f42d4c957f2d  # From Percival's paper
        C2 = 0x2127599bf4325c37
        
        # Initialize memory with one value
        memory = [seed]
        
        # Fill memory with values derived from previous ones
        for i in range(1, steps):
            # Start with previous value
            prev = memory[i-1]
            
            # Apply mixing function with bit rotations and XOR operations
            # (similar to operations in Salsa20/8 core used in scrypt)
            value = ((prev << 1) | (prev >> 63)) if prev.bit_length() <= 64 else prev << 1
            value ^= prev * C1 & 0xFFFFFFFFFFFFFFFF  # Limit to 64 bits
            
            # Access random earlier element if available
            if i > 2:
                # Use value to create a 'random' index
                idx = prev % (i - 1)
                random_prev = memory[idx]
                
                # Mix with random previous value
                value ^= random_prev
                value = ((value << 3) | (value >> 61)) if value.bit_length() <= 64 else value << 3
                value ^= value * C2 & 0xFFFFFFFFFFFFFFFF
            
            memory.append(value)
        
        # Compare with actual sequence
        print("\nComparing simulated values with actual sequence:")
        for i in range(min(10, steps)):  # Just show first 10
            if self.sequence[i] is not None:
                match = "MATCH" if memory[i] == self.sequence[i] else "DIFF"
                print(f"Position {i+1}: Simulated={hex(memory[i])}, Actual={hex(self.sequence[i])} - {match}")
        
        return memory
    
    def analyze_full_sequence(self) -> Dict:
        """
        Run all analysis methods and summarize findings
        """
        print("Starting full sequence analysis...")
        
        # Run all analyses
        growth_results = self.analyze_growth_pattern()
        bit_op_results = self.analyze_bit_operations()
        balloon_results = self.analyze_balloon_patterns()
        
        # Try different seeds for simulation
        simulations = {}
        for seed in [0x1, 0x5851f42d, 0x2127599b]:
            simulations[hex(seed)] = self.simulate_memory_hard_function(seed)
        
        # Combine results
        summary = {
            'growth': growth_results,
            'bit_operations': bit_op_results,
            'balloon_patterns': balloon_results,
            'simulations': {k: [hex(v) for v in vals[:10]] for k, vals in simulations.items()}
        }
        
        # Print conclusion
        print("\n" + "="*50)
        print("ANALYSIS SUMMARY:")
        print("="*50)
        
        # Growth pattern
        print(f"\nAverage growth ratio: {growth_results['average_ratio']:.4f}")
        print(f"Ratio std deviation: {growth_results['std_ratio']:.4f}")
        
        # Most promising bit operations
        top_ops = sorted(bit_op_results['match_counts'].items(), key=lambda x: x[1], reverse=True)[:3]
        print("\nTop bit operations:")
        for op, count in top_ops:
            print(f"- {op}: {count} matches")
        
        # Most promising balloon patterns
        top_funcs = sorted(balloon_results['count_by_function'].items(), key=lambda x: x[1], reverse=True)[:3]
        print("\nTop pattern functions:")
        for func, count in top_funcs:
            print(f"- {func}: {count} matches")
            
        # Conclusion
        if top_ops[0][1] > 0 or top_funcs[0][1] > 0:
            print("\nCONCLUSION: The sequence shows characteristics of a memory-hard function.")
            if top_ops[0][1] > top_funcs[0][1]:
                print(f"The most promising pattern appears to be the '{top_ops[0][0]}' operation.")
            else:
                print(f"The most promising pattern appears to be the '{top_funcs[0][0]}' function.")
        else:
            print("\nCONCLUSION: No strong evidence found for a simple memory-hard function pattern.")
            print("The sequence may use a more complex combination of operations or a different approach.")
        
        return summary

def main():
    analyzer = SequenceAnalyzer()
    results = analyzer.analyze_full_sequence()
    print("\nAnalysis complete. Results saved to 'sequence_analysis_results/' directory.")

if __name__ == "__main__":
    main() 