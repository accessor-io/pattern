import math

def analyze_sequence_formula():
    # Read the original sequence
    numbers = []
    with open('organized/data/32bHex.txt') as f:
        for line in f:
            hex_str = line.strip()
            numbers.append(int(hex_str, 16))
    
    print("Analyzing sequence patterns...")
    
    # Analyze first-order differences
    diffs = []
    for i in range(1, len(numbers)):
        diff = numbers[i] - numbers[i-1]
        diffs.append(diff)
    
    # Analyze second-order differences
    second_diffs = []
    for i in range(1, len(diffs)):
        diff = diffs[i] - diffs[i-1]
        second_diffs.append(diff)
    
    print("\nFirst 5 numbers in sequence:")
    for i in range(min(5, len(numbers))):
        print(f"{i}: {hex(numbers[i])}")
    
    print("\nFirst 5 first-order differences:")
    for i in range(min(5, len(diffs))):
        print(f"{i}: {diffs[i]} (hex: {hex(diffs[i])})")
    
    print("\nFirst 5 second-order differences:")
    for i in range(min(5, len(second_diffs))):
        print(f"{i}: {second_diffs[i]} (hex: {hex(second_diffs[i])})")
    
    # Check for common mathematical patterns
    print("\nAnalyzing mathematical patterns...")
    
    # Test for exponential growth
    if len(numbers) >= 3:
        ratio1 = numbers[1] / numbers[0] if numbers[0] != 0 else float('inf')
        ratio2 = numbers[2] / numbers[1] if numbers[1] != 0 else float('inf')
        if abs(ratio1 - ratio2) < 0.1:
            print(f"Possible exponential growth with ratio ≈ {ratio1:.4f}")
    
    # Test for polynomial growth
    if len(second_diffs) >= 3:
        if all(abs(second_diffs[i] - second_diffs[0]) < second_diffs[0] * 0.1 
               for i in range(min(3, len(second_diffs)))):
            print("Possible quadratic growth pattern")
            a = second_diffs[0] / 2
            print(f"Approximate formula: an = {a}n² + bn + c")
    
    # Generate next 5 values using discovered pattern
    print("\nPredicted next 5 values:")
    n = len(numbers)
    for i in range(n, n+5):
        # Using quadratic formula as base
        next_val = numbers[-1] + diffs[-1] + second_diffs[-1]
        print(f"n={i}: {hex(next_val)}")

if __name__ == '__main__':
    analyze_sequence_formula() 