import math
import numpy as np
import hashlib
from typing import List, Optional, Tuple
import logging
from pathlib import Path
from collections import defaultdict
import base58
import binascii
from Crypto.Hash import RIPEMD160
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('puzzle_solver.log'),
        logging.StreamHandler()
    ]
)

class PuzzleSolver:
    # Static counters and tracking
    total_candidates_checked = 0
    total_generations = 0
    best_fitness_overall = float('-inf')
    seen_addresses = set()  # Track previously seen addresses
    stagnation_counter = 0  # Track generations without improvement
    
    def __init__(self, index: int = 67):
        """Initialize the puzzle solver"""
        self.index = index
        self.target_address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"
        self.target_hash160 = "739437bb3dd6d1983e66629c5f08c70e52769371"
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Initialize output directory
        self.output_dir = Path('output')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load sequence data
        self.sequence = self.load_sequence()
        if not self.sequence:
            logging.error("Failed to load sequence data")
            return
        
        # Initialize tracking sets
        self.seen_addresses = set()
        self.stagnation_counter = 0
        
        # Initialize best fitness tracking
        PuzzleSolver.best_fitness_overall = float('-inf')
        PuzzleSolver.total_candidates_checked = 0
        PuzzleSolver.total_generations = 0
        
        logging.info(f"Starting puzzle solving process for index {self.index}")
        logging.info(f"Target address: {self.target_address}")
        logging.info(f"Target Hash160: {self.target_hash160}")

    def load_sequence(self) -> List[int]:
        """Load and expand sequence values to 67 bits"""
        try:
            with open('sequence.txt', 'r') as f:
                lines = f.readlines()
            
            sequence = []
            for line in lines:
                try:
                    # Clean and parse the value
                    value = line.strip()
                    if value.startswith('0x'):
                        value = value[2:]
                    # Remove any non-hex characters
                    value = ''.join(c for c in value if c in '0123456789abcdefABCDEF')
                    if value:
                        num = int(value, 16)
                        # Ensure 67 bits
                        if num.bit_length() < 67:
                            num |= (1 << 66)  # Set MSB to 1
                        sequence.append(num)
                except Exception as e:
                    logging.debug(f"Error parsing sequence value {line.strip()}: {str(e)}")
                    continue
            
            logging.info(f"Loaded and expanded {len(sequence)} sequence values to 67 bits")
            return sequence
        except Exception as e:
            logging.error(f"Error loading sequence: {str(e)}")
            return []

    def load_known_sequences(self) -> None:
        """Load known sequence data from files"""
        try:
            # Load sequence data
            hex_path = self.data_dir / '32bHex.txt'
            if hex_path.exists():
                with open(hex_path, 'r') as f:
                    # Convert 32-bit values to potential 67-bit values using pattern analysis
                    base_sequences = [int(line.strip(), 16) for line in f]
                    self.known_sequences = self.expand_to_67bit(base_sequences)
                logging.info(f"Loaded and expanded {len(self.known_sequences)} sequence values to 67 bits")
            else:
                logging.warning("32bHex.txt not found")
        except Exception as e:
            logging.error(f"Error loading sequences: {str(e)}")

    def expand_to_67bit(self, base_sequences: List[int]) -> List[int]:
        """Expand 32-bit values to 67-bit values using pattern analysis"""
        expanded = []
        for value in base_sequences:
            # Start with the original 32 bits
            binary = format(value, '032b')
            
            # Analyze patterns in the binary representation
            ones_ratio = binary.count('1') / len(binary)
            
            # Generate additional 35 bits based on patterns
            extra_bits = ''
            for i in range(35):
                # Use various patterns to determine additional bits
                if i < len(binary):
                    # Mirror some bits from the original sequence
                    extra_bits += binary[i]
                else:
                    # Generate new bits based on the ones ratio and position
                    if ones_ratio > 0.5:
                        extra_bits += '1' if (i % 2 == 0) else '0'
                    else:
                        extra_bits += '0' if (i % 2 == 0) else '1'
            
            # Combine original bits and extra bits
            full_binary = binary + extra_bits
            # Ensure exactly 67 bits by setting MSB to 1
            full_binary = '1' + full_binary[1:]
            expanded.append(int(full_binary, 2))
        
        return expanded

    def find_bit_patterns(self, values: np.ndarray) -> dict:
        """Analyze bit patterns in the sequence"""
        patterns = {}
        
        try:
            # Convert to binary strings (right-aligned 67-bit)
            binary_strings = [format(int(v), '067b') for v in values]
            
            # Analyze bit positions (0 is rightmost bit)
            bit_positions = np.zeros((67,), dtype=float)
            for binary in binary_strings:
                binary_list = list(binary)  # Convert to list for easier indexing
                for i in range(67):
                    bit_positions[i] += int(binary_list[i])
            
            # Calculate bit probabilities
            bit_probabilities = bit_positions / len(binary_strings)
            
            # Find strongly biased bits
            strong_ones = np.where(bit_probabilities > 0.8)[0]
            strong_zeros = np.where(bit_probabilities < 0.2)[0]
            
            patterns['bit_probabilities'] = bit_probabilities.tolist()
            patterns['strong_ones'] = strong_ones.tolist()
            patterns['strong_zeros'] = strong_zeros.tolist()
            
            # Log bit pattern insights
            logging.info(f"Found {len(strong_ones)} strongly biased 1's and {len(strong_zeros)} strongly biased 0's")
            if len(strong_ones) > 0:
                logging.info(f"Positions with strong 1's: {strong_ones.tolist()}")
            if len(strong_zeros) > 0:
                logging.info(f"Positions with strong 0's: {strong_zeros.tolist()}")
                
        except Exception as e:
            logging.error(f"Error in bit pattern analysis: {str(e)}")
            patterns['error'] = str(e)
        
        return patterns

    def scale_to_67bit(self, value: float) -> int:
        """Scale a value to fit within 67-bit range while preserving relative magnitude"""
        # Convert to binary string, ensuring exactly 67 bits
        binary = format(int(value) & ((1 << 67) - 1), 'b')
        if len(binary) > 67:
            binary = binary[-67:]  # Take last 67 bits
        elif len(binary) < 67:
            binary = '0' * (67 - len(binary)) + binary  # Pad with leading zeros
        
        # Always set MSB to 1 to ensure 67 bits
        binary = '1' + binary[1:]
        
        return int(binary, 2)

    def analyze_crypto_patterns(self, sequence_array: np.ndarray) -> dict:
        """Analyze cryptographic patterns in the sequence"""
        crypto_patterns = {}
        
        # Avalanche effect analysis
        avalanche_scores = []
        for i in range(1, len(sequence_array)):
            prev = format(int(sequence_array[i-1]), '067b')
            curr = format(int(sequence_array[i]), '067b')
            bit_changes = sum(p != c for p, c in zip(prev, curr))
            avalanche_scores.append(bit_changes / 67)  # Normalize to [0,1]
        
        crypto_patterns['avalanche'] = {
            'mean': float(np.mean(avalanche_scores)) if avalanche_scores else None,
            'std': float(np.std(avalanche_scores)) if avalanche_scores else None
        }
        
        # Entropy analysis
        entropies = []
        for num in sequence_array:
            freq = defaultdict(int)
            # Convert to bytes (67 bits = 9 bytes)
            hex_str = format(int(num), '017x').zfill(18)  # Ensure even length
            try:
                num_bytes = bytes.fromhex(hex_str)
                for byte in num_bytes:
                    freq[byte] += 1
                
                entropy = 0
                total_bytes = len(num_bytes)
                for count in freq.values():
                    p = count / total_bytes
                    entropy -= p * math.log2(p) if p > 0 else 0
                entropies.append(entropy)
            except ValueError as e:
                logging.warning(f"Error processing hex string {hex_str}: {str(e)}")
                continue
        
        if entropies:
            crypto_patterns['entropy'] = {
                'mean': float(np.mean(entropies)),
                'std': float(np.std(entropies))
            }
        
        # Hash chain analysis
        hash_similarities = []
        for i in range(len(sequence_array)-1):
            current = int(sequence_array[i])
            next_val = int(sequence_array[i+1])
            try:
                hex_str = format(current, '017x').zfill(18)
                hashed = int(hashlib.sha256(hex_str.encode()).hexdigest(), 16) % self.max_value
                similarity = bin(hashed ^ next_val).count('1') / 67  # Normalized XOR difference
                hash_similarities.append(similarity)
            except ValueError as e:
                logging.warning(f"Error processing hash for value {current}: {str(e)}")
                continue
        
        if hash_similarities:
            crypto_patterns['hash_chain'] = {
                'mean_similarity': float(np.mean(hash_similarities)),
                'std_similarity': float(np.std(hash_similarities))
            }
        
        return crypto_patterns

    def predict_67th_value(self) -> Optional[int]:
        """
        Predict the 67th value using multiple approaches and combine their results
        """
        predictions = []
        
        # Convert sequence to numpy array
        sequence_array = np.array(self.known_sequences, dtype=np.float64)
        
        # Analyze cryptographic patterns
        crypto_patterns = self.analyze_crypto_patterns(sequence_array)
        self.pattern_insights['crypto'] = crypto_patterns
        
        # Method 1: Linear extrapolation from last few values
        if len(sequence_array) >= 3:
            last_values = sequence_array[-3:]
            diff = last_values[-1] - last_values[-2]
            steps = self.target_index - len(sequence_array)
            linear_pred = last_values[-1] + diff * steps
            scaled_linear = self.scale_to_67bit(linear_pred)
            predictions.append(('linear', scaled_linear))

        # Method 2: Geometric progression-based prediction
        if 'geometric' in self.pattern_insights:
            ratio = self.pattern_insights['geometric']['mean_ratio']
            steps = self.target_index - len(sequence_array)
            if steps > 0:
                # Use log space to prevent overflow
                log_base = np.log(sequence_array[-1])
                log_ratio = np.log(ratio)
                log_pred = log_base + steps * log_ratio
                geo_pred = np.exp(log_pred)
                scaled_geo = self.scale_to_67bit(geo_pred)
                predictions.append(('geometric', scaled_geo))

        # Method 3: Pattern-based prediction using FFT insights
        if len(sequence_array) >= 4:
            # Normalize the sequence for FFT
            normalized_sequence = (sequence_array - np.mean(sequence_array)) / np.std(sequence_array)
            fft_result = np.fft.fft(normalized_sequence)
            
            # Find dominant frequencies
            frequencies = np.fft.fftfreq(len(normalized_sequence))
            main_freqs = np.argsort(np.abs(fft_result))[-3:]
            
            # Reconstruct signal using dominant frequencies
            t = np.arange(len(sequence_array))
            reconstruction = np.zeros_like(t, dtype=np.complex128)
            
            for freq_idx in main_freqs:
                freq = frequencies[freq_idx]
                amplitude = np.abs(fft_result[freq_idx]) / len(normalized_sequence)
                phase = np.angle(fft_result[freq_idx])
                reconstruction += amplitude * np.exp(2j * np.pi * freq * t + phase)
            
            # Denormalize and scale
            fft_pred = (reconstruction[-1].real * np.std(sequence_array) + np.mean(sequence_array))
            scaled_fft = self.scale_to_67bit(fft_pred)
            predictions.append(('fft', scaled_fft))

        # Method 4: Crypto-pattern-based prediction
        if 'crypto' in self.pattern_insights:
            crypto_patterns = self.pattern_insights['crypto']
            if 'hash_chain' in crypto_patterns:
                # Use hash chain similarity to predict
                last_value = sequence_array[-1]
                hashed = int(hashlib.sha256(format(int(last_value), '017x').encode()).hexdigest(), 16) % self.max_value
                predictions.append(('crypto', hashed))

        if not predictions:
            logging.warning("Unable to make predictions - insufficient data")
            return None

        # Dynamic weights based on pattern quality
        weights = {
            'linear': 0.2,
            'geometric': 0.3,
            'fft': 0.2,
            'crypto': 0.3
        }
        
        # Normalize weights
        total_weight_sum = sum(weights.values())
        if total_weight_sum > 0:
            weights = {k: v/total_weight_sum for k, v in weights.items()}
        
        # Apply weights to predictions
        weighted_sum = 0
        total_weight = 0
        for method, pred in predictions:
            weight = weights.get(method, 0.1)
            weighted_sum += pred * weight
            total_weight += weight

        final_prediction = int(weighted_sum / total_weight) if total_weight > 0 else None
        
        # Ensure final prediction is within 67-bit range
        if final_prediction is not None:
            final_prediction = self.scale_to_67bit(final_prediction)
        
        # Log predictions and weights
        logging.info(f"Prediction weights: {weights}")
        logging.info(f"Individual predictions: {predictions}")
        logging.info(f"Final weighted prediction for index {self.target_index}: {final_prediction}")
        logging.info(f"Binary length: {len(format(final_prediction, 'b'))} bits")
        
        return final_prediction

    def ripemd160(self, data: bytes) -> bytes:
        """Compute RIPEMD160 hash using pycryptodome"""
        h = RIPEMD160.new()
        h.update(data)
        return h.digest()

    def pubkey_to_address(self, pubkey_hex: str) -> str:
        """Convert a public key to a Bitcoin address"""
        # Step 1: SHA-256
        sha256_hash = hashlib.sha256(bytes.fromhex(pubkey_hex)).digest()
        
        # Step 2: RIPEMD-160
        ripemd160_hash = self.ripemd160(sha256_hash)
        
        # Step 3: Add version byte (0x00 for mainnet)
        version_ripemd160_hash = b'\x00' + ripemd160_hash
        
        # Step 4: Double SHA-256
        double_sha256 = hashlib.sha256(hashlib.sha256(version_ripemd160_hash).digest()).digest()
        
        # Step 5: Add checksum
        binary_address = version_ripemd160_hash + double_sha256[:4]
        
        # Step 6: Base58 encode
        address = base58.b58encode(binary_address).decode('utf-8')
        
        return address

    def get_hash160(self, hex_str: str) -> str:
        """Get hash160 from hex string, handling non-hex characters"""
        try:
            # Clean hex string - remove any non-hex characters
            clean_hex = ''.join(c for c in hex_str if c in '0123456789abcdefABCDEF')
            clean_hex = clean_hex.zfill(64)  # Ensure 64 characters
            
            # Add public key prefix
            pubkey_hex = '04' + clean_hex
            
            # Calculate hash160
            sha256_hash = hashlib.sha256(bytes.fromhex(pubkey_hex)).digest()
            ripemd160_hash = self.ripemd160(sha256_hash)
            return ripemd160_hash.hex()
        except Exception as e:
            logging.debug(f"Error processing hex string {hex_str}: {str(e)}")
            return ''  # Return empty string on error

    def validate_prediction(self, prediction: int) -> bool:
        """
        Validate the prediction using known constraints and patterns
        """
        if prediction is None:
            return False

        # Check if prediction is within expected bounds
        if prediction < 0 or prediction > self.max_value:
            logging.warning("Prediction outside valid 67-bit range")
            return False

        # Verify bit length
        bit_length = len(format(prediction, 'b'))
        if bit_length != 67:
            logging.warning(f"Prediction has incorrect bit length: {bit_length} (expected 67)")
            return False

        # Convert prediction to potential public key
        try:
            # Format as hex string (padded to 64 characters)
            hex_str = format(prediction, 'x').zfill(64)
            # Add Bitcoin public key prefix (0x04 for uncompressed)
            pubkey_hex = '04' + hex_str
            
            # Generate address and hash160
            address = self.pubkey_to_address(pubkey_hex)
            hash160 = self.get_hash160(pubkey_hex)
            
            # Log current attempt
            logging.info(f"Generated address: {address}")
            logging.info(f"Generated Hash160: {hash160}")
            
            # Validate against targets
            if address == self.target_address and hash160 == self.target_hash160:
                logging.info("Found matching Bitcoin address and Hash160!")
                return True
            else:
                if address != self.target_address:
                    logging.warning(f"Address mismatch. Got: {address}")
                if hash160 != self.target_hash160:
                    logging.warning(f"Hash160 mismatch. Got: {hash160}")
                return False
        except Exception as e:
            logging.error(f"Error validating Bitcoin address: {str(e)}")
            return False

    def quick_filter(self, candidate: int) -> bool:
        """Quick validation of candidates before expensive checks"""
        try:
            # Verify bit length
            if candidate.bit_length() != 67:
                return False
                
            # Get hex string and hash160
            hex_str = hex(candidate)[2:].zfill(64)  # Pad to 64 chars
            hash160_hex = self.get_hash160(hex_str)
            
            # Skip if hash160 calculation failed
            if not hash160_hex:
                return False
            
            # Check against target hash160
            match_levels = [
                (3, 1.0),    # First 3 chars must match (739)
                (4, 0.8),    # Next char (4) with 80% probability
                (5, 0.6),    # Next char (3) with 60% probability
                (6, 0.4),    # Next char (7) with 40% probability
            ]
            
            for length, prob in match_levels:
                prefix = hash160_hex[:length]
                target_prefix = self.target_hash160[:length]
                
                if prefix != target_prefix:
                    # For levels beyond first, accept some probability of mismatch
                    if length == 3 or random.random() > prob:
                        return False
            
            return True
        except Exception:
            return False

    def is_novel_candidate(self, candidate: int) -> bool:
        """Check if this candidate produces a new, unseen address"""
        try:
            hex_str = hex(candidate)[2:].zfill(64)
            hash160_hex = self.get_hash160(hex_str)
            
            # Skip if hash160 calculation failed
            if not hash160_hex:
                return False
            
            if hash160_hex in self.seen_addresses:
                return False
                
            self.seen_addresses.add(hash160_hex)
            return True
        except Exception:
            return False

    def generate_diverse_candidate(self, base_value: int, mutation_rate: float, max_attempts: int = 10) -> int:
        """Generate a novel candidate that produces a new address"""
        attempts = 0
        while attempts < max_attempts:
            # Start with more dramatic mutations if we're having trouble finding novel candidates
            current_mutation_rate = mutation_rate * (1 + attempts * 0.2)
            
            # Generate candidate with current mutation rate
            candidate = self.mutate_value(base_value, current_mutation_rate)
            
            # Check if it's novel
            if self.is_novel_candidate(candidate):
                return candidate
                
            attempts += 1
        
        # If we failed to find a novel candidate, return a heavily mutated version
        return self.mutate_value(base_value, 0.5)

    def generate_initial_population(self, base_prediction: int, population_size: int) -> List[int]:
        """Generate initial population with diversity checks"""
        population = []
        attempts = 0
        max_attempts = population_size * 3  # Allow more attempts to ensure diversity
        
        while len(population) < population_size and attempts < max_attempts:
            # Generate candidate with increasing mutation rate based on attempts
            mutation_rate = 0.1 * (1 + attempts / max_attempts)
            candidate = self.generate_diverse_candidate(base_prediction, mutation_rate)
            
            # Only add if it passes quick filter
            if self.quick_filter(candidate):
                population.append(candidate)
            
            attempts += 1
        
        return population

    def generate_candidate_with_prefix(self, target_prefix: str) -> Optional[int]:
        """Generate a candidate that might produce a hash160 with the target prefix"""
        try:
            # Start with random 67-bit number
            candidate = random.getrandbits(67)
            candidate |= (1 << 66)  # Set MSB to 1
            
            # Format and check
            hex_str = format(candidate, 'x').zfill(64)
            pubkey_hex = '04' + hex_str
            
            # Quick hash check
            sha256_hash = hashlib.sha256(bytes.fromhex(pubkey_hex)).digest()
            ripemd160_hash = self.ripemd160(sha256_hash)
            hash160_hex = ripemd160_hash.hex()
            
            if hash160_hex.startswith(target_prefix):
                return candidate
            
            return None
        except Exception:
            return None

    def evolve_prediction(self, base_prediction: int, generation: int = 0, max_generations: int = 2000) -> Optional[int]:
        """Evolve prediction using genetic algorithm with adaptive strategies"""
        population_size = 2000  # Larger population
        elite_size = 200  # More elites
        initial_mutation_rate = 0.1
        
        # Create multiple initial populations with different strategies
        populations = []
        
        # Population 1: Based on base prediction
        pop1 = self.generate_initial_population(base_prediction, population_size // 3)
        if pop1:
            populations.extend(pop1)
        
        # Population 2: Based on bit-flipped variants
        if pop1:
            best_candidate = max(pop1, key=lambda x: self.evaluate_fitness(x))
            pop2 = []
            for i in range(67):
                variant = best_candidate ^ (1 << i)  # Flip each bit
                if self.quick_filter(variant):
                    pop2.append(variant)
            populations.extend(pop2)
        
        # Population 3: Random candidates with prefix matching
        pop3 = []
        for _ in range(population_size // 3):
            candidate = random.randint(0, 2**67 - 1)
            candidate |= (1 << 66)  # Ensure 67 bits
            if self.quick_filter(candidate):
                pop3.append(candidate)
        populations.extend(pop3)
        
        # Ensure minimum population size
        while len(populations) < population_size:
            candidate = self.generate_diverse_candidate(base_prediction, 0.2)
            if self.quick_filter(candidate):
                populations.append(candidate)
        
        population = populations[:population_size]
        best_fitness = float('-inf')
        best_candidate = None
        generations_without_improvement = 0
        mutation_rate = initial_mutation_rate
        
        while generation < max_generations:
            PuzzleSolver.total_generations += 1
            
            # Evaluate fitness
            fitness_scores = []
            for candidate in population:
                PuzzleSolver.total_candidates_checked += 1
                if self.quick_filter(candidate):
                    fitness = self.evaluate_fitness(candidate)
                    fitness_scores.append((candidate, fitness))
                    
                    if self.validate_prediction(candidate):
                        return candidate
                    
                    if fitness > best_fitness:
                        best_fitness = fitness
                        best_candidate = candidate
                        generations_without_improvement = 0
                        mutation_rate = initial_mutation_rate  # Reset mutation rate
                        if fitness > PuzzleSolver.best_fitness_overall:
                            PuzzleSolver.best_fitness_overall = fitness
                            logging.info(f"New best fitness: {fitness} (Gen {generation})")
            
            # Adaptive mutation rate
            if generations_without_improvement > 0:
                if generations_without_improvement % 10 == 0:
                    mutation_rate = min(0.5, mutation_rate * 1.2)  # Increase mutation rate
                if generations_without_improvement % 50 == 0:
                    # Introduce completely new candidates
                    num_new = population_size // 4
                    new_candidates = []
                    for _ in range(num_new):
                        candidate = random.randint(0, 2**67 - 1)
                        candidate |= (1 << 66)
                        if self.quick_filter(candidate):
                            new_candidates.append(candidate)
                    population = population[:-len(new_candidates)] + new_candidates
            
            # Create next generation
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Keep elite candidates
            new_population = [score[0] for score in fitness_scores[:elite_size]]
            
            # Tournament selection and crossover
            while len(new_population) < population_size:
                parent1 = self.tournament_select(fitness_scores)
                parent2 = self.tournament_select(fitness_scores)
                child = self.crossover(parent1, parent2)
                
                # Apply mutation with adaptive rate
                if random.random() < mutation_rate:
                    child = self.mutate_value(child, mutation_rate)
                    # Ensure at least one bit is flipped
                    if child == parent1 or child == parent2:
                        bit_to_flip = random.randint(0, 66)
                        child ^= (1 << bit_to_flip)
                
                if self.quick_filter(child):
                    new_population.append(child)
            
            population = new_population
            generation += 1
            generations_without_improvement += 1
            
            # Progress logging
            if generation % 10 == 0:
                logging.info(f"Generation {generation}: Best fitness = {best_fitness:.6f}, Mutation rate = {mutation_rate:.3f}")
        
        return best_candidate

    def mutate_value(self, value: int, mutation_rate: float) -> int:
        """Apply sophisticated mutation strategies"""
        # Convert to binary for bit manipulation
        binary = format(value, '067b')
        result = list(binary)
        
        # Strategy 1: Single bit flips with decreasing probability
        for i in range(67):
            if random.random() < mutation_rate * (1 - i/67):  # Higher probability for lower bits
                result[i] = '1' if result[i] == '0' else '0'
        
        # Strategy 2: Bit swaps (10% chance)
        if random.random() < 0.1:
            pos1, pos2 = random.sample(range(67), 2)
            result[pos1], result[pos2] = result[pos2], result[pos1]
        
        # Strategy 3: Segment reversal (5% chance)
        if random.random() < 0.05:
            start = random.randint(1, 60)  # Avoid MSB
            length = random.randint(2, 6)  # Small segments
            end = min(start + length, 66)
            segment = result[start:end]
            segment.reverse()
            result[start:end] = segment
        
        # Strategy 4: Pattern-based mutations (15% chance)
        if random.random() < 0.15:
            pattern_length = random.randint(2, 4)
            start = random.randint(1, 67 - pattern_length)
            pattern = result[start:start + pattern_length]
            # Repeat or invert pattern
            if random.random() < 0.5:
                result[start + pattern_length:start + 2*pattern_length] = pattern
            else:
                inverted = ['1' if b == '0' else '0' for b in pattern]
                result[start + pattern_length:start + 2*pattern_length] = inverted
        
        # Convert back to integer
        mutated = int(''.join(result), 2)
        
        # Ensure MSB is 1
        mutated |= (1 << 66)
        
        return mutated

    def crossover(self, parent1: int, parent2: int) -> int:
        """Perform multi-point crossover between two parents"""
        # Convert parents to binary strings
        bin1 = format(parent1, '067b')
        bin2 = format(parent2, '067b')
        
        # Choose 2-4 crossover points
        num_points = random.randint(2, 4)
        points = sorted(random.sample(range(1, 66), num_points))  # Avoid endpoints
        
        # Build child by alternating segments
        result = ''
        start = 0
        use_parent1 = True
        
        for point in points + [67]:  # Add endpoint
            if use_parent1:
                result += bin1[start:point]
            else:
                result += bin2[start:point]
            start = point
            use_parent1 = not use_parent1
        
        # Convert back to integer
        child = int(result, 2)
        
        # Ensure MSB is 1
        child |= (1 << 66)
        
        return child

    def tournament_select(self, fitness_scores: List[Tuple[int, float]], base_tournament_size: int = 5) -> int:
        """Tournament selection with adaptive size and diversity preservation"""
        if not fitness_scores:
            return None
        
        # Adjust tournament size based on population diversity
        unique_fitness = len(set(score[1] for score in fitness_scores))
        diversity_ratio = unique_fitness / len(fitness_scores)
        
        # Smaller tournaments when diversity is low to reduce selection pressure
        tournament_size = max(2, int(base_tournament_size * diversity_ratio))
        
        # Select tournament participants
        tournament = random.sample(fitness_scores, min(tournament_size, len(fitness_scores)))
        
        # Primary selection based on fitness
        best_candidate = max(tournament, key=lambda x: x[1])[0]
        
        # Secondary tournament for diversity (20% chance)
        if random.random() < 0.2:
            second_tournament = random.sample(fitness_scores, min(tournament_size, len(fitness_scores)))
            second_best = max(second_tournament, key=lambda x: x[1])[0]
            
            # XOR distance between candidates
            distance = bin(best_candidate ^ second_best).count('1')
            
            # If candidates are very similar, pick the second one (30% chance)
            if distance < 10 and random.random() < 0.3:
                return second_best
        
        return best_candidate

    def evaluate_fitness(self, candidate: int) -> float:
        """Enhanced fitness evaluation using sequence insights"""
        try:
            hex_str = format(candidate, 'x').zfill(64)
            pubkey_hex = '04' + hex_str
            
            # Generate hash160
            sha256_hash = hashlib.sha256(bytes.fromhex(pubkey_hex)).digest()
            ripemd160_hash = self.ripemd160(sha256_hash)
            hash160_hex = ripemd160_hash.hex()
            
            fitness = 0.0
            
            # Base fitness on matching prefix length
            matching_length = 0
            for i, (a, b) in enumerate(zip(hash160_hex, self.target_hash160)):
                if a != b:
                    break
                matching_length = i + 1
            
            if matching_length >= 3:
                # Core prefix matching (739)
                fitness += 0.5
                
                # Additional matches
                additional_matches = matching_length - 3
                if additional_matches > 0:
                    fitness += 0.5 * (1.5 ** additional_matches)
                
                # Sequence-based scoring
                key_66 = 0x2832ed74f2b5e35ee
                
                # Check mathematical relationships
                if (candidate > key_66 and 
                    candidate < key_66 * 2 and
                    bin(candidate).count('1') >= bin(key_66).count('1')):
                    fitness += 0.3
                
                # Check XOR relationships
                xor_with_66 = candidate ^ key_66
                if bin(xor_with_66).count('1') <= 20:  # Limited bit differences
                    fitness += 0.2
                
                # Check growth pattern
                if candidate > key_66 and candidate - key_66 < key_66 - 0x1a838b13505b26867:
                    fitness += 0.2
                
                # Analyze bit patterns
                candidate_bits = format(candidate, '067b')
                target_bits = format(int(self.target_hash160[:16], 16), '067b')
                matching_bits = sum(a == b for a, b in zip(candidate_bits, target_bits))
                fitness += 0.1 * (matching_bits / 67)
            
            return fitness
        except Exception as e:
            logging.error(f"Error evaluating fitness: {str(e)}")
            return float('-inf')

    def generate_optimized_population(self, base_candidate: int, size: int) -> List[int]:
        """Generate population using mathematical optimization and sequence insights"""
        population = []
        
        # Known key 66 from sequence
        key_66 = 0x2832ed74f2b5e35ee
        
        # Calculate expected growth patterns based on sequence analysis
        patterns = [
            lambda x: ((x + 2) ** 4) & ((1 << 67) - 1),  # (x+2)^4 pattern
            lambda x: (x ^ 67) * 2,  # XOR with key pattern
            lambda x: x + (x ^ key_66),  # Relationship with previous key
            lambda x: x | (1 << 66),  # Ensure 67 bits with MSB
        ]
        
        # Generate candidates using each pattern
        for pattern in patterns:
            for _ in range(size // len(patterns)):
                try:
                    variant = pattern(base_candidate)
                    # Ensure 67 bits
                    variant |= (1 << 66)
                    if self.quick_filter(variant):
                        population.append(variant)
                except Exception:
                    continue
        
        # Add mathematically derived candidates
        while len(population) < size:
            # Try different mathematical transformations based on sequence
            ops = [
                lambda x: x + (key_66 & 0xFFFF),  # Add lower 16 bits of key 66
                lambda x: x ^ (key_66 >> 32),     # XOR with upper bits of key 66
                lambda x: x + ((x & 0xFF) << 8),  # Byte-based transformation
                lambda x: x ^ ((x >> 16) << 32),  # Bit shifting pattern
            ]
            
            op = random.choice(ops)
            try:
                variant = op(base_candidate)
                variant |= (1 << 66)  # Ensure 67 bits
                if self.quick_filter(variant):
                    population.append(variant)
            except Exception:
                continue
            
            if len(population) >= size:
                break
        
        # If we still need more candidates, use bit pattern analysis
        if len(population) < size:
            # Analyze bit patterns in successful candidates
            if population:
                successful_bits = []
                for candidate in population[:10]:  # Analyze top 10
                    binary = format(candidate, '067b')
                    successful_bits.append([int(b) for b in binary])
                
                # Calculate bit probabilities
                bit_probs = [sum(bits[i] for bits in successful_bits) / len(successful_bits) 
                           for i in range(67)]
                
                # Generate new candidates based on probabilities
                while len(population) < size:
                    new_bits = ['1']  # MSB always 1
                    for prob in bit_probs[1:]:
                        new_bits.append('1' if random.random() < prob else '0')
                    
                    variant = int(''.join(new_bits), 2)
                    if self.quick_filter(variant):
                        population.append(variant)
        
        return population[:size]  # Ensure we return exactly size candidates

    def string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using Levenshtein distance
        """
        def levenshtein(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein(s2, s1)
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        max_len = max(len(str1), len(str2))
        distance = levenshtein(str1, str2)
        similarity = 1 - (distance / max_len)
        return similarity

    def make_initial_prediction(self) -> Optional[int]:
        """Make initial prediction based on sequence analysis"""
        if not self.sequence:
            return None
        
        # Get the last few values for analysis
        last_values = self.sequence[-5:]
        if not last_values:
            return None
        
        # Try different prediction methods
        predictions = []
        weights = {
            'linear': 0.2,
            'geometric': 0.3,
            'fft': 0.2,
            'crypto': 0.3
        }
        
        # Linear extrapolation
        try:
            diffs = [b - a for a, b in zip(last_values[:-1], last_values[1:])]
            avg_diff = sum(diffs) / len(diffs)
            linear_pred = int(last_values[-1] + avg_diff)
            if linear_pred.bit_length() == 67:
                predictions.append(('linear', linear_pred))
        except Exception:
            pass
        
        # FFT-based prediction
        try:
            fft_values = np.fft.fft(last_values)
            next_value = np.real(np.fft.ifft(fft_values))[0]
            fft_pred = int(next_value)
            if fft_pred.bit_length() == 67:
                predictions.append(('fft', fft_pred))
        except Exception:
            pass
        
        # Cryptographic pattern
        try:
            # XOR the last two values
            crypto_pred = last_values[-1] ^ last_values[-2]
            if crypto_pred.bit_length() < 67:
                crypto_pred |= (1 << 66)  # Set MSB to 1
            predictions.append(('crypto', crypto_pred))
        except Exception:
            pass
        
        if not predictions:
            return None
        
        # Log prediction weights and individual predictions
        logging.info(f"Prediction weights: {weights}")
        logging.info(f"Individual predictions: {predictions}")
        
        # Calculate weighted average
        total_weight = sum(weights[p[0]] for p in predictions if p[0] in weights)
        if total_weight == 0:
            return None
        
        weighted_sum = sum(weights[p[0]] * p[1] for p in predictions if p[0] in weights)
        final_prediction = int(weighted_sum / total_weight)
        
        # Ensure 67 bits
        if final_prediction.bit_length() < 67:
            final_prediction |= (1 << 66)  # Set MSB to 1
        
        logging.info(f"Final weighted prediction for index {self.index}: {final_prediction}")
        logging.info(f"Binary length: {final_prediction.bit_length()} bits")
        
        return final_prediction

    def solve(self) -> Optional[int]:
        """
        Main solving routine to find the 67th index key using evolutionary approach
        """
        logging.info("Starting puzzle solving process for index 67")
        logging.info(f"Target address: {self.target_address}")
        logging.info(f"Target Hash160: {self.target_hash160}")
        
        # Reset static counters
        PuzzleSolver.total_candidates_checked = 0
        PuzzleSolver.total_generations = 0
        PuzzleSolver.best_fitness_overall = float('-inf')
        PuzzleSolver.seen_addresses = set()
        PuzzleSolver.stagnation_counter = 0
        
        # Load and analyze known sequences
        self.load_sequence()
        
        # Make initial prediction
        initial_prediction = self.make_initial_prediction()
        
        if initial_prediction is None:
            logging.error("Could not generate initial prediction")
            return None
        
        # Evolve the prediction
        final_prediction = self.evolve_prediction(initial_prediction)
        
        # Validate and save final prediction
        if final_prediction is not None and self.validate_prediction(final_prediction):
            # Save result with private key information
            self.save_result(final_prediction)
            return final_prediction
        else:
            logging.warning("Could not find valid prediction through evolution")
            return None

    def save_result(self, result: int) -> None:
        """Save the successful result to files"""
        try:
            # Format result in different representations
            hex_str = hex(result)[2:].zfill(64)
            pubkey_hex = '04' + hex_str
            hash160_hex = self.get_hash160(hex_str)
            address = self.pubkey_to_address(pubkey_hex)
            
            # Save to index_67_prediction.txt
            prediction_file = self.output_dir / 'index_67_prediction.txt'
            with open(prediction_file, 'w') as f:
                f.write("=== SOLUTION FOUND ===\n\n")
                f.write("Private Key:\n")
                f.write(f"Decimal: {result}\n")
                f.write(f"Hexadecimal: {hex_str}\n")
                f.write(f"Binary: {format(result, '067b')}\n\n")
                f.write("Public Key Information:\n")
                f.write(f"Public key: {pubkey_hex}\n")
                f.write(f"Bitcoin address: {address}\n")
                f.write(f"Hash160: {hash160_hex}\n")
                f.write(f"\nBit length: {result.bit_length()} bits\n")
            
            # Save to private_key.txt
            private_key_file = self.output_dir / 'private_key.txt'
            with open(private_key_file, 'w') as f:
                f.write(f"Private key for index {self.index}:\n")
                f.write(f"Decimal: {result}\n")
                f.write(f"Hexadecimal: {hex_str}\n")
                f.write(f"Binary: {format(result, '067b')}\n")
                f.write(f"\nFound after {PuzzleSolver.total_generations} generations\n")
                f.write(f"Total candidates checked: {PuzzleSolver.total_candidates_checked}\n")
            
            logging.info(f"Results saved to {prediction_file} and {private_key_file}")
            
        except Exception as e:
            logging.error(f"Error saving result: {str(e)}")

def main():
    """Main entry point"""
    solver = PuzzleSolver(index=67)
    if not solver.sequence:
        return
    
    # Make initial prediction
    prediction = solver.make_initial_prediction()
    if prediction is None:
        logging.error("Failed to make initial prediction")
        return
    
    # Try to evolve a solution
    result = solver.evolve_prediction(prediction)
    
    if result:
        # Save successful result
        solver.save_result(result)
        print(f"\nFound valid prediction for index 67: {hex(result)}")
    else:
        print("\nCould not determine a valid prediction for index 67")

if __name__ == '__main__':
    main()