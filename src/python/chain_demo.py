import hashlib
import math
import secrets
import json
import time
from datetime import datetime
import logging
from collections import defaultdict
import os
import numpy as np
from typing import Dict, List, Set, Tuple
import random
try:
    from chain_search_v3 import ChainSearcher
except ImportError:
    ChainSearcher = None
    logging.warning("ChainSearcher not available from chain_search_v3")

try:
    from validate_solutions import validate_solution
except ImportError:
    validate_solution = None
    logging.warning("validate_solution not available")

import multiprocessing as mp
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='chain_search.log'
)

def int_to_bytes(i, length):
    """Convert an integer i to a byte string of the given length (big-endian)."""
    print(f"Converting integer {i} to bytes of length {length}")
    return i.to_bytes(length, byteorder='big')

def determine_L(n):
    """
    Determine the number of significant hex digits L for chain element n.
    Here we use the rule:
         L = ceil(n / 4)
    This rule reproduces the known lengths for n=1..65.
    """
    print(f"Determining L for n={n}")
    return math.ceil(n / 4)

def chain_next_value(prev_value, n):
    """
    Given the previous 256-bit integer `prev_value` and the chain index n,
    compute the next 256-bit integer Xₙ by hashing (prev_value || n).
    
    Then the "significant" part is defined as:
         Sₙ = Xₙ mod (16^L)
    where L = determine_L(n).
    """
    print(f"Computing next chain value for prev_value={prev_value} and n={n}")
    L = determine_L(n)
    m = 16 ** L

    # Prepare input: previous 256-bit value (32 bytes) concatenated with n (4 bytes).
    input_bytes = prev_value.to_bytes(32, byteorder='big') + int_to_bytes(n, 4)
    
    # Compute SHA-256 hash.
    h_bytes = hashlib.sha256(input_bytes).digest()
    X = int.from_bytes(h_bytes, byteorder='big')  # a 256-bit integer
    
    # The "significant" part is the remainder modulo m.
    S = X % m
    print(f"Computed X={X}, S={S}, L={L}")
    return X, S, L

def format_256bit(X):
    """Return a 64-character hexadecimal string for a 256-bit integer X."""
    print(f"Formatting 256-bit integer {X}")
    return format(X, '064x')

# Expected significant parts for indices 1 through 65 (given in hexadecimal, without leading zeros).
expected_significant = {
    1: "1",
    2: "3",
    3: "7",
    4: "8",
    5: "15",
    6: "31",
    7: "4c",
    8: "e0",
    9: "1d3",
    10: "202",
    11: "483",
    12: "a7b",
    13: "1460",
    14: "2930",
    15: "68f3",
    16: "c936",
    17: "1764f",
    18: "3080d",
    19: "5749f",
    20: "d2c55",
    21: "1ba534",
    22: "2de40f",
    23: "556e52",
    24: "dc2a04",
    25: "1fa5ee5",
    26: "340326e",
    27: "6ac3875",
    28: "d916ce8",
    29: "17e2551e",
    30: "3d94cd64",
    31: "7d4fe747",
    32: "b862a62e",
    33: "1a96ca8d8",
    34: "34a65911d",
    35: "4aed21170",
    36: "9de820a7c",
    37: "1757756a93",
    38: "22382facd0",
    39: "4b5f8303e9",
    40: "e9ae4933d6",
    41: "153869acc5b",
    42: "2a221c58d8f",
    43: "6bd3b27c591",
    44: "e02b35a358f",
    45: "122fca143c05",
    46: "2ec18388d544",
    47: "6cd610b53cba",
    48: "ade6d7ce3b9b",
    49: "174176b015f4d",
    50: "22bd43c2e9354",
    51: "75070a1a009d4",
    52: "efae164cb9e3c",
    53: "180788e47e326c",
    54: "236fb6d5ad1f43",
    55: "6abe1f9b67e114",
    56: "9d18b63ac4ffdf",
    57: "1eb25c90795d61c",
    58: "2c675b852189a21",
    59: "7496cbb87cab44f",
    60: "fc07a1825367bbe",
    61: "13c96a3742f64906",
    62: "363d541eb611abee",
    63: "7cce5efdaccf6808",
    64: "f7051f27b09112d4",
    65: "1a838b13505b26867"
}

def generate_random_seed():
    """Generate a random 256-bit seed."""
    print("Generating a random 256-bit seed")
    return secrets.token_bytes(32)

def test_seed(seed_bytes, expected_significant):
    """Test a seed and return the number of matching elements."""
    print(f"Testing seed {seed_bytes.hex()}")
    current_value = int.from_bytes(seed_bytes, 'big')
    matches = 0
    
    for n in range(1, len(expected_significant) + 1):
        current_value, S, L = chain_next_value(current_value, n)
        significant_str = format_256bit(current_value)[-L:]
        
        if n in expected_significant:
            expected = expected_significant[n].lower()
            if significant_str.lower() == expected:
                matches += 1
                print(f"Match found for index {n}: {significant_str.lower()} == {expected}")
            else:
                print(f"No match for index {n}: {significant_str.lower()} != {expected}")
                break
                
    print(f"Total matches: {matches}")
    return matches

def save_best_result(seed_hex, matches, total_attempts):
    """Save the best result to a JSON file."""
    print(f"Saving best result: seed={seed_hex}, matches={matches}, total_attempts={total_attempts}")
    result = {
        'timestamp': datetime.now().isoformat(),
        'seed': seed_hex,
        'matching_elements': matches,
        'total_attempts': total_attempts,
    }
    
    try:
        with open('best_seeds.json', 'r') as f:
            results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        results = []
    
    results.append(result)
    
    with open('best_seeds.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Best result saved")

class ChainSeedAnalyzer:
    def __init__(self):
        print("Initializing ChainSeedAnalyzer")
        self.seeds_by_index = defaultdict(list)
        self.max_seeds_per_index = 10  # Store top 10 seeds for each index
        self.total_attempts = 0
        
    def test_seed_for_index(self, seed_bytes, target_index):
        """Test if a seed generates the expected value at specific index."""
        print(f"Testing seed for index {target_index}")
        current_value = int.from_bytes(seed_bytes, 'big')
        
        # Generate chain up to target index
        for n in range(1, target_index + 1):
            current_value, S, L = chain_next_value(current_value, n)
            if n == target_index:
                significant_str = format_256bit(current_value)[-L:]
                expected = expected_significant[n].lower()
                result = significant_str.lower() == expected
                print(f"Test result for index {target_index}: {result}")
                return result
                
        return False

    def analyze_seed_relationships(self):
        """Analyze relationships between successful seeds."""
        print("Analyzing seed relationships")
        relationships = []
        
        for idx1 in self.seeds_by_index:
            for idx2 in self.seeds_by_index:
                if idx1 < idx2:
                    for seed1 in self.seeds_by_index[idx1]:
                        for seed2 in self.seeds_by_index[idx2]:
                            relationship = {
                                'index1': idx1,
                                'index2': idx2,
                                'seed1': seed1,
                                'seed2': seed2,
                                'xor_diff': hex(int(seed1, 16) ^ int(seed2, 16)),
                                'add_diff': hex(int(seed2, 16) - int(seed1, 16)),
                                'bit_diff_count': bin(int(seed1, 16) ^ int(seed2, 16)).count('1')
                            }
                            relationships.append(relationship)
        
        print(f"Total relationships analyzed: {len(relationships)}")
        return relationships

    def save_analysis(self):
        """Save current analysis results."""
        print("Saving analysis results")
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_attempts': self.total_attempts,
            'seeds_by_index': dict(self.seeds_by_index),
            'relationships': self.analyze_seed_relationships()
        }
        
        with open('seed_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        print("Analysis results saved")

    def search(self):
        """Continuously search for seeds that generate expected values."""
        last_log_time = time.time()
        log_interval = 60
        
        print("Starting seed analysis search...")
        logging.info("Analysis search started")
        
        try:
            while True:
                seed_bytes = generate_random_seed()
                seed_hex = seed_bytes.hex()
                self.total_attempts += 1
                
                # Test seed against each index
                for target_index in expected_significant:
                    if self.test_seed_for_index(seed_bytes, target_index):
                        if len(self.seeds_by_index[target_index]) < self.max_seeds_per_index:
                            self.seeds_by_index[target_index].append(seed_hex)
                            print(f"\nFound seed for index {target_index}!")
                            print(f"Seed: {seed_hex}")
                            print(f"Total seeds for this index: {len(self.seeds_by_index[target_index])}")
                            logging.info(f"New seed found for index {target_index}: {seed_hex}")
                            
                            # Save analysis after each new find
                            self.save_analysis()
                
                # Periodic progress logging
                current_time = time.time()
                if current_time - last_log_time >= log_interval:
                    self._log_progress(current_time - last_log_time)
                    last_log_time = current_time
                    
        except KeyboardInterrupt:
            self._log_final_stats()

    def _log_progress(self, elapsed_time):
        """Log progress information."""
        print("\nProgress update:")
        print(f"Total attempts: {self.total_attempts}")
        print(f"Current rate: {self.total_attempts/elapsed_time:.2f} attempts/second")
        print("\nSeeds found per index:")
        for idx in sorted(self.seeds_by_index.keys()):
            print(f"Index {idx}: {len(self.seeds_by_index[idx])} seeds")

    def _log_final_stats(self):
        """Log final statistics."""
        print("\nSearch stopped by user")
        print(f"Final statistics:")
        print(f"Total attempts: {self.total_attempts}")
        print("\nSeeds found per index:")
        for idx in sorted(self.seeds_by_index.keys()):
            print(f"Index {idx}: {len(self.seeds_by_index[idx])} seeds")
        logging.info(f"Search stopped. Total attempts: {self.total_attempts}")

class EnhancedChainAnalyzer:
    def __init__(self):
        print("Initializing EnhancedChainAnalyzer")
        self.seeds_by_index = defaultdict(list)
        self.max_seeds_per_index = 10
        self.total_attempts = 0
        self.pattern_cache = {}
        self.successful_patterns = set()
        
        # Add validation tools
        self.solution_validator = None
        if Path('validate_solutions.py').exists():
            try:
                from validate_solutions import SolutionValidator
                self.solution_validator = SolutionValidator()
            except ImportError:
                logging.warning("SolutionValidator not available")
        
        # Initialize chain searcher if available
        self.chain_searcher = None
        if ChainSearcher is not None:
            try:
                self.chain_searcher = ChainSearcher()
            except Exception as e:
                logging.warning(f"Failed to initialize ChainSearcher: {e}")
        
        # Load puzzle solutions summary
        self.solutions_summary = {}
        if Path('puzzle_solutions_summary.txt').exists():
            self.load_solutions_summary()
            
        self.load_historical_data()

    def load_solutions_summary(self):
        """Load and parse puzzle solutions summary."""
        print("Loading puzzle solutions summary")
        try:
            with open('puzzle_solutions_summary.txt', 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        self.solutions_summary[key.strip()] = value.strip()
        except Exception as e:
            logging.warning(f"Error loading solutions summary: {e}")

    def load_historical_data(self):
        """Load and analyze historical results from all available data files."""
        print("Loading historical data")
        self.historical_seeds = set()
        self.pattern_frequencies = defaultdict(int)
        
        # Load previous analysis results
        if os.path.exists('seed_analysis.json'):
            with open('seed_analysis.json', 'r') as f:
                data = json.load(f)
                for index, seeds in data.get('seeds_by_index', {}).items():
                    self.analyze_seed_patterns(seeds)

        # Load puzzle solutions if available
        if os.path.exists('puzzle_solutions_analysis.json'):
            with open('puzzle_solutions_analysis.json', 'r') as f:
                solutions = json.load(f)
                self.analyze_solution_patterns(solutions)

    def analyze_seed_patterns(self, seeds: List[str]):
        """Analyze patterns in successful seeds."""
        print(f"Analyzing seed patterns for {len(seeds)} seeds")
        for seed in seeds:
            seed_bytes = bytes.fromhex(seed)
            patterns = self.extract_patterns(seed_bytes)
            for pattern in patterns:
                self.pattern_frequencies[pattern] += 1
                if self.pattern_frequencies[pattern] > 2:
                    self.successful_patterns.add(pattern)

    def extract_patterns(self, seed_bytes: bytes) -> Set[str]:
        """Extract potentially meaningful patterns from a seed."""
        print(f"Extracting patterns from seed {seed_bytes.hex()}")
        patterns = set()
        
        # Byte sequence patterns
        for i in range(len(seed_bytes) - 3):
            pattern = seed_bytes[i:i+4]
            patterns.add(pattern.hex())

        # Bit patterns
        bits = ''.join(format(b, '08b') for b in seed_bytes)
        for i in range(0, len(bits) - 31, 8):
            pattern = bits[i:i+32]
            patterns.add(pattern)

        return patterns

    @staticmethod
    def generate_guided_seed(patterns=None) -> bytes:
        """Generate a seed incorporating successful patterns."""
        print("Generating guided seed")
        if not patterns or random.random() < 0.2:  # 20% random exploration
            return secrets.token_bytes(32)

        # Start with random bytes
        seed = bytearray(secrets.token_bytes(32))
        
        # Incorporate successful patterns
        pattern = random.choice(list(patterns))
        if len(pattern) == 8:  # hex pattern
            pattern_bytes = bytes.fromhex(pattern)
            pos = random.randint(0, 28)
            seed[pos:pos+4] = pattern_bytes
        else:  # bit pattern
            pattern_bytes = int(pattern, 2).to_bytes(4, 'big')
            pos = random.randint(0, 28)
            seed[pos:pos+4] = pattern_bytes

        return bytes(seed)

    def analyze_chain_properties(self, seed: bytes, depth: int) -> Dict:
        """Analyze mathematical properties of the chain generated by a seed."""
        print(f"Analyzing chain properties for seed {seed.hex()} up to depth {depth}")
        properties = {
            'bit_transitions': [],
            'hamming_weights': [],
            'value_diffs': []
        }
        
        current_value = int.from_bytes(seed, 'big')
        prev_value = None
        
        for n in range(1, depth + 1):
            current_value, S, L = chain_next_value(current_value, n)
            # Calculate expected number of bits based on L
            num_bits = L * 4  # L hex digits = L*4 bits
            binary = format(S, f'0{num_bits}b')
            
            properties['hamming_weights'].append(binary.count('1'))
            if prev_value is not None:
                properties['value_diffs'].append(S - prev_value)
                # Use same number of bits for transition count
                prev_binary = format(prev_value, f'0{num_bits}b')
                properties['bit_transitions'].append(sum(a != b for a, b in zip(binary, prev_binary)))
            
            prev_value = S
            
        print(f"Chain properties: {properties}")
        return properties

    def test_seed_for_index(self, seed_bytes, target_index):
        """Enhanced seed testing with validation."""
        try:
            # Use chain searcher if available
            if self.chain_searcher:
                return self.chain_searcher.test_seed(seed_bytes, target_index)
                
            # Fallback to basic testing
            return super().test_seed_for_index(seed_bytes, target_index)
        except Exception as e:
            logging.error(f"Error testing seed: {e}")
            return False

    def _generate_seeds_parallel(self, num_processes):
        """Generate seeds in parallel."""
        seeds = []
        for _ in range(num_processes):
            seed = self.generate_guided_seed(self.successful_patterns)
            seeds.append(seed)
        return seeds

    def search(self):
        """Enhanced parallel search."""
        print("Starting enhanced parallel search...")
        
        # Use multiple processes for search
        num_processes = mp.cpu_count()
        
        try:
            while True:
                # Generate seeds sequentially (for now)
                seeds = self._generate_seeds_parallel(num_processes)
                
                for seed_bytes in seeds:
                    self.process_seed(seed_bytes)
                    
        except KeyboardInterrupt:
            print("\nStopping search gracefully...")
            self._log_final_stats()

    def process_seed(self, seed_bytes):
        """Process a single seed with enhanced validation."""
        seed_hex = seed_bytes.hex()
        self.total_attempts += 1
        
        # Analyze chain properties
        chain_props = self.analyze_chain_properties(seed_bytes, 5)
        
        if self.is_promising_seed(chain_props):
            # Validate seed if validator available
            if self.solution_validator and not self.solution_validator.validate_seed(seed_hex):
                return
                
            # Test against expected values
            for target_index in expected_significant:
                if self.test_seed_for_index(seed_bytes, target_index):
                    self.handle_successful_seed(seed_hex, target_index, chain_props)

    def handle_successful_seed(self, seed_hex, target_index, chain_props):
        """Handle a successful seed match."""
        if len(self.seeds_by_index[target_index]) < self.max_seeds_per_index:
            self.seeds_by_index[target_index].append(seed_hex)
            self.analyze_seed_patterns([seed_hex])
            self.log_success(target_index, seed_hex, chain_props)
            self.save_analysis()
            
            # Additional validation if available
            if self.solution_validator:
                self.solution_validator.validate_and_save(seed_hex, target_index)

    def is_promising_seed(self, chain_props: Dict) -> bool:
        """Evaluate if a seed's chain properties look promising."""
        if not chain_props['hamming_weights']:
            return True
        
        # Look for balanced hamming weights (between 40% and 60% of bits set)
        avg_weight = np.mean(chain_props['hamming_weights'])
        expected_bits = 4  # Start with minimum 4 bits
        for i, weight in enumerate(chain_props['hamming_weights']):
            expected_bits = max(expected_bits, math.ceil((i + 1) / 4) * 4)
        
        if not (0.4 <= avg_weight/expected_bits <= 0.6):
            return False
        
        # Check for reasonable bit transitions
        if chain_props['bit_transitions']:
            avg_transitions = np.mean(chain_props['bit_transitions'])
            if avg_transitions < 5:
                return False
                
        return True

    def log_success(self, target_index: int, seed_hex: str, chain_props: Dict):
        """Log detailed information about successful seeds."""
        print(f"\nFound seed for index {target_index}!")
        print(f"Seed: {seed_hex}")
        print(f"Chain properties:")
        print(f"- Average Hamming weight: {np.mean(chain_props['hamming_weights']):.2f}")
        if chain_props['bit_transitions']:
            print(f"- Average bit transitions: {np.mean(chain_props['bit_transitions']):.2f}")
        print(f"Total seeds for this index: {len(self.seeds_by_index[target_index])}")
        logging.info(f"New seed found for index {target_index}: {seed_hex}")

    def _log_final_stats(self):
        """Log final statistics."""
        print("\nSearch stopped by user")
        print(f"Final statistics:")
        print(f"Total attempts: {self.total_attempts}")
        print("\nSeeds found per index:")
        for idx in sorted(self.seeds_by_index.keys()):
            print(f"Index {idx}: {len(self.seeds_by_index[idx])} seeds")
        logging.info(f"Search stopped. Total attempts: {self.total_attempts}")

    def analyze_solution_patterns(self, solutions: Dict):
        """Analyze patterns from previous puzzle solutions."""
        try:
            for solution in solutions.get('solutions', []):
                if 'seed' in solution:
                    seed = solution['seed']
                    if isinstance(seed, str):
                        self.historical_seeds.add(seed)
                        self.analyze_seed_patterns([seed])
                        
                # Also analyze any intermediate or partial solutions
                if 'intermediate_seeds' in solution:
                    for intermediate_seed in solution['intermediate_seeds']:
                        if isinstance(intermediate_seed, str):
                            self.historical_seeds.add(intermediate_seed)
                            self.analyze_seed_patterns([intermediate_seed])
                            
                # Look for patterns in successful chain values
                if 'chain_values' in solution:
                    for value in solution['chain_values']:
                        if isinstance(value, str):
                            patterns = self.extract_patterns(bytes.fromhex(value))
                            for pattern in patterns:
                                self.pattern_frequencies[pattern] += 1
                                
        except Exception as e:
            logging.warning(f"Error analyzing solution patterns: {e}")

def main():
    # Initialize analyzer with available tools
    analyzer = EnhancedChainAnalyzer()
    
    # Load any existing analysis
    if Path('puzzle_solutions_analysis.json').exists():
        print("Loading existing analysis...")
        analyzer.load_historical_data()
    
    # Start the search
    analyzer.search()

if __name__ == "__main__":
    main()
