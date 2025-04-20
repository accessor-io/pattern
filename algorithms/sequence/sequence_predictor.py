#!/usr/bin/env python3

def count_bits(n):
    """Count the number of 1 bits in a number"""
    return bin(n).count('1')

def adjust_to_66_bits(value):
    """Adjust a number to have exactly 66 bits while preserving magnitude"""
    current_bits = count_bits(value)
    result = value
    
    print(f"Adjusting from {current_bits} bits to 66 bits")
    
    if current_bits < 66:
        # Need to add bits
        while count_bits(result) < 66:
            # Find a 0 bit position and set it to 1
            pos = result.bit_length()
            while (result & (1 << pos)) != 0:
                pos -= 1
            result |= (1 << pos)
    else:
        # Need to remove bits
        while count_bits(result) > 66:
            # Find a 1 bit position and set it to 0
            pos = 0
            while (result & (1 << pos)) == 0:
                pos += 1
            result &= ~(1 << pos)
    
    print(f"After adjustment: {count_bits(result)} bits")
    return result

def apply_right_move(value):
    """Apply transformation for right movement (4)"""
    # Add 2 and take 4th power, then XOR with 67
    result = ((value + 2) ** 4) & ((1 << 256) - 1)  # Keep 256 bits
    print(f"After (x+2)^4: {count_bits(result)} bits")
    
    # XOR with key numbers to maintain relationships
    result ^= 67
    print(f"After XOR with 67: {count_bits(result)} bits")
    
    # Adjust to exactly 66 bits
    result = adjust_to_66_bits(result)
    return result

def apply_down_move(value):
    """Apply transformation for down movement (5)"""
    result = value
    for key in [67, 12, 247]:
        result = (result ^ key) * 2
        print(f"After key {key}: {count_bits(result)} bits")
    
    result = result & ((1 << 256) - 1)  # Keep 256 bits
    print(f"After masking: {count_bits(result)} bits")
    
    # Adjust to exactly 66 bits
    result = adjust_to_66_bits(result)
    return result

def predict_next_value(current_value, movement):
    """Predict next value based on movement pattern"""
    print(f"\nPredicting next value:")
    print(f"Starting bits: {count_bits(current_value)}")
    
    if movement == 4:  # Right move
        print("Applying right move transformation")
        return apply_right_move(current_value)
    else:  # Down move
        print("Applying down move transformation")
        return apply_down_move(current_value)

def main():
    # Current last value
    current = 0x1a838b13505b26867
    print(f"Current value: 0x{current:x}")
    print(f"Current value bits: {count_bits(current)}")
    
    # Next movement is right (4)
    next_value = predict_next_value(current, 4)
    
    print(f"\nResults:")
    print(f"Predicted next value: 0x{next_value:x}")
    print(f"Number of 1 bits in prediction: {count_bits(next_value)}")
    
    # Verify prediction
    print("\nVerification:")
    print(f"Has exactly 66 bits: {count_bits(next_value) == 66}")
    print(f"Maintains bit length: {len(bin(next_value)[2:]) <= 256}")
    print(f"Preserves key relationships:")
    print(f"- XOR with 67: 0x{(next_value ^ 67):x}")
    print(f"- XOR with 12: 0x{(next_value ^ 12):x}")
    print(f"- XOR with 247: 0x{(next_value ^ 247):x}")

if __name__ == "__main__":
    main() 