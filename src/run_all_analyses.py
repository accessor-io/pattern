gi#!/usr/bin/python3

import os
from bit_pattern_2bit import hex_to_2bit_patterns
from bit_pattern_4bit import hex_to_4bit_patterns
from bit_pattern_byte_ascii import hex_to_byte_patterns
from bit_pattern_sliding import sliding_window_analysis
from bit_pattern_hamming import hamming_analysis
from bit_pattern_runs import run_length_analysis
from bit_pattern_transitions import transition_analysis
from bit_pattern_views import analyze_bit_views, format_bit_views
from bit_pattern_sequence import analyze_byte_sequence, format_sequence_analysis
import math
from zlib import compress
import statistics
from collections import Counter
import hashlib
import numpy as np
from scipy.fft import fft
import sympy
from collections import defaultdict

def read_hex_strings(filename):
    """Read and clean hex strings from file"""
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def ensure_output_dir():
    """Ensure output directory exists"""
    os.makedirs('output', exist_ok=True)

def write_analysis(hex_string, index, outfile):
    """Write all analyses for a single hex string"""
    outfile.write(f"\nAnalysis for String {index}:\n")
    outfile.write("=" * 80 + "\n")
    
    # Bit views analysis
    bit_views = analyze_bit_views(hex_string)
    outfile.write(format_bit_views(bit_views))
    outfile.write("\n" + "-" * 80 + "\n\n")
    
    # 2-bit pattern analysis
    two_bit = hex_to_2bit_patterns(hex_string)
    outfile.write("2-Bit Pattern Analysis:\n")
    for pattern in ['00', '01', '10', '11']:
        positions = two_bit['positions'][pattern]
        outfile.write(f"{pattern}: {len(positions)} occurrences at positions {positions}\n")
    outfile.write("\n")
    
    # 4-bit pattern analysis
    four_bit = hex_to_4bit_patterns(hex_string)
    outfile.write("4-Bit Pattern Analysis:\n")
    for pattern in sorted(four_bit['positions'].keys()):
        positions = four_bit['positions'][pattern]
        if positions:  # Only show patterns that occur
            outfile.write(f"{pattern}: {len(positions)} occurrences at positions {positions}\n")
    outfile.write("\n")
    
    # Byte-ASCII analysis
    byte_patterns = hex_to_byte_patterns(hex_string)
    outfile.write("Byte-ASCII Analysis:\n")
    for i, pattern in enumerate(byte_patterns):
        outfile.write(f"Byte {i:2d}: 0x{pattern['hex']} | {pattern['binary']} | ASCII: {pattern['ascii']}\n")
    outfile.write("\n")
    
    # Sliding window analysis
    for window_size in [4, 8, 16]:
        sliding = sliding_window_analysis(hex_string, window_size)
        outfile.write(f"Sliding Window Analysis (window size {window_size}):\n")
        outfile.write("Most common patterns:\n")
        for pattern, positions in sliding['most_common']:
            outfile.write(f"{pattern}: {len(positions)} occurrences at positions {positions}\n")
        outfile.write("\n")
    
    # Hamming weight analysis
    ham = hamming_analysis(hex_string)
    outfile.write("Hamming Weight Analysis:\n")
    for chunk_size, weights in ham.items():
        outfile.write(f"{chunk_size}-bit chunks:\n")
        for w in weights:
            outfile.write(f"Position {w['position']}: {w['weight']} bits set ({w['percentage']:.1f}%)\n")
    outfile.write("\n")
    
    # Run length analysis
    runs = run_length_analysis(hex_string)
    outfile.write("Run Length Analysis:\n")
    outfile.write(f"Total runs: {runs['total_runs']}\n")
    outfile.write(f"Longest run of 0s: {runs['longest_0_run']}\n")
    outfile.write(f"Longest run of 1s: {runs['longest_1_run']}\n")
    outfile.write("All runs:\n")
    for run in runs['runs']:
        outfile.write(f"Bit {run['bit']}: length {run['length']}\n")
    outfile.write("\n")
    
    # Transition analysis
    trans = transition_analysis(hex_string)
    outfile.write("Transition Analysis:\n")
    for transition, count in trans.items():
        if count > 0:  # Only show transitions that occur
            outfile.write(f"{transition}: {count} times\n")
    outfile.write("\n")
    outfile.write("=" * 80 + "\n\n")

def get_prime_factors(n):
    """Calculate prime factors of a number"""
    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
        if d * d > n:
            if n > 1:
                factors.append(n)
            break
    return factors

def calculate_randomness_score(binary):
    """Calculate a randomness score based on bit distribution and patterns"""
    # Count consecutive bits
    consecutive_ones = max(len(s) for s in binary.split('0'))
    consecutive_zeros = max(len(s) for s in binary.split('1'))
    
    # Calculate bit balance
    ones = binary.count('1')
    zeros = binary.count('0')
    balance = min(ones, zeros) / max(ones, zeros)
    
    # Look for repeating patterns
    pattern_penalty = 0
    for length in range(2, 9):
        patterns = {}
        for i in range(len(binary) - length + 1):
            pattern = binary[i:i+length]
            patterns[pattern] = patterns.get(pattern, 0) + 1
        max_repetition = max(patterns.values()) if patterns else 0
        pattern_penalty += max_repetition / (len(binary) - length + 1)
    
    # Combine metrics (higher score = more random)
    score = (
        balance * 0.4 +  # Weight bit balance
        (1 - pattern_penalty/7) * 0.3 +  # Weight pattern distribution
        (1 - consecutive_ones/len(binary)) * 0.15 +  # Weight consecutive ones
        (1 - consecutive_zeros/len(binary)) * 0.15    # Weight consecutive zeros
    )
    
    return score

def entropy_analysis(hex_string):
    """Analyze entropy and randomness metrics"""
    binary = bin(int(hex_string, 16))[2:].zfill(256)
    
    # Calculate Shannon entropy
    prob_1 = binary.count('1') / len(binary)
    prob_0 = 1 - prob_1
    shannon_entropy = 0
    if prob_0 > 0: shannon_entropy -= prob_0 * math.log2(prob_0)
    if prob_1 > 0: shannon_entropy -= prob_1 * math.log2(prob_1)
    
    return {
        'shannon_entropy': shannon_entropy,
        'bit_distribution': {
            '0': binary.count('0'),
            '1': binary.count('1')
        },
        'randomness_score': calculate_randomness_score(binary),
        'compression_ratio': len(compress(binary.encode())) / len(binary)
    }

def calculate_chi_square(binary):
    """Calculate chi-square test for randomness"""
    # Count occurrences of 0s and 1s
    counts = Counter(binary)
    expected = len(binary) / 2  # Expected count for truly random sequence
    
    # Calculate chi-square statistic
    chi_square = sum((obs - expected) ** 2 / expected for obs in counts.values())
    return chi_square

def calculate_autocorrelation(binary):
    """Calculate autocorrelation of the binary sequence"""
    n = len(binary)
    binary_int = [int(b) for b in binary]
    
    # Calculate for different shifts
    correlations = {}
    for shift in range(1, min(9, n)):  # Calculate for shifts 1-8
        correlation = 0
        for i in range(n - shift):
            if binary_int[i] == binary_int[i + shift]:
                correlation += 1
            else:
                correlation -= 1
        correlations[shift] = correlation / (n - shift)
    
    return correlations

def calculate_byte_frequency(chunks):
    """Calculate frequency distribution of byte values"""
    freq = Counter(int(chunk, 2) for chunk in chunks)
    return {f"0x{byte:02x}": count for byte, count in freq.items()}

def statistical_analysis(hex_string):
    """Analyze statistical properties"""
    binary = bin(int(hex_string, 16))[2:].zfill(256)
    chunks = [binary[i:i+8] for i in range(0, 256, 8)]
    
    return {
        'chi_square_test': calculate_chi_square(binary),
        'autocorrelation': calculate_autocorrelation(binary),
        'byte_frequency': calculate_byte_frequency(chunks),
        'distribution_metrics': {
            'mean': statistics.mean(int(chunk, 2) for chunk in chunks),
            'median': statistics.median(int(chunk, 2) for chunk in chunks),
            'stdev': statistics.stdev(int(chunk, 2) for chunk in chunks)
        }
    }

def calculate_quadrant_densities(grid):
    """Calculate bit densities in each quadrant of the grid"""
    size = len(grid)
    half = size // 2
    
    quadrants = {
        'top_left': [],
        'top_right': [],
        'bottom_left': [],
        'bottom_right': []
    }
    
    # Split grid into quadrants
    for i in range(size):
        for j in range(size):
            bit = grid[i][j]
            if i < half:
                if j < half:
                    quadrants['top_left'].append(bit)
                else:
                    quadrants['top_right'].append(bit)
            else:
                if j < half:
                    quadrants['bottom_left'].append(bit)
                else:
                    quadrants['bottom_right'].append(bit)
    
    # Calculate densities
    return {
        quad: bits.count('1') / len(bits)
        for quad, bits in quadrants.items()
    }

def visual_pattern_analysis(hex_string):
    """Create visual representations of the bit pattern"""
    binary = bin(int(hex_string, 16))[2:].zfill(256)
    
    # Create 16x16 grid representation
    grid = []
    for i in range(0, 256, 16):
        grid.append(binary[i:i+16])
    
    # Create visual patterns
    return {
        'grid': grid,
        'row_patterns': [''.join(set(row)) for row in grid],
        'col_patterns': [''.join(set(col)) for col in zip(*grid)],
        'diagonal_pattern': ''.join(grid[i][i] for i in range(16)),
        'quadrant_densities': calculate_quadrant_densities(grid)
    }

def calculate_hamming_distance(bin1, bin2):
    """Calculate Hamming distance between two binary strings"""
    return sum(c1 != c2 for c1, c2 in zip(bin1, bin2))

def calculate_avalanche(binary):
    """Calculate avalanche effect - how many bits change when flipping each bit"""
    n = len(binary)
    total_changes = 0
    for i in range(n):
        # Flip one bit
        modified = list(binary)
        modified[i] = '1' if binary[i] == '0' else '0'
        modified = ''.join(modified)
        
        # Count changed bits
        changes = calculate_hamming_distance(binary, modified)
        total_changes += changes
    
    # Return average number of bits that change
    return total_changes / n

def calculate_linear_complexity(binary):
    """Estimate linear complexity using Berlekamp-Massey algorithm"""
    n = len(binary)
    c = [0] * n  # Connection polynomial
    b = [0] * n  # Previous connection polynomial
    c[0] = 1
    b[0] = 1
    
    L = 0  # Current length
    m = -1  # Last update point
    for N in range(n):
        # Compute discrepancy
        d = int(binary[N])
        for i in range(1, L + 1):
            d ^= c[i] & int(binary[N-i])
        
        if d == 1:  # If there is a discrepancy
            t = c[:]  # Save current connection polynomial
            for j in range(N-m):
                if N-j < n:
                    c[N-j] ^= b[j]
            if L <= N/2:
                L = N + 1 - L
                m = N
                b = t
    
    return L  # Return linear complexity

def crypto_analysis(hex_string):
    """Analyze potential cryptographic properties"""
    binary = bin(int(hex_string, 16))[2:].zfill(256)
    
    return {
        'avalanche_effect': calculate_avalanche(binary),
        'hamming_distance_to_complement': calculate_hamming_distance(
            binary, 
            ''.join('1' if b == '0' else '0' for b in binary)
        ),
        'linear_complexity': calculate_linear_complexity(binary),
        'hash_values': {
            'md5': hashlib.md5(bytes.fromhex(hex_string)).hexdigest(),
            'sha1': hashlib.sha1(bytes.fromhex(hex_string)).hexdigest(),
            'sha256': hashlib.sha256(bytes.fromhex(hex_string)).hexdigest()
        }
    }

def write_sequence_analysis(hex_strings, outfile_path):
    """Write sequence analysis to a separate file"""
    with open(outfile_path, 'w') as outfile:
        outfile.write("Byte Position Sequential Analysis\n")
        outfile.write("=" * 80 + "\n\n")
        sequence_stats = analyze_byte_sequence(hex_strings)
        outfile.write(format_sequence_analysis(sequence_stats))

def write_pattern_analysis(hex_strings, outfile_path):
    """Write pattern analysis to a separate file"""
    with open(outfile_path, 'w') as outfile:
        outfile.write("Pattern Analysis for All Strings\n")
        outfile.write("=" * 80 + "\n\n")
        for i, hex_string in enumerate(hex_strings, 1):
            write_analysis(hex_string, i, outfile)

def write_entropy_analysis(hex_strings, outfile_path):
    """Write entropy analysis to a separate file"""
    with open(outfile_path, 'w') as outfile:
        outfile.write("Entropy Analysis for All Strings\n")
        outfile.write("=" * 80 + "\n\n")
        for i, hex_string in enumerate(hex_strings, 1):
            outfile.write(f"\nEntropy Analysis for String {i}:\n")
            outfile.write("=" * 80 + "\n")
            analysis = entropy_analysis(hex_string)
            outfile.write(f"Shannon Entropy: {analysis['shannon_entropy']:.4f}\n")
            outfile.write(f"Bit Distribution: {analysis['bit_distribution']}\n")
            outfile.write(f"Randomness Score: {analysis['randomness_score']:.4f}\n")
            outfile.write(f"Compression Ratio: {analysis['compression_ratio']:.4f}\n")
            outfile.write("\n")

def write_statistical_analysis(hex_strings, outfile_path):
    """Write statistical analysis to a separate file"""
    with open(outfile_path, 'w') as outfile:
        outfile.write("Statistical Analysis for All Strings\n")
        outfile.write("=" * 80 + "\n\n")
        for i, hex_string in enumerate(hex_strings, 1):
            outfile.write(f"\nStatistical Analysis for String {i}:\n")
            outfile.write("=" * 80 + "\n")
            analysis = statistical_analysis(hex_string)
            outfile.write(f"Chi-Square Test: {analysis['chi_square_test']:.4f}\n")
            outfile.write("\nAutocorrelation:\n")
            for shift, corr in analysis['autocorrelation'].items():
                outfile.write(f"Shift {shift}: {corr:.4f}\n")
            outfile.write("\nByte Frequency:\n")
            for byte, freq in analysis['byte_frequency'].items():
                outfile.write(f"{byte}: {freq}\n")
            outfile.write("\nDistribution Metrics:\n")
            for metric, value in analysis['distribution_metrics'].items():
                outfile.write(f"{metric}: {value:.4f}\n")
            outfile.write("\n")

def write_visual_analysis(hex_strings, text_base_path, visual_base_path):
    """Write visual pattern analysis to separate files for text and visual data"""
    # Write text analysis
    with open(f"{text_base_path}_text.txt", 'w') as outfile:
        outfile.write("Visual Pattern Analysis - Text Summary\n")
        outfile.write("=" * 80 + "\n\n")
        for i, hex_string in enumerate(hex_strings, 1):
            outfile.write(f"\nVisual Analysis for String {i}:\n")
            outfile.write("=" * 80 + "\n")
            analysis = visual_pattern_analysis(hex_string)
            outfile.write("\nQuadrant Densities:\n")
            for quad, density in analysis['quadrant_densities'].items():
                outfile.write(f"{quad}: {density:.4f}\n")
            outfile.write("\nRow Patterns:\n")
            for i, pattern in enumerate(analysis['row_patterns']):
                outfile.write(f"Row {i}: {pattern}\n")
            outfile.write("\nColumn Patterns:\n")
            for i, pattern in enumerate(analysis['col_patterns']):
                outfile.write(f"Column {i}: {pattern}\n")
            outfile.write(f"\nDiagonal Pattern: {analysis['diagonal_pattern']}\n")
            outfile.write("\n")

    # Write grid representations
    with open(f"{visual_base_path}_grid.txt", 'w') as outfile:
        outfile.write("Visual Pattern Analysis - Grid Representations\n")
        outfile.write("=" * 80 + "\n\n")
        for i, hex_string in enumerate(hex_strings, 1):
            outfile.write(f"\nGrid Representation for String {i}:\n")
            outfile.write("=" * 80 + "\n\n")
            analysis = visual_pattern_analysis(hex_string)
            
            # Draw the grid with borders
            outfile.write("┌" + "─" * 32 + "┐\n")  # Top border
            for row in analysis['grid']:
                outfile.write("│" + row + "│\n")  # Side borders
            outfile.write("└" + "─" * 32 + "┘\n")  # Bottom border
            outfile.write("\n\n")

    # Write density maps
    with open(f"{visual_base_path}_density.txt", 'w') as outfile:
        outfile.write("Visual Pattern Analysis - Density Maps\n")
        outfile.write("=" * 80 + "\n\n")
        for i, hex_string in enumerate(hex_strings, 1):
            outfile.write(f"\nDensity Map for String {i}:\n")
            outfile.write("=" * 80 + "\n\n")
            analysis = visual_pattern_analysis(hex_string)
            
            # Add visual density map
            densities = analysis['quadrant_densities']
            density_grid = [
                f"┌{'─' * 15}┬{'─' * 15}┐",
                f"│ TOP LEFT     │ TOP RIGHT    │",
                f"│ {densities['top_left']:6.2%}       │ {densities['top_right']:6.2%}       │",
                f"├{'─' * 15}┼{'─' * 15}┤",
                f"│ BOTTOM LEFT  │ BOTTOM RIGHT │",
                f"│ {densities['bottom_left']:6.2%}       │ {densities['bottom_right']:6.2%}       │",
                f"└{'─' * 15}┴{'─' * 15}┘"
            ]
            outfile.write("\n".join(density_grid))
            outfile.write("\n\n")

def write_crypto_analysis(hex_strings, outfile_path):
    """Write cryptographic analysis to a separate file"""
    with open(outfile_path, 'w') as outfile:
        outfile.write("Cryptographic Analysis for All Strings\n")
        outfile.write("=" * 80 + "\n\n")
        for i, hex_string in enumerate(hex_strings, 1):
            outfile.write(f"\nCryptographic Analysis for String {i}:\n")
            outfile.write("=" * 80 + "\n")
            analysis = crypto_analysis(hex_string)
            outfile.write(f"Avalanche Effect: {analysis['avalanche_effect']:.4f}\n")
            outfile.write(f"Hamming Distance to Complement: {analysis['hamming_distance_to_complement']}\n")
            outfile.write(f"Linear Complexity: {analysis['linear_complexity']}\n")
            outfile.write("\nHash Values:\n")
            for hash_type, hash_value in analysis['hash_values'].items():
                outfile.write(f"{hash_type}: {hash_value}\n")
            outfile.write("\n")

def analyze_mathematical_sequences(hex_strings):
    """Analyze sequences for advanced mathematical patterns"""
    # Convert hex strings to numerical sequences
    sequences = [int(hex_str, 16) for hex_str in hex_strings]
    
    # Analyze differences between consecutive terms
    differences = [sequences[i+1] - sequences[i] for i in range(len(sequences)-1)]
    
    # Look for multiplicative patterns
    ratios = [sequences[i+1] / sequences[i] if sequences[i] != 0 else float('inf') 
              for i in range(len(sequences)-1)]
    
    # FFT analysis for hidden periodicities
    fft_result = np.abs(fft(sequences))
    
    # Prime factorization patterns
    prime_patterns = []
    for num in sequences[:10]:  # First 10 numbers for demonstration
        if num == 0:
            continue
        factors = list(sympy.factorint(num).items())
        prime_patterns.append(factors)
    
    # Polynomial fitting attempt
    x = np.arange(len(sequences))
    for degree in range(1, 5):
        coeffs = np.polyfit(x, sequences, degree)
    
    # Modular patterns
    modular_patterns = defaultdict(list)
    for mod in [2, 3, 5, 7, 11, 13, 17, 19]:
        pattern = [num % mod for num in sequences]
        modular_patterns[mod] = pattern
    
    return {
        'differences': differences,
        'ratios': ratios,
        'fft_peaks': list(fft_result[:10]),  # First 10 FFT components
        'prime_patterns': prime_patterns,
        'modular_patterns': dict(modular_patterns)
    }

def write_abstract_analysis(hex_strings, outfile_path):
    """Write abstract mathematical analysis to a file"""
    analysis = analyze_mathematical_sequences(hex_strings)
    
    with open(outfile_path, 'w') as outfile:
        outfile.write("Abstract Mathematical Pattern Analysis\n")
        outfile.write("=" * 80 + "\n\n")
        
        # Write difference analysis
        outfile.write("Sequential Differences Pattern:\n")
        outfile.write("-" * 40 + "\n")
        differences = analysis['differences']
        outfile.write("First 10 differences:\n")
        outfile.write(", ".join(f"{d:x}" for d in differences[:10]))
        outfile.write("\n\n")
        
        # Write ratio analysis
        outfile.write("Growth Ratio Patterns:\n")
        outfile.write("-" * 40 + "\n")
        ratios = analysis['ratios']
        outfile.write("First 10 ratios:\n")
        outfile.write(", ".join(f"{r:.4f}" for r in ratios[:10]))
        outfile.write("\n\n")
        
        # Write FFT analysis
        outfile.write("Frequency Domain Patterns:\n")
        outfile.write("-" * 40 + "\n")
        fft_peaks = analysis['fft_peaks']
        outfile.write("Dominant frequencies:\n")
        outfile.write(", ".join(f"{p:.4f}" for p in fft_peaks))
        outfile.write("\n\n")
        
        # Write prime factorization patterns
        outfile.write("Prime Factorization Patterns:\n")
        outfile.write("-" * 40 + "\n")
        for i, factors in enumerate(analysis['prime_patterns']):
            outfile.write(f"Number {i+1}: {factors}\n")
        outfile.write("\n")
        
        # Write modular patterns
        outfile.write("Modular Arithmetic Patterns:\n")
        outfile.write("-" * 40 + "\n")
        for mod, pattern in analysis['modular_patterns'].items():
            outfile.write(f"Modulo {mod}: {pattern[:20]}...\n")
        outfile.write("\n")

def write_visual_abstract_patterns(hex_strings, visual_base_path):
    """Create abstract visual representations of the patterns"""
    sequences = [int(hex_str, 16) for hex_str in hex_strings]
    
    # Create spiral pattern visualization
    with open(f"{visual_base_path}_spiral.txt", 'w') as outfile:
        outfile.write("Spiral Pattern Visualization\n")
        outfile.write("=" * 80 + "\n\n")
        
        for i, num in enumerate(sequences[:20]):  # First 20 numbers
            # Create a spiral pattern based on binary representation
            binary = bin(num)[2:].zfill(64)
            spiral_size = 16
            spiral = []
            
            # Build spiral pattern
            for row in range(spiral_size):
                spiral_row = []
                for col in range(spiral_size):
                    idx = (row * spiral_size + col) % 64
                    spiral_row.append('●' if binary[idx] == '1' else '○')
                spiral.append(spiral_row)
            
            # Write spiral pattern
            outfile.write(f"Number {i+1} Spiral Pattern:\n")
            for row in spiral:
                outfile.write(''.join(row) + '\n')
            outfile.write("\n")
    
    # Create wave pattern visualization
    with open(f"{visual_base_path}_wave.txt", 'w') as outfile:
        outfile.write("Wave Pattern Visualization\n")
        outfile.write("=" * 80 + "\n\n")
        
        for i, num in enumerate(sequences[:10]):  # First 10 numbers
            binary = bin(num)[2:].zfill(64)
            wave = []
            
            # Create wave pattern using ASCII art
            height = 8
            for h in range(height):
                line = []
                for bit in binary:
                    if bit == '1':
                        if h == height // 2:
                            line.append('━')
                        elif h < height // 2:
                            line.append('╱')
                        else:
                            line.append('╲')
                    else:
                        if h == height // 2:
                            line.append('─')
                        else:
                            line.append(' ')
                wave.append(''.join(line))
            
            outfile.write(f"Number {i+1} Wave Pattern:\n")
            for line in wave:
                outfile.write(line + '\n')
            outfile.write("\n")

def main():
    """Main function to run all analyses."""
    print("Processing 65 hex strings...")
    
    # Read hex strings from file
    hex_strings = []
    with open('../data/32bHex.txt', 'r') as f:
        for line in f:
            hex_string = line.strip()
            if len(hex_string) == 64:  # 32 bytes = 64 hex chars
                hex_strings.append(hex_string)
    
    # Create output directories if they don't exist
    os.makedirs('../output/text', exist_ok=True)
    os.makedirs('../output/visual', exist_ok=True)
    os.makedirs('../output/abstract', exist_ok=True)
    
    # Write each analysis to a separate file
    print("Writing sequence analysis...")
    write_sequence_analysis(hex_strings, '../output/text/sequence_analysis.txt')
    
    print("Writing pattern analysis...")
    write_pattern_analysis(hex_strings, '../output/text/pattern_analysis.txt')
    
    print("Writing entropy analysis...")
    write_entropy_analysis(hex_strings, '../output/text/entropy_analysis.txt')
    
    print("Writing statistical analysis...")
    write_statistical_analysis(hex_strings, '../output/text/statistical_analysis.txt')
    
    print("Writing visual analysis...")
    write_visual_analysis(hex_strings, '../output/text/visual_analysis', '../output/visual/visual_analysis')
    
    print("Writing cryptographic analysis...")
    write_crypto_analysis(hex_strings, '../output/text/crypto_analysis.txt')
    
    print("Writing abstract mathematical analysis...")
    write_abstract_analysis(hex_strings, '../output/abstract/mathematical_patterns.txt')
    
    print("Writing abstract visual patterns...")
    write_visual_abstract_patterns(hex_strings, '../output/abstract/visual_patterns')
    
    print("Analysis complete. Results written to separate files in the output directories:")
    print("\nText Analysis Files (in output/text/):")
    print("- sequence_analysis.txt")
    print("- pattern_analysis.txt")
    print("- entropy_analysis.txt")
    print("- statistical_analysis.txt")
    print("- visual_analysis_text.txt")
    print("- crypto_analysis.txt")
    print("\nVisual Analysis Files (in output/visual/):")
    print("- visual_analysis_grid.txt")
    print("- visual_analysis_density.txt")
    print("\nAbstract Analysis Files (in output/abstract/):")
    print("- mathematical_patterns.txt")
    print("- visual_patterns_spiral.txt")
    print("- visual_patterns_wave.txt")

if __name__ == "__main__":
    main() 