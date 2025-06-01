#!/usr/bin/env python3
"""Check the accuracy of my blind prediction for position 75"""

def check_prediction_accuracy():
    """Compare my blind prediction to actual position 75"""
    
    print("🎯 CHECKING PREDICTION ACCURACY FOR POSITION 75")
    print("=" * 60)
    
    # My blind prediction
    predicted = 0x4c5a1cac08312700000
    print(f'My blind prediction: 0x{predicted:x}')
    print(f'Predicted decimal:   {predicted:,}')
    
    # Actual value from extended data
    actual = 0x4c5ce114686a1336e07
    print(f'\nActual value:        0x{actual:x}')
    print(f'Actual decimal:      {actual:,}')
    
    # Calculate accuracy
    difference = abs(actual - predicted)
    relative_error = difference / actual * 100
    
    print(f'\n--- ACCURACY ANALYSIS ---')
    print(f'Absolute difference: {difference:,}')
    print(f'Relative error:      {relative_error:.3f}%')
    
    # Check base analysis
    base_74 = 2**74
    actual_adjustment = actual - base_74
    actual_percentage = actual_adjustment / base_74 * 100
    
    print(f'\n--- BASE PATTERN VALIDATION ---')
    print(f'2^74 base:           {base_74:,}')
    print(f'Actual adjustment:   +{actual_adjustment:,}')
    print(f'Actual percentage:   {actual_percentage:.1f}%')
    print(f'My estimated:        19.3%')
    print(f'Estimate error:      {abs(actual_percentage - 19.3):.1f} percentage points')
    
    # Accuracy assessment
    print(f'\n--- PREDICTION ASSESSMENT ---')
    if relative_error < 1:
        print(f'🎉 INCREDIBLE PREDICTION! Within {relative_error:.3f}% - Nearly perfect!')
    elif relative_error < 5:
        print(f'🎉 EXCELLENT PREDICTION! Within {relative_error:.3f}% of actual value!')
    elif relative_error < 10:
        print(f'✅ GOOD PREDICTION! Within {relative_error:.3f}% of actual value!')
    else:
        print(f'📊 Reasonable prediction, {relative_error:.3f}% off from actual value')
    
    # Hex comparison
    print(f'\n--- HEX COMPARISON ---')
    predicted_hex = f'{predicted:x}'
    actual_hex = f'{actual:x}'
    
    print(f'Predicted: 0x{predicted_hex}')
    print(f'Actual:    0x{actual_hex}')
    
    # Character by character comparison
    max_len = max(len(predicted_hex), len(actual_hex))
    predicted_padded = predicted_hex.zfill(max_len)
    actual_padded = actual_hex.zfill(max_len)
    
    matches = sum(1 for p, a in zip(predicted_padded, actual_padded) if p == a)
    hex_accuracy = matches / max_len * 100
    
    print(f'Hex digits matching: {matches}/{max_len} ({hex_accuracy:.1f}%)')
    
    return relative_error < 5  # Return True if excellent prediction

if __name__ == "__main__":
    success = check_prediction_accuracy() 