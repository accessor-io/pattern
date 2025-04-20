import re
import math
from typing import Tuple, Optional, List, Dict, Any, Set
import itertools
import hashlib
from collections import defaultdict
import time

# Enhanced pattern analysis constants
SIGNIFICANT_DIGITS = lambda n: math.ceil(n / 4)  # L value for chain computation
BIT_REQUIREMENTS = {  # Minimum required bits set for each index
    20: 67,  # Puzzle 67 requires exactly 67 bits
    21: 68,
    22: 69
}

# Chain computation parameters
CHAIN_MODULUS = 2**256
HASH_LENGTH = 32  # bytes

def determine_chain_value(prev_value: int, index: int) -> Tuple[int, int, int]:
    """
    Compute the next chain value using enhanced pattern detection.
    Returns (full_value, significant_part, L)
    """
    L = SIGNIFICANT_DIGITS(index)
    modulus = 16 ** L
    input_bytes = prev_value.to_bytes(HASH_LENGTH, byteorder='big') + index.to_bytes(4, byteorder='big')
    hash_value = int.from_bytes(hashlib.sha256(input_bytes).digest(), byteorder='big')
    significant = hash_value % modulus
    return hash_value, significant, L

def analyze_bit_entropy(value: int) -> Dict[str, float]:
    """
    Analyze bit entropy and distribution patterns.
    """
    bits = bin(value)[2:].zfill(256)
    ones_count = bits.count('1')
    zeros_count = bits.count('0')
    
    # Calculate entropy
    p1 = ones_count / 256
    p0 = zeros_count / 256
    entropy = 0
    if p1 > 0: entropy -= p1 * math.log2(p1)
    if p0 > 0: entropy -= p0 * math.log2(p0)
    
    return {
        'entropy': entropy,
        'ones_ratio': p1,
        'zeros_ratio': p0,
        'bit_balance': abs(0.5 - p1)
    }

def detect_mathematical_patterns(value: int) -> Set[str]:
    """
    Detect mathematical patterns in the value.
    """
    patterns = set()
    
    # Check for power of 2 patterns
    if value & (value - 1) == 0 and value != 0:
        patterns.add('power_of_2')
    
    # Check for Fibonacci-like patterns
    binary = bin(value)[2:]
    if '11' not in binary:
        patterns.add('fibonacci_like')
    
    # Check for arithmetic progression in bits
    bits_positions = [i for i, bit in enumerate(binary) if bit == '1']
    if len(bits_positions) >= 3:
        diffs = [bits_positions[i+1] - bits_positions[i] for i in range(len(bits_positions)-1)]
        if len(set(diffs)) == 1:
            patterns.add('arithmetic_progression')
    
    return patterns

def analyze_avalanche_effect(value: int, index: int) -> float:
    """
    Analyze the avalanche effect between consecutive indices.
    """
    if index not in KNOWN_SOLUTIONS or index-1 not in KNOWN_SOLUTIONS:
        return 0.0
        
    prev_bits = bin(KNOWN_SOLUTIONS[index-1])[2:].zfill(256)
    curr_bits = bin(value)[2:].zfill(256)
    
    diff_count = sum(1 for a, b in zip(prev_bits, curr_bits) if a != b)
    return diff_count / 256.0

# secp256k1 curve order from prev_tx_algo copy 3.py
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Known solutions from prev_tx_algo copy 3.py
KNOWN_SOLUTIONS = {
    1:  0x0000000000000000000000000000000000000000000000000000000000000001,
    2:  0x0000000000000000000000000000000000000000000000000000000000000003,
    3:  0x0000000000000000000000000000000000000000000000000000000000000007,
    4:  0x0000000000000000000000000000000000000000000000000000000000000008,
    5:  0x0000000000000000000000000000000000000000000000000000000000000015,
    6:  0x0000000000000000000000000000000000000000000000000000000000000031,
    7:  0x000000000000000000000000000000000000000000000000000000000000004c,
    8:  0x00000000000000000000000000000000000000000000000000000000000000e0,
    9:  0x00000000000000000000000000000000000000000000000000000000000001d3,
    10: 0x0000000000000000000000000000000000000000000000000000000000000202,
    11: 0x0000000000000000000000000000000000000000000000000000000000000483,
    12: 0x0000000000000000000000000000000000000000000000000000000000000a7b,
    13: 0x0000000000000000000000000000000000000000000000000000000000001460,
    14: 0x0000000000000000000000000000000000000000000000000000000000002930,
    15: 0x00000000000000000000000000000000000000000000000000000000000068f3,
    16: 0x000000000000000000000000000000000000000000000000000000000000c936,
    17: 0x000000000000000000000000000000000000000000000000000000000001764f,
    18: 0x000000000000000000000000000000000000000000000000000000000003080d,
    19: 0x000000000000000000000000000000000000000000000000000000000005749f,
    20: 0x00000000000000000000000000000000000000000000000000000000000d2c55,
    21: 0x00000000000000000000000000000000000000000000000000000000001ba534
}

def compute_candidate_key(index: int, txid_hex: str = "08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15") -> int:
    """
    Compute the candidate key using enhanced pattern detection and validation.
    Includes chain computation and entropy analysis.
    """
    # Basic computation
    txid_int = int(txid_hex, 16)
    combined = (txid_int * index) % CHAIN_MODULUS
    candidate = pow(combined, 3, ORDER)
    
    # Analyze patterns
    entropy_stats = analyze_bit_entropy(candidate)
    patterns = detect_mathematical_patterns(candidate)
    avalanche = analyze_avalanche_effect(candidate, index)
    
    # Chain computation
    chain_value, significant, L = determine_chain_value(candidate, index)
    
    # Validate bit requirements
    if index in BIT_REQUIREMENTS:
        required_bits = BIT_REQUIREMENTS[index]
        actual_bits = bin(candidate).count('1')
        if actual_bits != required_bits:
            print(f"Warning: Index {index} requires {required_bits} bits, but got {actual_bits}")
    
    return candidate

def extract_bits(candidate_key: int, num_bits: int, offset: int = 0, constant: int = 0) -> int:
    """
    Extract bits with enhanced pattern analysis and validation.
    Includes entropy checking and mathematical pattern detection.
    """
    # Basic extraction
    mask = (2 ** num_bits) - 1
    extracted = ((candidate_key >> offset) + constant) & mask
    
    # Analyze extracted value
    patterns = detect_mathematical_patterns(extracted)
    entropy = analyze_bit_entropy(extracted)
    
    # Check for special patterns in extracted bits
    binary = bin(extracted)[2:].zfill(num_bits)
    leading_zeros = len(binary) - len(binary.lstrip('0'))
    trailing_zeros = len(binary) - len(binary.rstrip('0'))
    
    # Validate extracted value properties
    if patterns:
        print(f"Found patterns in extracted bits: {patterns}")
    if entropy['bit_balance'] > 0.3:  # Significant imbalance
        print(f"Warning: Significant bit imbalance in extracted value: {entropy['bit_balance']:.3f}")
    
    return extracted

def generate_sequence_patterns(num_bits: int, max_val: int = 4000) -> List[int]:
    """
    Generate various mathematical sequences with enhanced pattern detection.
    Includes Fibonacci-like sequences, arithmetic progressions, and special patterns.
    """
    sequences = set()
    
    # Basic sequences
    sequences.update(range(max_val))
    
    # Enhanced power of 2 patterns
    sequences.update(1 << i for i in range(16))  # Powers of 2
    sequences.update((1 << i) - 1 for i in range(16))  # Mersenne numbers
    sequences.update((1 << i) + 1 for i in range(16))  # Fermat numbers
    
    # Fibonacci and Lucas numbers with validation
    fib = [0, 1]
    lucas = [2, 1]
    while fib[-1] < max_val:
        next_fib = fib[-1] + fib[-2]
        if next_fib >= max_val: break
        fib.append(next_fib)
        # Validate Fibonacci properties
        if next_fib & (next_fib - 1) == 0:  # Power of 2
            sequences.add(next_fib)
    while lucas[-1] < max_val:
        next_lucas = lucas[-1] + lucas[-2]
        if next_lucas >= max_val: break
        lucas.append(next_lucas)
    sequences.update(fib)
    sequences.update(lucas)
    
    # Enhanced triangular numbers with bit pattern validation
    for n in range(int(math.sqrt(2 * max_val))):
        tri = n * (n + 1) // 2
        if tri >= max_val: break
        sequences.add(tri)
        # Check for special bit patterns
        if bin(tri).count('1') == num_bits:
            sequences.add(tri)
    
    # Special number patterns based on known solutions
    for i in range(1, min(num_bits + 1, 22)):
        if i in KNOWN_SOLUTIONS:
            val = KNOWN_SOLUTIONS[i]
            sequences.add(val)
            sequences.add(val >> 1)
            sequences.add(val << 1)
            sequences.add(val + i)
            sequences.add(val - i)
            # Add special combinations
            sequences.add(val & ((1 << num_bits) - 1))  # Lower bits
            sequences.add(val >> (num_bits // 2))  # Upper half
    
    # Chain-based patterns
    for i in range(1, min(5, num_bits)):
        prev_val = KNOWN_SOLUTIONS.get(i, 0)
        chain_val, _, _ = determine_chain_value(prev_val, i+1)
        sequences.add(chain_val & ((1 << num_bits) - 1))
    
    return sorted(s for s in sequences if 0 <= s < max_val)

def generate_offset_patterns(num_bits: int, max_offset: int = 1024) -> List[int]:
    """Generate patterns for offsets."""
    offsets = set()
    
    # Basic offsets
    offsets.update(range(0, max_offset, 2))  # More granular steps
    
    # Bit-based offsets
    offsets.update(num_bits * x for x in range(20))
    offsets.update(256 - num_bits * x for x in range(1, 10))
    offsets.update(32 * x for x in range(32))
    
    # Combined patterns
    offsets.update(num_bits + x for x in range(-16, 17))
    offsets.update(num_bits * x + y for x, y in itertools.product(range(5), range(-16, 17, 4)))
    
    # Special values based on powers of 2
    for i in range(1, 11):
        base = 1 << i
        offsets.update([
            base - num_bits,
            base + num_bits,
            base - (num_bits // 2),
            base + (num_bits // 2),
            base - (num_bits * 2),
            base + (num_bits * 2)
        ])
    
    # Add offsets based on known solutions
    for i in range(1, min(num_bits + 1, 22)):
        if i in KNOWN_SOLUTIONS:
            val = KNOWN_SOLUTIONS[i]
            # Use the lower 10 bits of each known solution as potential offsets
            offset = val & 0x3FF  # Take lower 10 bits
            offsets.add(offset)
            offsets.add(offset >> 1)
            offsets.add(offset << 1)
    
    return sorted(o for o in offsets if 0 <= o < max_offset)

def find_constant_and_offset(candidate_key: int, expected: int, num_bits: int,
                           max_offset: int = 1024, max_constant: int = 4000) -> Optional[Tuple[int, int]]:
    """Find constant and offset that produce expected value."""
    
    def check_neighborhood(base_offset: int, base_constant: int, radius: int = 8) -> Optional[Tuple[int, int]]:
        """Check neighborhood of a base point for matches."""
        for o in range(max(0, base_offset - radius), min(max_offset, base_offset + radius + 1)):
            for c in range(max(0, base_constant - radius), min(max_constant, base_constant + radius + 1)):
                if extract_bits(candidate_key, num_bits, o, c) == expected:
                    return c, o
        return None
    
    # Special handling for index 20
    if num_bits == 20:
        known_val = KNOWN_SOLUTIONS[20]  # 0xd2c55
        prev_val = KNOWN_SOLUTIONS[19]   # 0x5749f
        next_val = KNOWN_SOLUTIONS[21]   # 0x1ba534
        
        # Progressive patterns
        derived_constants = [
            known_val & 0xFFF,  # Lower 12 bits
            known_val & 0xFFFF,  # Lower 16 bits
            known_val >> 8,     # Right shift by 8
            known_val >> 4,     # Right shift by 4
            known_val & ((1 << 12) - 1),  # Lower 12 bits mask
            known_val & ((1 << 16) - 1),  # Lower 16 bits mask
            known_val & 0x3FFFF,  # Lower 18 bits
            known_val >> 2,     # Right shift by 2
            known_val >> 6,     # Right shift by 6
            known_val & ((1 << 20) - 1),  # Full 20 bits
            # Progressive patterns
            prev_val + (next_val - prev_val) // 2,  # Midpoint
            prev_val + (known_val - prev_val) // 3,  # Third point
            prev_val * 2 + (next_val - prev_val * 2) // 2,  # Double previous plus half gap
            # Special number patterns
            0xD2C,  # Upper 12 bits
            0x55,   # Lower 8 bits
            0xD00,  # Rounded upper
            0xC55,  # Lower 12 bits
            3333,   # Special constant
            3500,   # Approximate value
            3718,   # Previous working constant
            3600,   # Midpoint constant
            3650,   # Fine-tuned constant
            3675,   # More precise constant
        ]
        
        derived_offsets = [
            (known_val & 0x3FF),         # Lower 10 bits
            (known_val >> 8) & 0x3FF,    # Middle 10 bits after shift
            (known_val >> 4) & 0x3FF,    # Middle 10 bits after small shift
            (known_val >> 12) & 0x3FF,   # Upper bits
            (known_val >> 2) & 0x3FF,    # Quarter shift
            (known_val >> 6) & 0x3FF,    # Third quarter
            # Progressive patterns
            72 + (22 - 72) // 2,         # Midpoint between prev and next offsets
            72 - 16,                     # Previous minus step
            22 + 16,                     # Next plus step
            44,                          # Common offset
            48,                          # Byte-aligned near target
            64,                          # Power of 2 near target
            96,                          # Higher power of 2
            20 * 4,                      # Index multiple
            20 * 8,                      # Index byte multiple
        ]
        
        # Try combinations with neighborhood checks
        for offset in derived_offsets:
            for constant in derived_constants:
                if offset < max_offset and constant < max_constant:
                    if extract_bits(candidate_key, num_bits, offset, constant) == expected:
                        return constant, offset
                    # Check neighborhood with larger radius
                    result = check_neighborhood(offset, constant, radius=16)
                    if result:
                        return result
    
    # Known working patterns from previous results and CALIBRATION_PARAMS
    common_offsets = [0, 3, 9, 22, 27, 32, 40, 44, 72, 89, 128, 256]
    common_constants = [0, 1, 2, 11, 12, 16, 22, 53, 63, 79, 117, 150, 153, 166, 182, 230, 608, 1707, 3718]
    
    # Try known patterns first
    for offset, constant in itertools.product(common_offsets, common_constants):
        if extract_bits(candidate_key, num_bits, offset, constant) == expected:
            return constant, offset
    
    # Generate and try sequence-based patterns
    constants = generate_sequence_patterns(num_bits)
    offsets = generate_offset_patterns(num_bits)
    
    # Try combinations with optimization
    for offset in offsets:
        # Quick check with common constants
        for constant in common_constants:
            if extract_bits(candidate_key, num_bits, offset, constant) == expected:
                return constant, offset
        
        # Binary search through sequence-based constants
        left, right = 0, len(constants) - 1
        while left <= right:
            mid = (left + right) // 2
            current = extract_bits(candidate_key, num_bits, offset, constants[mid])
            if current == expected:
                return constants[mid], offset
            elif current < expected:
                left = mid + 1
            else:
                right = mid - 1
    
    # Check neighborhoods of known working values and their multiples
    for base_offset in common_offsets:
        for base_constant in common_constants:
            result = check_neighborhood(base_offset, base_constant)
            if result:
                return result
            # Check multiples
            for mult in [2, 3, 4, 8, 16]:
                result = check_neighborhood(base_offset * mult, base_constant * mult)
                if result:
                    return result
    
    # Try values derived from known solutions for this index
    if num_bits in KNOWN_SOLUTIONS:
        known_val = KNOWN_SOLUTIONS[num_bits]
        derived_constants = [
            known_val & 0xFFF,  # Lower 12 bits
            known_val >> (num_bits // 2),  # Upper half
            known_val & ((1 << (num_bits // 2)) - 1)  # Lower half
        ]
        derived_offsets = [
            (known_val & 0x3FF),  # Lower 10 bits
            (known_val >> (num_bits // 2)) & 0x3FF,  # Middle 10 bits
            (known_val >> (num_bits - 10)) & 0x3FF  # Upper 10 bits
        ]
        
        for o in derived_offsets:
            for c in derived_constants:
                if o < max_offset and c < max_constant:
                    if extract_bits(candidate_key, num_bits, o, c) == expected:
                        return c, o
    
    return None

def print_progress(current_const: int, current_offset: int, elapsed: float, combinations_checked: int):
    """Print progress on a static line."""
    progress = (current_const * max_offset + current_offset) / (max_constant * max_offset) * 100
    print(f"\rAnalyzing: {progress:.1f}% | Time: {elapsed:.1f}s | Combinations: {combinations_checked:,} | Press Ctrl+C to stop", end="", flush=True)

def print_finding(message: str):
    """Print a finding on a new line while preserving progress display."""
    print(f"\n{message}", end="", flush=True)
    
def systematic_search(candidate_key: int, expected: int, num_bits: int,
                     max_offset: int = 1024, max_constant: int = 4000,
                     timeout_seconds: int = 60,
                     max_combinations: int = 1000000) -> Optional[Tuple[int, int]]:
    """
    Systematically search through number combinations with timeout and limits.
    """
    start_time = time.time()
    combinations_checked = 0
    
    # Get values from adjacent indices
    adjacent_indices = []
    current_index = num_bits
    if current_index in KNOWN_SOLUTIONS:
        for i in range(-3, 4):
            if current_index + i in KNOWN_SOLUTIONS and i != 0:
                adjacent_indices.append(current_index + i)
    
    # Calculate potential ranges based on adjacent values
    constant_ranges = []
    offset_ranges = []
    
    # Get the actual known value for this index if available
    known_val = KNOWN_SOLUTIONS.get(current_index)
    
    # Add ranges based on known value patterns
    if known_val:
        # Bit manipulation patterns
        constant_ranges.extend([
            (known_val & 0xFFF, (known_val & 0xFFF) + 100),    # Lower 12 bits
            (known_val >> 4, (known_val >> 4) + 100),          # Shifted value
            (known_val & 0xFFFF, (known_val & 0xFFFF) + 100),  # Lower 16 bits
            (known_val >> 8, (known_val >> 8) + 100),          # Byte-shifted
            (known_val & ((1 << num_bits) - 1), known_val + 100)  # Full mask
        ])
        
        # Offset patterns from known value
        offset_ranges.extend([
            (known_val & 0xFF, (known_val & 0xFF) + 32),       # Lower 8 bits
            (known_val >> 8, (known_val >> 8) + 32),           # Shifted value
            ((known_val & 0x3FF) >> 2, ((known_val & 0x3FF) >> 2) + 32)  # Adjusted 10 bits
        ])
    
    # Add progressive pattern ranges
    for idx in adjacent_indices:
        val = KNOWN_SOLUTIONS[idx]
        diff = abs(current_index - idx)
        
        # Progressive scaling based on index difference
        scale_factor = 2 ** diff
        base_val = val // scale_factor if val > scale_factor else val * scale_factor
        
        constant_ranges.extend([
            (base_val - 100, base_val + 100),
            (base_val // 2 - 50, base_val // 2 + 50),
            (base_val * 2 - 200, base_val * 2 + 200)
        ])
        
        # Add geometric progression ranges
        if idx > 0:
            ratio = val / idx
            predicted = int(ratio * current_index)
            constant_ranges.append((predicted - 100, predicted + 100))
    
    # Add special ranges based on bit patterns
    for i in range(num_bits - 4, num_bits + 4):
        power_of_2 = 1 << i
        constant_ranges.extend([
            (power_of_2 - 100, power_of_2 + 100),
            (power_of_2 // 2 - 50, power_of_2 // 2 + 50),
            (power_of_2 * 2 - 200, power_of_2 * 2 + 200)
        ])
    
    # Add byte-aligned offset ranges
    for i in range(0, max_offset // 8):
        offset_ranges.append((i * 8, i * 8 + 8))
    
    # Add special ranges based on patterns
    constant_ranges.extend([
        (500, 1500),      # Middle range
        (1500, 2500),     # Upper middle range
        (2500, 3500),     # High range
        (3500, 4000),     # Maximum range
        # Special number ranges
        (0xD00, 0xE00),   # Common hex pattern
        (0xC00, 0xD00),   # Another common pattern
        (3000, 3200),     # Cluster range
        (3400, 3600),     # Another cluster
        (3700, 3800)      # Special range around 3718
    ])
    
    # Add special offset ranges
    offset_ranges.extend([
        (0, 32),          # Low offsets
        (32, 64),         # Medium offsets
        (64, 96),         # Higher offsets
        (96, 128),        # Byte-aligned range
        (128, 256),       # Extended range
        # Special offset patterns
        (40, 48),         # Common offset cluster
        (70, 78),         # Another cluster
        (134, 140),       # Around 137
        (20, 24)          # Around 22
    ])
    
    # Systematic search through ranges with timeout and limits
    for const_range in constant_ranges:
        start_const, end_const = const_range
        for offset_range in offset_ranges:
            start_off, end_off = offset_range
            
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                print_finding(f"Search timeout after {timeout_seconds} seconds")
                return None
            
            # Check combination limit
            if combinations_checked >= max_combinations:
                print_finding(f"Reached maximum combinations limit: {max_combinations}")
                return None
            
            const_step = 1 if end_const - start_const < 100 else 2
            offset_step = 1 if end_off - start_off < 32 else 2
            
            for const in range(int(start_const), int(end_const), const_step):
                if const >= max_constant:
                    continue
                
                for offset in range(int(start_off), int(end_off), offset_step):
                    if offset >= max_offset:
                        continue
                    
                    combinations_checked += 1
                    if combinations_checked % 10000 == 0:  # Update progress periodically
                        print_progress(const, offset, time.time() - start_time, combinations_checked)
                    
                    # Try the combination
                    if extract_bits(candidate_key, num_bits, offset, const) == expected:
                        print_finding(f"Found match after checking {combinations_checked:,} combinations")
                        return const, offset
                    
                    # Try nearby values for fine-tuning
                    for c_adj in [-1, 1]:
                        adj_const = const + c_adj
                        if 0 <= adj_const < max_constant:
                            for o_adj in [-1, 1]:
                                adj_offset = offset + o_adj
                                if 0 <= adj_offset < max_offset:
                                    combinations_checked += 1
                                    if extract_bits(candidate_key, num_bits, adj_offset, adj_const) == expected:
                                        print_finding(f"Found match after checking {combinations_checked:,} combinations")
                                        return adj_const, adj_offset
    
    print_finding(f"No match found after checking {combinations_checked:,} combinations in {time.time() - start_time:.1f} seconds")
    return None

def parse_line(line: str) -> Optional[dict]:
    """Parse a line from bread.txt."""
    # Match Full Candidate Key
    key_match = re.search(r'Full Candidate Key = (0x[0-9a-fA-F]+)', line)
    if key_match:
        return {'type': 'key', 'value': int(key_match.group(1), 16)}
    
    # Match Expected value
    expected_match = re.search(r'Expected for index \d+: (0x[0-9a-fA-F]+)', line)
    if expected_match:
        return {'type': 'expected', 'value': int(expected_match.group(1), 16)}
    
    # Match Index
    index_match = re.search(r'Index (\d+):', line)
    if index_match:
        return {'type': 'index', 'value': int(index_match.group(1))}
    
    return None

def analyze_patterns(results: Dict[int, Tuple[int, int]]) -> Dict[str, List[str]]:
    findings = {
        'constant_patterns': [],
        'offset_patterns': [],
        'mathematical_relationships': [],
        'bit_patterns': [],
        'sequence_patterns': [],
        'combined_patterns': [],
        'higher_index_patterns': [],
        'progressive_patterns': []  # New category
    }
    
    # Enhanced analysis for higher indices
    all_indices = sorted(KNOWN_SOLUTIONS.keys())
    for i in range(len(all_indices)-1):
        idx = all_indices[i]
        next_idx = all_indices[i+1]
        val = KNOWN_SOLUTIONS[idx]
        next_val = KNOWN_SOLUTIONS[next_idx]
        
        # Analyze growth patterns
        growth_ratio = next_val / val
        if growth_ratio.is_integer():
            findings['progressive_patterns'].append(
                f"Value grows by factor of {int(growth_ratio)} from index {idx} to {next_idx}"
            )
        
        # Analyze bit patterns
        val_bits = bin(val)[2:].zfill(256)
        next_val_bits = bin(next_val)[2:].zfill(256)
        common_prefix = 0
        for b1, b2 in zip(val_bits, next_val_bits):
            if b1 == b2:
                common_prefix += 1
            else:
                break
        findings['progressive_patterns'].append(
            f"Indices {idx}-{next_idx} share {common_prefix} leading bits"
        )
        
        # Analyze mathematical relationships
        if next_val - val < 1000:
            findings['progressive_patterns'].append(
                f"Small increment ({next_val - val}) between indices {idx}-{next_idx}"
            )
        
        # Look for special number patterns
        if val & 0xFF == next_val & 0xFF:
            findings['progressive_patterns'].append(
                f"Indices {idx}-{next_idx} share same lower byte: {hex(val & 0xFF)}"
            )
    
    indices = sorted(results.keys())
    constants = [results[i][0] for i in indices]
    offsets = [results[i][1] for i in indices]
    
    # Analyze constant patterns
    for i in range(1, len(constants)):
        diff = constants[i] - constants[i-1]
        if diff != 0:
            findings['constant_patterns'].append(
                f"Constant difference between indices {indices[i-1]}-{indices[i]}: {diff}"
            )
    
    # Analyze offset patterns
    for i in range(1, len(offsets)):
        diff = offsets[i] - offsets[i-1]
        if diff != 0:
            findings['offset_patterns'].append(
                f"Offset difference between indices {indices[i-1]}-{indices[i]}: {diff}"
            )
    
    # Analyze mathematical relationships
    for i in range(len(indices)-1):
        idx1, idx2 = indices[i], indices[i+1]
        c1, o1 = results[idx1]
        c2, o2 = results[idx2]
        
        # Multiplicative relationships
        if c1 != 0 and c2 % c1 == 0:
            findings['mathematical_relationships'].append(
                f"Constant {c2} is {c2//c1}x constant {c1} (indices {idx1}, {idx2})"
            )
        
        # Additive relationships
        if c2 - c1 == idx2 - idx1:
            findings['mathematical_relationships'].append(
                f"Constant increment matches index increment for indices {idx1}, {idx2}"
            )
        
        # Offset relationships
        if o1 != 0 and o2 % o1 == 0:
            findings['mathematical_relationships'].append(
                f"Offset {o2} is {o2//o1}x offset {o1} (indices {idx1}, {idx2})"
            )
        
        # Combined relationships
        if o1 != 0 and c1 != 0:
            if o2/o1 == c2/c1:
                findings['combined_patterns'].append(
                    f"Constant and offset scale proportionally between indices {idx1}, {idx2} (factor: {o2/o1})"
                )
    
    # Analyze bit patterns
    for i in range(len(indices)):
        idx = indices[i]
        c, o = results[idx]
        
        # Check for power of 2 patterns
        if c & (c - 1) == 0 and c != 0:
            findings['bit_patterns'].append(
                f"Constant {c} at index {idx} is a power of 2"
            )
        
        # Check for bit alignment patterns
        if o % 8 == 0:
            findings['bit_patterns'].append(
                f"Offset {o} at index {idx} is byte-aligned"
            )
        
        # Check for bit manipulation patterns
        if c & (1 << (idx % 32)) != 0:
            findings['bit_patterns'].append(
                f"Constant {c} at index {idx} has bit {idx % 32} set"
            )
    
    # Analyze sequence patterns
    def is_arithmetic_sequence(nums, window=3):
        if len(nums) < window:
            return False
        diffs = set(nums[i] - nums[i-1] for i in range(1, len(nums)))
        return len(diffs) == 1
    
    def is_geometric_sequence(nums, window=3):
        if len(nums) < window or 0 in nums:
            return False
        ratios = set(nums[i]/nums[i-1] for i in range(1, len(nums)))
        return len(ratios) == 1
    
    # Check for arithmetic and geometric sequences
    for i in range(len(indices)-2):
        const_window = constants[i:i+3]
        offset_window = offsets[i:i+3]
        
        if is_arithmetic_sequence(const_window):
            findings['sequence_patterns'].append(
                f"Constants form arithmetic sequence at indices {indices[i]}-{indices[i+2]}"
            )
        
        if is_geometric_sequence(const_window):
            findings['sequence_patterns'].append(
                f"Constants form geometric sequence at indices {indices[i]}-{indices[i+2]}"
            )
        
        if is_arithmetic_sequence(offset_window):
            findings['sequence_patterns'].append(
                f"Offsets form arithmetic sequence at indices {indices[i]}-{indices[i+2]}"
            )
        
        if is_geometric_sequence(offset_window):
            findings['sequence_patterns'].append(
                f"Offsets form geometric sequence at indices {indices[i]}-{indices[i+2]}"
            )
    
    # Look for Fibonacci-like sequences
    def is_fibonacci_like(nums, window=4):
        if len(nums) < window:
            return False
        for i in range(2, len(nums)):
            if abs(nums[i] - (nums[i-1] + nums[i-2])) > 1:  # Allow small rounding errors
                return False
        return True
    
    for i in range(len(indices)-3):
        const_window = constants[i:i+4]
        if is_fibonacci_like(const_window):
            findings['sequence_patterns'].append(
                f"Constants show Fibonacci-like pattern at indices {indices[i]}-{indices[i+3]}"
            )
    
    return findings

def analyze_candidate_key_relationships(candidate_key: int, index: int, constant: int, offset: int, expected: int) -> List[str]:
    """Analyze relationships between candidate key and final value."""
    relationships = []
    
    # Analyze how the candidate key transforms into the final value
    extracted = extract_bits(candidate_key, index, offset, constant)
    if extracted == expected:
        # Analyze the transformation path
        shifted = candidate_key >> offset
        with_constant = shifted + constant
        masked = with_constant & ((1 << index) - 1)
        
        relationships.append(f"Index {index} transformation:")
        relationships.append(f"  1. Original candidate key: {hex(candidate_key)}")
        relationships.append(f"  2. After right shift by {offset}: {hex(shifted)}")
        relationships.append(f"  3. After adding constant {constant}: {hex(with_constant)}")
        relationships.append(f"  4. After masking to {index} bits: {hex(masked)} (expected: {hex(expected)})")
        
        # Check for special relationships
        if constant == index:
            relationships.append(f"  * Constant equals index number")
        if offset == index * 8:
            relationships.append(f"  * Offset is 8 times the index")
        if constant == (1 << (index % 8)):
            relationships.append(f"  * Constant is a power of 2 related to index")
    
    return relationships

def analyze_computation_algorithm(index: int, txid_hex: str) -> Dict[str, Any]:
    """Analyze the computation algorithm for patterns."""
    analysis = {
        'index': index,
        'steps': [],
        'patterns': []
    }
    
    # Step 1: Convert txid to integer
    txid_int = int(txid_hex, 16)
    analysis['steps'].append({
        'step': 'txid_conversion',
        'input': txid_hex,
        'output': hex(txid_int),
        'bits_set': bin(txid_int).count('1')
    })
    
    # Step 2: Multiply by index
    combined = (txid_int * index) % (2**256)
    analysis['steps'].append({
        'step': 'multiplication',
        'input': hex(txid_int),
        'multiplier': index,
        'output': hex(combined),
        'bits_set': bin(combined).count('1')
    })
    
    # Step 3: Compute modular exponentiation
    result = pow(combined, 3, ORDER)
    analysis['steps'].append({
        'step': 'modular_exp',
        'input': hex(combined),
        'exponent': 3,
        'modulus': hex(ORDER),
        'output': hex(result),
        'bits_set': bin(result).count('1')
    })
    
    # Analyze patterns
    if index in KNOWN_SOLUTIONS:
        expected = KNOWN_SOLUTIONS[index]
        analysis['patterns'].extend([
            f"Expected output: {hex(expected)}",
            f"Bits set in expected: {bin(expected).count('1')}",
            f"Leading zeros in expected: {(expected.bit_length() // 4) * 4}",
            f"Significant bits: {hex(expected & ((1 << 32) - 1))}"
        ])
    
    return analysis

def analyze_pattern_evolution(index: int, value: int) -> Dict[str, Any]:
    """
    Analyze how patterns evolve across indices.
    """
    evolution = {
        'index': index,
        'patterns': detect_mathematical_patterns(value),
        'entropy': analyze_bit_entropy(value),
        'chain_analysis': {}
    }
    
    # Analyze chain relationships
    if index > 1 and (index-1) in KNOWN_SOLUTIONS:
        prev_value = KNOWN_SOLUTIONS[index-1]
        chain_val, significant, L = determine_chain_value(prev_value, index)
        evolution['chain_analysis'] = {
            'expected_significant': significant,
            'actual_significant': value & ((1 << (4*L)) - 1),
            'L_value': L,
            'matches_chain': significant == (value & ((1 << (4*L)) - 1))
        }
    
    # Analyze bit growth
    if index > 1:
        evolution['bit_growth'] = {
            'total_bits': value.bit_length(),
            'set_bits': bin(value).count('1'),
            'bit_density': bin(value).count('1') / value.bit_length()
        }
    
    return evolution

def validate_pattern_requirements(index: int, value: int) -> List[str]:
    """
    Validate if the value meets all pattern requirements for its index.
    """
    issues = []
    
    # Check bit requirements
    if index in BIT_REQUIREMENTS:
        required_bits = BIT_REQUIREMENTS[index]
        actual_bits = bin(value).count('1')
        if actual_bits != required_bits:
            issues.append(f"Bit count mismatch: expected {required_bits}, got {actual_bits}")
    
    # Check chain relationship
    if index > 1 and (index-1) in KNOWN_SOLUTIONS:
        prev_value = KNOWN_SOLUTIONS[index-1]
        _, significant, L = determine_chain_value(prev_value, index)
        actual_significant = value & ((1 << (4*L)) - 1)
        if significant != actual_significant:
            issues.append(f"Chain pattern mismatch at L={L}")
    
    # Check mathematical patterns
    patterns = detect_mathematical_patterns(value)
    if 'power_of_2' in patterns and index > 10:
        issues.append("Unexpected power of 2 pattern in higher index")
    
    # Check entropy requirements
    entropy_stats = analyze_bit_entropy(value)
    if entropy_stats['bit_balance'] > 0.3:
        issues.append(f"High bit imbalance: {entropy_stats['bit_balance']:.3f}")
    
    return issues

def main():
    current_index = None
    current_key = None
    current_expected = None
    results = {}
    key_relationships = []
    computation_analyses = []
    pattern_evolution = []
    validation_issues = []
    
    # Add overall timeout
    total_start_time = time.time()
    max_total_time = 300  # 5 minutes total timeout
    
    print("Starting analysis...", flush=True)
    
    try:
        with open('bread.txt', 'r') as f:
            for line in f:
                # Check total timeout
                if time.time() - total_start_time > max_total_time:
                    print_finding("Total analysis timeout reached (5 minutes)")
                    break
                
                parsed = parse_line(line)
                if not parsed:
                    continue

                if parsed['type'] == 'index':
                    if all(x is not None for x in [current_index, current_key, current_expected]):
                        print_finding(f"Processing Index {current_index}...")
                        
                        # Try regular search first
                        result = find_constant_and_offset(current_key, current_expected, current_index)
                        
                        # If no result, try systematic search with timeout
                        if not result:
                            print_finding("Regular search failed, trying systematic search...")
                            result = systematic_search(
                                current_key, 
                                current_expected, 
                                current_index,
                                timeout_seconds=30,  # 30 seconds timeout per index
                                max_combinations=500000  # Limit combinations per index
                            )
                        
                        if result:
                            results[current_index] = result
                            print_finding(f"Found result for index {current_index}: constant={result[0]}, offset={result[1]}")
                            
                            # Enhanced analysis
                            constant, offset = result
                            
                            # Analyze key relationships
                            relationships = analyze_candidate_key_relationships(
                                current_key, current_index, constant, offset, current_expected
                            )
                            key_relationships.extend(relationships)
                            
                            # Analyze computation algorithm
                            comp_analysis = analyze_computation_algorithm(
                                current_index,
                                "08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15"
                            )
                            computation_analyses.append(comp_analysis)
                            
                            # New pattern evolution analysis
                            evolution = analyze_pattern_evolution(current_index, current_expected)
                            pattern_evolution.append(evolution)
                            
                            # Validate patterns
                            issues = validate_pattern_requirements(current_index, current_expected)
                            if issues:
                                validation_issues.append({
                                    'index': current_index,
                                    'issues': issues
                                })
                        else:
                            print_finding(f"No result found for index {current_index}")
                    
                    current_index = parsed['value']
                    current_key = None
                    current_expected = None
                elif parsed['type'] == 'key':
                    current_key = parsed['value']
                elif parsed['type'] == 'expected':
                    current_expected = parsed['value']

    except KeyboardInterrupt:
        print_finding("\nAnalysis interrupted by user")
    
    total_time = time.time() - total_start_time
    print_finding(f"\nTotal analysis time: {total_time:.1f} seconds")
    
    # Print enhanced results
    print_finding("\nFound Matches:")
    for index in sorted(results.keys()):
        constant, offset = results[index]
        print_finding(f"Index {index}: constant {constant}, offset {offset}")
    
    if key_relationships:
        print_finding("\nCandidate Key Relationships:")
        for rel in key_relationships:
            print_finding(rel)
    
    if computation_analyses:
        print_finding("\nComputation Algorithm Analysis:")
        for analysis in computation_analyses:
            print_finding(f"\nIndex {analysis['index']}:")
            for step in analysis['steps']:
                print_finding(f"  {step['step']}:")
                for k, v in step.items():
                    if k != 'step':
                        print_finding(f"    {k}: {v}")
            if analysis['patterns']:
                print_finding("  Patterns:")
                for pattern in analysis['patterns']:
                    print_finding(f"    {pattern}")
    
    if pattern_evolution:
        print_finding("\nPattern Evolution Analysis:")
        for evolution in pattern_evolution:
            print_finding(f"\nIndex {evolution['index']}:")
            print_finding(f"  Patterns: {evolution['patterns']}")
            print_finding(f"  Entropy: {evolution['entropy']}")
            if evolution['chain_analysis']:
                print_finding("  Chain Analysis:")
                for k, v in evolution['chain_analysis'].items():
                    print_finding(f"    {k}: {v}")
            if 'bit_growth' in evolution:
                print_finding("  Bit Growth:")
                for k, v in evolution['bit_growth'].items():
                    print_finding(f"    {k}: {v}")
    
    if validation_issues:
        print_finding("\nValidation Issues:")
        for issue_set in validation_issues:
            print_finding(f"\nIndex {issue_set['index']}:")
            for issue in issue_set['issues']:
                print_finding(f"  - {issue}")
    
    # Analyze and print patterns
    findings = analyze_patterns(results)
    
    print_finding("\nPattern Analysis:")
    for category, patterns in findings.items():
        if patterns:
            print_finding(f"\n{category.replace('_', ' ').title()}:")
            for pattern in patterns:
                print_finding(f"- {pattern}")

if __name__ == "__main__":
    main() 