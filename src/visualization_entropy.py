import matplotlib.pyplot as plt
import numpy as np
from bit_pattern_sequence import analyze_byte_sequence
import seaborn as sns
import math

def visualize_entropy_gradient(hex_strings, analysis=None):
    """Create visualizations for entropy gradient analysis."""
    # Get sequence analysis results if not provided
    if analysis is None:
        analysis = analyze_byte_sequence(hex_strings)
    
    # Extract entropy values for each position
    positions = range(32)
    entropy_values = [analysis['positions'][pos]['entropy'] for pos in positions]
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Plot entropy values
    plt.plot(positions, entropy_values, 'b-', label='Entropy')
    plt.fill_between(positions, entropy_values, alpha=0.2)
    
    # Add gradient arrows for significant changes
    gradients = analysis['entropy_gradients']
    significant_changes = [(pos, grad) for pos, grad in gradients if abs(grad) > 0.5]
    for pos, grad in significant_changes:
        plt.arrow(pos-1, entropy_values[pos-1], 0.5, grad/2, 
                 head_width=0.2, head_length=0.1, fc='r', ec='r', alpha=0.5)
    
    # Customize the plot
    plt.title('Byte Position Entropy Gradient Analysis')
    plt.xlabel('Byte Position')
    plt.ylabel('Entropy (bits)')
    plt.grid(True, alpha=0.3)
    
    # Add region labels
    plt.axvspan(0, 22, alpha=0.2, color='g', label='Deterministic')
    plt.axvspan(23, 26, alpha=0.2, color='y', label='Mixed')
    plt.axvspan(27, 31, alpha=0.2, color='r', label='High Randomness')
    
    plt.legend()
    
    # Save the plot
    plt.savefig('output/entropy_gradient.png')
    plt.close()

def visualize_transition_heatmap(hex_strings, analysis=None):
    """Create a heatmap of byte-to-byte transitions."""
    # Get sequence analysis results if not provided
    if analysis is None:
        analysis = analyze_byte_sequence(hex_strings)
    
    # Create transition matrix
    matrix_size = 256  # For all possible byte values
    transition_matrix = np.zeros((matrix_size, matrix_size))
    
    # Fill transition matrix
    for pos in range(31):  # Up to second-to-last position
        transitions = analysis['positions'][pos]['transitions']
        for transition, count in transitions.items():
            from_byte, to_byte = map(lambda x: int(x, 16), transition.split('->'))
            transition_matrix[from_byte][to_byte] = count
    
    # Create heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(transition_matrix, cmap='YlOrRd', 
                xticklabels=32, yticklabels=32,  # Show every 32nd label
                cbar_kws={'label': 'Transition Count'})
    
    plt.title('Byte-to-Byte Transition Heatmap')
    plt.xlabel('To Byte (hex)')
    plt.ylabel('From Byte (hex)')
    
    # Save the plot
    plt.savefig('output/transition_heatmap.png')
    plt.close()

def visualize_pattern_distribution(hex_strings, analysis=None):
    """Create a visualization of pattern distribution across positions."""
    # Get sequence analysis results if not provided
    if analysis is None:
        analysis = analyze_byte_sequence(hex_strings)
    
    # Extract pattern counts for each position
    positions = range(32)
    pattern_counts = []
    pattern_types = set()
    
    for pos in positions:
        counts = {}
        for value, count in analysis['positions'][pos]['most_common']:
            pattern = f"{value:02x}"
            counts[pattern] = count
            pattern_types.add(pattern)
        pattern_counts.append(counts)
    
    # Create stacked bar plot
    plt.figure(figsize=(15, 8))
    bottom = np.zeros(32)
    
    # Sort patterns by frequency
    pattern_types = sorted(list(pattern_types))
    colors = plt.cm.tab20(np.linspace(0, 1, len(pattern_types)))
    
    for i, pattern in enumerate(pattern_types):
        values = [counts.get(pattern, 0) for counts in pattern_counts]
        plt.bar(positions, values, bottom=bottom, label=f'0x{pattern}',
                color=colors[i], alpha=0.7)
        bottom += values
    
    plt.title('Pattern Distribution Across Byte Positions')
    plt.xlabel('Byte Position')
    plt.ylabel('Count')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Save the plot
    plt.savefig('output/pattern_distribution.png', bbox_inches='tight')
    plt.close()

def visualize_entropy_correlation(hex_strings, analysis=None):
    """Create a visualization of entropy correlation between positions."""
    # Get sequence analysis results if not provided
    if analysis is None:
        analysis = analyze_byte_sequence(hex_strings)
    
    # Create correlation matrix
    positions = range(32)
    correlation_matrix = np.zeros((32, 32))
    
    # Calculate correlations
    for i in positions:
        for j in positions:
            # Get value distributions
            values_i = analysis['positions'][i]['values']
            values_j = analysis['positions'][j]['values']
            
            # Calculate correlation
            common_values = set(values_i.keys()) & set(values_j.keys())
            if common_values:
                correlation = sum(values_i[v] * values_j[v] for v in common_values)
                correlation /= math.sqrt(sum(c*c for c in values_i.values()) * 
                                      sum(c*c for c in values_j.values()))
                correlation_matrix[i][j] = correlation
    
    # Create heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, cmap='coolwarm', center=0,
                xticklabels=positions, yticklabels=positions,
                cbar_kws={'label': 'Correlation'})
    
    plt.title('Entropy Correlation Between Byte Positions')
    plt.xlabel('Byte Position')
    plt.ylabel('Byte Position')
    
    # Save the plot
    plt.savefig('output/entropy_correlation.png')
    plt.close()

def visualize_byte_value_distribution(hex_strings, analysis=None):
    """Create a violin plot of byte value distributions across positions."""
    if analysis is None:
        analysis = analyze_byte_sequence(hex_strings)
    
    # Prepare data for violin plot
    positions = range(32)
    data = []
    for pos in positions:
        pos_values = []
        for value, count in analysis['positions'][pos]['values'].items():
            try:
                byte_val = int(str(value), 16)
                pos_values.extend([byte_val] * int(count))
            except (ValueError, TypeError):
                continue
        data.append(pos_values)
    
    # Create violin plot
    plt.figure(figsize=(15, 8))
    parts = plt.violinplot(data, positions=positions, showmeans=True)
    
    # Customize plot
    plt.title('Byte Value Distribution Across Positions')
    plt.xlabel('Byte Position')
    plt.ylabel('Byte Value')
    plt.grid(True, alpha=0.3)
    
    # Color coding
    for pc in parts['bodies']:
        pc.set_facecolor('#3498db')
        pc.set_edgecolor('black')
        pc.set_alpha(0.6)
    
    # Save plot
    plt.savefig('output/byte_distribution.png')
    plt.close()

def visualize_pattern_evolution(hex_strings, analysis=None):
    """Create a visualization of how patterns evolve across positions."""
    if analysis is None:
        analysis = analyze_byte_sequence(hex_strings)
    
    # Prepare data
    positions = range(31)  # Up to second-to-last position
    evolution_data = []
    
    for pos in positions:
        transitions = analysis['positions'][pos]['transitions']
        top_transitions = sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:5]
        evolution_data.append(top_transitions)
    
    # Create plot
    plt.figure(figsize=(15, 8))
    
    # Plot transitions
    for i, pos_transitions in enumerate(evolution_data):
        y_offset = 0
        for transition, count in pos_transitions:
            from_byte, to_byte = transition.split('->')
            plt.plot([i, i+1], [int(from_byte, 16), int(to_byte, 16)], 
                    alpha=count/max(t[1] for t in pos_transitions),
                    color='#2ecc71', linewidth=1)
    
    plt.title('Pattern Evolution Across Positions')
    plt.xlabel('Position Transition')
    plt.ylabel('Byte Value')
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.savefig('output/pattern_evolution.png')
    plt.close()

def visualize_pattern_landscape(hex_strings, analysis=None):
    """Create a 2D heatmap visualization of the pattern landscape."""
    if analysis is None:
        analysis = analyze_byte_sequence(hex_strings)
    
    # Prepare data for heatmap
    positions = range(32)
    byte_values = range(0, 256, 4)  # Sample every 4th byte value for clarity
    Z = np.zeros((len(byte_values), len(positions)))
    
    for i, byte_val in enumerate(byte_values):
        for j, pos in enumerate(positions):
            byte_hex = f"{byte_val:02x}"
            Z[i, j] = analysis['positions'][pos]['values'].get(byte_hex, 0)
    
    # Create enhanced heatmap
    plt.figure(figsize=(15, 10))
    sns.heatmap(Z, cmap='viridis', 
                xticklabels=[f"{pos}" for pos in positions],
                yticklabels=[f"{val:02x}" for val in byte_values],
                cbar_kws={'label': 'Frequency'})
    
    plt.title('Pattern Landscape Heatmap')
    plt.xlabel('Byte Position')
    plt.ylabel('Byte Value (hex)')
    
    # Save plot
    plt.savefig('output/pattern_landscape.png')
    plt.close()

def visualize_circular_pattern(hex_strings, analysis=None):
    """Create an enhanced circular visualization of byte patterns."""
    if analysis is None:
        analysis = analyze_byte_sequence(hex_strings)
    
    # Prepare data
    positions = range(32)
    angles = np.linspace(0, 2*np.pi, 32, endpoint=False)
    
    # Create figure with polar projection
    plt.figure(figsize=(15, 15))
    
    # Create two subplots: main circular plot and mini entropy plot
    gs = plt.GridSpec(3, 3)
    ax_main = plt.subplot(gs[0:3, 0:2], projection='polar')
    ax_entropy = plt.subplot(gs[0:1, 2])
    
    # Plot each position's most common values in main plot
    max_count = 0
    for pos in positions:
        most_common = analysis['positions'][pos]['most_common'][:5]  # Top 5 values
        for i, (value, count) in enumerate(most_common):
            radius = count / len(hex_strings)  # Normalize by total strings
            max_count = max(max_count, radius)
            angle = angles[pos]
            
            # Use different colors for different value ranges
            try:
                byte_val = int(str(value), 16)
                if byte_val == 0:
                    color = '#e74c3c'  # Red for zero
                elif byte_val < 64:
                    color = '#3498db'  # Blue for low values
                elif byte_val < 128:
                    color = '#2ecc71'  # Green for medium values
                elif byte_val < 192:
                    color = '#f1c40f'  # Yellow for medium-high values
                else:
                    color = '#9b59b6'  # Purple for high values
            except (ValueError, TypeError):
                color = '#95a5a6'  # Gray for invalid values
            
            # Plot point with size proportional to frequency
            ax_main.scatter(angle, radius, 
                          s=300 * (radius/max_count), 
                          alpha=0.7,
                          color=color,
                          label=f'0x{value}' if pos == 0 else "")
            
            # Add connecting lines between consecutive positions
            if pos < 31:
                next_common = analysis['positions'][pos+1]['most_common'][:5]
                for next_value, next_count in next_common:
                    next_radius = next_count / len(hex_strings)
                    next_angle = angles[pos+1]
                    # Make line alpha proportional to combined frequency
                    line_alpha = min(0.3, (radius + next_radius) / 4)
                    ax_main.plot([angle, next_angle], 
                               [radius, next_radius],
                               alpha=line_alpha, 
                               color='gray',
                               linestyle=':')
    
    # Add position markers and grid
    ax_main.set_xticks(angles)
    ax_main.set_xticklabels([f"{i}" for i in range(32)])
    
    # Add concentric circles for value ranges
    circles = [0.25, 0.5, 0.75, 1.0]
    for circle in circles:
        ax_main.plot(angles, [circle]*len(angles), 'gray', alpha=0.2)
        ax_main.text(0, circle, f"{circle*100:.0f}%", 
                    ha='right', va='bottom', alpha=0.5)
    
    # Customize main plot
    ax_main.set_title('Circular Pattern Visualization\n(Top 5 values per position)', 
                     pad=20)
    ax_main.grid(True, alpha=0.2)
    
    # Add mini entropy plot
    entropy_values = [analysis['positions'][pos]['entropy'] for pos in positions]
    ax_entropy.plot(entropy_values, positions, 'r-', alpha=0.7)
    ax_entropy.fill_betweenx(positions, 0, entropy_values, alpha=0.2, color='red')
    ax_entropy.set_ylim(0, 31)
    ax_entropy.set_title('Entropy\nProfile')
    ax_entropy.grid(True, alpha=0.2)
    
    # Add legend for value ranges
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', 
                  markerfacecolor=c, label=l, markersize=10)
        for c, l in [
            ('#e74c3c', '0x00'),
            ('#3498db', '0x00-0x3F'),
            ('#2ecc71', '0x40-0x7F'),
            ('#f1c40f', '0x80-0xBF'),
            ('#9b59b6', '0xC0-0xFF'),
            ('#95a5a6', 'Invalid')
        ]
    ]
    ax_entropy.legend(handles=legend_elements, 
                     title='Byte Ranges',
                     bbox_to_anchor=(0, -0.2),
                     loc='upper left')
    
    plt.tight_layout()
    
    # Save plot with extra margin for legend
    plt.savefig('output/circular_pattern.png', 
                bbox_inches='tight', 
                dpi=300)
    plt.close()

def visualize_address_patterns(hex_strings, analysis=None):
    """Create visualizations showing relationships between byte positions and potential address interpretations."""
    if analysis is None:
        analysis = analyze_byte_sequence(hex_strings)
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(20, 15))
    gs = plt.GridSpec(3, 2)
    
    # 1. Address Alignment Plot (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    positions = range(32)
    alignments = [0, 2, 4, 8]  # Common address alignments
    
    for alignment in alignments:
        # Calculate potential address positions
        addr_positions = range(alignment, 32, alignment + 1) if alignment > 0 else positions
        values = [analysis['positions'][pos]['entropy'] for pos in addr_positions]
        ax1.plot(list(addr_positions), values, 
                marker='o', label=f'{alignment}-byte aligned',
                alpha=0.7, linewidth=2)
    
    ax1.set_title('Entropy by Address Alignment')
    ax1.set_xlabel('Byte Position')
    ax1.set_ylabel('Entropy')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Word-size Pattern Distribution (top right)
    ax2 = fig.add_subplot(gs[0, 1])
    word_sizes = [2, 4, 8]  # 16-bit, 32-bit, 64-bit
    x_positions = np.arange(len(word_sizes))
    
    for pos in range(0, 32, 8):  # Sample every 8 bytes
        patterns = []
        for size in word_sizes:
            if pos + size <= 32:
                # Count unique patterns for this word size
                pattern_count = len(set(
                    hex_string[pos*2:(pos+size)*2] 
                    for hex_string in hex_strings
                ))
                patterns.append(pattern_count)
            else:
                patterns.append(0)
        
        ax2.plot(x_positions, patterns, 
                marker='s', label=f'Offset {pos}',
                alpha=0.7, linewidth=2)
    
    ax2.set_title('Unique Patterns by Word Size')
    ax2.set_xticks(x_positions)
    ax2.set_xticklabels([f'{size*8}-bit' for size in word_sizes])
    ax2.set_ylabel('Unique Pattern Count')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. Offset Correlation Matrix (bottom left)
    ax3 = fig.add_subplot(gs[1:, 0])
    offsets = [0, 2, 4, 8, 16]
    correlation_matrix = np.zeros((len(offsets), 32))
    
    for i, offset in enumerate(offsets):
        for pos in range(32):
            if pos + offset < 32:
                # Calculate correlation between position and offset
                values_pos = analysis['positions'][pos]['values']
                values_offset = analysis['positions'][pos + offset]['values']
                
                # Get common values
                common_values = set(values_pos.keys()) & set(values_offset.keys())
                if common_values:
                    correlation = sum(values_pos[v] * values_offset[v] for v in common_values)
                    correlation /= math.sqrt(sum(c*c for c in values_pos.values()) * 
                                          sum(c*c for c in values_offset.values()))
                    correlation_matrix[i, pos] = correlation
    
    sns.heatmap(correlation_matrix, 
                xticklabels=range(32),
                yticklabels=[f'+{offset}' for offset in offsets],
                cmap='coolwarm', center=0,
                ax=ax3)
    ax3.set_title('Byte Position Offset Correlations')
    ax3.set_xlabel('Base Position')
    ax3.set_ylabel('Offset')
    
    # 4. Address Space Distribution (bottom right)
    ax4 = fig.add_subplot(gs[1:, 1])
    addr_ranges = [(0x0, 0xFF), (0x100, 0xFFFF), (0x10000, 0xFFFFFFFF)]
    range_labels = ['8-bit', '16-bit', '32-bit']
    
    for pos in range(0, 32, 4):  # Sample every 4 bytes
        if pos + 4 <= 32:
            values = []
            for start, end in addr_ranges:
                # Count values in each address range
                count = sum(
                    1 for hex_string in hex_strings
                    if start <= int(hex_string[pos*2:(pos+4)*2], 16) <= end
                )
                values.append(count)
            
            ax4.plot(range_labels, values,
                    marker='o', label=f'Pos {pos}-{pos+3}',
                    alpha=0.7, linewidth=2)
    
    ax4.set_title('Address Space Distribution')
    ax4.set_xlabel('Address Range')
    ax4.set_ylabel('Count')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('output/address_patterns.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_all_visualizations(hex_strings):
    """Create all visualizations."""
    # Get analysis results once to reuse
    analysis = analyze_byte_sequence(hex_strings)
    
    # Create each visualization
    visualize_entropy_gradient(hex_strings, analysis)
    visualize_transition_heatmap(hex_strings, analysis)
    visualize_pattern_distribution(hex_strings, analysis)
    visualize_entropy_correlation(hex_strings, analysis)
    visualize_byte_value_distribution(hex_strings, analysis)
    visualize_pattern_evolution(hex_strings, analysis)
    visualize_pattern_landscape(hex_strings, analysis)
    visualize_circular_pattern(hex_strings, analysis)
    visualize_address_patterns(hex_strings, analysis)

if __name__ == "__main__":
    # Read hex strings
    hex_strings = []
    with open('../data/32bHex.txt', 'r') as f:
        for line in f:
            hex_string = line.strip()
            if len(hex_string) == 64:  # 32 bytes = 64 hex chars
                hex_strings.append(hex_string)
    
    # Create all visualizations
    create_all_visualizations(hex_strings)
    print("Visualizations saved to output directory:") 
    print("- entropy_gradient.png")
    print("- transition_heatmap.png")
    print("- pattern_distribution.png")
    print("- entropy_correlation.png")
    print("- byte_distribution.png")
    print("- pattern_evolution.png")
    print("- pattern_landscape.png")
    print("- circular_pattern.png")
    print("- address_patterns.png")