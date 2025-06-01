#!/usr/bin/env python3
"""
Analyze only the KNOWN (verified) Bitcoin puzzle keys.
Ignores all GENERATED predictions for unsolved positions.
"""

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def load_known_keys():
    """Load only KNOWN keys from verified_bitcoin_sequence.txt"""
    known_keys = {}
    try:
        with open('verified_bitcoin_sequence.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or 'GENERATED' in line:
                    continue  # Skip generated predictions
                if 'KNOWN' in line:
                    parts = line.split('.')
                    if len(parts) >= 2:
                        pos = int(parts[0])
                        hex_part = parts[1].strip().split(' - ')[0].strip()
                        known_keys[pos] = int(hex_part, 16)
    except Exception as e:
        print(f"Error loading keys: {e}")
        return {}
    
    return known_keys

def analyze_known_transitions():
    """Analyze transitions between consecutive KNOWN keys"""
    known_keys = load_known_keys()
    
    print("=== ANALYZING KNOWN BITCOIN PUZZLE KEYS ===")
    print(f"Total KNOWN keys: {len(known_keys)}")
    print()
    
    # Show all known positions
    positions = sorted(known_keys.keys())
    print("Known positions:")
    for i in range(0, len(positions), 10):
        batch = positions[i:i+10]
        print("  " + ", ".join(str(p) for p in batch))
    print()
    
    # Analyze transitions between consecutive known keys
    print("=== TRANSITIONS BETWEEN CONSECUTIVE KNOWN KEYS ===")
    print()
    
    transitions = []
    for i in range(len(positions) - 1):
        pos1 = positions[i]
        pos2 = positions[i + 1]
        
        if pos2 == pos1 + 1:  # Consecutive positions
            key1 = known_keys[pos1]
            key2 = known_keys[pos2]
            diff = key2 - key1
            transitions.append((pos1, pos2, diff))
    
    # Display transitions
    print("Consecutive position transitions (showing first 30):")
    print("From -> To   : Constant (difference)")
    print("-" * 50)
    for pos1, pos2, diff in transitions[:30]:
        print(f"{pos1:4} -> {pos2:<4} : {diff:,}")
    
    # Analyze gaps (non-consecutive positions)
    print("\n=== GAPS IN KNOWN POSITIONS ===")
    gaps = []
    for i in range(len(positions) - 1):
        pos1 = positions[i]
        pos2 = positions[i + 1]
        gap_size = pos2 - pos1 - 1
        if gap_size > 0:
            gaps.append((pos1, pos2, gap_size))
    
    print("Gaps between known positions:")
    for pos1, pos2, gap_size in gaps[:20]:  # Show first 20 gaps
        print(f"  {pos1} to {pos2}: {gap_size} unknown positions")
    
    # Analyze growth patterns
    print("\n=== GROWTH PATTERN ANALYSIS ===")
    if len(transitions) > 1:
        print("\nGrowth factors between consecutive transitions:")
        for i in range(1, min(len(transitions), 20)):
            prev_diff = transitions[i-1][2]
            curr_diff = transitions[i][2]
            if prev_diff > 0:
                growth = curr_diff / prev_diff
                print(f"  Position {transitions[i-1][0]}->{transitions[i-1][1]} to {transitions[i][0]}->{transitions[i][1]}: {growth:.4f}x")
    
    # Focus on positions ending in 0 or 5
    print("\n=== ANALYSIS OF POSITIONS ENDING IN 0 OR 5 ===")
    five_zero_positions = [p for p in positions if p % 5 == 0 and p >= 70]
    
    if len(five_zero_positions) > 1:
        print("\nPositions: " + ", ".join(str(p) for p in five_zero_positions))
        print("\nDifferences between consecutive 5/0 positions:")
        
        for i in range(1, len(five_zero_positions)):
            pos1 = five_zero_positions[i-1]
            pos2 = five_zero_positions[i]
            key1 = known_keys[pos1]
            key2 = known_keys[pos2]
            diff = key2 - key1
            print(f"  {pos1} -> {pos2}: {diff:,}")
        
        # Check growth pattern
        print("\nGrowth factors between 5/0 positions:")
        prev_diff = None
        for i in range(1, len(five_zero_positions)):
            pos1 = five_zero_positions[i-1]
            pos2 = five_zero_positions[i]
            key1 = known_keys[pos1]
            key2 = known_keys[pos2]
            diff = key2 - key1
            
            if prev_diff and prev_diff > 0:
                growth = diff / prev_diff
                print(f"  {five_zero_positions[i-2]} -> {pos1} to {pos1} -> {pos2}: {growth:.4f}x")
            prev_diff = diff
    
    # Export clean known keys
    print("\n=== EXPORTING CLEAN KNOWN KEYS ===")
    with open('known_keys_only.txt', 'w') as f:
        f.write("# Bitcoin Puzzle - KNOWN Keys Only\n")
        f.write("# Position. Hex_Key\n")
        for pos in sorted(known_keys.keys()):
            f.write(f"{pos}. 0x{known_keys[pos]:064x}\n")
    
    print("Exported clean known keys to: known_keys_only.txt")
    
    # Summary statistics
    print("\n=== SUMMARY ===")
    print(f"Total known keys: {len(known_keys)}")
    print(f"Consecutive transitions: {len(transitions)}")
    print(f"Gaps in sequence: {len(gaps)}")
    print(f"Largest gap: {max(g[2] for g in gaps) if gaps else 0} positions")
    
    return known_keys

if __name__ == "__main__":
    analyze_known_transitions() 