#!/usr/bin/python3

from collections import defaultdict, Counter
import math

def analyze_byte_sequence(hex_strings):
    position_stats = {}
    total_strings = len(hex_strings)
    
    # Initialize stats for each position
    for pos in range(32):
        position_stats[pos] = {
            'values': {},
            'transitions': {},
            'entropy': 0.0
        }
    
    # Analyze each hex string
    for hex_string in hex_strings:
        bytes_list = [int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2)]
        
        # Count values at each position
        for pos, byte in enumerate(bytes_list):
            if byte not in position_stats[pos]['values']:
                position_stats[pos]['values'][byte] = 0
            position_stats[pos]['values'][byte] += 1
            
            # Track transitions to next byte
            if pos < len(bytes_list) - 1:
                next_byte = bytes_list[pos + 1]
                transition = f"{byte:02x}->{next_byte:02x}"
                if transition not in position_stats[pos]['transitions']:
                    position_stats[pos]['transitions'][transition] = 0
                position_stats[pos]['transitions'][transition] += 1
    
    # Calculate entropy and sort values
    for pos in position_stats:
        # Calculate entropy
        entropy = 0
        for count in position_stats[pos]['values'].values():
            prob = count / total_strings
            entropy -= prob * math.log2(prob)
        position_stats[pos]['entropy'] = entropy
        
        # Sort values by frequency
        position_stats[pos]['most_common'] = sorted(
            [(val, count) for val, count in position_stats[pos]['values'].items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Keep top 5
    
    # Add pattern clustering
    clusters = {
        'deterministic': [],
        'semi_random': [],
        'highly_random': []
    }
    
    for pos, stats in position_stats.items():
        entropy = stats['entropy']
        if entropy < 0.1:
            clusters['deterministic'].append(pos)
        elif entropy < 3.0:
            clusters['semi_random'].append(pos)
        else:
            clusters['highly_random'].append(pos)
    
    # Add entropy gradient analysis
    gradients = []
    positions = sorted(position_stats.keys())
    for i in range(1, len(positions)):
        prev_entropy = position_stats[positions[i-1]]['entropy']
        curr_entropy = position_stats[positions[i]]['entropy']
        gradient = curr_entropy - prev_entropy
        gradients.append((positions[i], gradient))
    
    # Prepare results
    results = {
        'positions': position_stats,
        'pattern_clusters': clusters,
        'entropy_gradients': gradients,
        'total_strings': total_strings
    }
    
    return results

def format_sequence_analysis(analysis):
    output = []
    output.append("Sequence Pattern Analysis:")
    output.append("----------------------------------------")
    
    # Format pattern clusters
    clusters = analysis['pattern_clusters']
    output.append(f"* Positions {clusters['deterministic']} show deterministic behavior")
    if clusters['semi_random']:
        output.append(f"* Positions {clusters['semi_random']} show mixed behavior")
    output.append(f"* Positions {clusters['highly_random']} show high randomness")
    
    # Format entropy gradients
    gradients = analysis['entropy_gradients']
    significant_changes = [(pos, grad) for pos, grad in gradients if abs(grad) > 0.5]
    if significant_changes:
        output.append("\nSignificant Entropy Changes:")
        for pos, grad in significant_changes:
            direction = "increase" if grad > 0 else "decrease"
            output.append(f"* Position {pos}: {abs(grad):.2f} bits {direction}")
    
    # Position-by-position analysis
    for pos in range(32):
        stats = analysis['positions'][pos]
        output.append(f"\nPosition {pos:2d}:")
        output.append("-" * 40)
        
        # Most common values
        output.append("Most common values:")
        for value, count in stats['most_common']:
            percentage = (count / analysis['total_strings']) * 100
            output.append(f"  0x{value:02x}: {count} times ({percentage:.2f}%)")
        
        output.append(f"\nPosition entropy: {stats['entropy']:.2f} bits")
        
        # Most common transitions
        if stats['transitions']:
            output.append("\nMost common transitions to next byte:")
            top_transitions = sorted(
                [(t, c) for t, c in stats['transitions'].items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Show top 5
            for transition, count in top_transitions:
                percentage = (count / analysis['total_strings']) * 100
                output.append(f"  {transition}: {percentage:.2f}%")
    
    return "\n".join(output) 