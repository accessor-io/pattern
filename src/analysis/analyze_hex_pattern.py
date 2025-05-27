import sys

def analyze_hex_sequence(filename):
    # Read hex numbers and convert to integers
    numbers = []
    with open(filename) as f:
        for line in f:
            hex_str = line.strip()
            numbers.append(int(hex_str, 16))
    
    print("Sequence Analysis:")
    print("-----------------")
    
    # Analyze differences
    print("\nDifferences between consecutive numbers:")
    diffs = []
    for i in range(1, len(numbers)):
        diff = numbers[i] - numbers[i-1]
        diffs.append(diff)
        if i < 5:  # Print first few differences
            print(f"{i}: {diff} (hex: {hex(diff)})")
    
    # Analyze ratios
    print("\nRatios between consecutive numbers:")
    ratios = []
    for i in range(1, len(numbers)):
        ratio = numbers[i] / numbers[i-1] if numbers[i-1] != 0 else float('inf')
        ratios.append(ratio)
        if i < 5:  # Print first few ratios
            print(f"{i}: {ratio:.4f}")
    
    # Look for patterns in differences
    print("\nPattern Analysis:")
    # Check if differences follow geometric progression
    if len(diffs) >= 2:
        ratio = diffs[1] / diffs[0] if diffs[0] != 0 else float('inf')
        is_geometric = True
        for i in range(2, min(5, len(diffs))):
            if diffs[i] / diffs[i-1] != ratio:
                is_geometric = False
                break
        if is_geometric:
            print(f"Differences appear to follow geometric progression with ratio {ratio:.4f}")
    
    # Predict next value based on patterns
    if len(numbers) >= 2:
        last = numbers[-1]
        diff_prediction = last + diffs[-1]
        ratio_prediction = int(last * (ratios[-1]))
        
        print("\nPredictions for next value:")
        print(f"Based on last difference: {hex(diff_prediction)}")
        print(f"Based on last ratio: {hex(ratio_prediction)}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <hex_file>")
        sys.exit(1)
    analyze_hex_sequence(sys.argv[1]) 