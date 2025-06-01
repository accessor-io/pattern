import math
import hashlib
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import defaultdict

# Constants from the original code
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
CHAIN_MODULUS = 2**256
HASH_LENGTH = 32

# Known solutions for first 21 indices
KNOWN_SOLUTIONS = {
    1:  0x0000000000000000000000000000000000000000000000000000000000000001,
    2:  0x0000000000000000000000000000000000000000000000000000000000000003,
    3:  0x0000000000000000000000000000000000000000000000000000000000000007,
    4:  0x0000000000000000000000000000000000000000000000000000000000000008,
    5:  0x0000000000000000000000000000000000000000000000000000000000000015,
    6:  0x0000000000000000000000000000000000000000000000000000000000000031,
    7:  0x000000000000000000000000000000000000000000000000000000000000004c,
    8:  0x00000000000000000000000000000000000000000000000000000000000000e0,
    9:  0x00000000000000000000000000000000000000000000000000000000000001d3,
    10: 0x0000000000000000000000000000000000000000000000000000000000000202,
    11: 0x0000000000000000000000000000000000000000000000000000000000000483,
    12: 0x0000000000000000000000000000000000000000000000000000000000000a7b,
    13: 0x0000000000000000000000000000000000000000000000000000000000001460,
    14: 0x0000000000000000000000000000000000000000000000000000000000002930,
    15: 0x00000000000000000000000000000000000000000000000000000000000068f3,
    16: 0x000000000000000000000000000000000000000000000000000000000000c936,
    17: 0x000000000000000000000000000000000000000000000000000000000001764f,
    18: 0x000000000000000000000000000000000000000000000000000000000003080d,
    19: 0x000000000000000000000000000000000000000000000000000000000005749f,
    20: 0x00000000000000000000000000000000000000000000000000000000000d2c55,
    21: 0x00000000000000000000000000000000000000000000000000000000001ba534
}

def analyze_growth_patterns() -> Dict[str, List[float]]:
    """Analyze growth patterns between consecutive indices."""
    patterns = {
        'ratios': [],
        'differences': [],
        'bit_growth': [],
        'hex_patterns': [],
        'binary_patterns': []
    }
    
    indices = sorted(KNOWN_SOLUTIONS.keys())
    for i in range(len(indices)-1):
        curr_idx = indices[i]
        next_idx = indices[i+1]
        curr_val = KNOWN_SOLUTIONS[curr_idx]
        next_val = KNOWN_SOLUTIONS[next_idx]
        
        # Calculate growth ratio
        ratio = next_val / curr_val if curr_val != 0 else float('inf')
        patterns['ratios'].append(ratio)
        
        # Calculate difference
        diff = next_val - curr_val
        patterns['differences'].append(diff)
        
        # Analyze bit growth
        curr_bits = curr_val.bit_length()
        next_bits = next_val.bit_length()
        patterns['bit_growth'].append(next_bits - curr_bits)
        
        # Analyze hex patterns
        curr_hex = hex(curr_val)[2:].zfill(64)
        next_hex = hex(next_val)[2:].zfill(64)
        common_prefix = 0
        for j in range(min(len(curr_hex), len(next_hex))):
            if curr_hex[j] == next_hex[j]:
                common_prefix += 1
            else:
                break
        patterns['hex_patterns'].append(common_prefix)
        
        # Analyze binary patterns
        curr_bin = bin(curr_val)[2:].zfill(256)
        next_bin = bin(next_val)[2:].zfill(256)
        patterns['binary_patterns'].append(sum(1 for a, b in zip(curr_bin, next_bin) if a == b))
    
    return patterns

def predict_next_value(index: int) -> Optional[int]:
    """Predict the next value based on observed patterns."""
    if index <= 21:
        return KNOWN_SOLUTIONS.get(index)
    
    # Get the last few known values
    last_known = sorted(KNOWN_SOLUTIONS.items())[-3:]
    patterns = analyze_growth_patterns()
    
    # Calculate average growth patterns
    avg_ratio = sum(patterns['ratios'][-5:]) / 5
    avg_diff = sum(patterns['differences'][-5:]) / 5
    avg_bit_growth = sum(patterns['bit_growth'][-5:]) / 5
    
    # Get the last known value
    last_index, last_value = last_known[-1]
    
    # Predict using multiple methods
    predictions = []
    
    # Method 1: Ratio-based prediction
    ratio_pred = int(last_value * avg_ratio)
    predictions.append(ratio_pred)
    
    # Method 2: Difference-based prediction
    diff_pred = int(last_value + avg_diff)
    predictions.append(diff_pred)
    
    # Method 3: Bit pattern-based prediction
    bit_growth_pred = last_value << int(avg_bit_growth)
    predictions.append(bit_growth_pred)
    
    # Method 4: Pattern-based prediction using last few values
    pattern_pred = last_value
    for i in range(3):
        curr_val = last_known[i][1]
        if i < 2:
            next_val = last_known[i+1][1]
            pattern = next_val / curr_val
            pattern_pred = int(pattern_pred * pattern)
    predictions.append(pattern_pred)
    
    # Take the median of predictions to avoid outliers
    predictions.sort()
    median_pred = predictions[len(predictions)//2]
    
    # Validate prediction
    if validate_prediction(index, median_pred):
        return median_pred
    
    return None

def validate_prediction(index: int, predicted_value: int) -> bool:
    """Validate if the predicted value meets known patterns and constraints."""
    # Check bit length constraints
    min_bits = math.ceil(math.log2(index)) + 4
    max_bits = min_bits * 3
    actual_bits = predicted_value.bit_length()
    if not (min_bits <= actual_bits <= max_bits):
        return False
    
    # Check if value is within reasonable range
    last_known_val = KNOWN_SOLUTIONS[max(KNOWN_SOLUTIONS.keys())]
    if predicted_value < last_known_val:
        return False
    if predicted_value > last_known_val * 4:  # Assuming reasonable growth
        return False
    
    # Check bit pattern consistency
    predicted_bits = bin(predicted_value)[2:].zfill(256)
    ones_count = predicted_bits.count('1')
    if ones_count < index // 2 or ones_count > index * 2:
        return False
    
    return True

def find_chain_patterns() -> Dict[str, List[Tuple[int, int]]]:
    """Find patterns in the chain of values."""
    patterns = defaultdict(list)
    
    # Analyze consecutive triples
    indices = sorted(KNOWN_SOLUTIONS.keys())
    for i in range(len(indices)-2):
        idx1, idx2, idx3 = indices[i:i+3]
        val1 = KNOWN_SOLUTIONS[idx1]
        val2 = KNOWN_SOLUTIONS[idx2]
        val3 = KNOWN_SOLUTIONS[idx3]
        
        # Look for arithmetic sequences
        if val3 - val2 == val2 - val1:
            patterns['arithmetic'].append((idx1, idx3))
        
        # Look for geometric sequences
        if val1 != 0 and val2 != 0 and val2/val1 == val3/val2:
            patterns['geometric'].append((idx1, idx3))
        
        # Look for bit shift patterns
        shift1 = (val2.bit_length() - val1.bit_length())
        shift2 = (val3.bit_length() - val2.bit_length())
        if shift1 == shift2:
            patterns['bit_shift'].append((idx1, idx3))
    
    return patterns

def predict_range(start_index: int, end_index: int) -> Dict[int, int]:
    """Predict a range of values."""
    predictions = {}
    chain_patterns = find_chain_patterns()
    
    print(f"\nPredicting values from index {start_index} to {end_index}")
    print("Using chain patterns:", dict(chain_patterns))
    
    for index in range(start_index, end_index + 1):
        predicted = predict_next_value(index)
        if predicted is not None:
            predictions[index] = predicted
            print(f"Predicted value for index {index}: {hex(predicted)}")
    
    return predictions

def main():
    # Analyze existing patterns
    growth_patterns = analyze_growth_patterns()
    chain_patterns = find_chain_patterns()
    
    print("Growth Pattern Analysis:")
    for pattern_type, values in growth_patterns.items():
        print(f"\n{pattern_type.replace('_', ' ').title()}:")
        print(f"Average: {sum(values)/len(values)}")
        print(f"Min: {min(values)}")
        print(f"Max: {max(values)}")
    
    print("\nChain Pattern Analysis:")
    for pattern_type, sequences in chain_patterns.items():
        print(f"\n{pattern_type.replace('_', ' ').title()} Sequences:")
        for start, end in sequences:
            print(f"Indices {start}-{end}")
    
    # Predict next set of values
    print("\nPredicting next set of values...")
    predictions = predict_range(22, 30)  # Start with a small range to validate
    
    print("\nPredicted Values:")
    for index, value in predictions.items():
        print(f"Index {index}: {hex(value)}")

if __name__ == "__main__":
    main() 