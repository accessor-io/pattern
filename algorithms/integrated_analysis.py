"""
Integrated Analysis Algorithm
Combines sequence analysis with collision resistance properties
"""

import math
from typing import List, Dict, Tuple

class IntegratedAnalyzer:
    def __init__(self):
        self.min_security_bits = 120
        self.min_permutations = 3
        self.min_bit_change = 0.25
        
    def analyze_transition(self, val1: int, val2: int) -> Dict:
        """Complete transition analysis between two values"""
        bin1 = format(val1, 'b').zfill(256)
        bin2 = format(val2, 'b').zfill(256)
        
        # Bit-level analysis
        changes = []
        for i in range(len(bin1)):
            if bin1[i] != bin2[i]:
                changes.append(i)
                
        # Calculate properties
        weight1 = bin1.count('1')
        weight2 = bin2.count('1')
        
        # Group changes into rounds
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
            'changes': {
                'count': len(changes),
                'positions': changes,
                'ratio': len(changes) / 256
            },
            'weights': {
                'from': weight1,
                'to': weight2,
                'difference': abs(weight1 - weight2)
            },
            'rounds': {
                'count': len(rounds),
                'positions': rounds,
                'avg_size': len(changes)/len(rounds) if rounds else 0
            }
        }
        
    def analyze_block_structure(self, val1: int, val2: int, block_size: int = 8) -> Dict:
        """Analyze block-level patterns"""
        bin1 = format(val1, 'b').zfill(256)
        bin2 = format(val2, 'b').zfill(256)
        
        blocks = []
        for i in range(0, 256, block_size):
            block1 = bin1[i:i+block_size]
            block2 = bin2[i:i+block_size]
            blocks.append({
                'position': i//block_size,
                'from': block1,
                'to': block2,
                'changes': sum(1 for j in range(block_size) if block1[j] != block2[j])
            })
            
        avg_changes = sum(b['changes'] for b in blocks)/len(blocks)
        return {
            'blocks': blocks,
            'statistics': {
                'avg_changes': avg_changes,
                'max_changes': max(b['changes'] for b in blocks),
                'min_changes': min(b['changes'] for b in blocks),
                'distribution': avg_changes/block_size
            }
        }
        
    def calculate_security_properties(self, val1: int, val2: int) -> Dict:
        """Calculate security-related properties"""
        if val1 == 0 or val2 == 0:
            return {
                'alpha': 0.5,
                'n': 0,
                'collision_resistance': {
                    'bits': 0,
                    'value': 0,
                    'meets_requirement': False
                }
            }
            
        n = math.log2(max(val1, val2))
        growth = math.log2(val2) - math.log2(val1)
        
        # Handle edge cases
        if abs(growth) < 1e-10:  # Values too close
            alpha = 0.5
        else:
            log_diff = math.log2(val2) - math.log2(val1)
            if abs(log_diff) < 1e-10:  # Log values too close
                alpha = 0.5
            else:
                alpha = 1 - (growth / log_diff)
        
        # Ensure alpha is in valid range
        alpha = max(0, min(1, alpha))
        
        collision_resistance = 2 ** (n * (1-alpha))
        
        return {
            'alpha': alpha,
            'n': n,
            'collision_resistance': {
                'bits': math.log2(collision_resistance),
                'value': collision_resistance,
                'meets_requirement': collision_resistance >= 2**self.min_security_bits
            }
        }
        
    def verify_sequence_properties(self, val1: int, val2: int) -> Dict:
        """Verify all required properties for sequence"""
        transition = self.analyze_transition(val1, val2)
        blocks = self.analyze_block_structure(val1, val2)
        security = self.calculate_security_properties(val1, val2)
        
        # Verify requirements
        sufficient_changes = transition['changes']['count'] >= 256 * self.min_bit_change
        sufficient_rounds = transition['rounds']['count'] >= self.min_permutations
        good_distribution = blocks['statistics']['distribution'] >= 0.3
        meets_security = security['collision_resistance']['meets_requirement']
        
        return {
            'valid': all([
                sufficient_changes,
                sufficient_rounds,
                good_distribution,
                meets_security
            ]),
            'properties': {
                'changes_valid': sufficient_changes,
                'rounds_valid': sufficient_rounds,
                'distribution_valid': good_distribution,
                'security_valid': meets_security
            },
            'analysis': {
                'transition': transition,
                'blocks': blocks,
                'security': security
            }
        }
        
    def analyze_sequence_range(self, values: List[int]) -> List[Dict]:
        """Analyze a range of sequence values"""
        results = []
        for i in range(len(values)-1):
            val1 = values[i]
            val2 = values[i+1]
            results.append(self.verify_sequence_properties(val1, val2))
        return results

def main():
    analyzer = IntegratedAnalyzer()
    
    # Example sequence values
    values = [
        0x2832ed74f2b5e35ee,  # Position 66
        0x349b84b6431a6c4ef1, # Position 70
        0x4c5ce114686a1336e07 # Position 75
    ]
    
    # Analyze sequence
    results = analyzer.analyze_sequence_range(values)
    
    print("Sequence Analysis Results:")
    for i, result in enumerate(results):
        print(f"\nTransition {i+1}->>{i+2}:")
        print(f"Valid: {result['valid']}")
        print("Properties:")
        for prop, valid in result['properties'].items():
            print(f"  {prop}: {valid}")
        print(f"Security bits: {result['analysis']['security']['collision_resistance']['bits']:.2f}")
        print(f"Alpha value: {result['analysis']['security']['alpha']:.4f}")
        
if __name__ == "__main__":
    main() 