from typing import List, Dict, Tuple
from collections import defaultdict
import secrets
import math
from datetime import datetime

class DeepPatternAnalyzer:
    def __init__(self, prime: int = 2**251 + 17*2**192 + 1):
        self.prime = prime
        self.patterns = defaultdict(list)
        self.merkle_layers = []
        self.field_statistics = defaultdict(int)
        
    def deep_analyze(self, hex_strings: List[str]) -> Dict:
        print("\nStarting Deep Analysis...")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        
        results = {
            'merkle': self._analyze_merkle(hex_strings),
            'field': self._analyze_field_properties(hex_strings),
            'patterns': self._analyze_patterns(hex_strings),
            'relationships': self._analyze_relationships(hex_strings)
        }
        
        print(f"\nAnalysis Complete - Time: {datetime.now().strftime('%H:%M:%S')}")
        return results
        
    def _analyze_merkle(self, hex_strings: List[str]) -> Dict:
        """Analyze Merkle tree structure and properties"""
        print("\nAnalyzing Merkle structure...")
        
        values = [int(h, 16) for h in hex_strings]
        layers = []
        current_layer = values
        
        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                if i + 1 < len(current_layer):
                    combined = (current_layer[i] + current_layer[i+1]) % self.prime
                    next_layer.append(combined)
            layers.append(next_layer)
            current_layer = next_layer
            
        return {
            'depth': len(layers),
            'layer_sizes': [len(layer) for layer in layers],
            'root_value': layers[-1][0] if layers else None
        }
        
    def _analyze_field_properties(self, hex_strings: List[str]) -> Dict:
        """Analyze field arithmetic properties"""
        print("\nAnalyzing field properties...")
        
        properties = []
        for hex_str in hex_strings:
            value = int(hex_str, 16)
            props = {
                'quadratic': self._is_quadratic_residue(value),
                'order': self._find_multiplicative_order(value),
                'primitive': self._check_primitive_root(value),
                'factors': self._find_small_factors(value)
            }
            properties.append(props)
            
        return {
            'properties': properties,
            'statistics': self._calculate_field_statistics(properties)
        }
        
    def _analyze_patterns(self, hex_strings: List[str]) -> Dict:
        """Analyze bit patterns and sequences"""
        print("\nAnalyzing patterns...")
        
        patterns = {
            'hamming_weights': [],
            'zero_runs': [],
            'periodic': [],
            'subsequences': []
        }
        
        for hex_str in hex_strings:
            binary = bin(int(hex_str, 16))[2:].zfill(256)
            patterns['hamming_weights'].append(binary.count('1'))
            patterns['zero_runs'].append(self._find_zero_runs(binary))
            patterns['periodic'].append(self._find_periodic_segments(binary))
            patterns['subsequences'].append(self._find_interesting_subsequences(binary))
            
        return patterns
        
    def _analyze_relationships(self, hex_strings: List[str]) -> Dict:
        """Analyze relationships between consecutive values"""
        print("\nAnalyzing relationships...")
        
        relationships = {
            'xor_patterns': [],
            'add_patterns': [],
            'mul_patterns': [],
            'differences': []
        }
        
        values = [int(h, 16) for h in hex_strings]
        for i in range(len(values)-1):
            relationships['xor_patterns'].append(values[i] ^ values[i+1])
            relationships['add_patterns'].append((values[i] + values[i+1]) % self.prime)
            relationships['mul_patterns'].append((values[i] * values[i+1]) % self.prime)
            relationships['differences'].append((values[i+1] - values[i]) % self.prime)
            
        return relationships

    def print_analysis(self, results: Dict):
        """Print comprehensive analysis results"""
        print("\n=== COMPREHENSIVE ANALYSIS RESULTS ===")
        
        print("\n1. Merkle Tree Analysis:")
        print(f"- Depth: {results['merkle']['depth']}")
        print(f"- Layer sizes: {results['merkle']['layer_sizes']}")
        print(f"- Root value: {hex(results['merkle']['root_value'])}")
        
        print("\n2. Field Properties:")
        stats = results['field']['statistics']
        print(f"- Quadratic residues: {stats['quadratic_residues']}")
        print(f"- Average order: {stats['avg_order']:.2f}")
        print(f"- Primitive roots found: {stats['primitive_roots']}")
        
        print("\n3. Pattern Analysis:")
        patterns = results['patterns']
        print(f"- Unique Hamming weights: {len(set(patterns['hamming_weights']))}")
        print(f"- Average zero runs: {sum(len(x) for x in patterns['zero_runs'])/len(patterns['zero_runs']):.2f}")
        print(f"- Total periodic patterns: {sum(len(x) for x in patterns['periodic'])}")
        
        print("\n4. Relationship Analysis:")
        rel = results['relationships']
        print(f"- Unique XOR patterns: {len(set(rel['xor_patterns']))}")
        print(f"- Unique ADD patterns: {len(set(rel['add_patterns']))}")
        print(f"- Unique MUL patterns: {len(set(rel['mul_patterns']))}")
        print(f"- Average difference: {sum(rel['differences'])/len(rel['differences'])}")

    def _is_quadratic_residue(self, value: int) -> bool:
        """Check if value is a quadratic residue"""
        if value == 0:
            return True
        return pow(value, (self.prime - 1) // 2, self.prime) == 1

    def _find_multiplicative_order(self, value: int, max_check: int = 100) -> int:
        """Find multiplicative order up to max_check"""
        if value == 0:
            return 0
        current = value
        for i in range(1, max_check):
            if current == 1:
                return i
            current = (current * value) % self.prime
        return -1

    def _check_primitive_root(self, value: int, sample_size: int = 20) -> float:
        """Check if value might be a primitive root"""
        if value == 0:
            return 0.0
        
        factors = [2, 3, 5, 7, 11, 13]
        power = (self.prime - 1)
        tests_passed = 0
        
        try:
            for factor in factors:
                if power % factor == 0:
                    if pow(value, power // factor, self.prime) == 1:
                        return 0.0
                    tests_passed += 1
            
            for _ in range(sample_size - len(factors)):
                random_exp = secrets.randbelow(min(power, 2**256))
                test = pow(value, random_exp + 1, self.prime)
                if test != 1:
                    tests_passed += 1
            
            return tests_passed / sample_size
        except Exception as e:
            print(f"Warning: Error in primitive root check: {e}")
            return 0.0

    def _find_small_factors(self, value: int, limit: int = 100) -> List[int]:
        """Find small prime factors up to limit"""
        factors = []
        n = value
        for i in range(2, limit + 1):
            while n % i == 0:
                factors.append(i)
                n //= i
            if n == 1:
                break
        return factors

    def _find_zero_runs(self, binary: str) -> List[int]:
        """Find runs of consecutive zeros"""
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

    def _find_interesting_subsequences(self, binary: str) -> List[Dict]:
        """Find interesting subsequences"""
        sequences = []
        # Look for repeating patterns
        for length in range(2, min(32, len(binary))):
            for start in range(len(binary) - length):
                pattern = binary[start:start+length]
                count = binary.count(pattern)
                if count > 1:
                    sequences.append({
                        'pattern': pattern,
                        'length': length,
                        'count': count
                    })
        return sequences

    def _calculate_field_statistics(self, properties: List[Dict]) -> Dict:
        """Calculate statistics from field properties"""
        stats = {
            'quadratic_residues': sum(1 for p in properties if p['quadratic']),
            'primitive_roots': sum(1 for p in properties if p['primitive'] > 0.8),
            'avg_order': sum(p['order'] for p in properties if p['order'] > 0) / len(properties),
            'factor_frequencies': defaultdict(int)
        }
        
        for prop in properties:
            for factor in prop['factors']:
                stats['factor_frequencies'][factor] += 1
                
        return stats

def main():
    try:
        with open('../../data/32bHex.txt', 'r') as f:
            hex_strings = [line.strip() for line in f]
        
        analyzer = DeepPatternAnalyzer()
        results = analyzer.deep_analyze(hex_strings)
        analyzer.print_analysis(results)
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 