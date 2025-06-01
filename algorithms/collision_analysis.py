"""
Collision Resistance Analysis
Focuses on proving the collision resistance properties from the paper
"""

import math
from typing import List, Dict, Tuple

class CollisionAnalyzer:
    def __init__(self):
        self.min_security_bits = 120  # Paper's minimum security requirement
        
    def analyze_value_distribution(self, val1: int, val2: int) -> Dict:
        """Analyze the distribution between two values"""
        bin1 = format(val1, 'b').zfill(256)
        bin2 = format(val2, 'b').zfill(256)
        
        # Analyze bit differences
        differences = []
        for i in range(len(bin1)):
            if bin1[i] != bin2[i]:
                differences.append(i)
                
        # Calculate hamming weights
        weight1 = bin1.count('1')
        weight2 = bin2.count('1')
        
        return {
            'difference_count': len(differences),
            'difference_positions': differences,
            'hamming_weight1': weight1,
            'hamming_weight2': weight2,
            'weight_difference': abs(weight1 - weight2)
        }
        
    def calculate_collision_resistance(self, val1: int, val2: int) -> Dict:
        """Calculate collision resistance between values"""
        # Using paper's formula N^(1-α)
        n = math.log2(max(val1, val2))
        
        # Calculate α based on value growth
        growth = math.log2(val2) - math.log2(val1)
        alpha = 1 - (growth / (math.log2(val2) - math.log2(val1)))
        
        collision_resistance = 2 ** (n * (1-alpha))
        meets_requirement = collision_resistance >= 2**self.min_security_bits
        
        return {
            'collision_resistance': collision_resistance,
            'security_bits': math.log2(collision_resistance),
            'meets_requirement': meets_requirement,
            'alpha': alpha,
            'n': n
        }
        
    def analyze_collision_patterns(self, val1: int, val2: int) -> Dict:
        """Analyze patterns that could lead to collisions"""
        bin1 = format(val1, 'b').zfill(256)
        bin2 = format(val2, 'b').zfill(256)
        
        # Analyze 8-bit block patterns
        blocks = []
        for i in range(0, 256, 8):
            block1 = bin1[i:i+8]
            block2 = bin2[i:i+8]
            blocks.append({
                'position': i//8,
                'from': block1,
                'to': block2,
                'changes': sum(1 for j in range(8) if block1[j] != block2[j])
            })
            
        # Calculate pattern statistics
        avg_changes = sum(b['changes'] for b in blocks)/len(blocks)
        max_changes = max(b['changes'] for b in blocks)
        min_changes = min(b['changes'] for b in blocks)
        
        return {
            'block_count': len(blocks),
            'blocks': blocks,
            'avg_changes': avg_changes,
            'max_changes': max_changes,
            'min_changes': min_changes,
            'change_distribution': avg_changes/8  # Should be close to 0.5 for good diffusion
        }
        
    def verify_collision_resistance(self, val1: int, val2: int) -> Dict:
        """Verify all collision resistance properties"""
        distribution = self.analyze_value_distribution(val1, val2)
        resistance = self.calculate_collision_resistance(val1, val2)
        patterns = self.analyze_collision_patterns(val1, val2)
        
        # Verify all required properties
        good_distribution = distribution['difference_count'] >= 64  # At least 25% bits should differ
        good_resistance = resistance['meets_requirement']
        good_patterns = patterns['change_distribution'] >= 0.3  # Should have good diffusion
        
        return {
            'satisfies_distribution': good_distribution,
            'satisfies_resistance': good_resistance,
            'satisfies_patterns': good_patterns,
            'overall_valid': all([good_distribution, good_resistance, good_patterns]),
            'distribution_analysis': distribution,
            'resistance_analysis': resistance,
            'pattern_analysis': patterns
        }

def main():
    analyzer = CollisionAnalyzer()
    
    # Example values from sequence
    val1 = 0x2832ed74f2b5e35ee  # Position 66
    val2 = 0x349b84b6431a6c4ef1 # Position 70
    
    # Analyze collision resistance
    results = analyzer.verify_collision_resistance(val1, val2)
    
    print("Collision Resistance Analysis:")
    print(f"Satisfies distribution: {results['satisfies_distribution']}")
    print(f"Satisfies resistance: {results['satisfies_resistance']}")
    print(f"Satisfies patterns: {results['satisfies_patterns']}")
    print(f"Overall valid: {results['overall_valid']}")
    print("\nResistance Analysis:")
    print(f"Security bits: {results['resistance_analysis']['security_bits']:.2f}")
    print(f"Alpha value: {results['resistance_analysis']['alpha']:.4f}")
    print(f"Change distribution: {results['pattern_analysis']['change_distribution']:.4f}")
    
if __name__ == "__main__":
    main() 