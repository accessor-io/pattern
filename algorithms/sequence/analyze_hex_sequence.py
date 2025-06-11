import sys
import math

def find_pattern_length(sequence):
    """Try to find repeating pattern length in differences."""
    if len(sequence) < 4:
        return None
    
    for length in range(2, min(len(sequence) // 2, 20)):
        is_pattern = True
        for i in range(len(sequence) - length):
            if abs(sequence[i] - sequence[i + length]) / max(sequence[i], 1) > 0.1:  # 10% tolerance
                is_pattern = False
                break
        if is_pattern:
            return length
    return None

def analyze_sequence(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    
    print('Analyzing sequence patterns...\n')
    
    # Convert hex to integers for analysis
    numbers = [int(line, 16) for line in lines]
    
    # Analyze differences between consecutive numbers
    diffs = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
    
    # Analyze second-order differences
    second_diffs = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
    
    print('Pattern Analysis:')
    print('-' * 50)
    
    # Look for geometric progression
    ratios = [numbers[i+1] / numbers[i] for i in range(len(numbers)-1)]
    avg_ratio = sum(ratios[:10]) / min(10, len(ratios))
    print(f'Average growth ratio (first 10): {avg_ratio:.4f}')
    
    # Check if differences form arithmetic sequence
    avg_second_diff = sum(second_diffs[:10]) / min(10, len(second_diffs))
    print(f'Average second-order difference: {avg_second_diff:.4f}')
    
    # Look for pattern length
    pattern_length = find_pattern_length(diffs)
    if pattern_length:
        print(f'Possible pattern length in differences: {pattern_length}')
    
    # Bit pattern analysis
    print('\nBit Pattern Analysis:')
    print('-' * 50)
    for i in range(min(10, len(numbers))):
        binary = bin(numbers[i])[2:].zfill(256)
        ones = binary.count('1')
        zeros = binary.count('0')
        leading_zeros = len(binary) - len(binary.lstrip('0'))
        print(f'Number {i+1}:')
        print(f'  Ones: {ones}, Zeros: {zeros}')
        print(f'  Leading zeros: {leading_zeros}')
        print(f'  First set bit position: {256 - leading_zeros - 1}')
    
    # Try to identify the sequence type
    print('\nSequence Type Analysis:')
    print('-' * 50)
    
    # Check if it might be fibonacci-like
    fib_like = all(abs(numbers[i+2] - (numbers[i+1] + numbers[i])) / numbers[i+2] < 0.1 for i in range(len(numbers)-2))
    if fib_like:
        print("Sequence shows Fibonacci-like properties")
    
    # Check if it might be exponential
    exp_like = all(abs(math.log(ratios[i+1]) - math.log(ratios[i])) < 0.1 for i in range(len(ratios)-1))
    if exp_like:
        print("Sequence shows exponential growth properties")
    
    # Check if it might be polynomial
    poly_like = all(abs(second_diffs[i+1] - second_diffs[i]) / max(second_diffs[i], 1) < 0.1 for i in range(len(second_diffs)-1))
    if poly_like:
        print("Sequence shows polynomial growth properties")
    
    # Predict next values
    print('\nNext Value Predictions:')
    print('-' * 50)
    if len(numbers) >= 3:
        last = numbers[-1]
        
        # Linear prediction
        linear_next = last + diffs[-1]
        print(f'Linear prediction: {hex(linear_next)}')
        
        # Geometric prediction
        geometric_next = int(last * ratios[-1])
        print(f'Geometric prediction: {hex(geometric_next)}')
        
        # Polynomial prediction
        if len(numbers) >= 4:
            poly_next = last + diffs[-1] + second_diffs[-1]
            print(f'Polynomial prediction: {hex(poly_next)}')
        
        # Pattern-based prediction
        if pattern_length:
            pattern_next = last + diffs[-pattern_length]
            print(f'Pattern-based prediction: {hex(pattern_next)}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <hex_file>")
        sys.exit(1)
    analyze_sequence(sys.argv[1]) 