import json
import statistics
from collections import Counter, defaultdict
import numpy as np
from typing import Dict, List, Tuple

# Known solutions from reference (same as before)
KNOWN_SOLUTIONS = {
    # ... (keeping the same KNOWN_SOLUTIONS dictionary)
    1: 0x0000000000000000000000000000000000000000000000000000000000000001,
    2: 0x0000000000000000000000000000000000000000000000000000000000000003,
    # ... (all entries preserved)
    66: 0x000000000000000000000000000000000000000000000002832ed74f2b5e35ee
}

class PatternAnalyzer:
    def __init__(self):
        self.last_two_counts: Dict[int, int] = {}
        self.first_two_counts: Dict[int, int] = {}
        self.length_counts: Dict[int, int] = {}
        self.zero_prefix_counts: Dict[int, int] = {}
        self.reference_counts: Dict[int, int] = {}
        
        # Advanced pattern tracking with sliding window
        self.window_size = 8  # Size of sliding window
        self.offset = 4      # Offset for pattern matching
        self.constant = 0x1234  # Constant for pattern matching
        
        self.byte_frequency: Dict[int, Dict[int, int]] = {i: {} for i in range(32)}
        self.consecutive_zeros: List[int] = []
        self.consecutive_ones: List[int] = []
        self.palindrome_counts: Dict[int, int] = {}
        self.repeated_pattern_counts: Dict[str, int] = {}
        self.pair_positions: Dict[str, List[int]] = {}
        self.value_positions: Dict[str, List[int]] = defaultdict(list)
        
    def analyze_hex_patterns(self, hex_str: str) -> Dict[str, List[str]]:
        patterns = {
            'repeating': [],
            'ascending': [],
            'descending': [],
            'palindromes': []
        }
        
        # Apply offset and constant
        hex_int = int(hex_str, 16)
        adjusted_value = (hex_int + self.offset) ^ self.constant
        hex_str = format(adjusted_value, 'x')
        
        # Sliding window analysis
        for i in range(len(hex_str) - self.window_size + 1):
            window = hex_str[i:i + self.window_size]
            
            # Track positions with offset
            value = window[:2]
            pos = (i + self.offset) % len(hex_str)
            self.value_positions[value].append(pos)
            
            # Find patterns in window
            if window.count(window[:2]) > 1:
                patterns['repeating'].append(window)
                
            # Check ascending/descending in window
            for j in range(0, len(window)-2, 2):
                current = int(window[j:j+2], 16)
                next_byte = int(window[j+2:j+4], 16)
                if next_byte == current + 1:
                    patterns['ascending'].append(window[j:j+4])
                elif next_byte == current - 1:
                    patterns['descending'].append(window[j:j+4])
        
        # Track pair positions with offset
        for i in range(0, len(hex_str)-1, 2):
            pair = hex_str[i:i+2]
            pos = (i + self.offset) % len(hex_str)
            if pair not in self.pair_positions:
                self.pair_positions[pair] = []
            self.pair_positions[pair].append(pos)
                
        return patterns

    def analyze_binary_patterns(self, hex_str: str) -> Dict[str, List[str]]:
        # Apply offset and constant
        hex_int = int(hex_str, 16)
        adjusted_value = (hex_int + self.offset) ^ self.constant
        binary = bin(adjusted_value)[2:].zfill(len(hex_str)*4)
        
        patterns = {
            'zero_runs': [],
            'one_runs': [],
            'alternating': []
        }
        
        # Sliding window for binary patterns
        for i in range(len(binary) - self.window_size + 1):
            window = binary[i:i + self.window_size]
            
            # Find runs in window
            current_run = 1
            current_bit = window[0]
            for j in range(1, len(window)):
                if window[j] == current_bit:
                    current_run += 1
                else:
                    if current_bit == '0':
                        patterns['zero_runs'].append(current_run)
                    else:
                        patterns['one_runs'].append(current_run)
                    current_run = 1
                    current_bit = window[j]
            
            # Find alternating patterns in window
            for j in range(0, len(window)-3, 2):
                if window[j:j+2] == '01' and window[j+2:j+4] == '01':
                    patterns['alternating'].append(f"{i+j}-{i+j+4}")
                
        return patterns

    def analyze_reference_solutions(self):
        for index, solution in KNOWN_SOLUTIONS.items():
            hex_str = format(solution, 'x')
            
            # Apply offset and constant
            hex_int = int(hex_str, 16)
            adjusted_value = (hex_int + self.offset) ^ self.constant
            hex_str = format(adjusted_value, 'x')
            
            # Basic patterns
            last_two = hex_str[-2:]
            significant_bits = int(last_two, 16)
            self.reference_counts[significant_bits] = self.reference_counts.get(significant_bits, 0) + 1
            
            # Advanced patterns with sliding window
            hex_patterns = self.analyze_hex_patterns(hex_str)
            bin_patterns = self.analyze_binary_patterns(hex_str)
            
            print(f"\nDetailed analysis for reference solution {index}:")
            print(f"Hex string: {hex_str}")
            print(f"Repeating patterns: {len(hex_patterns['repeating'])}")
            print(f"Ascending sequences: {len(hex_patterns['ascending'])}")
            print(f"Descending sequences: {len(hex_patterns['descending'])}")
            print(f"Longest zero run: {max(bin_patterns['zero_runs']) if bin_patterns['zero_runs'] else 0}")
            print(f"Longest one run: {max(bin_patterns['one_runs']) if bin_patterns['one_runs'] else 0}")
            
            # Print value position correlations
            print("\nValue position correlations:")
            for value, positions in sorted(self.value_positions.items()):
                if len(positions) > 1:
                    diffs = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                    if diffs:
                        correlation = np.corrcoef(diffs[:-1], diffs[1:])[0,1] if len(diffs) > 1 else 0
                        print(f"Value {value} appears at positions {positions}, position diff correlation: {correlation:.3f}")

    def analyze_transaction(self, tx):
        try:
            txid = tx['txid']
            hex_str = txid
            
            # Apply offset and constant
            hex_int = int(hex_str, 16)
            adjusted_value = (hex_int + self.offset) ^ self.constant
            hex_str = format(adjusted_value, 'x')
            
            # Basic pattern analysis
            last_two = hex_str[-2:]
            if all(c in '0123456789abcdef' for c in last_two.lower()):
                last_two_val = int(last_two, 16)
                self.last_two_counts[last_two_val] = self.last_two_counts.get(last_two_val, 0) + 1

            # Advanced pattern analysis with sliding window
            hex_patterns = self.analyze_hex_patterns(hex_str)
            bin_patterns = self.analyze_binary_patterns(hex_str)
            
            # Store results
            for pattern in hex_patterns['repeating']:
                self.repeated_pattern_counts[pattern] = self.repeated_pattern_counts.get(pattern, 0) + 1
            
            # Analyze address patterns if available
            if 'vin' in tx and tx['vin'] and 'prevout' in tx['vin'][0]:
                address = tx['vin'][0]['prevout'].get('scriptpubkey_address')
                if address:
                    self.analyze_address_patterns(address)
                    
        except (KeyError, ValueError, IndexError) as e:
            print(f"Error processing transaction: {str(e)}")

    def analyze_address_patterns(self, address: str):
        # Apply offset and constant
        hex_int = int(address, 16) if all(c in '0123456789abcdef' for c in address.lower()) else 0
        adjusted_value = (hex_int + self.offset) ^ self.constant
        hex_str = format(adjusted_value, 'x')
        
        # Analyze patterns with sliding window
        hex_patterns = self.analyze_hex_patterns(hex_str)
        bin_patterns = self.analyze_binary_patterns(hex_str)
        
        # Store unique patterns found in addresses
        for pattern in hex_patterns['repeating']:
            self.repeated_pattern_counts[f"addr_{pattern}"] = self.repeated_pattern_counts.get(f"addr_{pattern}", 0) + 1

    def print_analysis(self):
        print("\n=== EXTREME PATTERN ANALYSIS ===")
        
        # Statistical analysis
        print("\nStatistical Measures:")
        for pattern_type, counts in [
            ("Last Two Chars", self.last_two_counts),
            ("First Two Chars", self.first_two_counts),
            ("Lengths", self.length_counts)
        ]:
            if counts:
                values = list(counts.values())
                print(f"\n{pattern_type}:")
                print(f"Mean: {statistics.mean(values):.2f}")
                print(f"Median: {statistics.median(values):.2f}")
                print(f"Std Dev: {statistics.stdev(values) if len(values) > 1 else 0:.2f}")
                print(f"Max: {max(values)}")
                print(f"Min: {min(values)}")

        # Most common patterns
        print("\nMost Common Repeated Patterns:")
        for pattern, count in sorted(self.repeated_pattern_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{pattern}: {count}")

        # Value position correlations
        print("\nValue Position Correlations:")
        for value, positions in sorted(self.value_positions.items()):
            if len(positions) > 1:
                diffs = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                if len(diffs) > 1:
                    correlation = np.corrcoef(diffs[:-1], diffs[1:])[0,1]
                    avg_spacing = np.mean(diffs)
                    print(f"Value {value}: appears {len(positions)} times")
                    print(f"  Position diff correlation: {correlation:.3f}")
                    print(f"  Average spacing: {avg_spacing:.2f}")

# Main execution
analyzer = PatternAnalyzer()

# Load and analyze data
with open('tx_cache/1AVJKwzs9AskraJLGHAZPiaZcrpDr1U6AB.json') as f:
    data = json.load(f)

# Analyze reference solutions
analyzer.analyze_reference_solutions()

# Analyze transactions
for tx in data['txs']:
    analyzer.analyze_transaction(tx)

# Print final analysis
analyzer.print_analysis()