"""
Hybrid Cryptographic Sequence Analysis
Combines concepts from scrypt, Balloon Hashing, and other cryptographic primitives
"""

import math
import logging
import json
import os
import struct
import hashlib
import binascii
from typing import List, Dict, Optional, Tuple, Callable

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HybridCryptoAnalyzer:
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
        
        # Future known values (for verification)
        self.future_values = {
            70: 0x349b84b6431a6c4ef1,
            75: 0x4c5ce114686a1336e07,
            80: 0xea1a5c66dcc11b5ad180,
            85: 0x11720c4f018d51b8cebba8,
            90: 0x2ce00bb2136a445c71e85bf,
            95: 0x527a792b183c7f64a0e8b1f4,
            100: 0xaf55fc59c335c8ec67ed24826
        }
        
        # Create output directories
        os.makedirs('analysis_hybrid', exist_ok=True)
    
    def analyze_growth_rate(self):
        """Analyze the growth rate of the sequence"""
        growth_ratios = []
        log_growth = []
        bit_growth = []
        
        for i in range(1, len(self.sequence)):
            if self.sequence[i-1] != 0:
                ratio = self.sequence[i] / self.sequence[i-1]
                growth_ratios.append({
                    'position': i+1,
                    'ratio': ratio,
                    'prev': hex(self.sequence[i-1]),
                    'curr': hex(self.sequence[i])
                })
            
            # Calculate logarithmic growth
            if self.sequence[i-1] > 0 and self.sequence[i] > 0:
                log_growth.append({
                    'position': i+1,
                    'log_ratio': math.log(self.sequence[i]) / math.log(self.sequence[i-1]),
                    'log2_prev': math.log2(self.sequence[i-1]),
                    'log2_curr': math.log2(self.sequence[i])
                })
            
            # Calculate bit length growth
            bit_len_prev = self.sequence[i-1].bit_length()
            bit_len_curr = self.sequence[i].bit_length()
            bit_growth.append({
                'position': i+1,
                'bit_len_prev': bit_len_prev,
                'bit_len_curr': bit_len_curr,
                'bit_growth': bit_len_curr - bit_len_prev
            })
        
        # Calculate statistics on growth ratios
        ratios = [item['ratio'] for item in growth_ratios]
        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            min_ratio = min(ratios)
            max_ratio = max(ratios)
            
            logging.info(f"Growth ratio stats - Avg: {avg_ratio:.2f}, Min: {min_ratio:.2f}, Max: {max_ratio:.2f}")
        
        # Analyze bit length growth
        bit_growths = [item['bit_growth'] for item in bit_growth]
        if bit_growths:
            avg_bit_growth = sum(bit_growths) / len(bit_growths)
            
            logging.info(f"Average bit length growth: {avg_bit_growth:.2f} bits per step")
        
        results = {
            'growth_ratios': growth_ratios,
            'log_growth': log_growth,
            'bit_growth': bit_growth,
            'stats': {
                'avg_ratio': avg_ratio if ratios else None,
                'min_ratio': min_ratio if ratios else None,
                'max_ratio': max_ratio if ratios else None,
                'avg_bit_growth': avg_bit_growth if bit_growths else None
            }
        }
        
        # Save results
        with open('analysis_hybrid/growth_analysis.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        return results
    
    def analyze_prime_factors(self):
        """Analyze prime factors of sequence values"""
        results = []
        
        for i, value in enumerate(self.sequence):
            # Skip very large numbers to avoid excessive computation
            if value < 1_000_000:
                factors = self._find_prime_factors(value)
                results.append({
                    'position': i+1,
                    'value': value,
                    'hex': hex(value),
                    'prime_factors': factors,
                    'num_factors': len(factors)
                })
        
        # Save results
        with open('analysis_hybrid/prime_factors.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        return results
    
    def _find_prime_factors(self, n: int) -> List[int]:
        """Find prime factors of n"""
        i = 2
        factors = []
        while i * i <= n:
            if n % i:
                i += 1
            else:
                n //= i
                factors.append(i)
        if n > 1:
            factors.append(n)
        return factors
    
    def test_hybrid_bit_patterns(self):
        """Test hybrid bit manipulation patterns from various crypto primitives"""
        patterns = []
        pattern_names = []
        
        # Define patterns as lambda functions
        # Scrypt-inspired patterns
        patterns.append(lambda seq, i: ((seq[i-1] << 1) | (seq[i-1] >> 63)) ^ seq[i-2])
        pattern_names.append("Scrypt-Rotate1-XOR")
        
        patterns.append(lambda seq, i: ((seq[i-1] << 2) | (seq[i-1] >> 62)) ^ ((seq[i-2] << 1) | (seq[i-2] >> 63)))
        pattern_names.append("Scrypt-DoubleRotate-XOR")
        
        # Balloon Hashing inspired patterns
        patterns.append(lambda seq, i: seq[i-1] ^ (seq[i-1] >> 1) ^ seq[i-2])
        pattern_names.append("Balloon-XOR-Shift")
        
        patterns.append(lambda seq, i: seq[i-1] + ((seq[i-2] ^ seq[i-1]) >> 1))
        pattern_names.append("Balloon-Add-XOR-Shift")
        
        # PBKDF2-inspired patterns (nested hash-like operations)
        patterns.append(lambda seq, i: (seq[i-1] * 0x9E3779B97F4A7C15 + seq[i-2]) & 0xFFFFFFFFFFFFFFFF)
        pattern_names.append("PBKDF2-Multiply-Add")
        
        patterns.append(lambda seq, i: (seq[i-1] ^ ((seq[i-2] << 3) | (seq[i-2] >> 61))) * 0x5851F42D4C957F2D & 0xFFFFFFFFFFFFFFFF)
        pattern_names.append("PBKDF2-XOR-Rotate-Multiply")
        
        # Combination patterns
        patterns.append(lambda seq, i: (seq[i-1] + seq[i-2]) ^ ((seq[i-1] >> 1) | (seq[i-1] << 63)))
        pattern_names.append("Hybrid-Add-XOR-Rotate")
        
        patterns.append(lambda seq, i: (((seq[i-1] << 1) | (seq[i-1] >> 63)) + seq[i-2]) & 0xFFFFFFFFFFFFFFFF)
        pattern_names.append("Hybrid-Rotate-Add")
        
        # Bit shuffling patterns
        patterns.append(lambda seq, i: self._bit_shuffle(seq[i-1], seq[i-2]))
        pattern_names.append("BitShuffle-Basic")
        
        patterns.append(lambda seq, i: self._bit_shuffle_custom(seq[i-1], seq[i-2]))
        pattern_names.append("BitShuffle-Custom")
        
        # Patterns using multiple previous terms (more than 2)
        if len(self.sequence) >= 3:
            patterns.append(lambda seq, i: seq[i-1] ^ seq[i-2] ^ seq[i-3] if i >= 3 else 0)
            pattern_names.append("Triple-XOR")
            
            patterns.append(lambda seq, i: (seq[i-1] + seq[i-2] - seq[i-3]) & 0xFFFFFFFFFFFFFFFF if i >= 3 else 0)
            pattern_names.append("Add-Sub-Combination")
        
        # Custom multiplier patterns
        for mult in [0x9E3779B97F4A7C15, 0x5851F42D4C957F2D, 0x2127599BF4325C37]:
            patterns.append(lambda seq, i, m=mult: (seq[i-1] * m) & 0xFFFFFFFFFFFFFFFF)
            pattern_names.append(f"Multiply-{hex(mult)[-8:]}")
        
        # Test patterns against sequence
        results = []
        
        for idx, (pattern, name) in enumerate(zip(patterns, pattern_names)):
            matches = []
            predictions = []
            
            # Start from position 3 for simpler patterns, 4 for complex ones
            start_pos = 4 if "if i >= 3" in str(pattern) else 3
            
            # Test pattern on sequence
            for i in range(start_pos, len(self.sequence)):
                try:
                    prediction = pattern(self.sequence, i)
                    match = prediction == self.sequence[i]
                    matches.append(match)
                    
                    if match:
                        logging.info(f"Match found for pattern '{name}' at position {i+1}")
                    
                    predictions.append({
                        'position': i+1,
                        'actual': hex(self.sequence[i]),
                        'prediction': hex(prediction),
                        'match': match,
                        'bit_diff': bin(prediction ^ self.sequence[i]).count('1') if not match else 0
                    })
                except Exception as e:
                    logging.warning(f"Error applying pattern '{name}' at position {i+1}: {str(e)}")
            
            # Calculate success rate and bit difference statistics
            success_rate = (sum(matches) / len(matches)) * 100 if matches else 0
            
            # Calculate average bit difference for cases that didn't match
            bit_diffs = [p['bit_diff'] for p in predictions if not p['match']]
            avg_bit_diff = sum(bit_diffs) / len(bit_diffs) if bit_diffs else 0
            
            results.append({
                'pattern': name,
                'success_rate': success_rate,
                'matches': sum(matches),
                'total': len(matches),
                'match_positions': [p['position'] for p in predictions if p['match']],
                'avg_bit_diff': avg_bit_diff,
                'predictions': predictions
            })
            
            logging.info(f"Pattern '{name}': {success_rate:.2f}% matches ({sum(matches)}/{len(matches)}), "
                        f"Avg bit diff: {avg_bit_diff:.2f}")
        
        # Find best pattern
        best_pattern = max(results, key=lambda x: x['success_rate'])
        logging.info(f"Best pattern: '{best_pattern['pattern']}' with {best_pattern['success_rate']:.2f}% matches")
        
        # Find pattern with lowest bit difference (might be close to matching)
        best_bit_diff = min(results, key=lambda x: x['avg_bit_diff'] if x['success_rate'] < 100 else float('inf'))
        if best_pattern['pattern'] != best_bit_diff['pattern']:
            logging.info(f"Best bit diff pattern: '{best_bit_diff['pattern']}' with {best_bit_diff['avg_bit_diff']:.2f} avg bits")
            
        # Save results
        with open('analysis_hybrid/hybrid_patterns.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        return results, best_pattern, best_bit_diff
    
    def _bit_shuffle(self, a: int, b: int) -> int:
        """Simple bit shuffle operation combining two values"""
        a_bits = bin(a)[2:].zfill(64)
        b_bits = bin(b)[2:].zfill(64)
        
        result_bits = ""
        for i in range(0, 64, 2):
            if i < len(a_bits) and i < len(b_bits):
                result_bits += a_bits[i] + b_bits[i]
                if i+1 < len(a_bits) and i+1 < len(b_bits):
                    result_bits += a_bits[i+1] + b_bits[i+1]
        
        # Ensure we have a 64-bit result
        result_bits = result_bits[:64].ljust(64, '0')
        
        return int(result_bits, 2)
    
    def _bit_shuffle_custom(self, a: int, b: int) -> int:
        """More complex bit shuffle with bit shifts and XOR"""
        a_bytes = a.to_bytes(8, byteorder='big')
        b_bytes = b.to_bytes(8, byteorder='big')
        
        result = bytearray(8)
        
        for i in range(8):
            # Mix bytes from both inputs with byte position influencing the mix
            result[i] = (a_bytes[i] & (0xF0 >> (i % 2))) | (b_bytes[i] & (0x0F << (i % 2)))
            
            # Add additional bit transforms
            if i % 2 == 0:
                result[i] = (result[i] << 1) | (result[i] >> 7)
            else:
                result[i] = (result[i] >> 1) | ((result[i] & 0x01) << 7)
                
        return int.from_bytes(result, byteorder='big')
    
    def test_polynomial_recurrence(self):
        """Test if the sequence matches a polynomial recurrence relation"""
        if len(self.sequence) < 5:
            logging.warning("Sequence too short for polynomial recurrence analysis")
            return []
        
        # Test different polynomial degrees
        max_degree = 5  # Test up to 5th degree polynomials
        results = []
        
        for degree in range(1, max_degree + 1):
            recurrences = []
            
            # Test with different number of terms
            for terms in range(degree + 1, degree + 4):
                if terms >= len(self.sequence):
                    continue
                    
                matches = []
                predictions = []
                
                # Test polynomial recurrence on sequence
                for i in range(terms, len(self.sequence)):
                    try:
                        # Get the previous 'terms' values
                        prev_values = [self.sequence[i-j-1] for j in range(terms)]
                        
                        # Calculate polynomial prediction
                        prediction = self._polynomial_predict(prev_values, degree)
                        match = prediction == self.sequence[i]
                        matches.append(match)
                        
                        if match:
                            logging.info(f"Match found for polynomial (degree={degree}, terms={terms}) at position {i+1}")
                        
                        predictions.append({
                            'position': i+1,
                            'actual': hex(self.sequence[i]),
                            'prediction': hex(prediction),
                            'match': match,
                            'bit_diff': bin(prediction ^ self.sequence[i]).count('1') if not match else 0
                        })
                    except Exception as e:
                        logging.warning(f"Error in polynomial (degree={degree}, terms={terms}) at position {i+1}: {str(e)}")
                
                # Calculate success rate
                success_rate = (sum(matches) / len(matches)) * 100 if matches else 0
                
                # Calculate average bit difference for cases that didn't match
                bit_diffs = [p['bit_diff'] for p in predictions if not p['match']]
                avg_bit_diff = sum(bit_diffs) / len(bit_diffs) if bit_diffs else 0
                
                recurrences.append({
                    'degree': degree,
                    'terms': terms,
                    'success_rate': success_rate,
                    'matches': sum(matches),
                    'total': len(matches),
                    'avg_bit_diff': avg_bit_diff,
                    'match_positions': [p['position'] for p in predictions if p['match']],
                    'predictions': predictions
                })
                
                logging.info(f"Polynomial (degree={degree}, terms={terms}): {success_rate:.2f}% matches, "
                            f"Avg bit diff: {avg_bit_diff:.2f}")
            
            results.extend(recurrences)
        
        # Find best polynomial recurrence
        if results:
            best_recurrence = max(results, key=lambda x: x['success_rate'])
            logging.info(f"Best polynomial: degree={best_recurrence['degree']}, terms={best_recurrence['terms']} "
                        f"with {best_recurrence['success_rate']:.2f}% matches")
            
            # Save results
            with open('analysis_hybrid/polynomial_recurrence.json', 'w') as f:
                json.dump(results, f, indent=2)
                
            return best_recurrence
        
        return None
    
    def _polynomial_predict(self, values: List[int], degree: int) -> int:
        """Predict next value using polynomial recurrence of specified degree"""
        # For a degree 1 polynomial (linear recurrence), use simple linear combination
        if degree == 1:
            # Linear combination of previous values with exponential weights
            result = 0
            for i, val in enumerate(values):
                weight = 2 ** (len(values) - i - 1)
                result = (result + (val * weight)) & 0xFFFFFFFFFFFFFFFF
            return result
            
        # For degree 2, use a quadratic recurrence
        elif degree == 2:
            if len(values) >= 2:
                # Quadratic recurrence: a(n) = 2*a(n-1) - a(n-2) + adjustment
                # Apply bitwise operations for additional complexity
                a, b = values[0], values[1]
                result = (2*b - a + ((a ^ b) & 0xFF)) & 0xFFFFFFFFFFFFFFFF
                return result
        
        # For higher degrees, use a combination of operations
        elif degree >= 3:
            # Initialize with weighted sum
            result = 0
            for i, val in enumerate(values):
                weight = (degree + 1) ** (len(values) - i - 1)
                result = (result + (val * weight)) & 0xFFFFFFFFFFFFFFFF
            
            # Apply additional transformations based on degree
            for i in range(degree - 2):
                if i < len(values) - 1:
                    # Mix in bitwise operations
                    result = (result ^ ((values[i] << (i+1)) | (values[i] >> (63-(i+1))))) & 0xFFFFFFFFFFFFFFFF
            
            return result
        
        # Default fallback
        return values[0]
    
    def simulate_custom_hash_chain(self):
        """Simulate a custom hash chain to see if sequence matches hash chain behavior"""
        # Different hash chain configurations to test
        configs = [
            {'hash_type': 'sha256', 'iterations': 1, 'use_bits': 64, 'add_index': True},
            {'hash_type': 'sha512', 'iterations': 1, 'use_bits': 64, 'add_index': False},
            {'hash_type': 'md5', 'iterations': 2, 'use_bits': 64, 'add_index': True},
            {'hash_type': 'sha1', 'iterations': 1, 'use_bits': 64, 'add_index': False},
            {'hash_type': 'sha256', 'iterations': 2, 'use_bits': 64, 'add_index': True}
        ]
        
        hash_results = []
        
        for config in configs:
            matches = []
            predictions = []
            
            # Start from position 2 (need at least one previous value)
            for i in range(1, len(self.sequence)):
                try:
                    # Get input for hash function
                    prev_value = self.sequence[i-1]
                    
                    # Convert to bytes
                    input_bytes = prev_value.to_bytes(8, byteorder='big')
                    
                    # Add position index if specified
                    if config['add_index']:
                        input_bytes += (i+1).to_bytes(4, byteorder='big')
                    
                    # Apply hash function with iterations
                    hash_output = input_bytes
                    for _ in range(config['iterations']):
                        if config['hash_type'] == 'sha256':
                            hash_output = hashlib.sha256(hash_output).digest()
                        elif config['hash_type'] == 'sha512':
                            hash_output = hashlib.sha512(hash_output).digest()
                        elif config['hash_type'] == 'md5':
                            hash_output = hashlib.md5(hash_output).digest()
                        elif config['hash_type'] == 'sha1':
                            hash_output = hashlib.sha1(hash_output).digest()
                    
                    # Take first 8 bytes and convert to integer
                    hash_int = int.from_bytes(hash_output[:8], byteorder='big')
                    
                    # Use specific number of bits if specified
                    if config['use_bits'] < 64:
                        hash_int &= (1 << config['use_bits']) - 1
                    
                    # Check if it matches
                    match = hash_int == self.sequence[i]
                    matches.append(match)
                    
                    if match:
                        logging.info(f"Match found for hash config {config} at position {i+1}")
                    
                    predictions.append({
                        'position': i+1,
                        'actual': hex(self.sequence[i]),
                        'prediction': hex(hash_int),
                        'match': match,
                        'bit_diff': bin(hash_int ^ self.sequence[i]).count('1') if not match else 0
                    })
                except Exception as e:
                    logging.warning(f"Error applying hash config {config} at position {i+1}: {str(e)}")
            
            # Calculate success rate
            success_rate = (sum(matches) / len(matches)) * 100 if matches else 0
            
            # Calculate average bit difference for cases that didn't match
            bit_diffs = [p['bit_diff'] for p in predictions if not p['match']]
            avg_bit_diff = sum(bit_diffs) / len(bit_diffs) if bit_diffs else 0
            
            hash_results.append({
                'config': config,
                'success_rate': success_rate,
                'matches': sum(matches),
                'total': len(matches),
                'avg_bit_diff': avg_bit_diff,
                'match_positions': [p['position'] for p in predictions if p['match']],
                'predictions': predictions
            })
            
            logging.info(f"Hash config {config}: {success_rate:.2f}% matches, "
                        f"Avg bit diff: {avg_bit_diff:.2f}")
        
        # Find best hash config
        best_hash = max(hash_results, key=lambda x: x['success_rate'])
        logging.info(f"Best hash config: {best_hash['config']} with {best_hash['success_rate']:.2f}% matches")
        
        # Save results
        with open('analysis_hybrid/hash_chain.json', 'w') as f:
            json.dump(hash_results, f, indent=2)
            
        return hash_results, best_hash
    
    def predict_next_positions(self, count=3):
        """Predict next positions using best methods found"""
        # Run analysis methods
        self.analyze_growth_rate()
        self.analyze_prime_factors()
        bit_pattern_results, best_pattern, best_bit_diff = self.test_hybrid_bit_patterns()
        poly_recurrence = self.test_polynomial_recurrence()
        hash_results, best_hash = self.simulate_custom_hash_chain()
        
        # Compare methods
        methods = []
        
        # Bit patterns
        if best_pattern:
            methods.append({
                'name': f"Bit Pattern: {best_pattern['pattern']}",
                'success_rate': best_pattern['success_rate'],
                'avg_bit_diff': best_pattern['avg_bit_diff'],
                'type': 'bit_pattern',
                'data': best_pattern
            })
        
        # Low bit difference pattern (might be close)
        if best_bit_diff and best_bit_diff['pattern'] != best_pattern['pattern']:
            methods.append({
                'name': f"Close Pattern: {best_bit_diff['pattern']}",
                'success_rate': best_bit_diff['success_rate'],
                'avg_bit_diff': best_bit_diff['avg_bit_diff'],
                'type': 'bit_diff',
                'data': best_bit_diff
            })
        
        # Polynomial recurrence
        if poly_recurrence:
            methods.append({
                'name': f"Polynomial (degree={poly_recurrence['degree']}, terms={poly_recurrence['terms']})",
                'success_rate': poly_recurrence['success_rate'],
                'avg_bit_diff': poly_recurrence['avg_bit_diff'],
                'type': 'polynomial',
                'data': poly_recurrence
            })
        
        # Hash chain
        if best_hash:
            methods.append({
                'name': f"Hash Chain: {best_hash['config']}",
                'success_rate': best_hash['success_rate'],
                'avg_bit_diff': best_hash['avg_bit_diff'],
                'type': 'hash',
                'data': best_hash
            })
        
        # Find best methods
        best_methods = sorted(methods, key=lambda x: x['success_rate'], reverse=True)
        
        # Generate predictions
        predictions = []
        current_seq = self.sequence.copy()
        
        for pos in range(len(self.sequence) + 1, len(self.sequence) + count + 1):
            method_predictions = []
            
            # Make prediction with each method
            for method in best_methods:
                try:
                    if method['type'] == 'bit_pattern' or method['type'] == 'bit_diff':
                        # Get the pattern
                        pattern_name = method['data']['pattern']
                        prediction = self._apply_bit_pattern(pattern_name, current_seq)
                        
                    elif method['type'] == 'polynomial':
                        # Get polynomial parameters
                        degree = method['data']['degree']
                        terms = method['data']['terms']
                        
                        # Get the previous 'terms' values
                        prev_values = current_seq[-terms:]
                        
                        # Apply polynomial prediction
                        prediction = self._polynomial_predict(prev_values, degree)
                        
                    elif method['type'] == 'hash':
                        # Get hash config
                        config = method['data']['config']
                        
                        # Apply hash function
                        prev_value = current_seq[-1]
                        
                        # Convert to bytes
                        input_bytes = prev_value.to_bytes(8, byteorder='big')
                        
                        # Add position index if specified
                        if config['add_index']:
                            input_bytes += pos.to_bytes(4, byteorder='big')
                        
                        # Apply hash function with iterations
                        hash_output = input_bytes
                        for _ in range(config['iterations']):
                            if config['hash_type'] == 'sha256':
                                hash_output = hashlib.sha256(hash_output).digest()
                            elif config['hash_type'] == 'sha512':
                                hash_output = hashlib.sha512(hash_output).digest()
                            elif config['hash_type'] == 'md5':
                                hash_output = hashlib.md5(hash_output).digest()
                            elif config['hash_type'] == 'sha1':
                                hash_output = hashlib.sha1(hash_output).digest()
                        
                        # Take first 8 bytes and convert to integer
                        prediction = int.from_bytes(hash_output[:8], byteorder='big')
                        
                        # Use specific number of bits if specified
                        if config['use_bits'] < 64:
                            prediction &= (1 << config['use_bits']) - 1
                    
                    else:
                        # Unknown method type, skip
                        continue
                    
                    # Record prediction
                    method_predictions.append({
                        'method': method['name'],
                        'value': prediction,
                        'hex': hex(prediction),
                        'success_rate': method['success_rate'],
                        'avg_bit_diff': method['avg_bit_diff']
                    })
                    
                except Exception as e:
                    logging.warning(f"Error generating prediction with method {method['name']} for position {pos}: {str(e)}")
            
            # Decide on prediction (use best performing method)
            if method_predictions:
                best_method_pred = max(method_predictions, key=lambda x: x['success_rate'])
                
                prediction_data = {
                    'position': pos,
                    'methods': method_predictions,
                    'selected_method': best_method_pred['method'],
                    'predicted_value': best_method_pred['hex'],
                    'success_rate': best_method_pred['success_rate']
                }
                
                # Check against known future values
                if pos in self.future_values:
                    actual = self.future_values[pos]
                    prediction_data['actual_value'] = hex(actual)
                    prediction_data['correct'] = int(best_method_pred['hex'], 16) == actual
                    
                    # Calculate bit difference if not correct
                    if not prediction_data['correct']:
                        predicted_int = int(best_method_pred['hex'], 16)
                        bit_diff = bin(predicted_int ^ actual).count('1')
                        prediction_data['bit_difference'] = bit_diff
                
                predictions.append(prediction_data)
                
                # Use this prediction for next iterations
                current_seq.append(int(best_method_pred['hex'], 16))
            else:
                logging.warning(f"No valid prediction methods for position {pos}")
        
        # Save predictions
        with open('analysis_hybrid/predictions.json', 'w') as f:
            json.dump(predictions, f, indent=2)
            
        # Print predictions
        print("\nPredictions for next positions:")
        for pred in predictions:
            pos = pred['position']
            print(f"Position {pos}: {pred['predicted_value']} (using {pred['selected_method']})")
            
            if 'actual_value' in pred:
                correct = "CORRECT" if pred.get('correct', False) else "INCORRECT"
                print(f"  Actual: {pred['actual_value']} - {correct}")
                if 'bit_difference' in pred:
                    print(f"  Bit difference: {pred['bit_difference']} bits")
            
            # Show alternate predictions
            print("  Other method predictions:")
            for method in pred['methods']:
                if method['method'] != pred['selected_method']:
                    print(f"    {method['method']}: {method['hex']}")
                    
            print("")
        
        return predictions
    
    def _apply_bit_pattern(self, pattern_name: str, sequence: List[int]) -> int:
        """Apply a named bit pattern to generate the next value"""
        if len(sequence) < 2:
            raise ValueError("Need at least 2 elements in sequence for bit patterns")
            
        a = sequence[-1]  # Most recent value
        b = sequence[-2]  # Second most recent value
        c = sequence[-3] if len(sequence) >= 3 else 0  # Third most recent value
        
        if pattern_name == "Scrypt-Rotate1-XOR":
            return ((a << 1) | (a >> 63)) ^ b
            
        elif pattern_name == "Scrypt-DoubleRotate-XOR":
            return ((a << 2) | (a >> 62)) ^ ((b << 1) | (b >> 63))
            
        elif pattern_name == "Balloon-XOR-Shift":
            return a ^ (a >> 1) ^ b
            
        elif pattern_name == "Balloon-Add-XOR-Shift":
            return a + ((b ^ a) >> 1)
            
        elif pattern_name == "PBKDF2-Multiply-Add":
            return (a * 0x9E3779B97F4A7C15 + b) & 0xFFFFFFFFFFFFFFFF
            
        elif pattern_name == "PBKDF2-XOR-Rotate-Multiply":
            return (a ^ ((b << 3) | (b >> 61))) * 0x5851F42D4C957F2D & 0xFFFFFFFFFFFFFFFF
            
        elif pattern_name == "Hybrid-Add-XOR-Rotate":
            return (a + b) ^ ((a >> 1) | (a << 63))
            
        elif pattern_name == "Hybrid-Rotate-Add":
            return (((a << 1) | (a >> 63)) + b) & 0xFFFFFFFFFFFFFFFF
            
        elif pattern_name == "BitShuffle-Basic":
            return self._bit_shuffle(a, b)
            
        elif pattern_name == "BitShuffle-Custom":
            return self._bit_shuffle_custom(a, b)
            
        elif pattern_name == "Triple-XOR":
            return a ^ b ^ c
            
        elif pattern_name == "Add-Sub-Combination":
            return (a + b - c) & 0xFFFFFFFFFFFFFFFF
            
        elif "Multiply-" in pattern_name:
            # Extract multiplier from pattern name
            mult_hex = "0x" + pattern_name.split('-')[1]
            mult = int(mult_hex, 16)
            return (a * mult) & 0xFFFFFFFFFFFFFFFF
            
        # Default fallback
        return a

def main():
    analyzer = HybridCryptoAnalyzer()
    
    print("Starting Hybrid Cryptographic Sequence Analysis")
    print("=" * 80)
    
    # Run full analysis
    analyzer.predict_next_positions(5)
    
    print("\nAnalysis complete. All results saved in analysis_hybrid/ directory")

if __name__ == "__main__":
    main() 