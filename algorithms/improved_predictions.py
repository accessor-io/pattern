#!/usr/bin/env python3
"""Improved predictions ensuring proper factorization and 16th power patterns"""

def adjust_for_factors(n):
    """Adjust number to ensure it has common factors (2,3,5,7)"""
    # Ensure number is divisible by 2,3,5,7
    while n % 2 != 0: n *= 2
    while n % 3 != 0: n *= 3
    while n % 5 != 0: n *= 5
    while n % 7 != 0: n *= 7
    return n

def predict_position_improved(position):
    """Generate improved prediction with proper factorization"""
    
    if position == 75:
        # Position 75 uses 2^(n-1) pattern with positive adjustment
        base = 2 ** (position - 1)
        adjustment_percent = 19.3
    else:
        # Other positions use 2^n pattern with negative adjustment
        base = 2 ** position
        adjustment_percent = {
            71: -18.0,
            72: -20.0,
            73: -19.0,
            74: -18.0
        }[position]
    
    adjustment = int(base * adjustment_percent / 100)
    predicted_key = base + adjustment
    
    # Adjust to ensure common factors
    predicted_key = adjust_for_factors(predicted_key)
    
    # Ensure proper 16th power alignment
    # Add trailing zeros if needed (should be multiple of 4 in hex)
    hex_key = hex(predicted_key)[2:]
    if len(hex_key) % 4 != 0:
        padding = 4 - (len(hex_key) % 4)
        predicted_key *= 16 ** padding
    
    return predicted_key

def main():
    """Generate improved predictions for positions 71-75"""
    
    print("IMPROVED PREDICTIONS WITH PROPER FACTORIZATION")
    print("=" * 60)
    
    predictions = {}
    for pos in range(71, 76):
        predicted_key = predict_position_improved(pos)
        predictions[pos] = predicted_key
        
        print(f"\nPosition {pos}:")
        print(f"Predicted hex: 0x{predicted_key:x}")
        print(f"Decimal: {predicted_key:,}")
        
        # Verify factors
        factors = []
        n = predicted_key
        for i in [2,3,5,7]:
            while n % i == 0:
                factors.append(i)
                n //= i
        
        print("Common factors present:")
        print(f"Powers of 2: {factors.count(2)}")
        print(f"Powers of 3: {factors.count(3)}")
        print(f"Powers of 5: {factors.count(5)}")
        print(f"Powers of 7: {factors.count(7)}")
        
        # Verify 16th power alignment
        hex_str = hex(predicted_key)[2:]
        print(f"Hex length: {len(hex_str)}")
        print(f"Trailing zeros (hex): {len(hex_str) - len(hex_str.rstrip('0'))}")
        print("-" * 60)
    
    print("\nSUMMARY OF IMPROVED PREDICTIONS:")
    print("=" * 60)
    for pos, key in predictions.items():
        print(f"Position {pos}: 0x{key:x}")

if __name__ == "__main__":
    main() 