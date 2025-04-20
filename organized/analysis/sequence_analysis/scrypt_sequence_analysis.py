"""
Sequence Analysis using scrypt's ROMix Algorithm
Based on concepts from Colin Percival's paper
"""

import math
import logging
import json
import os
import struct
import hashlib
from typing import List, Dict, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ScryptSequenceAnalyzer:
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
        os.makedirs('analysis_scrypt', exist_ok=True)
    
    def analyze_key_patterns(self):
        """Analyze the core patterns in the sequence"""
        results = {
            'first_order_diff': [],
            'second_order_diff': [],
            'bit_rotations': [],
            'potential_salsa_params': []
        }
        
        # First order differences (a[n] - a[n-1])
        for i in range(1, len(self.sequence)):
            diff = self.sequence[i] - self.sequence[i-1]
            results['first_order_diff'].append({
                'position': i+1,
                'value': diff,
                'hex': hex(diff)
            })
        
        # Second order differences
        for i in range(2, len(self.sequence)):
            diff = (self.sequence[i] - self.sequence[i-1]) - (self.sequence[i-1] - self.sequence[i-2])
            results['second_order_diff'].append({
                'position': i+1,
                'value': diff,
                'hex': hex(diff)
            })
        
        # Analyze potential bit rotations (common in ROMix and Salsa20/8)
        for i in range(1, len(self.sequence)):
            prev = self.sequence[i-1]
            curr = self.sequence[i]
            
            # Try different rotation amounts
            for rot in range(1, 32):
                # Left rotation
                left_rot = ((prev << rot) | (prev >> (64 - rot))) & 0xFFFFFFFFFFFFFFFF
                # Right rotation
                right_rot = ((prev >> rot) | (prev << (64 - rot))) & 0xFFFFFFFFFFFFFFFF
                
                # Check if either rotation matches or is close
                left_diff = bin(left_rot ^ curr).count('1')
                right_diff = bin(right_rot ^ curr).count('1')
                
                if left_diff < 20 or right_diff < 20:
                    results['bit_rotations'].append({
                        'position': i+1,
                        'rotation': rot,
                        'direction': 'left' if left_diff < right_diff else 'right',
                        'diff_bits': min(left_diff, right_diff),
                        'prev': hex(prev),
                        'curr': hex(curr)
                    })
        
        # Check for potential Salsa20/8 parameters
        for i in range(1, len(self.sequence)):
            prev = self.sequence[i-1]
            curr = self.sequence[i]
            
            # Try common multipliers used in crypto
            multipliers = [0x5851f42d4c957f2d, 0x2127599bf4325c37, 0x9E3779B97F4A7C15]
            for mult in multipliers:
                # Test Salsa20-like transformation
                v = prev
                v = ((v << 3) | (v >> 61)) & 0xFFFFFFFFFFFFFFFF
                v = v ^ ((v * mult) & 0xFFFFFFFFFFFFFFFF)
                
                diff = bin(v ^ curr).count('1')
                if diff < 30:  # If reasonably close
                    results['potential_salsa_params'].append({
                        'position': i+1,
                        'multiplier': hex(mult),
                        'diff_bits': diff,
                        'calculated': hex(v),
                        'actual': hex(curr)
                    })
        
        # Save results
        with open('analysis_scrypt/key_patterns.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def test_salsa_patterns(self):
        """Test patterns inspired by Salsa20/8 core (used in scrypt)"""
        salsa_results = []
        
        # Different configuration parameters to test
        # Generate comprehensive configs exploring different rotations, offsets and multipliers
        configs = []
        
        # Common multipliers used in crypto
        multipliers = [
            0x5851f42d4c957f2d,  # LCG multiplier
            0x2127599bf4325c37,  # Salsa20 constant
            0x9E3779B97F4A7C15   # TEA constant
        ]
        
        # Test rotations 1-64
        for rotation in range(1, 65):
            # Test offsets 1-8 
            for xor_offset in range(1, 9):
                # Test each multiplier
                for mult in multipliers:
                    configs.append({
                        'rotation': rotation,
                        'xor_offset': xor_offset,
                        'mult': mult
                    })
                    
        # Add some special offset patterns
        special_offsets = [
            lambda i: i,              # Linear
            lambda i: i * i,          # Square
            lambda i: 2**i,           # Powers of 2
            lambda i: i + (i//4),     # Position + quarter
            lambda i: i ^ (i//2)      # XOR with half
        ]
        
        for rotation in range(1, 65):
            for offset_fn in special_offsets:
                for mult in multipliers:
                    configs.append({
                        'rotation': rotation,
                        'xor_offset': offset_fn,
                        'mult': mult,
                        'dynamic_offset': True
                    })
        
        for config in configs:
            matches = []
            predictions = []
            
            # Test each config
            for i in range(2, len(self.sequence)):
                # Get inputs for the pattern
                a = self.sequence[i-1]
                b = self.sequence[i-2]
                
                # Apply transformations inspired by Salsa20/8
                # Rotate and XOR (common in Salsa20/8)
                rotated = ((a << config['rotation']) | (a >> (64 - config['rotation']))) & 0xFFFFFFFFFFFFFFFF
                xored = rotated ^ b
                
                # Apply multiplier (common in hash functions)
                result = (xored * config['mult']) & 0xFFFFFFFFFFFFFFFF
                
                # Check if it matches
                match = result == self.sequence[i]
                matches.append(match)
                predictions.append({
                    'position': i+1,
                    'actual': hex(self.sequence[i]),
                    'prediction': hex(result),
                    'match': match
                })
            
            # Calculate success rate
            success_rate = (sum(matches) / len(matches)) * 100 if matches else 0
            
            salsa_results.append({
                'config': config,
                'success_rate': success_rate,
                'matches': sum(matches),
                'total': len(matches),
                'predictions': predictions
            })
            
            logging.info(f"Salsa config {config}: {success_rate:.2f}% matches")
        
        # Find best config
        best_config = max(salsa_results, key=lambda x: x['success_rate'])
        logging.info(f"Best Salsa config: {best_config['config']} with {best_config['success_rate']:.2f}% matches")
        
        # Save results
        with open('analysis_scrypt/salsa_patterns.json', 'w') as f:
            json.dump(salsa_results, f, indent=2)
            
        return best_config
    
    def simulate_romix(self):
        """
        Simulate the ROMix algorithm from scrypt with various parameters.
        
        ROMix is a memory-hard function that:
        1. Fills a large vector V with pseudorandom values derived from the input
        2. Accesses these values in random order to force memory usage
        3. Mixes the accessed values to produce the final output
        
        Returns:
            dict: Results containing best parameters and match statistics
        """
        romix_results = []
        
        # Test different memory cost (N) and CPU cost (r) parameters
        for n in [4, 8, 16, 32]:  # Memory cost - vector size
            for r in [1, 2, 4, 8]:  # CPU cost - number of iterations
                matches = []
                predictions = []
                
                # Start from position n+1 to have enough history
                for i in range(n+1, len(self.sequence)):
                    # Get previous n values as input block
                    prev_values = self.sequence[i-n:i]
                    
                    # Initialize ROMix state
                    x = prev_values[-1]  # Start with most recent value
                    v = []  # Vector to store intermediate values
                    
                    # First phase: Sequential write
                    # Fill vector V with transformed values
                    for j in range(n):
                        v.append(x)
                        # Apply Salsa20/8-inspired mixing function
                        x = ((x << r) | (x >> (64 - r))) & 0xFFFFFFFFFFFFFFFF  # Rotate
                        x = x ^ ((x * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF)  # Mix with golden ratio
                        # Add additional mixing steps
                        x = x ^ (x >> 32)  # High-low word mixing
                        x = ((x + prev_values[j % len(prev_values)]) & 0xFFFFFFFFFFFFFFFF)  # Mix with history
                    
                    # Second phase: Random read and mix
                    # Access vector elements in pseudo-random order
                    for j in range(n):
                        # Use value of x to index into v (memory-hard step)
                        idx = x % n
                        # Mix with stored value
                        x = x ^ v[idx]
                        # Additional transformations
                        x = ((x << (r+1)) | (x >> (64 - (r+1)))) & 0xFFFFFFFFFFFFFFFF
                        x = x ^ ((x * 0x5851f42d4c957f2d) & 0xFFFFFFFFFFFFFFFF)  # Different constant
                        # Add bit mixing
                        x = ((x >> 16) | (x << 48)) ^ ((x << 16) | (x >> 48))  # Byte shuffling
                        x = x ^ (sum(prev_values) & 0xFFFFFFFFFFFFFFFF)  # Mix with input history
                    
                    # Final diffusion step
                    x = ((x * 0x9E3779B97F4A7C15) + (x >> 32)) & 0xFFFFFFFFFFFFFFFF
                    prediction = x
                    
                    # Validate prediction against actual value
                    match = prediction == self.sequence[i]
                    matches.append(match)
                    predictions.append({
                        'position': i+1,
                        'actual': hex(self.sequence[i]),
                        'prediction': hex(prediction),
                        'match': match,
                        'params': {'n': n, 'r': r}
                    })
                
                # Calculate success metrics
                success_rate = (sum(matches) / len(matches)) * 100 if matches else 0
                avg_hamming_distance = self._calculate_avg_hamming_distance(predictions)
                
                romix_results.append({
                    'params': {'n': n, 'r': r},
                    'success_rate': success_rate,
                    'matches': sum(matches),
                    'total': len(matches),
                    'avg_hamming_distance': avg_hamming_distance,
                    'predictions': predictions
                })
                
                logging.info(f"ROMix params n={n}, r={r}: {success_rate:.2f}% matches")
        
        # Find best parameters
        best_params = max(romix_results, key=lambda x: x['success_rate'])
        logging.info(f"Best ROMix params: n={best_params['params']['n']}, r={best_params['params']['r']} "
                    f"with {best_params['success_rate']:.2f}% matches")
        
        # Save results
        with open('analysis_scrypt/romix_results.json', 'w') as f:
            json.dump(romix_results, f, indent=2)
            
        return best_params
    
    def test_complex_bit_patterns(self):
        """Test comprehensive bit manipulation patterns for sequence analysis"""
        patterns = [
            # Basic bit shifts and rotations
            lambda seq, i: ((seq[i-1] << 1) | (seq[i-1] >> 63)) ^ seq[i-2],
            lambda seq, i: ((seq[i-1] << 2) | (seq[i-1] >> 62)) ^ seq[i-2],
            lambda seq, i: ((seq[i-1] << 4) | (seq[i-1] >> 60)) ^ seq[i-2],
            lambda seq, i: ((seq[i-1] << 8) | (seq[i-1] >> 56)) ^ seq[i-2],
            
            # Bit mixing with different word sizes
            lambda seq, i: ((seq[i-1] & 0xFFFF) << 16) | ((seq[i-1] & 0xFFFF0000) >> 16),
            lambda seq, i: ((seq[i-1] & 0xFF) << 24) | ((seq[i-1] & 0xFF000000) >> 24),
            lambda seq, i: ((seq[i-1] & 0xF) << 28) | ((seq[i-1] & 0xF0000000) >> 28),
            
            # Variable bit replacements
            lambda seq, i: (seq[i-1] & 0xFFFFFFFF00000000) | ((seq[i-2] & 0xFFFFFFFF) << 32),
            lambda seq, i: (seq[i-1] & 0xFFFF0000FFFF0000) | ((seq[i-2] & 0x0000FFFF0000FFFF) << 16),
            lambda seq, i: (seq[i-1] & 0xFF00FF00FF00FF00) | ((seq[i-2] & 0x00FF00FF00FF00FF) << 8),
            
            # Complex bit manipulations
            lambda seq, i: (seq[i-1] ^ ((seq[i-1] << 7) & 0xFFFFFFFFFFFFFFFF)) + (seq[i-2] & 0x7FFFFFFFFFFFFFFF),
            lambda seq, i: ((seq[i-1] << 3) ^ (seq[i-1] >> 5)) + ((seq[i-2] << 7) ^ (seq[i-2] >> 1)),
            lambda seq, i: (seq[i-1] + ((seq[i-2] << 11) & 0xFFFFFFFFFFFFFFFF)) ^ (seq[i-1] >> 3),
            
            # Bit interleaving patterns
            lambda seq, i: ((seq[i-1] & 0x5555555555555555) << 1) | ((seq[i-1] & 0xAAAAAAAAAAAAAAAA) >> 1),
            lambda seq, i: ((seq[i-1] & 0x3333333333333333) << 2) | ((seq[i-1] & 0xCCCCCCCCCCCCCCCC) >> 2),
            lambda seq, i: ((seq[i-1] & 0x0F0F0F0F0F0F0F0F) << 4) | ((seq[i-1] & 0xF0F0F0F0F0F0F0F0) >> 4),
            
            # Bit reversal and scrambling
            lambda seq, i: int(format(seq[i-1], '064b')[::-1], 2),
            lambda seq, i: int(''.join(format(seq[i-1], '064b')[i::2] + format(seq[i-1], '064b')[i+1::2]), 2),
            lambda seq, i: int(''.join(format(seq[i-1], '064b')[::3] + format(seq[i-1], '064b')[1::3] + format(seq[i-1], '064b')[2::3]), 2),
            
            # Advanced bit mixing
            lambda seq, i: ((seq[i-1] << 13) + (seq[i-2] >> 7)) ^ ((seq[i-1] >> 17) + (seq[i-2] << 5)),
            lambda seq, i: ((seq[i-1] ^ seq[i-2]) << 19) | ((seq[i-1] & seq[i-2]) >> 13),
            lambda seq, i: (seq[i-1] + seq[i-2]) ^ ((seq[i-1] ^ seq[i-2]) << 11)
        ]
        pattern_names = [
            "Rotate left 1 and XOR with previous",
            "Double rotation with XOR",
            "Triple term XOR",
            "Addition and XOR mix",
            "BlockMix-inspired",
            "Rotate-XOR-Multiply",
            "Fibonacci-XOR hybrid",
            "SMix-inspired"
        ]
        
        results = []
        
        for idx, (pattern, name) in enumerate(zip(patterns, pattern_names)):
            matches = []
            predictions = []
            
            # Determine starting position based on pattern
            start_pos = 3 if "if i >= 3" in str(pattern) else 2
            
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
                        'match': match
                    })
                except Exception as e:
                    logging.warning(f"Error applying pattern '{name}' at position {i+1}: {str(e)}")
            
            # Calculate success rate
            success_rate = (sum(matches) / len(matches)) * 100 if matches else 0
            
            results.append({
                'pattern': name,
                'success_rate': success_rate,
                'matches': sum(matches),
                'total': len(matches),
                'match_positions': [p['position'] for p in predictions if p['match']],
                'predictions': predictions
            })
            
            logging.info(f"Pattern '{name}': {success_rate:.2f}% matches ({sum(matches)}/{len(matches)})")
        
        # Find best pattern
        best_pattern = max(results, key=lambda x: x['success_rate'])
        logging.info(f"Best pattern: '{best_pattern['pattern']}' with {best_pattern['success_rate']:.2f}% matches")
        
        # Save results
        with open('analysis_scrypt/complex_patterns.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        return best_pattern
    
    def predict_next_positions(self, count=3):
        """Predict next positions using best method found"""
        # Run all analysis methods
        self.analyze_key_patterns()
        salsa_results = self.test_salsa_patterns()
        romix_results = self.simulate_romix()
        bit_pattern_results = self.test_complex_bit_patterns()
        
        # Compare methods
        methods = [
            ("Salsa", salsa_results['success_rate'], 'salsa'),
            ("ROMix", romix_results['success_rate'], 'romix'),
            ("Bit Pattern", bit_pattern_results['success_rate'], 'bit')
        ]
        
        # Find best method
        best_method = max(methods, key=lambda x: x[1])
        logging.info(f"Using {best_method[0]} method with {best_method[1]:.2f}% accuracy")
        
        # Generate predictions
        predictions = []
        current_seq = self.sequence.copy()
        
        for pos in range(len(self.sequence) + 1, len(self.sequence) + count + 1):
            # Make prediction based on best method
            if best_method[2] == 'salsa':
                config = salsa_results['config']
                
                # Get inputs
                a = current_seq[-1]
                b = current_seq[-2]
                
                # Apply transformations
                rotated = ((a << config['rotation']) | (a >> (64 - config['rotation']))) & 0xFFFFFFFFFFFFFFFF
                xored = rotated ^ b
                prediction = (xored * config['mult']) & 0xFFFFFFFFFFFFFFFF
                
            elif best_method[2] == 'romix':
                params = romix_results['params']
                n = params['n']
                r = params['r']
                
                # Get previous n values
                prev_values = current_seq[-n:]
                
                # Simulate ROMix
                x = prev_values[-1]
                v = []
                
                for j in range(n):
                    v.append(x)
                    x = ((x << r) | (x >> (64 - r))) & 0xFFFFFFFFFFFFFFFF
                    x = x ^ ((x * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF)
                
                for j in range(n):
                    idx = x % n
                    x = x ^ v[idx]
                    x = ((x << (r+1)) | (x >> (64 - (r+1)))) & 0xFFFFFFFFFFFFFFFF
                    x = x ^ ((x * 0x5851f42d4c957f2d) & 0xFFFFFFFFFFFFFFFF)
                
                prediction = x
                
            else:  # bit pattern
                # Determine which pattern had the best success rate
                pattern_name = bit_pattern_results['pattern']
                
                # Map name to function
                if pattern_name == "Rotate left 1 and XOR with previous":
                    prediction = ((current_seq[-1] << 1) | (current_seq[-1] >> 63)) ^ current_seq[-2]
                elif pattern_name == "Double rotation with XOR":
                    prediction = ((current_seq[-1] << 2) | (current_seq[-1] >> 62)) ^ ((current_seq[-2] << 1) | (current_seq[-2] >> 63))
                elif pattern_name == "Triple term XOR":
                    prediction = current_seq[-1] ^ current_seq[-2] ^ current_seq[-3]
                elif pattern_name == "Addition and XOR mix":
                    prediction = (current_seq[-1] + current_seq[-2]) ^ current_seq[-3]
                elif pattern_name == "BlockMix-inspired":
                    prediction = ((current_seq[-1] ^ current_seq[-2]) << 2) | ((current_seq[-1] ^ current_seq[-2]) >> 62)
                elif pattern_name == "Rotate-XOR-Multiply":
                    prediction = ((current_seq[-1] << 3) ^ current_seq[-2]) * 0x9E3779B97F4A7C15 & 0xFFFFFFFFFFFFFFFF
                elif pattern_name == "Fibonacci-XOR hybrid":
                    prediction = current_seq[-1] + (current_seq[-2] ^ current_seq[-3])
                else:  # SMix-inspired
                    prediction = current_seq[-1] ^ ((current_seq[-2] * 0x5851f42d4c957f2d) & 0xFFFFFFFFFFFFFFFF)
            
            # Store prediction
            predictions.append({
                'position': pos,
                'predicted_value': hex(prediction),
                'method': best_method[0],
                'success_rate': best_method[1]
            })
            
            # Add to sequence for next prediction
            current_seq.append(prediction)
        
        # Check against known future values
        for pred in predictions:
            pos = pred['position']
            if pos in self.future_values:
                actual = self.future_values[pos]
                pred['actual_value'] = hex(actual)
                pred['correct'] = int(pred['predicted_value'], 16) == actual
                
                # Calculate bit difference if not correct
                if not pred['correct']:
                    bin_pred = bin(int(pred['predicted_value'], 16))[2:].zfill(64)
                    bin_actual = bin(actual)[2:].zfill(64)
                    bit_diff = sum(1 for i in range(min(len(bin_pred), len(bin_actual))) 
                                   if i < len(bin_pred) and i < len(bin_actual) and bin_pred[i] != bin_actual[i])
                    pred['bit_difference'] = bit_diff
        
        # Save predictions
        with open('analysis_scrypt/predictions.json', 'w') as f:
            json.dump(predictions, f, indent=2)
            
        # Print predictions
        print("\nPredictions for next positions:")
        for pred in predictions:
            pos = pred['position']
            print(f"Position {pos}: {pred['predicted_value']}")
            if pos in self.future_values:
                correct = "CORRECT" if pred.get('correct', False) else "INCORRECT"
                print(f"  Actual: {hex(self.future_values[pos])} - {correct}")
                if 'bit_difference' in pred:
                    print(f"  Bit difference: {pred['bit_difference']} bits")
        
        return predictions

def main():
    analyzer = ScryptSequenceAnalyzer()
    
    print("Starting Sequence Analysis using scrypt/ROMix Concepts")
    print("=" * 80)
    
    # Analyze key patterns
    print("\nAnalyzing key patterns in the sequence...")
    analyzer.analyze_key_patterns()
    
    # Test Salsa20 patterns
    print("\nTesting Salsa20-inspired patterns...")
    analyzer.test_salsa_patterns()
    
    # Simulate ROMix
    print("\nSimulating ROMix algorithm with various parameters...")
    analyzer.simulate_romix()
    
    # Test complex bit patterns
    print("\nTesting complex bit manipulation patterns...")
    analyzer.test_complex_bit_patterns()
    
    # Predict next positions
    print("\nPredicting next positions in sequence...")
    analyzer.predict_next_positions(3)
    
    print("\nAnalysis complete. All results saved in analysis_scrypt/ directory")

if __name__ == "__main__":
    main() 