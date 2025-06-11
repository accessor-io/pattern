def analyze_special_format():
    key = "BHJKKXGOMMXCYTV"
    
    print("Special Format Analysis")
    print("=" * 50)
    
    # Break into 3-character groups
    groups = [key[i:i+3] for i in range(0, len(key), 3)]
    print("\nGroups:", ' '.join(groups))
    
    # Analyze each group's structure
    for i, group in enumerate(groups):
        print(f"\nGroup {i+1}: {group}")
        
        # Convert to ASCII values
        ascii_vals = [ord(c) for c in group]
        print(f"ASCII values: {ascii_vals}")
        
        # Convert to binary
        binary = ''.join(format(ord(c), '08b') for c in group)
        print(f"Binary: {binary}")
        
        # Show position meaning
        if len(group) == 3:
            print(f"Position 1 ({group[0]}): {ord(group[0]) - ord('A')} (Base-26)")
            print(f"Position 2 ({group[1]}): {ord(group[1]) - ord('A')} (Base-26)")
            print(f"Position 3 ({group[2]}): {ord(group[2]) - ord('A')} (Base-26)")
    
    # Analyze transitions between groups
    print("\nTransitions Between Groups:")
    for i in range(len(groups)-1):
        current = groups[i]
        next_group = groups[i+1]
        print(f"\n{current} -> {next_group}")
        
        # Show how values change
        for j in range(min(len(current), len(next_group))):
            diff = ord(next_group[j]) - ord(current[j])
            print(f"Position {j+1}: {current[j]} -> {next_group[j]} (Shift: {diff:+d})")
    
    # Look for special markers
    print("\nSpecial Markers:")
    
    # 1. Group markers (first char of each group)
    markers = [g[0] for g in groups]
    print(f"Group markers: {markers}")
    
    # 2. Operation codes (second char of each group)
    opcodes = [g[1] for g in groups if len(g) > 1]
    print(f"Operation codes: {opcodes}")
    
    # 3. Checksum chars (third char of each group)
    checksums = [g[2] for g in groups if len(g) > 2]
    print(f"Checksum chars: {checksums}")
    
    # Analyze the encoding pattern
    print("\nEncoding Pattern Analysis:")
    
    # Convert to base values (0-25)
    base_values = [[ord(c) - ord('A') for c in group] for group in groups]
    print("\nBase-26 values per group:")
    for i, values in enumerate(base_values):
        print(f"Group {i+1}: {values}")
    
    # Look for mathematical relationships
    print("\nMathematical Relationships:")
    for i, group_vals in enumerate(base_values):
        if len(group_vals) == 3:
            # Check for common relationships
            if group_vals[0] + group_vals[1] == group_vals[2]:
                print(f"Group {i+1}: First + Second = Third")
            elif group_vals[0] * group_vals[1] % 26 == group_vals[2]:
                print(f"Group {i+1}: (First * Second) mod 26 = Third")
            elif (group_vals[0] + group_vals[1] + group_vals[2]) % 26 == 0:
                print(f"Group {i+1}: Sum mod 26 = 0")

def main():
    analyze_special_format()

if __name__ == "__main__":
    main() 