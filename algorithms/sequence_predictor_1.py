import hashlib
from collections import defaultdict
import math

def predict_next_values(num_predictions=5):
    # Read existing sequence
    with open('organized/data/32bHex.txt') as f:
        numbers = [int(line.strip(), 16) for line in f]
    
    print("Sequence Prediction Analysis")
    print("=" * 50)
    
    # Get last few numbers for pattern matching
    last_numbers = numbers[-5:]
    predictions = []
    
    for i in range(num_predictions):
        # Apply discovered patterns to predict next value
        last = last_numbers[-1]
        
        # 1. Apply XOR growth pattern (discovered from analysis)
        xor_pattern = 0x7d  # Last observed pattern
        xor_result = last ^ xor_pattern
        
        # 2. Apply modular constraints
        mod2_val = xor_result % 2
        mod3_val = xor_result % 3
        
        # Adjust to satisfy modular relationships
        while (mod2_val != 1) or (mod3_val != 2):  # Target values from analysis
            xor_result += 1
            mod2_val = xor_result % 2
            mod3_val = xor_result % 3
        
        # 3. Preserve specific bit positions (from AND pattern analysis)
        preserved_bits = last & 0x40  # From last AND pattern
        predicted = (xor_result & ~0x40) | preserved_bits
        
        # Store prediction
        predictions.append(predicted)
        last_numbers = last_numbers[1:] + [predicted]
        
        # Print prediction
        print(f"\nPredicted value {i+1}:")
        print(f"Hex: {hex(predicted)}")
        print(f"Modulo 2: {predicted % 2}")
        print(f"Modulo 3: {predicted % 3}")
        print(f"Preserved bits: {bin(preserved_bits)}")

if __name__ == '__main__':
    predict_next_values() 