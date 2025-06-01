#!/usr/bin/env python3
"""
Polynomial Interpolation Attack Implementation
Attempts to calculate missing Bitcoin puzzle keys using polynomial fitting
with the known data points and exposed signature information.

This demonstrates the practical implementation of the cryptographic vulnerability.
"""

import numpy as np
from scipy.interpolate import lagrange, BarycentricInterpolator
from scipy.optimize import minimize
import hashlib

# Known private keys from positions 1-68 (from previous analysis)
KNOWN_KEYS = {
    1: 0x1,
    2: 0x3,
    3: 0x7,
    4: 0x8,
    5: 0x15,
    6: 0x31,
    7: 0x4c,
    8: 0xbc,
    9: 0x179,
    10: 0x2c0,
    11: 0x381,
    12: 0x8e9,
    13: 0x1abe,
    14: 0x2c95,
    15: 0x6a0e,
    16: 0xd6d5,
    17: 0x127a2,
    # Add more as discovered...
}

# Known keys at positions ending in 0 or 5 (from creator)
HINT_KEYS = {
    70: 0x1d4d0f36de24d2b,  # Example - replace with actual
    75: 0x7d14b6a1d2de,     # Example - replace with actual
    80: 0x1dca8c5d7ad5e,    # Example - replace with actual
    # Add actual hint keys here...
}

# Target missing positions
MISSING_POSITIONS = [69, 71, 72, 73, 74, 76, 77, 78, 79, 81, 82, 83, 84]

def polynomial_interpolation_attack(positions, private_keys, target_positions, max_degree=10):
    """
    Attempt to find missing private keys using polynomial interpolation
    """
    print("=== POLYNOMIAL INTERPOLATION ATTACK ===\n")
    
    # Convert to numpy arrays for easier processing
    pos_array = np.array(positions)
    key_array = np.array(private_keys)
    
    print(f"Known data points: {len(positions)}")
    print(f"Position range: {min(positions)} to {max(positions)}")
    print(f"Target positions: {target_positions}")
    print()
    
    results = {}
    
    # Try different polynomial degrees
    for degree in range(1, min(max_degree + 1, len(positions))):
        print(f"--- Trying polynomial degree {degree} ---")
        
        try:
            # Use numpy polyfit for polynomial fitting
            if degree < len(positions):
                coeffs = np.polyfit(pos_array, key_array, degree)
                poly = np.poly1d(coeffs)
                
                # Evaluate at target positions
                predictions = {}
                for target_pos in target_positions:
                    predicted_key = int(round(poly(target_pos)))
                    if predicted_key > 0:  # Ensure positive private key
                        predictions[target_pos] = predicted_key
                
                # Check quality of fit on known points
                fit_error = 0
                for i, pos in enumerate(positions):
                    predicted = poly(pos)
                    actual = private_keys[i]
                    error = abs(predicted - actual) / actual if actual != 0 else abs(predicted)
                    fit_error += error
                
                avg_fit_error = fit_error / len(positions)
                
                print(f"  Average fit error: {avg_fit_error:.6f}")
                print(f"  Predictions for missing positions:")
                for pos in sorted(predictions.keys()):
                    print(f"    Position {pos}: 0x{predictions[pos]:x} ({predictions[pos]})")
                
                if avg_fit_error < 0.1:  # Good fit threshold
                    results[degree] = {
                        'predictions': predictions,
                        'fit_error': avg_fit_error,
                        'coefficients': coeffs
                    }
                    print(f"  ✓ Good fit found with degree {degree}!")
                
                print()
                
        except Exception as e:
            print(f"  Error with degree {degree}: {e}")
            continue
    
    return results

def lagrange_interpolation_attack(positions, private_keys, target_positions):
    """
    Use Lagrange interpolation to find missing keys
    """
    print("=== LAGRANGE INTERPOLATION ATTACK ===\n")
    
    try:
        # Create Lagrange interpolating polynomial
        poly = lagrange(positions, private_keys)
        
        predictions = {}
        for target_pos in target_positions:
            predicted_key = int(round(poly(target_pos)))
            if predicted_key > 0:
                predictions[target_pos] = predicted_key
        
        print("Lagrange interpolation predictions:")
        for pos in sorted(predictions.keys()):
            print(f"  Position {pos}: 0x{predictions[pos]:x} ({predictions[pos]})")
        
        return predictions
        
    except Exception as e:
        print(f"Lagrange interpolation failed: {e}")
        return {}

def barycentric_interpolation_attack(positions, private_keys, target_positions):
    """
    Use Barycentric interpolation (numerically stable)
    """
    print("=== BARYCENTRIC INTERPOLATION ATTACK ===\n")
    
    try:
        interpolator = BarycentricInterpolator(positions, private_keys)
        
        predictions = {}
        for target_pos in target_positions:
            predicted_key = int(round(interpolator(target_pos)))
            if predicted_key > 0:
                predictions[target_pos] = predicted_key
        
        print("Barycentric interpolation predictions:")
        for pos in sorted(predictions.keys()):
            print(f"  Position {pos}: 0x{predictions[pos]:x} ({predictions[pos]})")
        
        return predictions
        
    except Exception as e:
        print(f"Barycentric interpolation failed: {e}")
        return {}

def exponential_pattern_attack(positions, private_keys, target_positions):
    """
    Try to fit an exponential pattern (common in cryptographic puzzles)
    """
    print("=== EXPONENTIAL PATTERN ATTACK ===\n")
    
    # Try log transformation for exponential fitting
    try:
        # Take log of private keys (skip zeros)
        log_keys = []
        log_positions = []
        
        for i, key in enumerate(private_keys):
            if key > 0:
                log_keys.append(np.log(key))
                log_positions.append(positions[i])
        
        # Fit polynomial to log values
        coeffs = np.polyfit(log_positions, log_keys, 2)  # Quadratic in log space
        log_poly = np.poly1d(coeffs)
        
        predictions = {}
        for target_pos in target_positions:
            log_prediction = log_poly(target_pos)
            predicted_key = int(round(np.exp(log_prediction)))
            if predicted_key > 0:
                predictions[target_pos] = predicted_key
        
        print("Exponential pattern predictions:")
        for pos in sorted(predictions.keys()):
            print(f"  Position {pos}: 0x{predictions[pos]:x} ({predictions[pos]})")
        
        return predictions
        
    except Exception as e:
        print(f"Exponential pattern fitting failed: {e}")
        return {}

def recurrence_pattern_attack(positions, private_keys, target_positions):
    """
    Try to find a recurrence relation (like Fibonacci)
    """
    print("=== RECURRENCE PATTERN ATTACK ===\n")
    
    # Look for patterns like k[n] = a*k[n-1] + b*k[n-2] + c
    if len(private_keys) < 3:
        print("Need at least 3 points for recurrence analysis")
        return {}
    
    try:
        # Try to find coefficients for k[n] = a*k[n-1] + b*k[n-2] + c
        # This creates a system of linear equations
        
        matrix = []
        targets = []
        
        for i in range(2, len(private_keys)):
            if positions[i] == positions[i-1] + 1 == positions[i-2] + 2:  # Consecutive positions
                # k[i] = a*k[i-1] + b*k[i-2] + c
                matrix.append([private_keys[i-1], private_keys[i-2], 1])
                targets.append(private_keys[i])
        
        if len(matrix) >= 3:  # Need at least 3 equations
            matrix = np.array(matrix)
            targets = np.array(targets)
            
            # Solve for coefficients [a, b, c]
            coeffs = np.linalg.lstsq(matrix, targets, rcond=None)[0]
            a, b, c = coeffs
            
            print(f"Recurrence relation: k[n] = {a:.6f}*k[n-1] + {b:.6f}*k[n-2] + {c:.6f}")
            
            # Predict missing values (this is complex for non-consecutive positions)
            # For now, just show the relation
            
            return {'recurrence_coeffs': [a, b, c]}
        else:
            print("Not enough consecutive positions for recurrence analysis")
            return {}
            
    except Exception as e:
        print(f"Recurrence pattern analysis failed: {e}")
        return {}

def validate_predictions(predictions):
    """
    Validate predictions using known Bitcoin puzzle properties
    """
    print("=== VALIDATING PREDICTIONS ===\n")
    
    for method, preds in predictions.items():
        print(f"Validating {method} predictions:")
        
        for pos, key in preds.items():
            # Check if key is in reasonable range for the position
            min_expected = 2**(pos-1) if pos > 1 else 1
            max_expected = 2**pos - 1
            
            if min_expected <= key <= max_expected:
                print(f"  Position {pos}: ✓ Key in expected range ({min_expected:x} - {max_expected:x})")
            else:
                print(f"  Position {pos}: ⚠ Key outside expected range ({key:x} not in {min_expected:x} - {max_expected:x})")
        
        print()

def main():
    print("🎯" * 20)
    print("BITCOIN PUZZLE POLYNOMIAL ATTACK IMPLEMENTATION")
    print("🎯" * 20)
    print()
    
    # Combine all known data points
    all_positions = list(KNOWN_KEYS.keys()) + list(HINT_KEYS.keys())
    all_private_keys = list(KNOWN_KEYS.values()) + list(HINT_KEYS.values())
    
    # Sort by position
    sorted_data = sorted(zip(all_positions, all_private_keys))
    positions = [x[0] for x in sorted_data]
    private_keys = [x[1] for x in sorted_data]
    
    print(f"Total known data points: {len(positions)}")
    print(f"Positions: {positions}")
    print(f"Target missing positions: {MISSING_POSITIONS}")
    print()
    
    # Run different attack methods
    results = {}
    
    # 1. Polynomial interpolation
    poly_results = polynomial_interpolation_attack(positions, private_keys, MISSING_POSITIONS)
    if poly_results:
        results['polynomial'] = poly_results
    
    # 2. Lagrange interpolation
    lagrange_results = lagrange_interpolation_attack(positions, private_keys, MISSING_POSITIONS)
    if lagrange_results:
        results['lagrange'] = lagrange_results
    
    # 3. Barycentric interpolation
    barycentric_results = barycentric_interpolation_attack(positions, private_keys, MISSING_POSITIONS)
    if barycentric_results:
        results['barycentric'] = barycentric_results
    
    # 4. Exponential pattern
    exponential_results = exponential_pattern_attack(positions, private_keys, MISSING_POSITIONS)
    if exponential_results:
        results['exponential'] = exponential_results
    
    # 5. Recurrence pattern
    recurrence_results = recurrence_pattern_attack(positions, private_keys, MISSING_POSITIONS)
    if recurrence_results:
        results['recurrence'] = recurrence_results
    
    # Validate all predictions
    if results:
        validate_predictions(results)
        
        print("=== SUMMARY OF ATTACK RESULTS ===")
        print("Most promising predictions for missing keys:")
        
        # Compare predictions across methods
        consensus_predictions = {}
        for pos in MISSING_POSITIONS:
            predictions_for_pos = []
            for method, method_results in results.items():
                if isinstance(method_results, dict) and pos in method_results:
                    predictions_for_pos.append(method_results[pos])
            
            if predictions_for_pos:
                # If multiple methods agree, that's more confident
                if len(set(predictions_for_pos)) == 1:
                    consensus_predictions[pos] = predictions_for_pos[0]
                    print(f"  Position {pos}: 0x{predictions_for_pos[0]:x} (CONSENSUS)")
                else:
                    print(f"  Position {pos}: Multiple predictions {[hex(p) for p in predictions_for_pos]}")
        
        if consensus_predictions:
            print(f"\n🎯 HIGH CONFIDENCE PREDICTIONS: {len(consensus_predictions)} positions")
            print("These could be the actual missing private keys!")
        
    else:
        print("❌ No successful attacks - need more sophisticated methods")
        print("Consider implementing lattice attacks or other advanced techniques")

if __name__ == "__main__":
    main() 