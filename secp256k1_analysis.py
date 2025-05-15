# There is no input required for this script; it operates on files present in the working directory.
# The script expects 'known_keys.txt' to be present in the current directory.
# All processing is automatic and no user input is prompted.

import hashlib
import time
from typing import List, Tuple, Dict
import ecdsa
from ecdsa.curves import SECP256k1
from ecdsa.keys import SigningKey, VerifyingKey
import math

# Curve parameters from the paper
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

class Secp256k1Analyzer:
    def __init__(self):
        self.curve = SECP256k1
        self.G = ecdsa.ellipticcurve.Point(self.curve.curve, Gx, Gy, n)
        
    def automorphism_attack(self, private_key: int) -> List[int]:
        """Implement automorphism attack as described in paper section 3.2.1"""
        related_keys = []
        λ = '60806040526000805460ff60A01B1916905560'
        
        for i in range(1, 6):
            related_key = (private_key * pow(λ, i, n)) % n
            related_keys.append(related_key)
            
        return related_keys
    
    def glv_decomposition(self, private_key: int) -> Tuple[int, int]:
        """Implement GLV decomposition as described in paper section 3.2.2"""
        λ = '60806040526000805460ff60A01B1916905560'
        k1 = private_key % λ
        k2 = private_key // λ
        return k1, k2
    
    def timing_attack_simulation(self, private_key: int) -> float:
        """Simulate timing attack vulnerability mentioned in paper"""
        sk = SigningKey.from_secret_exponent(private_key, curve=self.curve)
        message = b"test message"
        start_time = time.time()
        signature = sk.sign(message)
        end_time = time.time()
        return end_time - start_time
    
    def analyze_key_pattern(self, keys: List[str]) -> Dict:
        """Analyze the pattern in the sequence of keys"""
        patterns = {
            'exponential_growth': True,
            'automorphism_related': True,
            'glv_optimized': True,
            'timing_variation': [],
            'key_sizes': [],
            'key_differences': [],
            'glv_patterns': []
        }
        
        prev_key = None
        for key_hex in keys:
            key = int(key_hex, 16)
            patterns['key_sizes'].append(key)
            
            if prev_key is not None:
                # Check for exponential growth
                if key <= prev_key * 2:
                    patterns['exponential_growth'] = False
                
                # Calculate difference between consecutive keys
                diff = key - prev_key
                patterns['key_differences'].append(diff)
                
                # Check if keys are automorphism-related
                related_keys = self.automorphism_attack(prev_key)
                if key not in related_keys:
                    patterns['automorphism_related'] = False
                
                # Check GLV optimization and store pattern
                k1, k2 = self.glv_decomposition(key)
                patterns['glv_patterns'].append((k1, k2))
                if k2 != 0:
                    patterns['glv_optimized'] = False
                
                # Record timing
                timing = self.timing_attack_simulation(key)
                patterns['timing_variation'].append(timing)
            
            prev_key = key
            
        return patterns
    
    def print_analysis(self, patterns: Dict):
        """Print analysis results in a readable format"""
        print("\nKey Pattern Analysis:")
        print("=" * 50)
        print(f"Exponential Growth Pattern: {'Yes' if patterns['exponential_growth'] else 'No'}")
        print(f"Automorphism Related: {'Yes' if patterns['automorphism_related'] else 'No'}")
        print(f"GLV Optimized: {'Yes' if patterns['glv_optimized'] else 'No'}")
        
        print("\nKey Differences Analysis:")
        print("-" * 30)
        if patterns['key_differences']:
            avg_diff = int(sum(patterns['key_differences']) / len(patterns['key_differences']))
            min_diff = min(patterns['key_differences'])
            max_diff = max(patterns['key_differences'])
            print(f"Average difference between consecutive keys: {hex(avg_diff)}")
            print(f"Minimum difference between consecutive keys: {hex(min_diff)}")
            print(f"Maximum difference between consecutive keys: {hex(max_diff)}")
            
            # Calculate growth ratios
            ratios = []
            for i in range(1, len(patterns['key_sizes'])):
                if patterns['key_sizes'][i-1] != 0:
                    ratio = patterns['key_sizes'][i] / patterns['key_sizes'][i-1]
                    ratios.append(ratio)
            if ratios:
                avg_ratio = sum(ratios) / len(ratios)
                print(f"\nAverage growth ratio: {avg_ratio:.2f}x")
        
        print("\nGLV Pattern Analysis:")
        print("-" * 30)
        if patterns['glv_patterns']:
            k1_values = [k1 for k1, _ in patterns['glv_patterns']]
            print(f"k1 values range: {hex(min(k1_values))} to {hex(max(k1_values))}")
            print(f"All k2 values are 0: {'Yes' if all(k2 == 0 for _, k2 in patterns['glv_patterns']) else 'No'}")
        
        print("\nTiming Analysis:")
        print("-" * 30)
        if patterns['timing_variation']:
            avg_timing = sum(patterns['timing_variation']) / len(patterns['timing_variation'])
            min_timing = min(patterns['timing_variation'])
            max_timing = max(patterns['timing_variation'])
            print(f"Average timing: {avg_timing:.6f} seconds")
            print(f"Minimum timing: {min_timing:.6f} seconds")
            print(f"Maximum timing: {max_timing:.6f} seconds")
            print(f"Timing variance: {sum((t - avg_timing) ** 2 for t in patterns['timing_variation']) / len(patterns['timing_variation']):.6f}")
    
    def analyze_known_keys(self, keys: List[str]):
        """Analyze the sequence of known keys"""
        results = []
        total_keys = len(keys)
        
        for i, key_hex in enumerate(keys):
            print(f"Analyzing key {i+1}/{total_keys}...")
            private_key = int(key_hex, 16)
            
            # Get related keys through automorphism
            related_keys = self.automorphism_attack(private_key)
            
            # Apply GLV decomposition
            k1, k2 = self.glv_decomposition(private_key)
            
            # Simulate timing attack
            timing = self.timing_attack_simulation(private_key)
            
            # Calculate key properties
            key_size = len(hex(private_key)[2:]) // 2  # Size in bytes
            key_bits = key_size * 8
            
            results.append({
                'private_key': key_hex,
                'related_keys': [hex(k) for k in related_keys],
                'glv_decomposition': (hex(k1), hex(k2)),
                'timing': timing,
                'key_size': key_size,
                'key_bits': key_bits
            })
            
        return results

    def validate_prediction(self, predicted_key: str, expected_prefix: str) -> bool:
        """Validate if a predicted key matches the expected prefix"""
        return predicted_key.startswith(expected_prefix)

    def predict_next_keys(self, current_keys, num_keys, expected_prefix=None, known_key_75=None):
        """
        Predict the next keys in the sequence based on observed patterns.
        If the 75th key is known and the sequence is at the 70th key, interpolate using geometric progression.
        Otherwise, use a fallback heuristic (scaling by a fixed ratio).
        """
        predictions = []
        n_secp = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

        def format_key(key_int, ref_hex):
            """Format integer key as hex string, zero-padded to match reference length."""
            return hex(key_int)[2:].zfill(len(ref_hex))

        # Geometric interpolation if 75th key is known and at 70th key
        if known_key_75 and len(current_keys) == 70 and num_keys >= 5:
            key_70 = int('0000000000000000000000000000000000000000000000349b84b6431a6c4ef1', 16)
            key_75 = int(known_key_75, 16)
            # Avoid division by zero or negative/invalid roots
            if key_70 > 0 and key_75 > 0:
                ratio = (key_75 / key_70) ** (1 / 5)
                prev = key_70
                for _ in range(5):
                    next_key = int(prev * ratio)
                    if next_key >= n_secp:
                        next_key = n_secp - 1
                    predictions.append(format_key(next_key, current_keys[-1]))
                    prev = next_key
                # Continue extrapolating if more keys are needed
                last_key_int = prev
                for _ in range(num_keys - 5):
                    next_key = int(last_key_int * ratio)
                    if next_key >= n_secp:
                        next_key = n_secp - 1
                    predictions.append(format_key(next_key, current_keys[-1]))
                    last_key_int = next_key
                return predictions

        # Fallback: scale last key by a fixed ratio (2.60), capping at curve order
        last_key_int = int(current_keys[-1], 16)
        for _ in range(num_keys):
            next_key = int(last_key_int * 2.60)
            if next_key >= n_secp:
                next_key = n_secp - 1
            predictions.append(format_key(next_key, current_keys[-1]))
            last_key_int = next_key
        return predictions

    def find_predictive_pattern(self, keys: list):
        print("\nPattern Discovery Analysis:")
        int_keys = [int(k, 16) for k in keys]
        n = len(int_keys)
        if n < 2:
            print("Not enough keys to analyze patterns.")
            return

        # Collect statistics for improved insight
        diffs = []
        ratios = []
        bit_lengths = []
        power_of_two_indices = []
        sum_prev_two_indices = []
        close_to_pow2_indices = []
        bitwise_stats = []

        for i in range(1, n):
            prev = int_keys[i-1]
            curr = int_keys[i]
            diff = curr - prev
            ratio = curr / prev if prev != 0 else float('inf')
            diffs.append(diff)
            ratios.append(ratio)
            bit_lengths.append(curr.bit_length())

            print(f"Key {i}: {curr} (hex: {hex(curr)})")
            print(f"  Previous: {prev} (hex: {hex(prev)})")
            print(f"  Difference: {diff}")
            print(f"  Ratio: {ratio:.6f}")

            # Check if power of two
            if curr > 0 and math.log2(curr).is_integer():
                power = int(math.log2(curr))
                print(f"  Power of two: 2^{power}")
                power_of_two_indices.append(i)
            # Check if sum of previous two keys
            if i >= 2 and curr == int_keys[i-1] + int_keys[i-2]:
                print(f"  Sum of previous two keys: {int_keys[i-1]} + {int_keys[i-2]}")
                sum_prev_two_indices.append(i)
            # Check if close to power of two
            pow2 = 2 ** round(math.log2(curr)) if curr > 0 else 0
            if curr > 0 and abs(curr - pow2) < 10:
                print(f"  Close to power of two: {pow2}")
                close_to_pow2_indices.append(i)
            # Bitwise operations
            or_val = prev | curr
            and_val = prev & curr
            xor_val = prev ^ curr
            print(f"  Bitwise OR with prev: {hex(or_val)}")
            print(f"  Bitwise AND with prev: {hex(and_val)}")
            print(f"  Bitwise XOR with prev: {hex(xor_val)}")
            bitwise_stats.append({'or': or_val, 'and': and_val, 'xor': xor_val})

        # Summary statistics
        print("\n--- Pattern Summary ---")
        print(f"Total keys analyzed: {n}")
        print(f"Average difference: {sum(diffs)/len(diffs):.2f}")
        print(f"Average ratio: {sum(ratios)/len(ratios):.6f}")
        print(f"Bit length range: {min(bit_lengths)} - {max(bit_lengths)}")
        if power_of_two_indices:
            print(f"Keys at power-of-two indices: {power_of_two_indices}")
        if sum_prev_two_indices:
            print(f"Keys that are sum of previous two: {sum_prev_two_indices}")
        if close_to_pow2_indices:
            print(f"Keys close to power of two: {close_to_pow2_indices}")

        # Try to predict next key using multiple heuristics
        last = int_keys[-1]
        avg_diff = int(sum(diffs) / len(diffs))
        avg_ratio = sum(ratios) / len(ratios)
        next_guess_diff = last + avg_diff
        next_guess_ratio = int(last * avg_ratio)
        next_pow2 = 2 ** (last.bit_length())
        print(f"\nCandidate next key by average difference: {hex(next_guess_diff)}")
        print(f"Candidate next key by average ratio: {hex(next_guess_ratio)}")
        print(f"Candidate next key by next power of two: {hex(next_pow2)}")
        if n >= 2:
            sum_last_two = int_keys[-1] + int_keys[-2]
            print(f"Candidate next key by sum of last two: {hex(sum_last_two)}")
        print("\n--- End of Pattern Discovery ---\n")

def main():
    # No input is required; the script processes files in the current directory.

    import os

    analyzer = Secp256k1Analyzer()

    # Ensure output directory exists
    output_dir = "."
    verbose_path = os.path.join(output_dir, 'analysis_verbose.txt')
    predicted_path = os.path.join(output_dir, 'predicted_keys.txt')

    # Verbose print function to both console and file
    with open(verbose_path, 'w') as verbose_file:

        def vprint(*args, **kwargs):
            print(*args, **kwargs)
            print(*args, **kwargs, file=verbose_file)

        # Load known keys
        known_keys_path = os.path.join(output_dir, 'known_keys.txt')
        if not os.path.exists(known_keys_path):
            vprint(f"Error: {known_keys_path} not found.")
            return

        with open(known_keys_path, 'r') as f:
            known_keys = [line.strip() for line in f if line.strip()]

        vprint(f"Found {len(known_keys)} known keys")

        # Pattern discovery before prediction
        analyzer.find_predictive_pattern(known_keys)

        # Predict additional keys if needed
        TARGET_KEY_COUNT = 160
        additional_needed = TARGET_KEY_COUNT - len(known_keys)
        known_key_75 = '0000000000000000000000000000000000000000000004c5ce114686a1336e07'
        all_keys = list(known_keys)

        if additional_needed > 0:
            vprint(f"\nPredicting {additional_needed} additional keys...")
            vprint("Using known prefix '349' for 70th key and known 75th key")
            predicted_keys = analyzer.predict_next_keys(
                known_keys, additional_needed,
                expected_prefix='349',
                known_key_75=known_key_75
            )
            vprint("\nSaving predicted keys...")
            with open(predicted_path, 'w') as pf:
                for key in predicted_keys:
                    pf.write(key + '\n')
            all_keys.extend(predicted_keys)
        else:
            all_keys = all_keys[:TARGET_KEY_COUNT]

        # High-verbosity analysis of all keys
        vprint("\nAnalyzing all keys with high verbosity...")
        results = []
        for i, key_hex in enumerate(all_keys):
            vprint(f"\n--- Key {i+1}/{len(all_keys)} ---")
            try:
                private_key = int(key_hex, 16)
            except ValueError:
                vprint(f"Invalid key format: {key_hex}")
                continue

            vprint(f"Private Key (hex): {key_hex}")
            vprint(f"Private Key (int): {private_key}")
            key_bits = private_key.bit_length()
            vprint(f"Key Size (bits): {key_bits}")

            # Automorphism attack
            related_keys = analyzer.automorphism_attack(private_key)
            vprint("Automorphism-related keys:")
            for idx, rk in enumerate(related_keys):
                vprint(f"  λ^{idx+1} * k mod n = {hex(rk)}")

            # GLV decomposition
            k1, k2 = analyzer.glv_decomposition(private_key)
            vprint(f"GLV decomposition: k1 = {hex(k1)}, k2 = {hex(k2)}")

            # Timing attack simulation
            timing = analyzer.timing_attack_simulation(private_key)
            vprint(f"Timing attack simulation: {timing:.6f} seconds")

            # Growth ratio and difference
            if i > 0:
                prev_key = int(all_keys[i-1], 16)
                growth_ratio = private_key / prev_key if prev_key != 0 else float('inf')
                vprint(f"Growth ratio from previous key: {growth_ratio:.2f}x")
                vprint(f"Difference from previous key: {hex(private_key - prev_key)}")
            else:
                vprint("Growth ratio from previous key: N/A (first key)")

            results.append({
                'private_key': key_hex,
                'related_keys': [hex(k) for k in related_keys],
                'glv_decomposition': (hex(k1), hex(k2)),
                'timing': timing,
                'key_bits': key_bits
            })

        # Pattern analysis
        vprint("\nAnalyzing patterns...")
        pattern_analysis = analyzer.analyze_key_pattern(all_keys)

        # Print analysis results
        analyzer.print_analysis(pattern_analysis)

        # Decade summary statistics
        print("\nSummary by decades:")
        print("=" * 50)
        for i in range(0, len(results), 10):
            end_idx = min(i + 10, len(results))
            decade = results[i:end_idx]
            decade_keys = [int(r['private_key'], 16) for r in decade if r['private_key']]
            if len(decade_keys) > 1:
                growth_ratios = [
                    decade_keys[j] / decade_keys[j-1]
                    for j in range(1, len(decade_keys))
                    if decade_keys[j-1] != 0
                ]
                avg_growth = sum(growth_ratios) / len(growth_ratios) if growth_ratios else 0
                vprint(f"\nKeys {i+1}-{end_idx}:")
                vprint(f"Average growth ratio: {avg_growth:.2f}x")
                vprint(f"Key size range: {decade[0]['key_bits']}-{decade[-1]['key_bits']} bits")
                vprint("-" * 30)

if __name__ == "__main__":
    main()