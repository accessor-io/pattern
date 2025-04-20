"""
Sequence Analysis and Proof Algorithm
Based on Rogaway-Steinberger paper theorems
"""

import math
from typing import List, Dict, Tuple

class SequenceAnalyzer:
    def __init__(self):
        # Known sequence values from 5th onwards
        self.known_values = {
            5: 0x15,    # 21
            6: 0x31,    # 49
            7: 0x4c,    # 76
            8: 0xe0,    # 224
            9: 0x1d3,   # 467
            10: 0x202,  # 514
            # ... continuing through
            66: 0x2832ed74f2b5e35ee,
            70: 0x349b84b6431a6c4ef1,
            75: 0x4c5ce114686a1336e07,
            80: 0xea1a5c66dcc11b5ad180,
            85: 0x11720c4f018d51b8cebba8,
            90: 0x2ce00bb2136a445c71e85bf,
            95: 0x527a792b183c7f64a0e8b1f4,
            100: 0xaf55fc59c335c8ec67ed24826,
            105: 0x16f14fc2054cd87ee6396b33df3
        }

    def analyze_bit_transitions(self, val1: int, val2: int) -> Dict:
        """Analyze bit-level transitions between two values"""
        bin1 = format(val1, 'b').zfill(256)
        bin2 = format(val2, 'b').zfill(256)
        
        changes = sum(1 for i in range(len(bin1)) if bin1[i] != bin2[i])
        hamming_weight1 = bin1.count('1')
        hamming_weight2 = bin2.count('1')
        
        return {
            'changes': changes,
            'hamming_weight_from': hamming_weight1,
            'hamming_weight_to': hamming_weight2,
            'change_ratio': changes / 256
        }

    def calculate_rate_alpha(self, pos1: int, pos2: int) -> float:
        """Calculate rate-α between two positions"""
        val1 = self.known_values[pos1]
        val2 = self.known_values[pos2]
        
        # Using paper's formula: N^(1-α)
        n = math.log2(val2) - math.log2(val1)
        positions = pos2 - pos1
        
        return 1 - (n / positions)

    def verify_permutation_properties(self, pos: int) -> bool:
        """Verify permutation properties for a position"""
        if pos not in self.known_values or pos-1 not in self.known_values:
            return False
            
        val1 = self.known_values[pos-1]
        val2 = self.known_values[pos]
        
        transitions = self.analyze_bit_transitions(val1, val2)
        
        # Paper requires minimum 3 permutations
        # Each permutation affects ~25% of bits
        min_changes = 256 * 0.25 * 3
        
        return transitions['changes'] >= min_changes

    def check_collision_resistance(self, pos1: int, pos2: int) -> bool:
        """Check collision resistance between positions"""
        if pos1 not in self.known_values or pos2 not in self.known_values:
            return False
            
        val1 = self.known_values[pos1]
        val2 = self.known_values[pos2]
        
        # Paper requires collision resistance of N^(1-α)
        alpha = self.calculate_rate_alpha(pos1, pos2)
        n = math.log2(max(val1, val2))
        
        collision_resistance = 2 ** (n * (1-alpha))
        return collision_resistance >= 2**120  # Paper's minimum requirement

    def analyze_sequence_range(self, start_pos: int, end_pos: int) -> Dict:
        """Analyze a range of sequence values"""
        results = {
            'rate_alpha': [],
            'permutation_valid': [],
            'collision_resistant': [],
            'bit_transitions': []
        }
        
        for pos in range(start_pos, end_pos):
            if pos in self.known_values and pos+1 in self.known_values:
                results['rate_alpha'].append(
                    self.calculate_rate_alpha(pos, pos+1)
                )
                results['permutation_valid'].append(
                    self.verify_permutation_properties(pos+1)
                )
                results['collision_resistant'].append(
                    self.check_collision_resistance(pos, pos+1)
                )
                results['bit_transitions'].append(
                    self.analyze_bit_transitions(
                        self.known_values[pos],
                        self.known_values[pos+1]
                    )
                )
                
        return results

    def prove_sequence_properties(self) -> bool:
        """Prove that sequence satisfies paper's theorems"""
        all_positions = sorted(self.known_values.keys())
        
        for i in range(len(all_positions)-1):
            pos1 = all_positions[i]
            pos2 = all_positions[i+1]
            
            # Check rate-α requirement
            alpha = self.calculate_rate_alpha(pos1, pos2)
            if alpha >= 0.5:  # Paper requires α < 0.5
                return False
                
            # Check permutation properties
            if not self.verify_permutation_properties(pos2):
                return False
                
            # Check collision resistance
            if not self.check_collision_resistance(pos1, pos2):
                return False
                
        return True

def main():
    analyzer = SequenceAnalyzer()
    
    # Analyze early sequence (5-15)
    early_results = analyzer.analyze_sequence_range(5, 15)
    print("Early Sequence Analysis:")
    print(f"Average rate-α: {sum(early_results['rate_alpha'])/len(early_results['rate_alpha'])}")
    print(f"All permutations valid: {all(early_results['permutation_valid'])}")
    print(f"Collision resistant: {all(early_results['collision_resistant'])}")
    
    # Analyze later sequence (66-105)
    later_results = analyzer.analyze_sequence_range(66, 105)
    print("\nLater Sequence Analysis:")
    print(f"Average rate-α: {sum(later_results['rate_alpha'])/len(later_results['rate_alpha'])}")
    print(f"All permutations valid: {all(later_results['permutation_valid'])}")
    print(f"Collision resistant: {all(later_results['collision_resistant'])}")
    
    # Prove sequence properties
    satisfies_theorems = analyzer.prove_sequence_properties()
    print(f"\nSequence satisfies all paper theorems: {satisfies_theorems}")

if __name__ == "__main__":
    main() 