"""
Permutation Property Analysis
Focuses on proving the permutation requirements from the paper
"""

import math
from typing import List, Dict, Tuple

class PermutationAnalyzer:
    def __init__(self):
        self.min_permutations = 3  # Paper requires minimum 3 permutations
        self.min_bit_change = 0.25  # Each permutation affects ~25% of bits
        
    def analyze_permutation_round(self, val1: int, val2: int) -> Dict:
        """Analyze a single permutation round"""
        bin1 = format(val1, 'b').zfill(256)
        bin2 = format(val2, 'b').zfill(256)
        
        # Analyze bit changes
        changes = []
        for i in range(len(bin1)):
            if bin1[i] != bin2[i]:
                changes.append(i)
                
        # Group changes into potential permutation rounds
        rounds = []
        current_round = []
        for pos in changes:
            if not current_round or pos - current_round[-1] <= 4:
                current_round.append(pos)
            else:
                rounds.append(current_round)
                current_round = [pos]
        if current_round:
            rounds.append(current_round)
            
        return {
            'total_changes': len(changes),
            'rounds': rounds,
            'round_count': len(rounds),
            'avg_changes_per_round': len(changes)/len(rounds) if rounds else 0
        }
        
    def verify_permutation_count(self, val1: int, val2: int) -> bool:
        """Verify that transition uses minimum required permutations"""
        analysis = self.analyze_permutation_round(val1, val2)
        return (
            analysis['round_count'] >= self.min_permutations and
            analysis['total_changes'] >= 256 * self.min_bit_change * self.min_permutations
        )
        
    def analyze_permutation_structure(self, val1: int, val2: int) -> Dict:
        """Analyze the structure of permutations between values"""
        bin1 = format(val1, 'b').zfill(256)
        bin2 = format(val2, 'b').zfill(256)
        
        # Analyze 4-bit block changes
        blocks = []
        for i in range(0, 256, 4):
            block1 = bin1[i:i+4]
            block2 = bin2[i:i+4]
            blocks.append({
                'position': i//4,
                'from': block1,
                'to': block2,
                'changes': sum(1 for j in range(4) if block1[j] != block2[j])
            })
            
        return {
            'block_count': len(blocks),
            'blocks': blocks,
            'avg_block_changes': sum(b['changes'] for b in blocks)/len(blocks)
        }
        
    def verify_permutation_properties(self, val1: int, val2: int) -> Dict:
        """Verify all permutation properties required by paper"""
        round_analysis = self.analyze_permutation_round(val1, val2)
        structure_analysis = self.analyze_permutation_structure(val1, val2)
        
        sufficient_rounds = round_analysis['round_count'] >= self.min_permutations
        sufficient_changes = round_analysis['total_changes'] >= 256 * self.min_bit_change * self.min_permutations
        good_distribution = structure_analysis['avg_block_changes'] >= 1.0
        
        return {
            'satisfies_min_rounds': sufficient_rounds,
            'satisfies_min_changes': sufficient_changes,
            'satisfies_distribution': good_distribution,
            'overall_valid': all([sufficient_rounds, sufficient_changes, good_distribution]),
            'round_analysis': round_analysis,
            'structure_analysis': structure_analysis
        }

def main():
    analyzer = PermutationAnalyzer()
    
    # Example values from sequence
    val1 = 0x2832ed74f2b5e35ee  # Position 66
    val2 = 0x349b84b6431a6c4ef1 # Position 70
    
    # Analyze permutation properties
    results = analyzer.verify_permutation_properties(val1, val2)
    
    print("Permutation Analysis Results:")
    print(f"Satisfies minimum rounds: {results['satisfies_min_rounds']}")
    print(f"Satisfies minimum changes: {results['satisfies_min_changes']}")
    print(f"Satisfies distribution: {results['satisfies_distribution']}")
    print(f"Overall valid: {results['overall_valid']}")
    print("\nRound Analysis:")
    print(f"Total rounds: {results['round_analysis']['round_count']}")
    print(f"Total bit changes: {results['round_analysis']['total_changes']}")
    print(f"Average changes per round: {results['round_analysis']['avg_changes_per_round']:.2f}")
    
if __name__ == "__main__":
    main() 