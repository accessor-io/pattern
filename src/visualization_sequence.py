import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def visualize_stark_witness_patterns(hex_strings):
    """Create visualizations for STARK witness patterns."""
    # Convert hex strings to integer values
    values = []
    for hex_string in hex_strings:
        chunks = [int(hex_string[i:i+8], 16) for i in range(0, len(hex_string), 8)]
        values.extend(chunks)
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(15, 10))
    
    # 1. Trace polynomial visualization
    ax1 = fig.add_subplot(221)
    x = np.arange(len(values))
    ax1.plot(x, values, 'b-', alpha=0.5, label='Values')
    ax1.set_title('Trace Polynomial Pattern')
    ax1.set_xlabel('Position')
    ax1.set_ylabel('Value')
    ax1.legend()
    
    # 2. Transition pattern heatmap
    ax2 = fig.add_subplot(222)
    transitions = np.zeros((32, 32))
    for i in range(len(values)-1):
        v1, v2 = values[i] & 0x1F, values[i+1] & 0x1F  # Take last 5 bits
        transitions[v1][v2] += 1
    im = ax2.imshow(transitions, cmap='viridis')
    ax2.set_title('Transition Pattern Heatmap')
    plt.colorbar(im, ax=ax2)
    
    # 3. Boundary constraint visualization
    ax3 = fig.add_subplot(223)
    start_values = values[:32]
    end_values = values[-32:]
    x = np.arange(32)
    ax3.plot(x, start_values, 'g-', label='Start', alpha=0.7)
    ax3.plot(x, end_values, 'r-', label='End', alpha=0.7)
    ax3.set_title('Boundary Constraints')
    ax3.set_xlabel('Position')
    ax3.set_ylabel('Value')
    ax3.legend()
    
    # 4. ModExp pattern visualization
    ax4 = fig.add_subplot(224)
    diffs = np.diff(values)
    ratios = []
    for i in range(len(values)-1):
        if values[i] != 0:
            ratios.append(values[i+1] / values[i])
        else:
            ratios.append(0)
    ax4.plot(x[:-1], ratios, 'y-', alpha=0.5, label='Value Ratios')
    ax4.set_title('ModExp Patterns')
    ax4.set_xlabel('Position')
    ax4.set_ylabel('Ratio')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('output/stark_witness_patterns.png')
    plt.close()

def visualize_modexp_patterns(hex_strings):
    """Create visualizations for modular exponentiation patterns."""
    # Convert hex strings to integer values
    values = []
    for hex_string in hex_strings:
        chunks = [int(hex_string[i:i+8], 16) for i in range(0, len(hex_string), 8)]
        values.extend(chunks)
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(15, 10))
    
    # 1. Sliding window pattern visualization
    ax1 = fig.add_subplot(221)
    window_size = 4
    windows = []
    for i in range(len(values) - window_size + 1):
        windows.append(values[i:i+window_size])
    window_sums = [sum(w) for w in windows]
    ax1.plot(window_sums, 'b-', alpha=0.5)
    ax1.set_title('Sliding Window Patterns')
    ax1.set_xlabel('Window Position')
    ax1.set_ylabel('Window Sum')
    
    # 2. Power residue visualization
    ax2 = fig.add_subplot(222)
    squares = []
    cubes = []
    for v in values:
        if v != 0:
            squares.append(v * v)
            cubes.append(v * v * v)
    ax2.scatter(values[:len(squares)], squares, c='g', alpha=0.3, label='Squares')
    ax2.scatter(values[:len(cubes)], cubes, c='r', alpha=0.3, label='Cubes')
    ax2.set_title('Power Residues')
    ax2.set_xlabel('Value')
    ax2.set_ylabel('Power')
    ax2.legend()
    
    # 3. Multiplicative order visualization
    ax3 = fig.add_subplot(223)
    orders = defaultdict(int)
    M31_MODULUS = 2**31 - 1
    for v in values:
        if v != 0:
            power = v
            order = 1
            while power != 1 and order < 32:
                power = (power * v) % M31_MODULUS
                order += 1
            orders[order] += 1
    order_items = sorted(orders.items())
    if order_items:
        x, y = zip(*order_items)
        ax3.bar(x, y)
    ax3.set_title('Multiplicative Orders')
    ax3.set_xlabel('Order')
    ax3.set_ylabel('Count')
    
    # 4. Precomputed table visualization
    ax4 = fig.add_subplot(224)
    powers = []
    base = 2
    for i in range(32):
        powers.append(pow(base, i, M31_MODULUS))
    ax4.plot(powers, 'r-', alpha=0.7, label=f'Base {base}')
    ax4.set_title('Precomputed Powers')
    ax4.set_xlabel('Exponent')
    ax4.set_ylabel('Value')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('output/modexp_patterns.png')
    plt.close()

def visualize_field_patterns(hex_strings):
    """Create visualizations for field arithmetic patterns."""
    values = []
    for hex_string in hex_strings:
        chunks = [int(hex_string[i:i+8], 16) for i in range(0, len(hex_string), 8)]
        values.extend(chunks)
    
    M31_MODULUS = 2**31 - 1
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Field element distribution
    ax1 = fig.add_subplot(321)
    field_vals = [v % M31_MODULUS for v in values]
    ax1.hist(field_vals, bins=50, alpha=0.7, color='blue')
    ax1.set_title('Field Element Distribution')
    ax1.set_xlabel('Value')
    ax1.set_ylabel('Frequency')
    
    # 2. Multiplicative order visualization
    ax2 = fig.add_subplot(322)
    orders = defaultdict(int)
    for v in values:
        if v != 0:
            power = v % M31_MODULUS
            order = 1
            while power != 1 and order < 32:
                power = (power * v) % M31_MODULUS
                order += 1
            orders[order] += 1
    
    order_items = sorted(orders.items())
    if order_items:
        x, y = zip(*order_items)
        ax2.bar(x, y, alpha=0.7, color='green')
    ax2.set_title('Multiplicative Orders')
    ax2.set_xlabel('Order')
    ax2.set_ylabel('Count')
    
    # 3. State transition graph
    ax3 = fig.add_subplot(323)
    transitions = np.zeros((32, 32))
    for i in range(len(values)-1):
        v1, v2 = values[i] % 32, values[i+1] % 32
        transitions[v1][v2] += 1
    im = ax3.imshow(transitions, cmap='viridis')
    ax3.set_title('State Transition Heatmap')
    plt.colorbar(im, ax=ax3)
    
    # 4. Field arithmetic patterns
    ax4 = fig.add_subplot(324)
    diffs = []
    for i in range(len(values)-1):
        if values[i] != 0:
            diff = (values[i+1] * pow(values[i], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS
            diffs.append(diff)
    ax4.hist(diffs, bins=50, alpha=0.7, color='red')
    ax4.set_title('Field Arithmetic Patterns')
    ax4.set_xlabel('Ratio')
    ax4.set_ylabel('Frequency')
    
    # 5. Polynomial degree visualization
    ax5 = fig.add_subplot(325)
    degrees = []
    window_size = 4
    for i in range(len(values) - window_size + 1):
        window = values[i:i+window_size]
        # Estimate polynomial degree by differences
        diffs = window
        degree = 0
        while len(set(diffs)) > 1 and degree < window_size:
            diffs = np.diff(diffs)
            degree += 1
        degrees.append(degree)
    ax5.hist(degrees, bins=range(window_size+2), alpha=0.7, color='purple')
    ax5.set_title('Polynomial Degree Distribution')
    ax5.set_xlabel('Degree')
    ax5.set_ylabel('Frequency')
    
    # 6. STARK witness pattern visualization
    ax6 = fig.add_subplot(326)
    witness_patterns = []
    for i in range(len(values)-3):
        window = values[i:i+4]
        # Check for STARK-like patterns (constant differences or ratios)
        diffs = [(window[j+1] - window[j]) % M31_MODULUS for j in range(len(window)-1)]
        if len(set(diffs)) == 1:
            witness_patterns.append(1)  # Arithmetic sequence
        elif all(v != 0 for v in window):
            ratios = [(window[j+1] * pow(window[j], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS 
                     for j in range(len(window)-1)]
            if len(set(ratios)) == 1:
                witness_patterns.append(2)  # Geometric sequence
        else:
            witness_patterns.append(0)
    
    if witness_patterns:
        ax6.plot(witness_patterns, alpha=0.7, color='orange')
    ax6.set_title('STARK Witness Patterns')
    ax6.set_xlabel('Position')
    ax6.set_ylabel('Pattern Type')
    
    plt.tight_layout()
    plt.savefig('output/field_patterns.png')
    plt.close()

if __name__ == "__main__":
    # Read hex strings from input
    hex_strings = []
    try:
        with open('../data/32bHex.txt', 'r') as f:
            hex_strings = [line.strip() for line in f if line.strip()]
    except:
        print("Error reading input file")
        exit(1)
    
    # Generate visualizations
    visualize_stark_witness_patterns(hex_strings)
    visualize_modexp_patterns(hex_strings)
    visualize_field_patterns(hex_strings)
    print("Visualizations saved to output/stark_witness_patterns.png, output/modexp_patterns.png, and output/field_patterns.png") 