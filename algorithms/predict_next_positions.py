#!/usr/bin/env python3
"""Predict next positions (71-75) using discovered patterns"""

def predict_position(position):
    """Predict key for given position using appropriate pattern"""
    
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
    
    print(f"\nPrediction for position {position}:")
    print(f"Base pattern: {'2^(n-1)' if position == 75 else '2^n'}")
    print(f"Base value: {base:,}")
    print(f"Adjustment: {adjustment_percent}%")
    print(f"Predicted key: {predicted_key:,}")
    print(f"Predicted hex: 0x{predicted_key:x}")
    
    return predicted_key

def main():
    """Generate predictions for positions 71-75"""
    
    print("GENERATING PREDICTIONS FOR POSITIONS 71-75")
    print("=" * 50)
    
    predictions = {}
    for pos in range(71, 76):
        predictions[pos] = predict_position(pos)
    
    print("\nSUMMARY OF PREDICTIONS:")
    print("=" * 50)
    for pos, key in predictions.items():
        print(f"Position {pos}: 0x{key:x}")

if __name__ == "__main__":
    main() 