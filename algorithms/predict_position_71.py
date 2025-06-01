#!/usr/bin/env python3
"""Predict position 71 using our discovered patterns (blind prediction)"""

def predict_position_71():
    """Predict position 71 based on discovered extended patterns"""
    
    print("🔮 PREDICTING POSITION 71 (BLIND PREDICTION)")
    print("=" * 60)
    
    position = 71
    
    # Based on our extended pattern analysis, need to determine pattern group
    print("--- PATTERN CLASSIFICATION ANALYSIS ---")
    print("Known pattern groups:")
    print("- Position 69: 2^(n-1) pattern (2^68) - 0.7% deviation")  
    print("- Position 70: 2^n pattern (2^70) - ~17.8% deviation")
    print("- Position 75: 2^(n-1) pattern (2^74) - 19.3% deviation")
    print()
    
    # Pattern analysis: Most positions follow 2^n pattern
    # Positions 67, 68, 70 follow 2^n pattern
    # Positions 69, 75, 95 follow 2^(n-1) pattern
    # Position 71 is between 70 (2^n) and 75 (2^(n-1))
    
    print("Pattern prediction for position 71:")
    print("- Position 70 uses 2^n pattern")
    print("- Most positions use 2^n pattern") 
    print("- Likely: Position 71 follows 2^n pattern")
    print()
    
    # Calculate base power: 2^n = 2^71
    base_power = 2 ** position
    print(f"Selected pattern: 2^{position} (2^n pattern)")
    print(f"Base value: {base_power:,}")
    print(f"Base hex: 0x{base_power:x}")
    print()
    
    # Estimate adjustment based on 2^n pattern analysis
    print("--- ADJUSTMENT ESTIMATION ---")
    print("2^n pattern group analysis:")
    print("- Position 67: ~10.1% deviation (negative)")
    print("- Position 68: ~25.5% deviation (negative)")  
    print("- Position 70: ~17.8% deviation (negative)")
    print("- Average: ~17.8% negative deviation")
    print()
    
    # Estimate negative adjustment of ~18% for position 71
    estimated_adjustment_percent = -18.0  # Negative adjustment typical for 2^n pattern
    estimated_adjustment = int(base_power * estimated_adjustment_percent / 100)
    
    print(f"Estimated adjustment: {estimated_adjustment_percent}% of base")
    print(f"Estimated adjustment value: {estimated_adjustment:,}")
    print(f"Estimated adjustment hex: -0x{abs(estimated_adjustment):x}")
    print()
    
    # Calculate predicted key
    predicted_key = base_power + estimated_adjustment
    
    print("--- FINAL PREDICTION ---")
    print(f"Predicted key[71] = 2^71 + adjustment")
    print(f"Predicted key[71] = {base_power:,} + ({estimated_adjustment:,})")
    print(f"Predicted key[71] = {predicted_key:,}")
    print(f"Predicted key[71] = 0x{predicted_key:x}")
    print()
    
    # Validation checks
    expected_bit_length = position
    actual_bit_length = predicted_key.bit_length()
    
    print("--- VALIDATION CHECKS ---")
    print(f"Expected bit length for position {position}: {expected_bit_length} bits")
    print(f"Predicted key bit length: {actual_bit_length} bits")
    print(f"Bit length match: {'✓' if actual_bit_length == expected_bit_length else '✗'}")
    
    # Check if within expected range for position 71
    expected_min = 2 ** (position - 1)
    expected_max = (2 ** position) - 1
    in_range = expected_min <= predicted_key <= expected_max
    
    print(f"Expected range: 2^{position-1} to 2^{position}-1")
    print(f"Range check: {'✓' if in_range else '✗'}")
    print(f"Position within {position}-bit range: {'✓' if in_range else '✗'}")
    
    return predicted_key

def alternative_prediction_71():
    """Alternative prediction using 2^(n-1) pattern for comparison"""
    
    print("\n--- ALTERNATIVE PREDICTION (2^(n-1) pattern) ---")
    
    position = 71
    
    # Alternative: 2^(n-1) = 2^70
    alt_base = 2 ** (position - 1)
    alt_adjustment_percent = 15.0  # Positive adjustment typical for 2^(n-1)
    alt_adjustment = int(alt_base * alt_adjustment_percent / 100)
    alt_prediction = alt_base + alt_adjustment
    
    print(f"Alternative base (2^70): {alt_base:,}")
    print(f"Alternative adjustment: +{alt_adjustment_percent}%")
    print(f"Alternative prediction: 0x{alt_prediction:x}")
    
    return alt_prediction

if __name__ == "__main__":
    # Run main prediction
    primary_prediction = predict_position_71()
    
    # Get alternative prediction  
    alternative_prediction = alternative_prediction_71()
    
    # Compare both
    print(f"\n--- PREDICTION COMPARISON ---")
    print(f"Primary (2^71 pattern):     0x{primary_prediction:x}")
    print(f"Alternative (2^70 pattern): 0x{alternative_prediction:x}")
    
    print(f"\n🎯 FINAL BLIND PREDICTION FOR POSITION 71:")
    print(f"   0x{primary_prediction:x} (Primary - 2^71 with negative adjustment)") 