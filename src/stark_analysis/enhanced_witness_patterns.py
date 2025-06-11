from typing import List, Dict, Tuple
from collections import defaultdict
import secrets  # Replace numpy with secrets for large integers

class StarkPatternAnalyzer:
    def __init__(self, prime: int = 2**251 + 17*2**192 + 1):
        self.prime = prime
        self.patterns = defaultdict(list)
    
    def _check_primitive_root(self, value: int, sample_size: int = 20) -> float:
        """
        Check if value might be a primitive root modulo prime
        Using secrets for cryptographically secure random numbers
        """
        if value == 0:
            return 0.0
            
        # Test small factors first
        factors = [2, 3, 5, 7, 11, 13]
        power = (self.prime - 1)
        tests_passed = 0
        
        try:
            for factor in factors:
                if power % factor == 0:
                    if pow(value, power // factor, self.prime) == 1:
                        return 0.0
                    tests_passed += 1
                    
            # Random sampling for larger factors using secrets instead of numpy
            for _ in range(sample_size - len(factors)):
                # Use secrets.randbelow for large integers
                random_exp = secrets.randbelow(min(power, 2**256))
                test = pow(value, random_exp + 1, self.prime)
                if test != 1:
                    tests_passed += 1
                    
            return tests_passed / sample_size
            
        except Exception as e:
            print(f"Warning: Error in primitive root check: {e}")
            return 0.0

    def analyze_cycle_patterns(self, hex_strings: List[str]) -> Dict:
        """Detailed analysis of cycle patterns"""
        cycles = []
        
        for i in range(len(hex_strings)):
            current = int(hex_strings[i], 16)
            if i > 0:
                prev = int(hex_strings[i-1], 16)
                self.patterns['xor'].append(current ^ prev)
                self.patterns['add'].append((current + prev) % self.prime)
                self.patterns['mul'].append((current * prev) % self.prime)
                
            cycles.append(self._analyze_single_cycle(current))
            
        return {
            'cycles': cycles,
            'patterns': dict(self.patterns),
            'merkle_depth': self._calculate_merkle_depth(len(hex_strings)),
            'constraint_summary': self._summarize_constraints()
        }
    
    def _analyze_single_cycle(self, value: int) -> Dict:
        """Analyze a single cycle for patterns"""
        binary = bin(value)[2:].zfill(256)
        return {
            'hamming_weight': binary.count('1'),
            'zero_runs': self._count_zero_runs(binary),
            'periodic_segments': self._find_periodic_segments(binary),
            'field_properties': self._analyze_field_properties(value)
        }
    
    def _find_periodic_segments(self, binary: str) -> List[Dict]:
        """Find periodic segments in binary string"""
        segments = []
        for length in range(2, len(binary)//2):
            for start in range(len(binary) - 2*length):
                segment = binary[start:start+length]
                if binary[start+length:start+2*length] == segment:
                    segments.append({
                        'length': length,
                        'start': start,
                        'pattern': segment
                    })
        return segments
    
    def _analyze_field_properties(self, value: int) -> Dict:
        """Analyze field arithmetic properties"""
        return {
            'is_quadratic_residue': self._is_quadratic_residue(value),
            'multiplicative_order': self._find_multiplicative_order(value),
            'primitive_root_probability': self._check_primitive_root(value)
        }
    
    def _is_quadratic_residue(self, value: int) -> bool:
        """Check if value is a quadratic residue"""
        return pow(value, (self.prime - 1) // 2, self.prime) == 1
    
    def _find_multiplicative_order(self, value: int, max_check: int = 100) -> int:
        """Find multiplicative order (up to max_check)"""
        if value == 0:
            return 0
        current = value
        for i in range(1, max_check):
            if current == 1:
                return i
            current = (current * value) % self.prime
        return -1  # Order is larger than max_check
    
    @staticmethod
    def _count_zero_runs(binary: str) -> List[int]:
        """Count consecutive zeros"""
        runs = []
        current_run = 0
        for bit in binary:
            if bit == '0':
                current_run += 1
            elif current_run > 0:
                runs.append(current_run)
                current_run = 0
        if current_run > 0:
            runs.append(current_run)
        return runs
    
    @staticmethod
    def _calculate_merkle_depth(n: int) -> int:
        """Calculate theoretical Merkle tree depth"""
        return (n - 1).bit_length()
    
    def _summarize_constraints(self) -> Dict:
        """Summarize constraint patterns"""
        return {
            'xor_patterns': len(set(self.patterns['xor'])),
            'add_patterns': len(set(self.patterns['add'])),
            'mul_patterns': len(set(self.patterns['mul'])),
            'total_unique_patterns': len(set(
                self.patterns['xor'] + 
                self.patterns['add'] + 
                self.patterns['mul']
            ))
        }

def main():
    try:
        # Load hex strings
        with open('../../data/32bHex.txt', 'r') as f:
            hex_strings = [line.strip() for line in f]
        
        # Analyze patterns
        analyzer = StarkPatternAnalyzer()
        results = analyzer.analyze_cycle_patterns(hex_strings)
        
        # Print detailed results
        print("\n=== Enhanced STARK Pattern Analysis ===")
        print(f"\nTotal Cycles Analyzed: {len(results['cycles'])}")
        print(f"Merkle Tree Depth: {results['merkle_depth']}")
        print("\nConstraint Pattern Summary:")
        print(f"- Unique XOR patterns: {results['constraint_summary']['xor_patterns']}")
        print(f"- Unique ADD patterns: {results['constraint_summary']['add_patterns']}")
        print(f"- Unique MUL patterns: {results['constraint_summary']['mul_patterns']}")
        print(f"- Total unique patterns: {results['constraint_summary']['total_unique_patterns']}")
        
        # Print detailed cycle analysis for first few cycles
        print("\nDetailed Cycle Analysis (first 3 cycles):")
        for i, cycle in enumerate(results['cycles'][:3]):
            print(f"\nCycle {i}:")
            print(f"- Hamming weight: {cycle['hamming_weight']}")
            print(f"- Zero runs: {len(cycle['zero_runs'])} runs, max length: {max(cycle['zero_runs']) if cycle['zero_runs'] else 0}")
            print(f"- Periodic segments: {len(cycle['periodic_segments'])}")
            print(f"- Field properties:")
            print(f"  * Quadratic residue: {cycle['field_properties']['is_quadratic_residue']}")
            print(f"  * Multiplicative order: {cycle['field_properties']['multiplicative_order']}")
            print(f"  * Primitive root probability: {cycle['field_properties']['primitive_root_probability']:.2f}")

    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 