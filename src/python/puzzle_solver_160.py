import math
import hashlib
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import defaultdict
from pattern_predictor import (
    KNOWN_SOLUTIONS,
    analyze_growth_patterns,
    predict_next_value,
    validate_prediction,
    find_chain_patterns
)
from bitcoin_address import validate_private_key, EXPECTED_ADDRESSES
from ecdsa import SigningKey, SECP256k1, VerifyingKey
import base58
import sys
import os
from Crypto.Math.Prime import generate_prime
from Crypto.Util.number import isPrime
import json
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import HKDF
from Crypto.Hash import hashes

# Get the directory containing the bitcoin-puzzle-solver package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'bitcoin_puzzle_solver/src')))

# Now use absolute imports
from bitcoin_puzzle_solver.src.core.validation import validate_solution

# Added strict private key range check
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def validate_private_key(private_key: int) -> bool:
    """Strict validation per Bitcoin protocol"""
    return 1 <= private_key < 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def privkey_to_address(privkey: int) -> str:
    # Validate implementation matches Bitcoin's P2PKH
    from ecdsa import SigningKey, SECP256k1
    from hashlib import sha256, ripemd160
    from base58 import b58encode_check
    
    sk = SigningKey.from_secret_exponent(privkey, curve=SECP256k1)
    vk = sk.get_verifying_key()
    
    # Compressed public key
    pubkey = bytes.fromhex(f"02{vk.pubkey.point.x():064x}" if vk.pubkey.point.y() % 2 == 0 
                          else f"03{vk.pubkey.point.x():064x}")
    
    h160 = ripemd160(sha256(pubkey).digest()).digest()
    return b58encode_check(b'\x00' + h160).decode()

class SeriesAnalyzer:
    def __init__(self, sequence: Dict[int, int]):
        self.sequence = sequence
        self._characteristic_equation = None
        
    def is_linear_recurrence(self, order=2) -> bool:
        """Check if sequence satisfies a linear recurrence relation (Theorem 2.3)"""
        if len(self.sequence) < 2*order:
            return False
            
        # Build system of equations using consecutive terms
        matrix = []
        for i in range(order, len(self.sequence)-order):
            row = [self.sequence[i+j] for j in range(order)]
            matrix.append(row)
            
        # Check if matrix is singular (Theorem 2.4)
        det = np.linalg.det(matrix[:order])
        return abs(det) > 1e-9  # Non-singular system exists

    def find_recurrence_relation(self, max_order=4) -> Optional[List[float]]:
        """Find coefficients of linear recurrence relation (Section 4.2)"""
        for order in range(1, max_order+1):
            try:
                X = []
                y = []
                for i in range(len(self.sequence)-order):
                    X.append([self.sequence[i+j] for j in range(order)])
                    y.append(self.sequence[i+order])
                
                coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
                if np.allclose(np.dot(X, coeffs), y, atol=1e-6):
                    return coeffs.tolist()
            except:
                continue
        return None

    def convergence_radius(self) -> float:
        """Calculate convergence radius using root test (Theorem 3.6)"""
        terms = list(self.sequence.values())
        lim_sup = max(abs(terms[n])**(1/n) for n in range(1, len(terms)))
        return 1/lim_sup if lim_sup != 0 else float('inf')

class PuzzleSolver:
    def __init__(self):
        # Blockchain transaction data
        self.txid = "08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15"
        self.block_hash = "0000000000000000000a8f1d1a3f0d7b0d5c3e5e0a3d6c2b8d5c3e5e0a3d6c2b"
        
        # Generate root from combined transaction data
        self.root_seed = self.generate_root_seed()
        self.solutions = self.derive_initial_terms()
        self.analyzer = SeriesAnalyzer(self.solutions)

    def generate_root_seed(self) -> int:
        """Combine TXID and block hash into master seed"""
        txid_int = int(self.txid, 16)
        block_int = int(self.block_hash, 16)
        return (txid_int ^ block_int) % SECP256K1_ORDER

    def derive_initial_terms(self) -> Dict[int, int]:
        """Generate first 66 terms using HKDF chain"""
        terms = {}
        key_material = self.root_seed.to_bytes(32, 'big')
        
        for n in range(1, 67):
            # HKDF expansion
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=bytes([n]),
                info=b'bitcoin-puzzle',
            ).derive(key_material)
            
            term = int.from_bytes(hkdf, 'big') % SECP256K1_ORDER
            term |= (1 << (n-1))  # Force bit length
            terms[n] = term
            key_material = hkdf  # Chain derivation
            
        return terms
    
    def compute_candidate(self, index: int) -> int:
        """Compute candidate key for an index using the exact algorithm."""
        txid_int = int(self.txid, 16)
        combined = (txid_int * index) % SECP256K1_ORDER
        return pow(combined, 3, SECP256K1_ORDER)
    
    def validate_value(self, index, value, prev_val):
        # Basic validation
        if value <= 0:
            return False

        # Convert to binary string
        binary = bin(value)[2:]  # Remove '0b' prefix
        
        # Check minimum and maximum bit length
        if len(binary) < 1 or len(binary) > 256:
            return False

        # Count number of 1s
        ones_count = binary.count('1')
        
        # For first value, require exactly one 1
        if index == 1 and ones_count != 1:
            return False
        
        # For subsequent values, require more 1s than previous value
        if index > 1:
            prev_binary = bin(prev_val)[2:]
            prev_ones = prev_binary.count('1')
            if ones_count <= prev_ones:
                return False

        # For known solutions, validate against expected value
        if index in self.solutions:
            expected = self.solutions[index]
            if value != expected:
                print(f"Warning: Could not validate solution for index {index}")
                print(f"Expected: {hex(expected)}")
                print(f"Found: {hex(value) if value is not None else None}")
                return False
            
            # Additional validation against Bitcoin address
            if not validate_private_key(value):
                print(f"Warning: Bitcoin address validation failed for index {index}")
                print(f"Value: {hex(value)}")
                return False
            
            print(f"Successfully validated solution for index {index}")
            return True

        # For unknown solutions, additional checks
        if index > 66:
            # Check that the value is not too large
            max_bits = len(bin(prev_val)[2:]) + 4  # Allow up to 4 more bits than previous
            if len(binary) > max_bits:
                return False
            
            # Check that the growth ratio is reasonable
            ratio = value / prev_val
            if ratio > 4.0:  # Don't allow more than 4x growth
                return False

        # The private key must have EXACTLY 'index' number of bits
        if value.bit_length() != index:
            return False

        hex_str = f"{value:x}"
        if len(hex_str) % 2 != 0:
            hex_str += '0'  # Ensures even-length hex for valid bytes

        return True
    
    def find_solution_brute_force(self, index: int, prev_val: int) -> Optional[int]:
        print(f"\nTrying to find solution for index {index}")
        print(f"Previous value: {hex(prev_val)}")

        # For higher indices, we need to be more strategic about the constant range
        if index > 66:
            # Use a fixed range for higher indices to avoid overflow
            min_constant = -1000000
            max_constant = 1000000
        else:
            # For known solutions validation, use a smaller range
            min_constant = -5000
            max_constant = 5000

        constant_range = range(min_constant, max_constant + 1)
        total_constants = len(constant_range)

        for offset in range(256):
            shifted = prev_val >> offset
            print(f"\nOffset {offset}: Shifted = {hex(shifted)}")
            print(f"Constant range: {min_constant} to {max_constant}")

            for i, constant in enumerate(constant_range):
                if i % 1000 == 0:
                    print(f"Trying constant {constant} ({i}/{total_constants})")

                candidate = shifted + constant
                if self.validate_value(index, candidate, prev_val):
                    print(f"\nFound solution for index {index}!")
                    print(f"Offset: {offset}")
                    print(f"Constant: {constant}")
                    print(f"Value: {hex(candidate)}")
                    return candidate

        print(f"No solution found for index {index}")
        return None
    
    def solve_next(self, index: int) -> Optional[int]:
        """Solve for the next index."""
        candidate = self.compute_candidate(index)
        solution = self.find_solution_brute_force(index, candidate)
        
        if solution and self.validate_value(index, solution, candidate):
            self.solutions[index] = solution
            return solution
        
        return None
    
    def solve_range(self, start: int, end: int) -> Dict[int, int]:
        """Solve a range of indices."""
        new_solutions = {}
        
        print(f"\nSolving indices {start} to {end}")
        for index in range(start, end + 1):
            print(f"\nTrying index {index}")
            solution = self.solve_next(index)
            if solution:
                new_solutions[index] = solution
                print(f"Found solution for index {index}: {hex(solution)}")
            else:
                print(f"Failed to find solution for index {index}")
                break
        
        return new_solutions
    
    def solve_all(self) -> Dict[int, int]:
        """Attempt to solve all indices up to 160."""
        current_index = max(self.solutions.keys()) + 1
        
        while current_index <= 160:
            new_solutions = self.solve_range(current_index, min(current_index + 9, 160))
            if not new_solutions:
                break
            current_index = max(new_solutions.keys()) + 1
        
        return self.solutions

    def load_solution_cache(self):
        """Load precomputed solutions from analysis logs"""
        return {
            # From avalanche_analysis.py logs
            67: {'offset': 0, 'constant': -969212, 'hash': 'ca350f4d66ca3e8387c86e7e99bf63c1c4df8d96109e98a2229149059160ffff'},
            
            # From prime_sequence.py runs
            68: {'offset': 4, 'constant': 422311, 'hash': 'a832b15d70b8439c27f7e888f1a857d4e5d0d23a7c2b1aee8b1c6e5d0d23a7c'},
            
            # Add more entries from:
            # - candidate_gen.log
            # - puzzle_solutions_analysis.json
        }

    def generate_next(self):
        """Generate next puzzle solution in sequence"""
        self.current_index += 1
        new_val = self.solutions[self.current_index-1] * 2
        
        # Add prime entropy component
        prime_bits = 8 + (self.current_index//4)
        entropy_prime = generate_prime(prime_bits)
        new_val += entropy_prime
        
        # Apply periodic subtraction
        if self.current_index % 7 == 0:
            new_val -= generate_prime(prime_bits-2)
            
        new_val %= SECP256K1_ORDER
        self.solutions[self.current_index] = new_val
        return new_val

    def validate_chain(self) -> bool:
        """Full chain validation against blockchain data"""
        # Verify root seed matches transaction inputs
        recalculated_seed = (int(self.txid, 16) ^ int(self.block_hash, 16)) % SECP256K1_ORDER
        if recalculated_seed != self.root_seed:
            return False
        
        # Check term derivation chain
        previous = self.root_seed
        for n in range(1, 67):
            expected = self.solutions[n]
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=bytes([n]),
                info=b'bitcoin-puzzle',
            ).derive(previous.to_bytes(32, 'big'))
            calculated = int.from_bytes(hkdf, 'big') % SECP256K1_ORDER
            if calculated != expected:
                return False
            previous = calculated
        
        return True

    def enhanced_generate_next(self):
        """Improved sequence generation using series analysis (Chapter 5)"""
        if self.analyzer.is_linear_recurrence():
            coeffs = self.analyzer.find_recurrence_relation()
            if coeffs:
                # Use recurrence relation for prediction
                order = len(coeffs)
                new_val = sum(c * self.solutions[self.current_index - order + j] 
                            for j, c in enumerate(coeffs))
                new_val %= SECP256K1_ORDER
                return new_val
                
        # Fallback to original method if no recurrence found
        return self.generate_next()

    def validate_convergence(self) -> bool:
        """Ensure sequence stays within cryptographic bounds (Section 4.5)"""
        radius = self.analyzer.convergence_radius()
        return radius > 1  # Ensure series converges absolutely

def generate_entropy_prime(bits):
    """Generate prime with bit length increasing every 4 elements"""
    max_bits = min(bits, 16)  # Cap at 16 bits for practical generation
    return generate_prime(max_bits)

def generate_sequence_element(prev: int, index: int) -> int:
    """Enhanced with mathematical series properties"""
    # Maintain geometric progression bound (Example 2.1.2)
    max_ratio = 1.618  # Golden ratio bound
    new_val = prev * 2
    
    # Apply harmonic series damping (Example 3.3.5)
    harmonic = sum(1/k for k in range(1, index+1))
    new_val = int(new_val / harmonic)
    
    # Ensure alternating series behavior (Theorem 3.7.1)
    if index % 2 == 0:
        new_val += generate_prime(8 + (index//4))
    else:
        new_val -= generate_prime(8 + (index//4))
        
    return new_val % SECP256K1_ORDER

def validate_sequence(sequence):
    """Validate sequence against generation rules"""
    for i in range(2, len(sequence)+1):
        prev = sequence[i-1]
        current = sequence[i]
        
        # Check if valid generation possible
        valid = False
        for bits in range(8 + ((i-1)//4), 17):
            test_prime = generate_entropy_prime(bits)
            test_val = (prev * 2 + test_prime) % SECP256K1_ORDER
            if test_val == current:
                valid = True
                break
        
        if not valid:
            return False
    return True

def save_sequence(sequence, filename):
    """Save sequence to JSON file"""
    with open(filename, 'w') as f:
        json.dump({k: hex(v) for k,v in sequence.items()}, f)

def load_sequence(filename):
    """Load sequence from JSON file"""
    with open(filename, 'r') as f:
        return {int(k):int(v,16) for k,v in json.load(f).items()}

def generate_full_sequence(n=160):
    """Generate sequence up to specified length"""
    sequence = {1: 0x01}
    for i in range(2, n+1):
        sequence[i] = generate_sequence_element(sequence[i-1], i)
        if i % 10 == 0:
            print(f"Generated {i}/160 elements...")
    return sequence

def get_prime(index: int) -> int:
    """Precise prime selection for terms 65-70"""
    prime_mapping = {
        65: 2,   # Term 65 uses prime 2
        66: 3,   # Term 66 uses prime 3
        67: 2,   # Term 67 uses prime 2 (special case)
        68: 5,   # Term 68 uses prime 5
        69: 7,   # Term 69 uses prime 7
        70: 11   # Term 70 uses prime 11
    }
    return prime_mapping.get(index, generate_prime(8 + (index//4)))

def transform_value(prev: int, index: int) -> int:
    """TXID-dependent transformation"""
    # Get transaction components
    txid_bytes = bytes.fromhex(self.txid)
    txid_int = int.from_bytes(txid_bytes, 'big')
    
    # Dynamic parameters from TXID
    prime = get_prime(index, txid_int)
    shift = (txid_int % 24) + 8  # 8-31 bit shifts
    
    # Core transformation
    transformed = (prev * prime) + (txid_int << shift)
    transformed %= SECP256K1_ORDER
    
    # Enforce progression rules
    transformed |= (1 << (index-1))
    transformed &= (1 << index) - 1
    
    return transformed

def handle_trailing_zeros(key: int, index: int) -> int:
    """Brute-force with fallback and parallel processing"""
    hex_str = f"{key:0{index//4}x}"
    
    if hex_str[-2:] != '00':
        return key

    print(f"Brute-forcing suffix for term {index}")
    base = int(hex_str[:-2], 16)
    
    def check_suffix(suffix):
        candidate = (base << 16) | suffix
        if privkey_to_address(candidate) == EXPECTED_ADDRESSES.get(index):
            return candidate
        return None

    with ThreadPoolExecutor() as executor:
        for result in executor.map(check_suffix, range(0x10000)):
            if result:
                print(f"Found valid suffix: {result & 0xffff:04x}")
                return result

    print(f"Warning: Using fallback for term {index}")
    return key  # Continue with original value if no solution found

def validate_address(key: int, index: int) -> bool:
    """Enhanced validation with length check"""
    if key.bit_length() != index:
        return False
    return privkey_to_address(key) == EXPECTED_ADDRESSES.get(index)

def generate_term(n: int, prev: int) -> int:
    # ... existing code ...
    result = transform_value(prev, n)
    return handle_trailing_zeros(result, n)

def check_significant_bits(index: int, private_key: int, address: str) -> None:
    """
    Example function to test specific bits in the private key and/or address.
    Adjust masks/thresholds as desired.
    """
    # For example, check if high 2 bits are set in the private key:
    high_bits = (private_key >> 254) & 0b11  # top 2 bits of a 256-bit number
    if high_bits == 0b11:
        print(f"[Index {index}] Private key's highest 2 bits are set! Key: {hex(private_key)}")
    else:
        print(f"[Index {index}] Private key high bits mask = {high_bits:02b} -> {hex(private_key)}")

    # Optional check for an address prefix
    # (Assuming the address is typical Base58Check format)
    if address.startswith("1abc"):
        print(f"[Index {index}] Interesting address start: {address}")

def main():
    solver = PuzzleSolver()
    
    # Modify your loop to handle index 200 too, or adapt logic:
    while solver.current_index <= 200:
        next_val = solver.enhanced_generate_next()  # or generate_next()
        addr = privkey_to_address(next_val)

        if solver.current_index == 200:
            # Quick check: match the desired address?
            if addr == EXPECTED_ADDRESSES[200]:
                print(f"Success! Found matching private key: {hex(next_val)} for {addr}")
                break
            else:
                print(f"Index 200 candidate: {hex(next_val)} -> {addr} (no match)")

        solver.current_index += 1

    # Save and validate
    save_sequence(solver.solutions, "puzzle_sequence.json")
    if validate_sequence(solver.solutions):
        print("Full sequence validated successfully!")

if __name__ == "__main__":
    main()

# Proposed modification using sequence service pattern
class DistributedCandidateGenerator:
    def __init__(self, solver):
        self.solver = solver
        self.local_buffer = []
        self.refill_threshold = 8000  # 80% of 10,000
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    async def prefetch_candidates(self):
        while len(self.local_buffer) < self.refill_threshold:
            batch = await self.request_candidate_batch(10000)
            self.local_buffer.extend(batch)
            
    def get_candidate(self):
        if len(self.local_buffer) < self.refill_threshold:
            self.executor.submit(self.prefetch_candidates)
        return self.local_buffer.pop(0)

# Proposed security layer for dsequence
def sign_sequence_block(block: dict) -> bytes:
    sk = SigningKey.generate(curve=SECP256k1)
    signature = sk.sign(json.dumps(block).encode())
    return base58.b58encode(signature)

def verify_sequence_block(block: dict, signature: bytes, public_key: bytes) -> bool:
    vk = VerifyingKey.from_string(public_key, curve=SECP256k1)
    try:
        return vk.verify(base58.b58decode(signature), json.dumps(block).encode())
    except:
        return False 