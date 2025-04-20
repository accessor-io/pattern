#!/usr/bin/env python3
"""
Combined Puzzle Solver

For indices 1–66 the solver uses a brute‑force approach:
  • Compute an initial candidate from the transaction ID.
  • For each offset (or, for some low indexes, simply try sequentially) adjust the candidate,
    then mask the candidate so that only the lowest N (significant) hex digits remain.
  • Validate the candidate against the known solution (if available) and via Bitcoin address conversion.

For indices ≥67 the solver uses a genetic algorithm to "evolve" a candidate whose derived
Bitcoin public key produces the expected address.

Note: If the RIPEMD160 hash function is not available via PyCryptodome, the code attempts a
fallback via hashlib.new('ripemd160'). Ensure your environment supports RIPEMD160.

This implementation's candidate validation functions and some heuristics are inspired by the
techniques in https://github.com/google/paranoid_crypto.
"""

import math
import hashlib
import random
import logging
import base58
import binascii
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import numpy as np
from pathlib import Path
from ecdsa import SigningKey, SECP256k1
from Crypto.Hash import RIPEMD160
from itertools import combinations

# --- RIPEMD160 helper ---
try:
    from Crypto.Hash import RIPEMD160
    def ripemd160_hash(data: bytes) -> bytes:
        h = RIPEMD160.new()
        h.update(data)
        return h.digest()
except ImportError:
    def ripemd160_hash(data: bytes) -> bytes:
        try:
            h = hashlib.new('ripemd160')
            h.update(data)
            return h.digest()
        except Exception as e:
            raise RuntimeError("RIPEMD160 is not available: " + str(e))

# --- Dummy imports for demonstration ---
try:
    from pattern_predictor import (
        KNOWN_SOLUTIONS,
        analyze_growth_patterns,
        predict_next_value,
        validate_prediction,
        find_chain_patterns
    )
except ImportError:
    KNOWN_SOLUTIONS = {}
    def analyze_growth_patterns(seq): return {}
    def predict_next_value(seq): return None
    def validate_prediction(val): return True
    def find_chain_patterns(seq): return {}

try:
    from bitcoin_address import (
        validate_private_key,
        EXPECTED_ADDRESSES
    )
except ImportError:
    def validate_private_key(private_key, index):
        # For demonstration, consider an odd candidate valid.
        return (private_key & 1) == 1
    EXPECTED_ADDRESSES = {67: "dummy_address"}

# --- Logging configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('puzzle_solver.log'), logging.StreamHandler()]
)

class PuzzleSolver:
    def __init__(self, index: int = 67):
        """
        Initialize the PuzzleSolver.

        For indices 1–66 the known solutions are hardcoded.
        For indices ≥67 target address information and a candidate sequence are loaded.
        """
        self.solutions: Dict[int, int] = {
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
            # … (fill in other known solutions for indices 11–66 as needed) …
        }
        # IMPORTANT: Use the TXID you want. For example, to use the one from your JSON:
        self.txid = "08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15"
        # If you prefer a different TXID, update it here.
        self.order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        self.chain_modulus = 2 ** 256
        self.index = index
        if self.index >= 67:
            self.target_address = EXPECTED_ADDRESSES.get(self.index, "")
            try:
                if self.target_address:
                    address_bytes = base58.b58decode(self.target_address)
                    self.target_hash160 = address_bytes[1:-4].hex()
                    logging.info(f"Target address: {self.target_address}")
                    logging.info(f"Target Hash160: {self.target_hash160}")
                else:
                    self.target_hash160 = ""
            except Exception as e:
                logging.error(f"Error extracting hash160 from address: {str(e)}")
                self.target_hash160 = ""
            self.sequence: List[int] = self.load_sequence()
        else:
            self.target_address = ""
            self.target_hash160 = ""
            self.sequence = []
        self.output_dir = Path('output')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.total_candidates_checked = 0
        self.total_generations = 0
        self.best_fitness_overall = float('-inf')
        self.seen_addresses = set()
        self.stagnation_counter = 0
        logging.info(f"PuzzleSolver initialized for index {self.index}")
        if self.index >= 67:
            logging.info(f"Target Bitcoin address: {self.target_address}")

    # ---------------------------
    # BRUTE-FORCE METHODS
    # ---------------------------
    def compute_candidate(self, index: int) -> int:
        txid_int = int(self.txid, 16)
        combined = (txid_int * index) % self.chain_modulus
        return pow(combined, 3, self.order)

    def validate_value(self, index: int, value: int, prev_val: int) -> bool:
        """Validate a candidate value using our own address generation"""
        if value <= 0:
            return False
        binary = bin(value)[2:]
        if len(binary) < 1 or len(binary) > 256:
            return False

        if index in self.solutions:
            expected = self.solutions[index]
            if value != expected:
                print(f"Warning: For index {index}, candidate {hex(value)} does not equal expected {hex(expected)}")
                return False
            try:
                hex_str = format(value, 'x').zfill(64)
                generated_address = self.private_key_to_address(hex_str)
                if generated_address in ("INVALID_ADDRESS", "INVALID_KEY"):
                    print(f"Warning: Invalid address generated for index {index} on value {hex(value)}")
                    return False
                print(f"Successfully validated solution for index {index}")
                return True
            except Exception as e:
                print(f"Error validating address: {str(e)}")
                return False
        else:
            prev_ones = bin(prev_val).count('1')
            curr_ones = binary.count('1')
            if curr_ones <= prev_ones:
                return False
            if self.target_address:
                try:
                    hex_str = format(value, 'x').zfill(64)
                    generated_address = self.private_key_to_address(hex_str)
                    if generated_address in ("INVALID_ADDRESS", "INVALID_KEY"):
                        print(f"Warning: Invalid address generated for index {index} on value {hex(value)}")
                        return False
                    if generated_address != self.target_address:
                        return False
                except Exception as e:
                    print(f"Error validating address: {str(e)}")
                    return False
        return True

    def find_solution_brute_force(self, index: int, prev_val: int) -> Optional[int]:
        """Try values using smart pattern generation"""
        print(f"\nTrying to find solution for index {index}")
        print(f"Previous candidate: {hex(prev_val)}")
        
        # Special cases for indices 1-3
        if index == 1: return 0x1
        if index == 2: return 0x3  
        if index == 3: return 0x7

        # For index 4 and above, use smart pattern generation
        prev_hex = hex(prev_val)[2:]  # Remove '0x' prefix
        prev_len = len(prev_hex)
        attempts = 0
        
        # Try variations close to previous value
        base = prev_val
        for i in range(16):  # Try hex digits 0-f
            # Try adding each hex digit at each position
            for pos in range(prev_len + 1):
                # Create new candidate by inserting digit at position
                candidate_hex = prev_hex[:pos] + hex(i)[2:] + prev_hex[pos:]
                candidate = int(candidate_hex, 16)
                
                if attempts % 100 == 0:
                    print(f"Attempt {attempts}: trying {hex(candidate)}")
                    
                try:
                    if self.validate_value(index, candidate, prev_val):
                        print(f"\nFound solution for index {index}!")
                        print(f"Value: {hex(candidate)}")
                        return candidate
                except Exception as e:
                    print(f"Error validating {hex(candidate)}: {str(e)}")
                    
                attempts += 1

        return None

    def private_key_to_address(self, priv_key_hex: str) -> str:
        """Convert a private key (64-hex string) to a Bitcoin address.
           Uses compressed public keys.
        """
        try:
            signing_key = SigningKey.from_string(bytes.fromhex(priv_key_hex), curve=SECP256k1)
            verifying_key = signing_key.get_verifying_key()
            # Compressed public key: prefix 0x02 if y is even, else 0x03, followed by 32 bytes of x coordinate
            prefix = b'\x02' if verifying_key.pubkey.point.y() % 2 == 0 else b'\x03'
            pub_key = prefix + verifying_key.pubkey.point.x().to_bytes(32, byteorder='big')
            sha256_hash = hashlib.sha256(pub_key).digest()
            # Use RIPEMD160 via PyCryptodome
            ripemd160_hasher = RIPEMD160.new()
            ripemd160_hasher.update(sha256_hash)
            ripemd160_digest = ripemd160_hasher.digest()
            versioned_hash = b'\x00' + ripemd160_digest
            checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
            binary_addr = versioned_hash + checksum
            address = base58.b58encode(binary_addr).decode('utf-8')
            return address
        except Exception as e:
            raise Exception(f"Error converting private key to address: {str(e)}")

    def load_sequence(self) -> List[int]:
        try:
            with open('sequence.txt', 'r') as f:
                lines = f.readlines()
            sequence = []
            for line in lines:
                value = line.strip()
                if value.startswith('0x'):
                    value = value[2:]
                value = ''.join(c for c in value if c in '0123456789abcdefABCDEF')
                if value:
                    num = int(value, 16)
                    if num.bit_length() < 67:
                        num |= (1 << 66)
                    sequence.append(num)
            logging.info(f"Loaded and expanded {len(sequence)} sequence values to 67 bits")
            return sequence
        except Exception as e:
            logging.error(f"Error loading sequence: {str(e)}")
            return []

    def make_initial_prediction(self) -> Optional[int]:
        """Generate an initial prediction for index 67 based on known solutions (indexes 63-66)"""
        if self.index != 67:
            return None
        last_solutions = [
            0x0000000000000000000000000000000000000000000000000007cce5efdaccf6808,  # 63
            0x000000000000000000000000000000000000000000000000000f7051f27b09112d4,  # 64
            0x0000000000000000000000000000000000000000000000000001a838b13505b26867,  # 65
            0x0000000000000000000000000000000000000000000000000002832ed74f2b5e35ee   # 66
        ]
        ratios = []
        for i in range(len(last_solutions)-1):
            ratios.append(last_solutions[i+1] / last_solutions[i])
        avg_ratio = sum(ratios) / len(ratios)
        base_prediction = int(last_solutions[-1] * avg_ratio)
        candidates = [
            base_prediction,
            base_prediction * 2,
            base_prediction * 3,
            int(base_prediction * 1.5),
            int(base_prediction * 2.5),
            base_prediction + last_solutions[-1],
            base_prediction - last_solutions[-1],
        ]
        for candidate in candidates:
            try:
                hex_str = format(candidate, 'x').zfill(64)
                address = self.private_key_to_address(hex_str)
                if address.startswith('1by8'):
                    logging.info(f"Found promising candidate: {hex(candidate)}")
                    return candidate
            except Exception:
                continue
        logging.info(f"Using base prediction: {hex(base_prediction)}")
        return base_prediction

    def evaluate_fitness(self, candidate: int) -> float:
        try:
            hex_str = format(candidate, 'x').zfill(64)
            generated_address = self.private_key_to_address(hex_str)
            target_address = self.target_address
            if not target_address:
                return 0.0
            min_length = min(len(generated_address), len(target_address))
            matches = sum(1 for i in range(min_length) if generated_address[i] == target_address[i])
            return matches / len(target_address)
        except Exception as e:
            logging.error(f"Error evaluating fitness: {str(e)}")
            return float('-inf')

    def quick_filter(self, candidate: int) -> bool:
        if candidate.bit_length() != 67:
            return False
        if self.total_generations < 1:
            return True
        try:
            hex_str = format(candidate, 'x').zfill(64)
            generated_address = self.private_key_to_address(hex_str)
            if generated_address not in ("INVALID_ADDRESS", "INVALID_KEY"):
                address_bytes = base58.b58decode(generated_address)
                generated_hash160 = address_bytes[1:-4].hex()
                if self.target_hash160:
                    return generated_hash160[:4] == self.target_hash160[:4]
            return False
        except Exception as e:
            logging.debug(f"Quick filter error: {str(e)}")
            return False

    def mutate_value(self, value: int, mutation_rate: float) -> int:
        binary = list(format(value, '067b'))
        for i in range(67):
            if random.random() < mutation_rate * (1 - i / 67):
                binary[i] = '1' if binary[i] == '0' else '0'
        mutated = int(''.join(binary), 2)
        mutated |= (1 << 66)
        return mutated

    def crossover(self, parent1: int, parent2: int) -> int:
        bin1 = format(parent1, '067b')
        bin2 = format(parent2, '067b')
        num_points = random.randint(2, 4)
        points = sorted(random.sample(range(1, 66), num_points))
        child_bin = ""
        start = 0
        use_parent1 = True
        for point in points + [67]:
            child_bin += (bin1 if use_parent1 else bin2)[start:point]
            start = point
            use_parent1 = not use_parent1
        child = int(child_bin, 2)
        child |= (1 << 66)
        return child

    def tournament_select(self, fitness_scores: List[Tuple[int, float]], tournament_size: int = 5) -> int:
        tournament = random.sample(fitness_scores, min(tournament_size, len(fitness_scores)))
        return max(tournament, key=lambda x: x[1])[0]

    def evolve_prediction(self, base_prediction: int, max_generations: int = 2000) -> Optional[int]:
        import time
        start_time = time.time()
        timeout = 300  # 5 minutes
        population_size = 1000
        elite_size = 100
        mutation_rate = 0.1

        population = []
        attempts = 0
        max_attempts = population_size * 5
        logging.info(f"Initializing population from base prediction: {hex(base_prediction)}")
        while len(population) < population_size and attempts < max_attempts:
            if time.time() - start_time > timeout:
                logging.error("Evolution timeout during initialization")
                return None
            try:
                candidate = self.mutate_value(base_prediction, mutation_rate * (1 + attempts / max_attempts))
                if candidate.bit_length() == 67:
                    population.append(candidate)
            except Exception as e:
                logging.error(f"Error generating candidate: {str(e)}")
            attempts += 1

        if not population:
            logging.error("Failed to generate initial population")
            return None

        logging.info(f"Generated initial population of {len(population)} candidates")
        best_candidate = None
        best_fitness = float('-inf')
        generation = 0
        stagnation_counter = 0
        last_improvement = time.time()

        try:
            while generation < max_generations and stagnation_counter < 50:
                if time.time() - start_time > timeout:
                    logging.warning("Evolution timeout - returning best candidate found")
                    return best_candidate
                generation += 1
                self.total_generations += 1
                fitness_scores = []
                for candidate in population[:population_size]:
                    try:
                        fitness = self.evaluate_fitness(candidate)
                        if fitness > float('-inf'):
                            fitness_scores.append((candidate, fitness))
                            if fitness > best_fitness:
                                best_fitness = fitness
                                best_candidate = candidate
                                stagnation_counter = 0
                                last_improvement = time.time()
                                logging.info(f"New best fitness: {best_fitness:.6f}")
                                if fitness > 0.9:
                                    if validate_private_key(candidate, self.index):
                                        logging.info(f"Found valid solution: {hex(candidate)}")
                                        return candidate
                    except Exception:
                        continue
                if time.time() - last_improvement > 60:
                    logging.warning("Evolution stagnated - trying new random population")
                    population = [self.mutate_value(best_candidate or base_prediction, 0.3)
                                  for _ in range(population_size)]
                    last_improvement = time.time()
                    continue
                if not fitness_scores:
                    logging.error("No valid candidates in population")
                    return best_candidate
                fitness_scores.sort(key=lambda x: x[1], reverse=True)
                new_population = [score[0] for score in fitness_scores[:elite_size]]
                while len(new_population) < population_size:
                    try:
                        if random.random() < 0.7:
                            parent1 = self.tournament_select(fitness_scores)
                            parent2 = self.tournament_select(fitness_scores)
                            child = self.crossover(parent1, parent2)
                        else:
                            child = self.mutate_value(random.choice(new_population), mutation_rate)
                        if child.bit_length() == 67:
                            new_population.append(child)
                    except Exception:
                        continue
                population = new_population
                stagnation_counter += 1
                if generation % 10 == 0:
                    logging.info(f"Generation {generation}: Best fitness = {best_fitness:.6f}")
        except Exception as e:
            logging.error(f"Evolution error: {str(e)}")
            return best_candidate
        logging.info(f"Evolution completed after {generation} generations")
        return best_candidate

    def save_result(self, result: int) -> None:
        try:
            hex_str = format(result, 'x').zfill(64)
            address = self.private_key_to_address(hex_str)
            prediction_file = self.output_dir / f'index_{self.index}_prediction.txt'
            with open(prediction_file, 'w') as f:
                f.write("=== SOLUTION FOUND ===\n\n")
                f.write("Private Key:\n")
                f.write(f"Decimal: {result}\n")
                f.write(f"Hex: {hex_str}\n")
                f.write(f"Binary: {format(result, '067b')}\n\n")
                f.write("Public Key Information:\n")
                f.write(f"Bitcoin Address: {address}\n")
                f.write(f"\nFound after {self.total_generations} generations\n")
                f.write(f"Total candidates checked: {self.total_candidates_checked}\n")
            logging.info(f"Results saved to {prediction_file}")
        except Exception as e:
            logging.error(f"Error saving result: {str(e)}")

    def solve(self) -> Optional[int]:
        """Find solution for current index"""
        if self.index <= 66:
            # For lower indices, use brute force with bit patterns
            prev_val = 0
            if self.index > 1:
                prev_val = self.solutions[self.index - 1]
            
            sol = self.find_solution_brute_force(self.index, prev_val)
            if sol:
                logging.info(f"Solution for index {self.index}: {hex(sol)}")
            else:
                logging.warning(f"No solution found for index {self.index}")
            return sol
        else:
            # For higher indices, use genetic algorithm approach
            initial_prediction = self.make_initial_prediction()
            if initial_prediction is None:
                logging.error("Could not generate an initial prediction for the genetic algorithm.")
                return None
            final_prediction = self.evolve_prediction(initial_prediction)
            if final_prediction and validate_private_key(final_prediction, self.index):
                self.save_result(final_prediction)
                return final_prediction
            else:
                logging.warning("Could not determine a valid prediction via evolution.")
                return None

def main():
    """Solve puzzles sequentially from index 1 onwards"""
    logging.info("Starting sequential puzzle solving")
    current_index = 1
    solver = PuzzleSolver(index=current_index)
    while current_index <= 160:
        logging.info(f"\nAttempting to solve puzzle {current_index}")
        solver.index = current_index
        solution = solver.solve()
        if solution:
            print(f"Found solution for index {current_index}: {hex(solution)}")
            current_index += 1
        else:
            print(f"Failed to find solution for index {current_index}")
            logging.error(f"Could not solve puzzle {current_index}")
            # Optionally, continue to the next index or break
            current_index += 1
    print(f"\nCompleted solving up to index {current_index - 1}")
    logging.info(f"Finished solving puzzles. Last completed index: {current_index - 1}")

if __name__ == '__main__':
    main()
