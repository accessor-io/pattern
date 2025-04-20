def analyze_exact_ratios():
    # Read all numbers
    numbers = []
    with open('organized/data/32bHex.txt') as f:
        for line in f:
            hex_str = line.strip()
            numbers.append(int(hex_str, 16))
    
    # Calculate differences
    diffs = []
    for i in range(1, len(numbers)):
        diff = numbers[i] - numbers[i-1]
        diffs.append(diff)
    
    print("Analyzing exact ratios between consecutive differences:")
    print("Position: ratio (prev_diff -> curr_diff)")
    print("-" * 50)
    
    # Analyze ratios with full precision
    for i in range(1, len(diffs)):
        ratio = diffs[i] / diffs[i-1] if diffs[i-1] != 0 else float('inf')
        print(f"Pos {i:2d}: {ratio:.10f} ({hex(diffs[i-1])} -> {hex(diffs[i])})")
        
        # Look for pattern changes
        if i > 1:
            prev_ratio = diffs[i-1] / diffs[i-2] if diffs[i-2] != 0 else float('inf')
            ratio_change = abs(ratio - prev_ratio)
            if ratio_change > 0.5:  # Significant change in ratio
                print(f"*** Notable change in ratio at position {i} ***")
    
    # Also show the actual sequence values around any identified pattern changes
    print("\nSequence values around notable positions:")
    for i in range(len(numbers)):
        if i > 0 and i < len(diffs) and abs(diffs[i]/diffs[i-1] - diffs[i-1]/diffs[i-2]) > 0.5:
            print(f"\nAround position {i}:")
            start = max(0, i-2)
            end = min(len(numbers), i+3)
            for j in range(start, end):
                print(f"Pos {j:2d}: {hex(numbers[j])}")

if __name__ == '__main__':
    analyze_exact_ratios() 