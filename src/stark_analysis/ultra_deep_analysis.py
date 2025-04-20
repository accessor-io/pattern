#!/usr/bin/env python3

import os
import math
import secrets
from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime

# Define the class first
class UltraDeepAnalyzer:
    def __init__(self, prime: int = 2**251 + 17*2**192 + 1):
        self.prime = prime
        self.patterns = defaultdict(list)
        self.merkle_layers = []
        self.field_statistics = defaultdict(int)
        
    def ultra_deep_analyze(self, hex_strings: List[str]) -> Dict:
        print(f"\nStarting Ultra Deep Analysis at {datetime.now().strftime('%H:%M:%S')}")
        try:
            # Convert all hex strings to integers once
            values = [int(h, 16) for h in hex_strings]
            print(f"Converted {len(values)} hex strings to integers")
            
            results = {
                'merkle': self._deep_merkle_analysis(values),
                'field': self._deep_field_analysis(values),
                'patterns': self._deep_pattern_analysis(values),
                'relationships': self._deep_relationship_analysis(values),
                'sequences': self._analyze_sequence_properties(values),
                'cryptographic': self._analyze_crypto_properties(values)
            }
            
            # Cross-correlation analysis
            results['correlations'] = self._analyze_correlations(results)
            
            print(f"\nAnalysis Complete at {datetime.now().strftime('%H:%M:%S')}")
            return results
        except Exception as e:
            print(f"Error in ultra_deep_analyze: {e}")
            raise

    def _analyze_tree_properties(self, layers: List[List[int]]) -> Dict:
        """Analyze Merkle tree properties"""
        try:
            properties = {
                'balance_factor': self._calculate_balance_factor(layers),
                'branching_patterns': self._analyze_branching(layers),
                'layer_statistics': self._analyze_layer_stats(layers),
                'path_lengths': self._analyze_path_lengths(layers)
            }
            return properties
        except Exception as e:
            print(f"Warning: Error in tree property analysis: {e}")
            return {
                'balance_factor': 1.0,  # Perfect balance
                'branching_patterns': {'uniform': True},
                'layer_statistics': {'complete': True},
                'path_lengths': {'min': len(layers), 'max': len(layers)}
            }

    def _calculate_balance_factor(self, layers: List[List[int]]) -> float:
        """Calculate tree balance factor"""
        if not layers:
            return 1.0
        max_size = max(len(layer) for layer in layers)
        min_size = min(len(layer) for layer in layers)
        return min_size / max_size if max_size else 1.0

    def _analyze_branching(self, layers: List[List[int]]) -> Dict:
        """Analyze branching patterns in the tree"""
        patterns = {
            'uniform': True,
            'branch_factors': []
        }
        
        for i in range(len(layers)-1):
            if len(layers[i]) > 0:
                factor = len(layers[i]) / len(layers[i+1])
                patterns['branch_factors'].append(factor)
                if abs(factor - 2.0) > 0.001:  # Check if it's not binary
                    patterns['uniform'] = False
                    
        return patterns

    def _analyze_layer_stats(self, layers: List[List[int]]) -> Dict:
        """Analyze statistics for each layer"""
        stats = {
            'complete': True,
            'layer_sizes': [len(layer) for layer in layers],
            'value_ranges': []
        }
        
        for layer in layers:
            if layer:
                stats['value_ranges'].append({
                    'min': min(layer),
                    'max': max(layer),
                    'avg': sum(layer) / len(layer)
                })
                
        return stats

    def _analyze_path_lengths(self, layers: List[List[int]]) -> Dict:
        """Analyze path lengths in the tree"""
        return {
            'min': len(layers),
            'max': len(layers),
            'avg': len(layers),
            'is_balanced': True
        } 

    def _analyze_subgroup(self, value: int) -> Dict:
        """Analyze subgroup properties"""
        try:
            order = self._find_multiplicative_order(value)
            return {
                'order': order,
                'is_generator': order == self.prime - 1,
                'subgroup_size': order if order > 0 else None
            }
        except Exception as e:
            print(f"Warning: Error in subgroup analysis: {e}")
            return {'order': 0, 'is_generator': False, 'subgroup_size': None}

    def _check_field_extensions(self, value: int) -> Dict:
        """Check field extension properties"""
        try:
            return {
                'degree': self._estimate_extension_degree(value),
                'is_primitive': self._check_primitive_root(value) > 0.8
            }
        except Exception as e:
            print(f"Warning: Error in field extension check: {e}")
            return {'degree': 1, 'is_primitive': False}

    def _analyze_subgroup_structure(self, properties: List[Dict]) -> Dict:
        """Analyze subgroup structure patterns"""
        try:
            orders = [p['subgroup']['order'] for p in properties if p['subgroup']['order'] > 0]
            return {
                'unique_orders': len(set(orders)),
                'max_order': max(orders) if orders else 0,
                'min_order': min(orders) if orders else 0,
                'avg_order': sum(orders)/len(orders) if orders else 0
            }
        except Exception as e:
            print(f"Warning: Error in subgroup structure analysis: {e}")
            return {'unique_orders': 0, 'max_order': 0, 'min_order': 0, 'avg_order': 0}

    def _analyze_extension_patterns(self, properties: List[Dict]) -> Dict:
        """Analyze patterns in field extensions"""
        try:
            degrees = [p['field_extensions']['degree'] for p in properties]
            return {
                'unique_degrees': len(set(degrees)),
                'max_degree': max(degrees),
                'min_degree': min(degrees),
                'avg_degree': sum(degrees)/len(degrees)
            }
        except Exception as e:
            print(f"Warning: Error in extension pattern analysis: {e}")
            return {'unique_degrees': 0, 'max_degree': 1, 'min_degree': 1, 'avg_degree': 1}

    def _analyze_bit_patterns(self, values: List[int]) -> Dict:
        """Analyze bit-level patterns"""
        try:
            patterns = {
                'hamming_weights': [],
                'zero_runs': [],
                'one_runs': [],
                'bit_correlations': []
            }
            
            for value in values:
                binary = bin(value)[2:].zfill(256)
                patterns['hamming_weights'].append(binary.count('1'))
                patterns['zero_runs'].extend(self._find_zero_runs(binary))
                patterns['one_runs'].extend(self._find_one_runs(binary))
                patterns['bit_correlations'].append(self._analyze_bit_correlations(binary))
                
            return patterns
        except Exception as e:
            print(f"Warning: Error in bit pattern analysis: {e}")
            return {'hamming_weights': [], 'zero_runs': [], 'one_runs': [], 'bit_correlations': []}

    def _find_one_runs(self, binary: str) -> List[int]:
        """Find runs of consecutive ones"""
        runs = []
        current_run = 0
        for bit in binary:
            if bit == '1':
                current_run += 1
            elif current_run > 0:
                runs.append(current_run)
                current_run = 0
        if current_run > 0:
            runs.append(current_run)
        return runs

    def _analyze_bit_correlations(self, binary: str) -> Dict:
        """Analyze correlations between bits"""
        try:
            correlations = {
                'adjacent': 0,
                'alternate': 0,
                'third': 0
            }
            
            # Adjacent bits
            for i in range(len(binary)-1):
                if binary[i] == binary[i+1]:
                    correlations['adjacent'] += 1
                    
            # Alternate bits
            for i in range(len(binary)-2):
                if binary[i] == binary[i+2]:
                    correlations['alternate'] += 1
                    
            # Every third bit
            for i in range(len(binary)-3):
                if binary[i] == binary[i+3]:
                    correlations['third'] += 1
                    
            return correlations
        except Exception as e:
            print(f"Warning: Error in bit correlation analysis: {e}")
            return {'adjacent': 0, 'alternate': 0, 'third': 0}

    def _estimate_extension_degree(self, value: int) -> int:
        """Estimate the degree of the field extension"""
        try:
            # Simple estimation based on multiplicative order
            order = self._find_multiplicative_order(value)
            if order <= 1:
                return 1
            return math.ceil(math.log2(order))
        except Exception as e:
            print(f"Warning: Error in extension degree estimation: {e}")
            return 1

    def _analyze_sequence_properties(self, values: List[int]) -> Dict:
        """Analyze sequence-level properties"""
        try:
            return {
                'length': len(values),
                'unique_values': len(set(values)),
                'min_value': min(values),
                'max_value': max(values),
                'avg_value': sum(values) / len(values)
            }
        except Exception as e:
            print(f"Warning: Error in sequence property analysis: {e}")
            return {'length': 0, 'unique_values': 0, 'min_value': 0, 'max_value': 0, 'avg_value': 0}

    def _analyze_crypto_properties(self, values: List[int]) -> Dict:
        """Analyze cryptographic properties"""
        try:
            return {
                'entropy': self._estimate_entropy(values),
                'uniformity': self._check_uniformity(values),
                'independence': self._check_independence(values)
            }
        except Exception as e:
            print(f"Warning: Error in cryptographic analysis: {e}")
            return {'entropy': 0, 'uniformity': 0, 'independence': 0}

    def _estimate_entropy(self, values: List[int]) -> float:
        """Estimate entropy of the sequence"""
        try:
            frequencies = defaultdict(int)
            for value in values:
                frequencies[value] += 1
            
            entropy = 0
            n = len(values)
            for count in frequencies.values():
                p = count / n
                entropy -= p * math.log2(p)
            return entropy
        except Exception as e:
            print(f"Warning: Error in entropy estimation: {e}")
            return 0.0

    def _check_uniformity(self, values: List[int]) -> float:
        """Check uniformity of distribution"""
        try:
            unique_values = len(set(values))
            return unique_values / len(values)
        except Exception as e:
            print(f"Warning: Error in uniformity check: {e}")
            return 0.0

    def _check_independence(self, values: List[int]) -> float:
        """Check independence between consecutive values"""
        try:
            correlations = []
            for i in range(len(values)-1):
                correlations.append(abs(values[i+1] - values[i]) / max(values[i], 1))
            return sum(correlations) / len(correlations)
        except Exception as e:
            print(f"Warning: Error in independence check: {e}")
            return 0.0

    def _analyze_correlations(self, results: Dict) -> Dict:
        """Analyze correlations between different properties"""
        try:
            return {
                'merkle_field_correlation': self._correlate_merkle_field(results),
                'pattern_crypto_correlation': self._correlate_pattern_crypto(results),
                'sequence_relationship_correlation': self._correlate_sequence_relationship(results)
            }
        except Exception as e:
            print(f"Warning: Error in correlation analysis: {e}")
            return {'merkle_field_correlation': 0, 'pattern_crypto_correlation': 0, 'sequence_relationship_correlation': 0}

    def _correlate_merkle_field(self, results: Dict) -> float:
        """Correlate Merkle tree properties with field properties"""
        try:
            # Simple correlation metric
            return len(results['merkle']['layer_sizes']) / results['field']['statistics']['unique_orders']
        except Exception as e:
            print(f"Warning: Error in Merkle-field correlation: {e}")
            return 0.0

    def _correlate_pattern_crypto(self, results: Dict) -> float:
        """Correlate patterns with cryptographic properties"""
        try:
            return results['patterns']['bit_patterns']['hamming_weights'][0] / 256
        except Exception as e:
            print(f"Warning: Error in pattern-crypto correlation: {e}")
            return 0.0

    def _correlate_sequence_relationship(self, results: Dict) -> float:
        """Correlate sequence properties with relationships"""
        try:
            return results['sequences']['unique_values'] / results['sequences']['length']
        except Exception as e:
            print(f"Warning: Error in sequence-relationship correlation: {e}")
            return 0.0 

    def _deep_merkle_analysis(self, values: List[int]) -> Dict:
        """Detailed Merkle tree analysis"""
        print("\nPerforming deep Merkle analysis...")
        try:
            layers = []
            current_layer = values
            hashes = []
            
            while len(current_layer) > 1:
                next_layer = []
                layer_hashes = []
                for i in range(0, len(current_layer), 2):
                    if i + 1 < len(current_layer):
                        # Try different combining functions
                        xor_combined = current_layer[i] ^ current_layer[i+1]
                        add_combined = (current_layer[i] + current_layer[i+1]) % self.prime
                        mul_combined = (current_layer[i] * current_layer[i+1]) % self.prime
                        
                        # Store all combinations
                        next_layer.append(add_combined)  # Use addition for next layer
                        layer_hashes.append({
                            'xor': xor_combined,
                            'add': add_combined,
                            'mul': mul_combined
                        })
                
                layers.append(next_layer)
                hashes.append(layer_hashes)
                current_layer = next_layer
                
            return {
                'depth': len(layers),
                'layer_sizes': [len(layer) for layer in layers],
                'root_value': layers[-1][0] if layers else None,
                'layer_hashes': hashes,
                'tree_properties': self._analyze_tree_properties(layers)
            }
        except Exception as e:
            print(f"Error in deep Merkle analysis: {e}")
            return {
                'depth': 0,
                'layer_sizes': [],
                'root_value': None,
                'layer_hashes': [],
                'tree_properties': {}
            }

    def _deep_field_analysis(self, values: List[int]) -> Dict:
        """Detailed field arithmetic analysis"""
        print("\nPerforming deep field analysis...")
        try:
            properties = []
            for value in values:
                props = {
                    'quadratic': self._is_quadratic_residue(value),
                    'order': self._find_multiplicative_order(value),
                    'primitive': self._check_primitive_root(value),
                    'factors': self._find_small_factors(value),
                    'subgroup': self._analyze_subgroup(value),
                    'field_extensions': self._check_field_extensions(value)
                }
                properties.append(props)
                
            field_stats = {
                'properties': properties,
                'statistics': self._calculate_field_statistics(properties),
                'subgroup_structure': self._analyze_subgroup_structure(properties),
                'extension_patterns': self._analyze_extension_patterns(properties)
            }
            
            print("Field analysis complete")
            return field_stats
            
        except Exception as e:
            print(f"Error in deep field analysis: {e}")
            return {
                'properties': [],
                'statistics': {},
                'subgroup_structure': {},
                'extension_patterns': {}
            }

    def _deep_pattern_analysis(self, values: List[int]) -> Dict:
        """Detailed pattern analysis"""
        print("\nPerforming deep pattern analysis...")
        try:
            patterns = {
                'bit_patterns': self._analyze_bit_patterns(values),
                'value_patterns': self._analyze_value_patterns(values),
                'sequence_patterns': self._analyze_sequence_patterns(values),
                'mathematical_patterns': self._analyze_mathematical_patterns(values)
            }
            return patterns
        except Exception as e:
            print(f"Error in pattern analysis: {e}")
            return {
                'bit_patterns': {},
                'value_patterns': {},
                'sequence_patterns': {},
                'mathematical_patterns': {}
            }

    def _deep_relationship_analysis(self, values: List[int]) -> Dict:
        """Detailed relationship analysis"""
        print("\nPerforming deep relationship analysis...")
        try:
            relationships = {
                'consecutive': self._analyze_consecutive_relationships(values),
                'periodic': self._analyze_periodic_relationships(values),
                'mathematical': self._analyze_mathematical_relationships(values),
                'structural': self._analyze_structural_relationships(values)
            }
            return relationships
        except Exception as e:
            print(f"Error in relationship analysis: {e}")
            return {
                'consecutive': {},
                'periodic': {},
                'mathematical': {},
                'structural': {}
            }

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

    def _analyze_value_patterns(self, values: List[int]) -> Dict:
        """Analyze patterns in the values themselves"""
        try:
            return {
                'min_value': min(values),
                'max_value': max(values),
                'avg_value': sum(values) / len(values),
                'unique_values': len(set(values)),
                'value_frequencies': self._calculate_frequencies(values)
            }
        except Exception as e:
            print(f"Warning: Error in value pattern analysis: {e}")
            return {}

    def _calculate_frequencies(self, values: List[int]) -> Dict:
        """Calculate frequency distribution of values"""
        freq = defaultdict(int)
        for v in values:
            freq[v] += 1
        return dict(freq)

    def _analyze_consecutive_relationships(self, values: List[int]) -> Dict:
        """Analyze relationships between consecutive values"""
        try:
            relationships = {
                'differences': [],
                'ratios': [],
                'xor_results': []
            }
            
            for i in range(len(values)-1):
                relationships['differences'].append((values[i+1] - values[i]) % self.prime)
                if values[i] != 0:
                    relationships['ratios'].append((values[i+1] * pow(values[i], -1, self.prime)) % self.prime)
                relationships['xor_results'].append(values[i] ^ values[i+1])
                
            return relationships
        except Exception as e:
            print(f"Warning: Error in consecutive relationship analysis: {e}")
            return {}

    def _analyze_periodic_relationships(self, values: List[int]) -> Dict:
        """Analyze periodic relationships in the sequence"""
        try:
            return {
                'period_2': self._check_periodicity(values, 2),
                'period_3': self._check_periodicity(values, 3),
                'period_4': self._check_periodicity(values, 4)
            }
        except Exception as e:
            print(f"Warning: Error in periodic relationship analysis: {e}")
            return {}

    def _check_periodicity(self, values: List[int], period: int) -> Dict:
        """Check for periodicity with given period length"""
        patterns = defaultdict(int)
        for i in range(len(values) - period):
            pattern = tuple(values[i:i+period])
            patterns[pattern] += 1
        return dict(patterns)

    def _analyze_mathematical_relationships(self, values: List[int]) -> Dict:
        """Analyze mathematical relationships between values"""
        try:
            return {
                'linear': self._check_linear_relationships(values),
                'quadratic': self._check_quadratic_relationships(values),
                'exponential': self._check_exponential_relationships(values)
            }
        except Exception as e:
            print(f"Warning: Error in mathematical relationship analysis: {e}")
            return {}

    def _check_linear_relationships(self, values: List[int]) -> Dict:
        """Check for linear relationships"""
        diffs = [(values[i+1] - values[i]) % self.prime for i in range(len(values)-1)]
        return {
            'constant_diff': len(set(diffs)) == 1,
            'diff_values': list(set(diffs))
        }

    def _check_quadratic_relationships(self, values: List[int]) -> Dict:
        """Check for quadratic relationships"""
        if len(values) < 3:
            return {'found': False}
        
        second_diffs = []
        for i in range(len(values)-2):
            d1 = (values[i+1] - values[i]) % self.prime
            d2 = (values[i+2] - values[i+1]) % self.prime
            second_diffs.append((d2 - d1) % self.prime)
        
        return {
            'constant_second_diff': len(set(second_diffs)) == 1,
            'second_diff_values': list(set(second_diffs))
        }

    def _check_exponential_relationships(self, values: List[int]) -> Dict:
        """Check for exponential relationships"""
        if len(values) < 2:
            return {'found': False}
        
        ratios = []
        for i in range(len(values)-1):
            if values[i] != 0:
                ratios.append((values[i+1] * pow(values[i], -1, self.prime)) % self.prime)
        
        return {
            'constant_ratio': len(set(ratios)) == 1 if ratios else False,
            'ratio_values': list(set(ratios)) if ratios else []
        }

    def _analyze_structural_relationships(self, values: List[int]) -> Dict:
        """Analyze structural relationships in the sequence"""
        try:
            return {
                'symmetry': self._check_symmetry(values),
                'repetition': self._check_repetition(values),
                'reversibility': self._check_reversibility(values)
            }
        except Exception as e:
            print(f"Warning: Error in structural relationship analysis: {e}")
            return {}

    def _check_symmetry(self, values: List[int]) -> Dict:
        """Check for symmetrical patterns"""
        n = len(values)
        mid = n // 2
        return {
            'full_symmetry': values[:mid] == values[n-1:mid-1:-1],
            'partial_symmetry': self._find_partial_symmetries(values)
        }

    def _check_repetition(self, values: List[int]) -> Dict:
        """Check for repeating subsequences"""
        n = len(values)
        repetitions = []
        for length in range(1, n//2 + 1):
            if n % length == 0:
                if values[:length] * (n//length) == values:
                    repetitions.append(length)
        return {
            'repetition_lengths': repetitions,
            'shortest_repetition': min(repetitions) if repetitions else n
        }

    def _check_reversibility(self, values: List[int]) -> Dict:
        """Check if sequence can be reversed while maintaining properties"""
        return {
            'reversible': values == values[::-1],
            'partial_reversible': self._find_reversible_segments(values)
        }

    def _find_partial_symmetries(self, values: List[int]) -> List[Dict]:
        """Find partially symmetric segments"""
        symmetries = []
        n = len(values)
        for length in range(2, n):
            for start in range(n - length):
                segment = values[start:start+length]
                if segment == segment[::-1]:
                    symmetries.append({
                        'start': start,
                        'length': length,
                        'segment': segment
                    })
        return symmetries

    def _find_reversible_segments(self, values: List[int]) -> List[Dict]:
        """Find reversible segments in the sequence"""
        segments = []
        n = len(values)
        for length in range(2, n):
            for start in range(n - length):
                segment = values[start:start+length]
                if self._is_segment_reversible(segment):
                    segments.append({
                        'start': start,
                        'length': length,
                        'segment': segment
                    })
        return segments

    def _is_segment_reversible(self, segment: List[int]) -> bool:
        """Check if a segment is reversible"""
        return all((segment[i] - segment[i-1]) % self.prime == 
                   (segment[-i] - segment[-i-1]) % self.prime 
                   for i in range(1, len(segment)))

    def _analyze_sequence_patterns(self, values: List[int]) -> Dict:
        """Analyze sequence patterns in more detail"""
        try:
            return {
                'growth_rate': self._analyze_growth_rate(values),
                'recurring_differences': self._find_recurring_differences(values),
                'value_transitions': self._analyze_transitions(values),
                'pattern_metrics': self._calculate_pattern_metrics(values)
            }
        except Exception as e:
            print(f"Warning: Error in sequence pattern analysis: {e}")
            return {}

    def _is_quadratic_residue(self, value: int) -> bool:
        """Check if value is a quadratic residue"""
        try:
            return pow(value, (self.prime - 1) // 2, self.prime) == 1
        except Exception as e:
            print(f"Warning: Error in quadratic residue check: {e}")
            return False

    def _find_multiplicative_order(self, value: int) -> int:
        """Find multiplicative order of value"""
        try:
            if value == 0:
                return 0
            value = value % self.prime
            order = 1
            current = value
            while current != 1 and order < self.prime:
                current = (current * value) % self.prime
                order += 1
            return order if current == 1 else 0
        except Exception as e:
            print(f"Warning: Error in multiplicative order calculation: {e}")
            return 0

    def _analyze_growth_rate(self, values: List[int]) -> Dict:
        """Analyze the growth rate pattern"""
        try:
            growth_rates = []
            for i in range(len(values)-1):
                if values[i] != 0:
                    rate = values[i+1] / values[i]
                    growth_rates.append(rate)
            
            return {
                'min_rate': min(growth_rates),
                'max_rate': max(growth_rates),
                'avg_rate': sum(growth_rates) / len(growth_rates),
                'consistent_rates': [r for r in growth_rates if growth_rates.count(r) > 1]
            }
        except Exception as e:
            print(f"Warning: Error in growth rate analysis: {e}")
            return {}

    def _check_primitive_root(self, value: int, sample_size: int = 20) -> float:
        """Check if value might be a primitive root"""
        try:
            if value == 0:
                return 0.0
            
            count = 0
            seen = set()
            current = value % self.prime
            
            for _ in range(sample_size):
                if current in seen:
                    break
                seen.add(current)
                current = (current * value) % self.prime
                if current == 1:
                    count += 1
                
            return count / sample_size
        except Exception as e:
            print(f"Warning: Error in primitive root check: {e}")
            return 0.0

    def print_ultra_analysis(self, results: Dict):
        """Print comprehensive ultra-deep analysis results"""
        print("\n=== ULTRA-DEEP ANALYSIS RESULTS ===")
        
        print("\n1. Merkle Tree Analysis:")
        merkle = results.get('merkle', {})
        print(f"- Depth: {merkle.get('depth')}")
        print(f"- Layer sizes: {merkle.get('layer_sizes')}")
        print(f"- Root value: {hex(merkle.get('root_value', 0))}")
        
        print("\n2. Field Properties:")
        field = results.get('field', {})
        stats = field.get('statistics', {})
        for stat, value in stats.items():
            print(f"- {stat}: {value}")
        
        print("\n3. Pattern Analysis:")
        patterns = results.get('patterns', {})
        for category, data in patterns.items():
            print(f"\n{category}:")
            for key, value in data.items():
                print(f"- {key}: {value}")
        
        print("\n4. Relationship Analysis:")
        relationships = results.get('relationships', {})
        for category, data in relationships.items():
            print(f"\n{category}:")
            for key, value in data.items():
                print(f"- {key}: {value}")
        
        print("\n5. Sequence Properties:")
        sequences = results.get('sequences', {})
        for key, value in sequences.items():
            print(f"- {key}: {value}")
        
        print("\n6. Cryptographic Properties:")
        crypto = results.get('cryptographic', {})
        for key, value in crypto.items():
            print(f"- {key}: {value}")
        
        print("\n7. Correlations:")
        correlations = results.get('correlations', {})
        for key, value in correlations.items():
            print(f"- {key}: {value}")

# Define the main function after the class
def main():
    print("Starting script...")
    try:
        print("Trying to open file...")
        with open('../../data/32bHex.txt', 'r') as f:
            print("File opened successfully")
            hex_strings = [line.strip() for line in f]
            print(f"Read {len(hex_strings)} lines")
        
        print("Creating analyzer...")
        analyzer = UltraDeepAnalyzer()
        print("Running analysis...")
        results = analyzer.ultra_deep_analyze(hex_strings)
        print("Analysis complete, printing results...")
        analyzer.print_ultra_analysis(results)
        
    except FileNotFoundError:
        print("Error: Could not find the data file at ../../data/32bHex.txt")
        print("Current working directory:", os.getcwd())
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

# Run the main function
if __name__ == "__main__":
    print("Script initialized")
    main() 