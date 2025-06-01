#!/usr/bin/env python3

def load_verified_sequence():
    """Load the verified Bitcoin sequence from file"""
    keys = {}
    try:
        with open('verified_bitcoin_sequence.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or not line[0].isdigit():
                    continue
                parts = line.split('.', 1)
                if len(parts) != 2:
                    continue
                pos = int(parts[0])
                hex_and_status = parts[1].strip()
                if ' - ' in hex_and_status:
                    hex_key = hex_and_status.split(' - ')[0].strip()
                else:
                    hex_key = hex_and_status.strip()
                keys[pos] = int(hex_key, 16)
        return keys
    except Exception as e:
        print(f"Error loading sequence: {e}")
        return {}

def analyze_transitions(keys, max_pos=160):
    """Analyze transitions between consecutive keys to find patterns"""
    print("=== BITCOIN PUZZLE SOLUTION FORMULAS (ALL POSITIONS) ===\n")
    
    transitions = []
    
    for pos in range(1, min(max_pos + 1, max(keys.keys()))):
        if pos in keys and (pos + 1) in keys:
            k_curr = keys[pos]
            k_next = keys[pos + 1]
            diff = k_next - k_curr
            
            # Calculate various pattern types
            patterns = []
            
            # Simple addition
            if diff > 0:
                patterns.append(f"k + {diff}")
            elif diff < 0:
                patterns.append(f"k - {abs(diff)}")
            
            # Multiplication patterns
            if k_curr != 0:
                if k_next == k_curr * 2:
                    patterns.append("k * 2")
                elif k_next == k_curr * 3:
                    patterns.append("k * 3")
                elif k_next == k_curr * 2 + 1:
                    patterns.append("k * 2 + 1")
                elif k_next == k_curr * 2 - 1:
                    patterns.append("k * 2 - 1")
                elif k_next == k_curr * 3 + 1:
                    patterns.append("k * 3 + 1")
                elif k_next == k_curr * 3 - 1:
                    patterns.append("k * 3 - 1")
                
                # Check for k * m + c patterns
                for mult in range(2, 10):
                    for add in range(-20, 21):
                        if k_next == k_curr * mult + add:
                            if add > 0:
                                patterns.append(f"k * {mult} + {add}")
                            elif add < 0:
                                patterns.append(f"k * {mult} - {abs(add)}")
                            else:
                                patterns.append(f"k * {mult}")
            
            # Bitshift patterns
            for shift in range(1, 16):
                if k_next == (k_curr << shift):
                    patterns.append(f"k << {shift}")
                elif k_next == (k_curr >> shift):
                    patterns.append(f"k >> {shift}")
                elif k_next == ((k_curr << shift) + 1):
                    patterns.append(f"(k << {shift}) + 1")
                elif k_next == ((k_curr << shift) - 1):
                    patterns.append(f"(k << {shift}) - 1")
            
            # Position-based patterns
            if k_next == k_curr + pos:
                patterns.append(f"k + pos({pos})")
            if k_next == k_curr * pos:
                patterns.append(f"k * pos({pos})")
            
            # Remove duplicates and select best pattern
            patterns = list(dict.fromkeys(patterns))  # Remove duplicates while preserving order
            
            if patterns:
                primary = patterns[0]
                alternatives = patterns[1:3] if len(patterns) > 1 else []
            else:
                primary = f"k + {diff}" if diff != 0 else "k"
                alternatives = []
            
            transitions.append({
                'pos': pos + 1,
                'from_key': k_curr,
                'to_key': k_next,
                'diff': diff,
                'primary': primary,
                'alternatives': alternatives
            })
    
    # Display results
    for t in transitions:
        print(f"Position {t['pos']:3d}: {t['primary']:<35} (diff: {t['diff']:,})")
        if t['alternatives']:
            for alt in t['alternatives'][:2]:  # Show max 2 alternatives
                print(f"            Alt: {alt}")
        print(f"            0x{t['from_key']:x} → 0x{t['to_key']:x}")
        print()
    
    # Pattern analysis
    print("\n=== PATTERN ANALYSIS ===")
    
    # Group by pattern type
    arithmetic_positions = []
    multiplicative_positions = []
    bitshift_positions = []
    negative_positions = []
    
    for t in transitions:
        if t['diff'] < 0:
            negative_positions.append(t['pos'])
        elif '+' in t['primary'] and '*' not in t['primary']:
            arithmetic_positions.append(t['pos'])
        elif '*' in t['primary']:
            multiplicative_positions.append(t['pos'])
        elif '<<' in t['primary'] or '>>' in t['primary']:
            bitshift_positions.append(t['pos'])
    
    print(f"Simple Addition (k + constant): {len(arithmetic_positions)} positions")
    if arithmetic_positions:
        print(f"  First 10: {arithmetic_positions[:10]}")
        if len(arithmetic_positions) > 10:
            print(f"  Last 10:  {arithmetic_positions[-10:]}")
    
    print(f"\nNegative differences (k - constant): {len(negative_positions)} positions")
    if negative_positions:
        print(f"  Positions: {negative_positions}")
    
    print(f"\nMultiplicative patterns: {len(multiplicative_positions)} positions")
    if multiplicative_positions:
        print(f"  Positions: {multiplicative_positions}")
    
    print(f"\nBitshift patterns: {len(bitshift_positions)} positions")
    if bitshift_positions:
        print(f"  Positions: {bitshift_positions}")
    
    return transitions

def main():
    keys = load_verified_sequence()
    if not keys:
        print("Failed to load verified sequence")
        return
    
    print(f"Loaded {len(keys)} keys from verified sequence")
    print(f"Range: Position {min(keys.keys())} to {max(keys.keys())}\n")
    
    transitions = analyze_transitions(keys, max_pos=160)
    
    print(f"\nAnalyzed {len(transitions)} transitions (positions 1→2 through {len(transitions)}→{len(transitions)+1})")

if __name__ == "__main__":
    main() 