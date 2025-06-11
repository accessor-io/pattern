from crypto_data import CRYPTO_MAPPINGS
import time
import itertools

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def visualize_helix_pattern(address, window_size=12):  # Larger window size
    """Visualize the sliding window pattern as a helix"""
    patterns = []
    
    # Generate sliding windows with pattern analysis
    for i in range(len(address) - window_size + 1):
        window = address[i:i+window_size]
        
        # Analyze window content
        nums = sum(1 for c in window if c.isdigit())
        letters = sum(1 for c in window if c.isalpha())
        
        # Add pattern indicators
        pattern_type = f"[{nums}n,{letters}l]"
        patterns.append((window, pattern_type))
    
    return patterns

def find_repeating_sequences(patterns):
    """Find sequences that repeat in the helix"""
    sequences = {}
    
    for i, (pattern, _) in enumerate(patterns):
        window = pattern.strip()
        if window in sequences:
            sequences[window].append(i)
        else:
            sequences[window] = [i]
    
    # Return only sequences that appear more than once
    return {k: v for k, v in sequences.items() if len(v) > 1}

def analyze_helix_transitions(patterns):
    """Analyze how patterns transition in the helix"""
    transitions = []
    
    for i in range(len(patterns)-1):
        current = patterns[i][0].strip()
        next_pattern = patterns[i+1][0].strip()
        # Find what changed between patterns
        changes = []
        if current[1:] == next_pattern[:-1]:
            changes.append("Shift")
        if sum(1 for c in current if c.isdigit()) != sum(1 for c in next_pattern if c.isdigit()):
            changes.append("Number Change")
        transitions.append((current, next_pattern, changes))
    
    return transitions

def analyze_all_addresses():
    """Analyze helix patterns in all addresses and produce a command chain"""
    all_analyses = []
    command_chain = []
    all_transitions = []
    
    for addr, cmd in CRYPTO_MAPPINGS:
        patterns = visualize_helix_pattern(addr)
        repeating = find_repeating_sequences(patterns)
        transitions = analyze_helix_transitions(patterns)
        all_analyses.append((addr, patterns, repeating, transitions))
        command_chain.append(addr)
        all_transitions.extend(transitions)
    
    return all_analyses, command_chain, all_transitions

def colorize_output_base58(text, offset=0):
    """Colorize text with a gradient effect through the Base58 alphabet, repeating the shift 5 times"""
    colored_text = ""
    num_colors = len(BASE58_ALPHABET)
    
    for _ in range(5):  # Repeat the color shift 5 times
        for i, char in enumerate(text):
            if char in BASE58_ALPHABET:
                # Calculate color based on position in the Base58 alphabet
                color_index = (BASE58_ALPHABET.index(char) + i + offset) % num_colors
                color_code = 31 + (color_index * 8 // num_colors)  # Transition from red (31) to cyan (36)
                colored_text += f"\033[{color_code}m{char}\033[0m"
            else:
                colored_text += char
        colored_text += " "  # Add space between repetitions
    return colored_text

if __name__ == "__main__":
    print("Analyzing helix patterns in addresses...")
    analyses, command_chain, all_transitions = analyze_all_addresses()
    
    # Show the command chain
    print("\nCommand Chain:")
    full_chain = ' -> '.join(command_chain)
    print(colorize_output_base58(full_chain))
    
    # Show all addresses
    for i, (addr, patterns, repeating, transitions) in enumerate(analyses):
        print(f"\n{'='*50}")
        print(f"Address {i+1}: {addr}")
        
        print("\nHelix Pattern (scroll to see animation):")
        full_pattern = ''.join(pattern for pattern, _ in patterns)
        print(colorize_output_base58(full_pattern))
        
        if repeating:
            print("\nRepeating Sequences:")
            for seq, positions in repeating.items():
                print(f"'{colorize_output_base58(seq)}' appears at positions: {positions}")
        
        print("\nPattern Transitions:")
        for j, (curr, next_pat, changes) in enumerate(transitions):  # Show all transitions
            print(f"{colorize_output_base58(curr)} -> {colorize_output_base58(next_pat)} ({', '.join(changes)})")
        
        print('='*50)
    
    # Show all pattern transitions continuously with changing designs
    print("\nAll Pattern Transitions Continuously:")
    offset = 0
    for _ in range(5):  # Loop to simulate continuous output
        for curr, next_pat, changes in all_transitions:
            print(f"{colorize_output_base58(curr, offset)} -> {colorize_output_base58(next_pat, offset)} ({', '.join(changes)})")
            offset = (offset + 1) % len(BASE58_ALPHABET)  # Change the offset to create different designs
        time.sleep(0.05)  # Sleep to achieve 20 lines per second