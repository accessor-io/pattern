def analyze_growth():
    with open('data/32bHex.txt', 'r') as f:
        sequence = [int(line.strip(), 16) for line in f]
    
    # Look at last few positions and their growth
    last_positions = sequence[-5:]
    ratios = [last_positions[i+1]/last_positions[i] for i in range(len(last_positions)-1)]
    
    print("Last 5 values:")
    for i, val in enumerate(last_positions):
        print(f"Position {len(sequence)-5+i}: {hex(val)}")
        print(f"Binary length: {len(bin(val)[2:])}")
    
    print("\nGrowth ratios between last positions:")
    for i, ratio in enumerate(ratios):
        print(f"Ratio {i}: {ratio}")
    
    # Predict next ratios using the decay pattern
    ratio_diffs = [ratios[i+1] - ratios[i] for i in range(len(ratios)-1)]
    avg_diff = sum(ratio_diffs) / len(ratio_diffs)
    next_ratio = ratios[-1] + avg_diff
    
    # Predict positions 66 and 67
    pos_66_val = int(last_positions[-1] * next_ratio)
    pos_67_val = int(pos_66_val * (next_ratio + avg_diff))
    
    print("\nPredicted values:")
    print(f"Position 66: {hex(pos_66_val)}")
    print(f"Binary length 66: {len(bin(pos_66_val)[2:])}")
    print(f"Position 67: {hex(pos_67_val)}")
    print(f"Binary length 67: {len(bin(pos_67_val)[2:])}")

if __name__ == "__main__":
    analyze_growth() 