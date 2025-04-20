import math
from collections import defaultdict
import os

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up one level from src/

# Construct the correct path to the data file
DATA_FILE = os.path.join(project_root, 'data', '32bHex.txt')

try:
    with open(DATA_FILE, 'r') as f:
        # Your existing code here
        hex_strings = [line.strip() for line in f if line.strip()]
    
    # Rest of your modexp testing code...

except FileNotFoundError:
    print(f"\nError: Could not find the data file at: {os.path.abspath(DATA_FILE)}")
    print("\nCurrent directory structure:")
    print(f"Current directory: {os.getcwd()}")
    print(f"Project root: {os.path.dirname(os.getcwd())}")
    print(f"Expected data file: {os.path.abspath(DATA_FILE)}")
    print("\nPlease ensure your file exists at the correct location.")
    
except Exception as e:
    print(f"Error: {e}")

class ModExpPrecomp:
    """Modular exponentiation with precomputation, based on the approach from 
    https://github.com/weikengchen/mod_exp_with_precomputation"""
    
    def __init__(self, base, modulus):
        self.base = base
        self.modulus = modulus
        self.precomp_table = self._build_precomp_table()
    
    def _build_precomp_table(self):
        table = {}
        # Precompute powers of 2 up to modulus size
        max_power = int(math.log2(self.modulus))
        current = self.base
        for i in range(max_power + 1):
            power = 1 << i  # 2^i
            table[power] = current
            current = (current * current) % self.modulus
        
        # Add some small odd powers for optimization
        table[3] = (self.base * self.base * self.base) % self.modulus
        return table
    
    def modexp(self, exponent):
        """Compute base^exponent mod modulus using precomputed values."""
        if exponent == 0:
            return 1
        
        # Find largest precomputed power less than exponent
        max_precomp = max(k for k in self.precomp_table.keys() if k <= exponent)
        
        # Use precomputed value and recurse for remainder
        remainder = exponent - max_precomp
        if remainder == 0:
            return self.precomp_table[max_precomp]
        else:
            return (self.precomp_table[max_precomp] * 
                   self.modexp(remainder)) % self.modulus

def check_stark_patterns(values, M31_MODULUS):
    """Check for STARK-specific patterns in a sequence of values."""
    patterns = {
        'power_of_2': False,
        'fibonacci_like': False,
        'poseidon_state': False
    }
    
    def is_power_of_2(n):
        """Check if n is a power of 2."""
        return n > 0 and (n & (n - 1)) == 0
    
    # Check for power of 2 sequence
    if len(values) >= 3:
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        if all(is_power_of_2(abs(d)) for d in diffs) and any(d != 0 for d in diffs):
            patterns['power_of_2'] = True
    
    # Check for Fibonacci-like sequence (each value is sum of previous two mod M31)
    if len(values) >= 3:
        is_fibonacci = True
        has_nonzero = False
        for i in range(2, len(values)):
            expected = (values[i-1] + values[i-2]) % M31_MODULUS
            if values[i] != expected:
                is_fibonacci = False
                break
            if values[i] != 0 or values[i-1] != 0 or values[i-2] != 0:
                has_nonzero = True
        patterns['fibonacci_like'] = is_fibonacci and has_nonzero
    
    # Check for potential Poseidon state pattern
    if len(values) >= 4:
        # Check if values form a valid Poseidon state
        state_valid = True
        has_nonzero = False
        
        # Check values are in M31 field
        for v in values:
            if v >= M31_MODULUS or v < 0:
                state_valid = False
                break
            if v != 0:
                has_nonzero = True
        
        # Check for Poseidon-like patterns
        if state_valid and has_nonzero:
            # Check for MDS-like properties
            # In Poseidon, state elements often have linear relationships
            diffs = []
            for i in range(len(values)-1):
                for j in range(i+1, len(values)):
                    if values[i] != 0:  # Avoid division by zero
                        ratio = (values[j] * pow(values[i], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS
                        diffs.append(ratio)
            
            # Look for consistent ratios or differences that could indicate MDS matrix application
            if len(set(diffs)) <= 2:  # Allow for at most 2 different ratios
                patterns['poseidon_state'] = True
    
    return patterns

def analyze_sequence_for_modexp(hex_strings):
    analysis = {
        'potential_bases': set(),
        'potential_exponents': set(),
        'modexp_sequences': defaultdict(list),
        'sliding_window_patterns': [],
        'power_residues': defaultdict(list),
        'multiplicative_orders': defaultdict(list),
        'primitive_roots': set(),
        'stark_patterns': {
            'power_of_2_sequences': [],
            'fibonacci_like': [],
            'poseidon_state': []
        },
        'circle_patterns': {
            'curve_points': [],
            'pedersen_hashes': [],
            'rescue_states': []
        },
        'poseidon2_patterns': {
            'state_transitions': [],
            'round_constants': set(),
            'mds_patterns': [],
            'ark_patterns': []
        },
        'bit_patterns': {
            'hamming_weight_sequences': [],
            'run_length_sequences': [],
            'bit_transition_patterns': [],
            'bit_position_correlations': []
        },
        'stark_witness': {
            'trace_polynomials': [],
            'boundary_constraints': [],
            'transition_constraints': [],
            'composition_polynomials': []
        }
    }
    
    M31_MODULUS = 2**31 - 1
    PHI_M31 = M31_MODULUS - 1  # Euler's totient for prime modulus
    
    # Circle curve parameters
    CIRCLE_A = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001
    CIRCLE_B = 0x00
    
    def is_circle_point(x, y):
        """Check if (x,y) is a point on the Circle curve."""
        if x >= M31_MODULUS or y >= M31_MODULUS:
            return False
        if x == 0 and y == 0:
            return False  # Exclude point at infinity
        # Check y^2 = x^3 + ax + b
        lhs = (y * y) % M31_MODULUS
        rhs = ((x * x * x) % M31_MODULUS + (CIRCLE_A * x) % M31_MODULUS + CIRCLE_B) % M31_MODULUS
        return lhs == rhs
    
    def is_pedersen_hash(points):
        """Check if sequence could be a Pedersen hash computation."""
        if len(points) < 2:
            return False
        if any(x == 0 and y == 0 for x, y in points):
            return False  # Exclude points at infinity
        # Check for linear combinations of points
        # In Pedersen hash, points should be on the curve and have specific relationships
        if not all(is_circle_point(x, y) for x, y in points):
            return False
        # Check for potential scalar multiplication patterns
        x_diffs = []
        y_diffs = []
        for i in range(len(points)-1):
            if points[i][0] != 0:  # Avoid division by zero
                x_diff = (points[i+1][0] * pow(points[i][0], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS
                x_diffs.append(x_diff)
            if points[i][1] != 0:
                y_diff = (points[i+1][1] * pow(points[i][1], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS
                y_diffs.append(y_diff)
        # Look for consistent ratios that could indicate scalar multiplication
        return len(set(x_diffs)) <= 2 and len(set(y_diffs)) <= 2
    
    def is_rescue_state(values):
        """Check if sequence could be a Rescue state."""
        if len(values) != 4:  # Rescue typically uses 4-element state
            return False
        if all(v == 0 for v in values):
            return False  # Exclude all-zero state
        # Check for Rescue-like patterns
        # Values should be in the field and show evidence of power maps
        has_nonzero = any(v != 0 for v in values)
        in_field = all(0 <= v < M31_MODULUS for v in values)
        # Check for power map patterns (x^alpha mod p)
        alpha = 3  # Typical Rescue power
        powers = [pow(v, alpha, M31_MODULUS) if v != 0 else 0 for v in values]
        has_power_pattern = len(set(powers)) > 1
        # Check for MDS-like patterns
        diffs = []
        for i in range(len(values)-1):
            for j in range(i+1, len(values)):
                if values[i] != 0:
                    ratio = (values[j] * pow(values[i], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS
                    diffs.append(ratio)
        has_mds_pattern = len(set(diffs)) <= 2
        return has_nonzero and in_field and has_power_pattern and has_mds_pattern
    
    def check_poseidon2_patterns(values1, values2):
        """Check for Poseidon2-specific patterns between two consecutive states."""
        if len(values1) != 4 or len(values2) != 4:
            return None
        
        result = {
            'is_valid': False,
            'type': None,
            'constants': None
        }
        
        # Check if values are in the field
        if not all(0 <= v < M31_MODULUS for v in values1 + values2):
            return result
        
        # Check for S-box pattern (x^7 in M31)
        sbox_outputs = [pow(v, 7, M31_MODULUS) if v != 0 else 0 for v in values1]
        if all(abs(v2 - v1) <= M31_MODULUS//2 for v1, v2 in zip(sbox_outputs, values2)):
            result['is_valid'] = True
            result['type'] = 'sbox'
            return result
        
        # Check for MDS pattern
        # In Poseidon2, MDS matrix multiplication should preserve certain relationships
        diffs1 = []
        diffs2 = []
        for i in range(len(values1)-1):
            for j in range(i+1, len(values1)):
                if values1[i] != 0:
                    ratio1 = (values1[j] * pow(values1[i], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS
                    diffs1.append(ratio1)
                if values2[i] != 0:
                    ratio2 = (values2[j] * pow(values2[i], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS
                    diffs2.append(ratio2)
        
        if len(set(diffs1)) <= 2 and len(set(diffs2)) <= 2:
            result['is_valid'] = True
            result['type'] = 'mds'
            return result
        
        # Check for ARK pattern (addition of round constants)
        # Try to find potential round constants
        constants = [(v2 - v1) % M31_MODULUS for v1, v2 in zip(values1, values2)]
        if len(set(constants)) <= 2:  # Allow for at most 2 different constants
            result['is_valid'] = True
            result['type'] = 'ark'
            result['constants'] = constants
            return result
        
        return result
    
    def find_order(a, max_order=1000):
        """Find multiplicative order of a modulo M31_MODULUS."""
        if a == 0:
            return 0
        a = a % M31_MODULUS
        if math.gcd(a, M31_MODULUS) != 1:
            return 0
        for i in range(1, min(max_order, PHI_M31) + 1):
            if pow(a, i, M31_MODULUS) == 1:
                return i
        return -1  # Order is larger than max_order
    
    def is_primitive_root(a):
        """Check if a is a primitive root modulo M31_MODULUS."""
        if a == 0:
            return False
        order = find_order(a)
        return order == PHI_M31
    
    def is_power_of_2(n):
        """Check if n is a power of 2."""
        return n > 0 and (n & (n - 1)) == 0
    
    def analyze_bit_patterns(value):
        """Analyze bit patterns in a value."""
        if value == 0:
            return None
        
        # Convert to binary and analyze
        binary = bin(value)[2:]  # Remove '0b' prefix
        length = len(binary)
        
        # Calculate Hamming weight
        hamming_weight = binary.count('1')
        
        # Find run lengths
        runs = []
        current_run = 1
        for i in range(1, length):
            if binary[i] == binary[i-1]:
                current_run += 1
            else:
                runs.append((binary[i-1], current_run))
                current_run = 1
        runs.append((binary[-1], current_run))
        
        # Analyze bit transitions
        transitions = defaultdict(int)
        for i in range(1, length):
            transition = binary[i-1:i+1]
            transitions[transition] += 1
        
        # Find bit position correlations
        correlations = []
        for i in range(length-1):
            for j in range(i+1, length):
                if binary[i] == binary[j]:
                    correlations.append((i, j))
        
        return {
            'hamming_weight': hamming_weight,
            'runs': runs,
            'transitions': dict(transitions),
            'correlations': correlations,
            'length': length
        }
    
    def find_bit_sequences(values):
        """Find interesting sequences in bit patterns."""
        results = {
            'hamming': [],
            'runs': [],
            'transitions': [],
            'correlations': []
        }
        
        # Analyze consecutive values
        for i in range(len(values)-1):
            v1 = values[i]
            v2 = values[i+1]
            
            p1 = analyze_bit_patterns(v1)
            p2 = analyze_bit_patterns(v2)
            
            if p1 and p2:
                # Look for Hamming weight sequences
                if abs(p1['hamming_weight'] - p2['hamming_weight']) == 1:
                    results['hamming'].append((v1, v2))
                
                # Look for similar run length patterns
                if len(p1['runs']) == len(p2['runs']):
                    matching_runs = True
                    for r1, r2 in zip(p1['runs'], p2['runs']):
                        if abs(r1[1] - r2[1]) > 1:  # Allow for ±1 difference
                            matching_runs = False
                            break
                    if matching_runs:
                        results['runs'].append((v1, v2))
                
                # Look for similar transition patterns
                common_transitions = set(p1['transitions'].keys()) & set(p2['transitions'].keys())
                if len(common_transitions) >= 2:  # At least 2 common transition types
                    results['transitions'].append((v1, v2))
                
                # Look for similar correlation patterns
                if len(p1['correlations']) == len(p2['correlations']):
                    results['correlations'].append((v1, v2))
        
        return results
    
    def analyze_stark_witness_patterns(values):
        """Analyze patterns that could indicate STARK witness computations."""
        results = {
            'trace': [],
            'boundary': [],
            'transition': [],
            'composition': []
        }
        
        # Look for trace polynomial patterns
        # In STARK, trace polynomials often have regular step patterns
        for i in range(len(values)-3):
            window = values[i:i+4]
            # Check for arithmetic sequences mod M31
            diffs = [(window[j+1] - window[j]) % M31_MODULUS for j in range(len(window)-1)]
            if len(set(diffs)) == 1:  # Constant difference
                results['trace'].append(window)
            # Check for geometric sequences mod M31
            if all(v != 0 for v in window):
                ratios = [(window[j+1] * pow(window[j], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS 
                         for j in range(len(window)-1)]
                if len(set(ratios)) == 1:  # Constant ratio
                    results['trace'].append(window)
        
        # Look for boundary constraint patterns
        # Boundary constraints often involve specific values at start/end
        if len(values) >= 4:
            start_values = values[:2]
            end_values = values[-2:]
            # Check if start and end values have special relationships
            if any(v == 0 or v == 1 or v == M31_MODULUS-1 for v in start_values + end_values):
                results['boundary'].append((start_values, end_values))
        
        # Look for transition constraint patterns
        # Transition constraints often involve consecutive values
        for i in range(len(values)-2):
            triple = values[i:i+3]
            # Check for common STARK transition patterns
            # Example: x_{i+1} = x_i^2 mod M31
            if any(v != 0 for v in triple):
                # Check for square relationship
                if (triple[0] * triple[0]) % M31_MODULUS == triple[1]:
                    results['transition'].append(('square', triple))
                # Check for cube relationship
                if (triple[0] * triple[0] * triple[0]) % M31_MODULUS == triple[1]:
                    results['transition'].append(('cube', triple))
                # Check for inverse relationship
                if triple[0] != 0 and (triple[0] * triple[1]) % M31_MODULUS == 1:
                    results['transition'].append(('inverse', triple))
        
        # Look for composition polynomial patterns
        # Composition polynomials often combine multiple values
        for i in range(len(values)-3):
            window = values[i:i+4]
            # Check for linear combinations
            for j in range(1, len(window)):
                # Try to find linear relationship v[j] = a*v[0] + b
                if window[0] != 0:
                    a = (window[j] * pow(window[0], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS
                    b = (window[j] - (a * window[0])) % M31_MODULUS
                    if all((a * v + b) % M31_MODULUS == window[k] 
                          for k, v in enumerate(window[1:], 1)):
                        results['composition'].append(('linear', window, (a, b)))
        
        return results
    
    for hex_string in hex_strings:
        # Convert hex to int values in chunks of 8 (32 bits)
        chunks = [int(hex_string[i:i+8], 16) for i in range(0, len(hex_string), 8)]
        
        # Analyze STARK witness patterns
        witness_patterns = analyze_stark_witness_patterns(chunks)
        analysis['stark_witness']['trace_polynomials'].extend(witness_patterns['trace'])
        analysis['stark_witness']['boundary_constraints'].extend(witness_patterns['boundary'])
        analysis['stark_witness']['transition_constraints'].extend(witness_patterns['transition'])
        analysis['stark_witness']['composition_polynomials'].extend(witness_patterns['composition'])
        
        # Analyze bit patterns in sequences
        bit_sequences = find_bit_sequences(chunks)
        analysis['bit_patterns']['hamming_weight_sequences'].extend(bit_sequences['hamming'])
        analysis['bit_patterns']['run_length_sequences'].extend(bit_sequences['runs'])
        analysis['bit_patterns']['bit_transition_patterns'].extend(bit_sequences['transitions'])
        analysis['bit_patterns']['bit_position_correlations'].extend(bit_sequences['correlations'])
        
        # Look for Circle curve patterns
        for i in range(0, len(chunks)-1, 2):
            x, y = chunks[i] % M31_MODULUS, chunks[i+1] % M31_MODULUS
            if is_circle_point(x, y):
                analysis['circle_patterns']['curve_points'].append((x, y))
        
        # Look for Pedersen hash patterns
        window_size = 4
        for i in range(0, len(chunks)-window_size+1, 2):
            points = [(chunks[i+j] % M31_MODULUS, chunks[i+j+1] % M31_MODULUS) 
                     for j in range(0, window_size, 2)]
            if is_pedersen_hash(points):
                analysis['circle_patterns']['pedersen_hashes'].append(points)
        
        # Look for Rescue state patterns
        for i in range(len(chunks)-3):
            state = chunks[i:i+4]
            if is_rescue_state(state):
                analysis['circle_patterns']['rescue_states'].append(state)
        
        # Look for Poseidon2 patterns
        for i in range(0, len(chunks)-7, 4):
            state1 = [chunks[i+j] % M31_MODULUS for j in range(4)]
            state2 = [chunks[i+j+4] % M31_MODULUS for j in range(4)]
            
            result = check_poseidon2_patterns(state1, state2)
            if result['is_valid']:
                if result['type'] == 'sbox':
                    analysis['poseidon2_patterns']['state_transitions'].append({
                        'from': state1,
                        'to': state2,
                        'type': 'sbox'
                    })
                elif result['type'] == 'mds':
                    analysis['poseidon2_patterns']['mds_patterns'].append({
                        'input': state1,
                        'output': state2
                    })
                elif result['type'] == 'ark':
                    analysis['poseidon2_patterns']['ark_patterns'].append({
                        'state': state1,
                        'constants': result['constants']
                    })
                    for c in result['constants']:
                        analysis['poseidon2_patterns']['round_constants'].add(c)
        
        # Look for potential modexp sequences
        for i in range(len(chunks)-2):
            base = chunks[i] % M31_MODULUS
            exp = chunks[i+1] % (M31_MODULUS-1)  # Euler's theorem
            result = chunks[i+2] % M31_MODULUS
            
            # Test if it could be a modexp sequence
            if pow(base, exp, M31_MODULUS) == result:
                analysis['potential_bases'].add(base)
                analysis['potential_exponents'].add(exp)
                analysis['modexp_sequences'][hex_string].append((base, exp, result))
        
        # Look for sliding window patterns
        window_size = 4
        for i in range(len(chunks) - window_size + 1):
            window = chunks[i:i+window_size]
            # Check for geometric progressions
            ratios = []
            for j in range(1, len(window)):
                if window[j-1] != 0:
                    ratio = (window[j] * pow(window[j-1], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS
                    ratios.append(ratio)
            if len(set(ratios)) == 1:  # All ratios are the same
                analysis['sliding_window_patterns'].append({
                    'window': window,
                    'ratio': ratios[0]
                })
            
            # Check for STARK-specific patterns
            window_values = [v % M31_MODULUS for v in window]
            patterns = check_stark_patterns(window_values, M31_MODULUS)
            if patterns['power_of_2']:
                analysis['stark_patterns']['power_of_2_sequences'].append(window_values)
            if patterns['fibonacci_like']:
                analysis['stark_patterns']['fibonacci_like'].append(window_values)
            if patterns['poseidon_state']:
                analysis['stark_patterns']['poseidon_state'].append(window_values)
        
        # Look for power residues and multiplicative orders
        for chunk in chunks:
            value = chunk % M31_MODULUS
            # Check if it's a quadratic residue
            if pow(value, (M31_MODULUS-1)//2, M31_MODULUS) == 1:
                analysis['power_residues'][2].append(value)
            # Check if it's a cubic residue
            if pow(value, (M31_MODULUS-1)//3, M31_MODULUS) == 1:
                analysis['power_residues'][3].append(value)
            
            # Find multiplicative order
            order = find_order(value)
            if order > 0:
                analysis['multiplicative_orders'][order].append(value)
                if order == PHI_M31:
                    analysis['primitive_roots'].add(value)
    
    return analysis

def test_sequence(hex_string):
    """Test a single hex string for modular exponentiation patterns."""
    M31_MODULUS = 2**31 - 1
    results = []
    
    # Convert hex string to bytes and analyze in 8-byte chunks
    for i in range(0, len(hex_string)-24, 8):
        try:
            v1 = int(hex_string[i:i+8], 16)
            v2 = int(hex_string[i+8:i+16], 16)
            v3 = int(hex_string[i+16:i+24], 16)
            
            if v1 < M31_MODULUS and v2 < M31_MODULUS and v3 < M31_MODULUS:
                # Create ModExp instance for testing
                modexp = ModExpPrecomp(v1, M31_MODULUS)
                
                # Test if values form modexp relationship
                if modexp.modexp(v2) == v3:
                    results.append({
                        'offset': i//2,
                        'base': v1,
                        'exponent': v2,
                        'result': v3,
                        'precomp_table': modexp.precomp_table.copy()
                    })
        except ValueError:
            continue
    
    return results

def analyze_stark_patterns(hex_strings):
    """Analyze sequences for STARK-specific patterns."""
    M31_MODULUS = 2**31 - 1
    analysis = {
        'air_constraints': [],
        'step_functions': [],
        'permutation_cycles': [],
        'merkle_paths': []
    }
    
    def check_air_constraint(values):
        """Check if values satisfy typical AIR constraints."""
        if len(values) < 3:
            return False
        # Check for polynomial transitions
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        if all(d == diffs[0] for d in diffs):
            return True
        # Check for multiplicative relationships
        if all(values[i+1] * values[i] % M31_MODULUS == values[i+2] % M31_MODULUS 
               for i in range(len(values)-2)):
            return True
        return False
    
    def detect_permutation_cycle(values):
        """Detect if values form a permutation cycle in M31 field."""
        seen = set()
        current = values[0]
        cycle = []
        while current not in seen and len(cycle) < len(values):
            seen.add(current)
            cycle.append(current)
            # Apply permutation (using field multiplication)
            current = (current * values[1]) % M31_MODULUS
        return cycle if len(cycle) > 1 else None

    # Convert hex strings to integer values
    sequences = []
    for hex_string in hex_strings:
        values = [int(hex_string[i:i+8], 16) % M31_MODULUS 
                 for i in range(0, len(hex_string), 8)]
        sequences.append(values)
    
    # Analyze each sequence
    for seq in sequences:
        # Check for AIR constraints
        window_size = 4
        for i in range(len(seq) - window_size + 1):
            window = seq[i:i+window_size]
            if check_air_constraint(window):
                analysis['air_constraints'].append({
                    'window': window,
                    'offset': i
                })
        
        # Look for step function patterns
        for i in range(len(seq) - 2):
            x1, x2, x3 = seq[i:i+3]
            # Check for typical STARK step patterns
            if (x2 * x2) % M31_MODULUS == x3 % M31_MODULUS:
                analysis['step_functions'].append({
                    'input': x1,
                    'intermediate': x2,
                    'output': x3,
                    'type': 'square'
                })
            elif (x1 * x2) % M31_MODULUS == x3 % M31_MODULUS:
                analysis['step_functions'].append({
                    'input': x1,
                    'intermediate': x2,
                    'output': x3,
                    'type': 'multiply'
                })
        
        # Look for permutation cycles
        if len(seq) >= 2:
            cycle = detect_permutation_cycle(seq)
            if cycle:
                analysis['permutation_cycles'].append(cycle)
        
        # Look for potential Merkle paths
        for i in range(len(seq) - 3):
            window = seq[i:i+4]
            # Check if values could represent Merkle path nodes
            if all(v < M31_MODULUS for v in window):
                # Check if they follow Merkle-like combining pattern
                combined = [(window[i] * window[i+1]) % M31_MODULUS 
                           for i in range(len(window)-1)]
                if any(c in seq for c in combined):
                    analysis['merkle_paths'].append({
                        'nodes': window,
                        'combined': combined
                    })
    
    return analysis

def analyze_stark_witness(hex_strings):
    """Analyze sequences for STARK witness patterns."""
    M31_MODULUS = 2**31 - 1
    analysis = {
        'trace_polynomials': [],
        'boundary_constraints': [],
        'transition_constraints': [],
        'composition_polynomials': []
    }
    
    def is_power_of_two(n):
        return n > 0 and (n & (n - 1)) == 0
    
    def check_trace_polynomial(values):
        """Check if values form a valid trace polynomial."""
        if len(values) < 4:
            return False
        # Check if length is power of 2
        if not is_power_of_two(len(values)):
            return False
        # Check for polynomial interpolation pattern
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        second_diffs = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
        return all(d == second_diffs[0] for d in second_diffs)
    
    def check_boundary_constraint(values):
        """Check if values satisfy boundary constraints."""
        if len(values) < 2:
            return False
        # Check first and last values
        first, last = values[0], values[-1]
        # Common boundary patterns
        return (first == 1 and last == 1) or \
               (first == 0 and last == 0) or \
               (first * last % M31_MODULUS == 1)
    
    def check_transition_constraint(values):
        """Check if values satisfy transition constraints."""
        if len(values) < 3:
            return False
        # Check for common transition patterns
        for i in range(len(values)-2):
            x1, x2, x3 = values[i:i+3]
            # Check for multiplication transition
            if (x1 * x2) % M31_MODULUS == x3:
                return True
            # Check for addition transition
            if (x1 + x2) % M31_MODULUS == x3:
                return True
            # Check for exponentiation transition
            if pow(x1, x2, M31_MODULUS) == x3:
                return True
        return False
    
    def check_composition_polynomial(values):
        """Check if values form a composition polynomial."""
        if len(values) < 4:
            return False
        # Check for typical composition polynomial patterns
        # These often combine multiple constraints
        constraints_satisfied = 0
        
        # Check for degree bound pattern
        if all(v < M31_MODULUS//2 for v in values):
            constraints_satisfied += 1
            
        # Check for copy constraint pattern
        pairs = zip(values[::2], values[1::2])
        if any(a == b for a, b in pairs):
            constraints_satisfied += 1
            
        # Check for permutation argument pattern
        if len(set(values)) == len(values):  # All values unique
            constraints_satisfied += 1
            
        return constraints_satisfied >= 2
    
    # Convert and analyze sequences
    for hex_string in hex_strings:
        values = [int(hex_string[i:i+8], 16) % M31_MODULUS 
                 for i in range(0, len(hex_string), 8)]
        
        # Check for trace polynomials
        if check_trace_polynomial(values):
            analysis['trace_polynomials'].append(values)
            
        # Check for boundary constraints
        if check_boundary_constraint(values):
            analysis['boundary_constraints'].append(values)
            
        # Check for transition constraints
        if check_transition_constraint(values):
            analysis['transition_constraints'].append(values)
            
        # Check for composition polynomials
        if check_composition_polynomial(values):
            analysis['composition_polynomials'].append(values)
    
    return analysis

def analyze_poseidon2_patterns(hex_strings):
    """Analyze sequences for Poseidon2-specific patterns."""
    M31_MODULUS = 2**31 - 1
    analysis = {
        'state_transitions': [],
        'round_constants': set(),
        'mds_matrices': [],
        'ark_patterns': []
    }
    
    def is_poseidon2_state(values):
        """Check if values could represent a Poseidon2 state."""
        if len(values) != 4:  # Poseidon2 typically uses 4-element states
            return False
        # Check if values are in M31 field
        return all(0 <= v < M31_MODULUS for v in values)
    
    def check_sbox_pattern(x1, x2):
        """Check if two values could represent Poseidon2 S-box transition."""
        # Poseidon2 uses x^7 as S-box
        return pow(x1, 7, M31_MODULUS) == x2
    
    def check_mds_pattern(state1, state2):
        """Check if two states could be related by MDS multiplication."""
        if len(state1) != 4 or len(state2) != 4:
            return False
        # Check for linear combinations
        sums = []
        for i in range(4):
            s = sum((state1[j] * (j+1)) % M31_MODULUS for j in range(4)) % M31_MODULUS
            if s == state2[i]:
                sums.append(True)
        return len(sums) >= 2  # At least 2 positions match MDS pattern
    
    def find_round_constants(states):
        """Try to identify potential round constants."""
        if len(states) < 2:
            return None
        # Look for consistent differences between states
        diffs = [(states[1][i] - states[0][i]) % M31_MODULUS for i in range(4)]
        if all(d < M31_MODULUS//2 for d in diffs):
            return diffs
        return None
    
    # Analyze sequences for Poseidon2 patterns
    for i in range(len(hex_strings)-1):
        values1 = [int(hex_strings[i][j:j+8], 16) % M31_MODULUS 
                  for j in range(0, len(hex_strings[i]), 8)]
        values2 = [int(hex_strings[i+1][j:j+8], 16) % M31_MODULUS 
                  for j in range(0, len(hex_strings[i+1]), 8)]
        
        # Check for valid state transitions
        if is_poseidon2_state(values1[:4]) and is_poseidon2_state(values2[:4]):
            state1, state2 = values1[:4], values2[:4]
            
            # Check for S-box patterns
            sbox_matches = sum(1 for j in range(4) 
                             if check_sbox_pattern(state1[j], state2[j]))
            if sbox_matches >= 1:  # At least one position matches S-box pattern
                analysis['state_transitions'].append({
                    'from': state1,
                    'to': state2,
                    'type': 'sbox'
                })
            
            # Check for MDS patterns
            if check_mds_pattern(state1, state2):
                analysis['mds_matrices'].append({
                    'from': state1,
                    'to': state2
                })
            
            # Look for round constants
            constants = find_round_constants([state1, state2])
            if constants:
                for c in constants:
                    analysis['round_constants'].add(c)
                analysis['ark_patterns'].append({
                    'state': state1,
                    'constants': constants
                })
    
    return analysis

def analyze_modexp_optimizations(hex_strings):
    """Analyze sequences for modular exponentiation optimization patterns."""
    M31_MODULUS = 2**31 - 1
    analysis = {
        'precomputed_tables': [],
        'window_patterns': [],
        'sliding_window_opts': [],
        'power_chains': []
    }
    
    def find_precomputed_values(values):
        """Find potential precomputed values for modexp."""
        if len(values) < 4:
            return None
        # Look for geometric progressions
        ratios = set()
        for i in range(1, len(values)):
            if values[i-1] != 0:
                ratio = (values[i] * pow(values[i-1], M31_MODULUS-2, M31_MODULUS)) % M31_MODULUS
                ratios.add(ratio)
        if len(ratios) == 1:  # Consistent ratio found
            return {
                'base': values[0],
                'ratio': list(ratios)[0],
                'length': len(values)
            }
        return None
    
    def detect_window_pattern(values):
        """Detect fixed or sliding window patterns."""
        if len(values) < 8:
            return None
        # Look for repeated subsequences
        for window_size in range(2, 5):
            windows = {}
            for i in range(len(values) - window_size + 1):
                window = tuple(values[i:i+window_size])
                if window in windows:
                    windows[window].append(i)
                else:
                    windows[window] = [i]
            # Check for frequently occurring windows
            frequent = [(w, pos) for w, pos in windows.items() if len(pos) > 1]
            if frequent:
                return {
                    'window_size': window_size,
                    'patterns': frequent[:3]  # Return top 3 patterns
                }
        return None
    
    def find_power_chain(values):
        """Find potential addition chain for exponentiation."""
        if len(values) < 3:
            return None
        chains = []
        for i in range(len(values)-2):
            x, y, z = values[i:i+3]
            # Check if z could be derived from x and y
            if z % M31_MODULUS in [(x + y) % M31_MODULUS, 
                                 (x * y) % M31_MODULUS,
                                 (x * x) % M31_MODULUS]:
                chains.append((x, y, z))
        return chains if chains else None
    
    # Analyze sequences
    for hex_string in hex_strings:
        values = [int(hex_string[i:i+8], 16) % M31_MODULUS 
                 for i in range(0, len(hex_string), 8)]
        
        # Look for precomputed tables
        precomp = find_precomputed_values(values)
        if precomp:
            analysis['precomputed_tables'].append(precomp)
        
        # Detect window patterns
        window = detect_window_pattern(values)
        if window:
            analysis['window_patterns'].append(window)
        
        # Look for sliding window optimizations
        for i in range(len(values) - 3):
            window = values[i:i+4]
            if all(v < M31_MODULUS//2 for v in window):  # Small values
                analysis['sliding_window_opts'].append(window)
        
        # Find power chains
        chains = find_power_chain(values)
        if chains:
            analysis['power_chains'].extend(chains)
    
    return analysis

def analyze_sequence_patterns(hex_strings):
    """Analyze specific patterns in the sequence."""
    M31_MODULUS = 2**31 - 1
    analysis = {
        'growth_ratios': [],
        'bit_patterns': [],
        'value_cycles': [],
        'special_values': []
    }
    
    # Convert all strings to values
    sequences = []
    for hex_string in hex_strings:
        values = [int(hex_string[i:i+8], 16) for i in range(0, len(hex_string), 8)]
        sequences.append(values)
    
    # Analyze growth ratios
    for i in range(len(sequences)-1):
        curr = sequences[i][0]  # Take first value of each sequence
        next_val = sequences[i+1][0]
        if curr != 0:
            ratio = next_val / curr
            analysis['growth_ratios'].append(ratio)
    
    # Analyze bit patterns
    for seq in sequences:
        for value in seq:
            if value == 0:
                continue
            bits = bin(value)[2:]  # Remove '0b' prefix
            # Look for interesting bit patterns
            if bits.count('1') == 1:  # Power of 2
                analysis['bit_patterns'].append({
                    'value': value,
                    'type': 'power_of_2',
                    'position': len(bits) - bits.rindex('1') - 1
                })
            elif bits.count('1') == bits.count('0'):  # Equal 1s and 0s
                analysis['bit_patterns'].append({
                    'value': value,
                    'type': 'balanced',
                    'length': len(bits)
                })
    
    # Look for value cycles
    seen_values = {}
    for seq in sequences:
        for value in seq:
            if value in seen_values:
                seen_values[value] += 1
            else:
                seen_values[value] = 1
    
    # Find cycles (values that appear multiple times)
    cycles = [(v, c) for v, c in seen_values.items() if c > 1]
    analysis['value_cycles'] = sorted(cycles, key=lambda x: x[1], reverse=True)
    
    # Look for special values
    for seq in sequences:
        for value in seq:
            # Check for values with special properties
            if value < 256:  # Small values
                analysis['special_values'].append({
                    'value': value,
                    'type': 'small'
                })
            elif bin(value).count('1') <= 2:  # Sparse binary representation
                analysis['special_values'].append({
                    'value': value,
                    'type': 'sparse'
                })
            elif value % 3 == 0 and value % 7 == 0:  # Divisible by both 3 and 7
                analysis['special_values'].append({
                    'value': value,
                    'type': 'composite'
                })
    
    return analysis

def main():
    try:
        with open(DATA_FILE, 'r') as f:
            # Your existing code here
            hex_strings = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"\nError: Could not find the data file at: {os.path.abspath(DATA_FILE)}")
        print("\nCurrent directory structure:")
        print(f"Current directory: {os.getcwd()}")
        print(f"Project root: {os.path.dirname(os.getcwd())}")
        print(f"Expected data file: {os.path.abspath(DATA_FILE)}")
        print("\nPlease ensure your file exists at the correct location.")
        
        return
    
    # Analyze sequences
    analysis = analyze_sequence_for_modexp(hex_strings)
    
    # Print results
    print("\nPotential ModExp Patterns Found:")
    print(f"Number of potential bases: {len(analysis['potential_bases'])}")
    print(f"Number of potential exponents: {len(analysis['potential_exponents'])}")
    print(f"Number of ModExp sequences: {len(analysis['modexp_sequences'])}")
    
    print("\nSliding Window Patterns Found:")
    print(f"Number of geometric progressions: {len(analysis['sliding_window_patterns'])}")
    for i, pattern in enumerate(analysis['sliding_window_patterns'][:5]):
        print(f"\nPattern {i+1}:")
        print(f"Window: {pattern['window']}")
        print(f"Ratio: {pattern['ratio']}")
    
    print("\nPower Residues Found:")
    for power, values in analysis['power_residues'].items():
        print(f"{power}th power residues: {len(values)} values")
        if values:
            print(f"Example values: {values[:5]}")
    
    print("\nMultiplicative Orders Found:")
    orders = sorted(analysis['multiplicative_orders'].keys())
    print(f"Number of distinct orders: {len(orders)}")
    print("Most common orders:")
    for order in orders[:5]:
        values = analysis['multiplicative_orders'][order]
        print(f"Order {order}: {len(values)} values")
        if values:
            print(f"Example values: {values[:3]}")
    
    print("\nPrimitive Roots Found:")
    print(f"Number of primitive roots: {len(analysis['primitive_roots'])}")
    if analysis['primitive_roots']:
        print(f"Example primitive roots: {list(analysis['primitive_roots'])[:5]}")
    
    print("\nSTARK-Specific Patterns Found:")
    print("Power of 2 Sequences:")
    print(f"Number found: {len(analysis['stark_patterns']['power_of_2_sequences'])}")
    if analysis['stark_patterns']['power_of_2_sequences']:
        print(f"Example sequences: {analysis['stark_patterns']['power_of_2_sequences'][:3]}")
    
    print("\nFibonacci-like Sequences:")
    print(f"Number found: {len(analysis['stark_patterns']['fibonacci_like'])}")
    if analysis['stark_patterns']['fibonacci_like']:
        print(f"Example sequences: {analysis['stark_patterns']['fibonacci_like'][:3]}")
    
    print("\nPotential Poseidon States:")
    print(f"Number found: {len(analysis['stark_patterns']['poseidon_state'])}")
    if analysis['stark_patterns']['poseidon_state']:
        print(f"Example states: {analysis['stark_patterns']['poseidon_state'][:3]}")
    
    print("\nCircle Curve Patterns Found:")
    print("Curve Points:")
    print(f"Number found: {len(analysis['circle_patterns']['curve_points'])}")
    if analysis['circle_patterns']['curve_points']:
        print(f"Example points: {analysis['circle_patterns']['curve_points'][:3]}")
    
    print("\nPedersen Hash Computations:")
    print(f"Number found: {len(analysis['circle_patterns']['pedersen_hashes'])}")
    if analysis['circle_patterns']['pedersen_hashes']:
        print(f"Example computations: {analysis['circle_patterns']['pedersen_hashes'][:3]}")
    
    print("\nRescue States:")
    print(f"Number found: {len(analysis['circle_patterns']['rescue_states'])}")
    if analysis['circle_patterns']['rescue_states']:
        print(f"Example states: {analysis['circle_patterns']['rescue_states'][:3]}")
    
    print("\nPoseidon2 Patterns Found:")
    print("State Transitions:")
    print(f"Number found: {len(analysis['poseidon2_patterns']['state_transitions'])}")
    if analysis['poseidon2_patterns']['state_transitions']:
        for i, trans in enumerate(analysis['poseidon2_patterns']['state_transitions'][:3]):
            print(f"\nTransition {i+1}:")
            print(f"From: {trans['from']}")
            print(f"To: {trans['to']}")
            print(f"Type: {trans['type']}")
    
    print("\nRound Constants:")
    print(f"Number of unique constants: {len(analysis['poseidon2_patterns']['round_constants'])}")
    if analysis['poseidon2_patterns']['round_constants']:
        print(f"Example constants: {sorted(list(analysis['poseidon2_patterns']['round_constants']))[:5]}")
    
    print("\nMDS Patterns:")
    print(f"Number found: {len(analysis['poseidon2_patterns']['mds_patterns'])}")
    if analysis['poseidon2_patterns']['mds_patterns']:
        for i, pattern in enumerate(analysis['poseidon2_patterns']['mds_patterns'][:3]):
            print(f"\nPattern {i+1}:")
            print(f"Input: {pattern['input']}")
            print(f"Output: {pattern['output']}")
    
    print("\nARK Patterns:")
    print(f"Number found: {len(analysis['poseidon2_patterns']['ark_patterns'])}")
    if analysis['poseidon2_patterns']['ark_patterns']:
        for i, pattern in enumerate(analysis['poseidon2_patterns']['ark_patterns'][:3]):
            print(f"\nPattern {i+1}:")
            print(f"State: {pattern['state']}")
            print(f"Constants: {pattern['constants']}")
    
    # Test first few sequences in detail
    print("\nDetailed Analysis of First 5 ModExp Sequences:")
    for i, (seq, patterns) in enumerate(list(analysis['modexp_sequences'].items())[:5]):
        print(f"\nSequence {i+1}: {seq}")
        for base, exp, result in patterns:
            print(f"  {base}^{exp} mod 2^31-1 = {result}")
            # Test with our implementation
            modexp = ModExpPrecomp(base, M31_MODULUS)
            print(f"  Precomputed values used: {sorted(modexp.precomp_table.keys())}")
            print(f"  Precomputed table: {modexp.precomp_table}")
    
    # Add sequence-specific analysis
    print("\nAnalyzing sequence-specific patterns...")
    sequence_analysis = analyze_sequence_patterns(hex_strings)
    
    print("\nSequence Pattern Analysis Results:")
    print("Growth Ratios:")
    ratios = sequence_analysis['growth_ratios'][:5]
    print(f"First 5 ratios: {[f'{r:.2f}' for r in ratios]}")
    
    print("\nBit Patterns:")
    for pattern in sequence_analysis['bit_patterns'][:5]:
        if pattern['type'] == 'power_of_2':
            print(f"  2^{pattern['position']} = {pattern['value']}")
        else:
            print(f"  Balanced bits: {pattern['value']} (length {pattern['length']})")
    
    print("\nValue Cycles:")
    for value, count in sequence_analysis['value_cycles'][:5]:
        print(f"  Value {value} appears {count} times")
    
    print("\nSpecial Values:")
    by_type = {}
    for special in sequence_analysis['special_values']:
        if special['type'] not in by_type:
            by_type[special['type']] = []
        by_type[special['type']].append(special['value'])
    
    for type_name, values in by_type.items():
        print(f"  {type_name}: {len(values)} values")
        if values:
            print(f"    Examples: {values[:3]}")
    
    print("\nBit Pattern Analysis Results:")
    print("Hamming Weight Sequences:")
    print(f"Number found: {len(analysis['bit_patterns']['hamming_weight_sequences'])}")
    if analysis['bit_patterns']['hamming_weight_sequences']:
        print("Example sequences:")
        for v1, v2 in analysis['bit_patterns']['hamming_weight_sequences'][:3]:
            print(f"  {bin(v1)[2:]} -> {bin(v2)[2:]}")
    
    print("\nRun Length Sequences:")
    print(f"Number found: {len(analysis['bit_patterns']['run_length_sequences'])}")
    if analysis['bit_patterns']['run_length_sequences']:
        print("Example sequences:")
        for v1, v2 in analysis['bit_patterns']['run_length_sequences'][:3]:
            print(f"  {bin(v1)[2:]} -> {bin(v2)[2:]}")
    
    print("\nBit Transition Patterns:")
    print(f"Number found: {len(analysis['bit_patterns']['bit_transition_patterns'])}")
    if analysis['bit_patterns']['bit_transition_patterns']:
        print("Example patterns:")
        for v1, v2 in analysis['bit_patterns']['bit_transition_patterns'][:3]:
            print(f"  {bin(v1)[2:]} -> {bin(v2)[2:]}")
    
    print("\nBit Position Correlations:")
    print(f"Number found: {len(analysis['bit_patterns']['bit_position_correlations'])}")
    if analysis['bit_patterns']['bit_position_correlations']:
        print("Example correlations:")
        for v1, v2 in analysis['bit_patterns']['bit_position_correlations'][:3]:
            print(f"  {bin(v1)[2:]} -> {bin(v2)[2:]}")
    
    print("\nSTARK Witness Pattern Analysis Results:")
    print("Trace Polynomials:")
    print(f"Number found: {len(analysis['stark_witness']['trace_polynomials'])}")
    if analysis['stark_witness']['trace_polynomials']:
        print("Example polynomials:")
        for poly in analysis['stark_witness']['trace_polynomials'][:3]:
            print(f"  {poly}")
    
    print("\nBoundary Constraints:")
    print(f"Number found: {len(analysis['stark_witness']['boundary_constraints'])}")
    if analysis['stark_witness']['boundary_constraints']:
        print("Example constraints:")
        for start, end in analysis['stark_witness']['boundary_constraints'][:3]:
            print(f"  Start: {start}, End: {end}")
    
    print("\nTransition Constraints:")
    print(f"Number found: {len(analysis['stark_witness']['transition_constraints'])}")
    if analysis['stark_witness']['transition_constraints']:
        print("Example constraints:")
        for type_, values in analysis['stark_witness']['transition_constraints'][:3]:
            print(f"  Type: {type_}, Values: {values}")
    
    print("\nComposition Polynomials:")
    print(f"Number found: {len(analysis['stark_witness']['composition_polynomials'])}")
    if analysis['stark_witness']['composition_polynomials']:
        print("Example polynomials:")
        for type_, values, params in analysis['stark_witness']['composition_polynomials'][:3]:
            print(f"  Type: {type_}, Values: {values}, Parameters: {params}")

if __name__ == '__main__':
    main()