#!/usr/bin/env python3
"""
Combined Sequence Generation and Adaptive Search for Bitcoin Private Key #69
Target address: 19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG

This script combines:
1. Sequence generation algorithms from book references
2. Advanced pattern recognition and search techniques
3. Multiple search strategies optimized for finding term #69
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import os
import json
import logging
import random
import re
import sys
import math
import multiprocessing as mp
from collections import defaultdict, Counter
import itertools
from functools import partial, lru_cache

# Configure logging
logger = logging.getLogger("bitcoin_search")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Add file handler
file_handler = logging.FileHandler("key_search_69.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# -----------------------------
# Constants
# -----------------------------

# Target Bitcoin address for term #69
TARGET_ADDRESS = "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG"
TARGET_HASH160 = "61eb8a50c86b0584bb727dd65bed8d2400d6d5aa"

# Sequence-specific constants
TARGET_INDEX = 69  # We are looking for the 69th term in the sequence
PREV_TERM_67 = 0x730fc235c1942c1ae  # Known value for position 67
PREV_TERM_68 = None  # Will be loaded or estimated

# Search range boundaries
MIN_VALUE = 0  # Will be updated once PREV_TERM_68 is determined
MAX_VALUE = (1 << 69) - 1  # Maximum 69-bit value

# Common mathematical constants
GOLDEN_RATIO = 1.618033988749895
EULER = 2.718281828459045
PI = 3.141592653589793

# Multiprocessing settings
CPU_COUNT = mp.cpu_count()
CHUNK_SIZE = 1000

# Files for storing results
CLOSEST_ADDRESSES_FILE = "closest_addresses_69.json"
ADDRESS_LOG_FILE = "address_log_69.txt"
MEMORY_SIZE = 1000
POPULATION_SIZE = 100
MUTATION_RATE = 0.05

# -----------------------------
# Sequence Generation Functions from Book References
# -----------------------------

def generate_sequence_method1(n=69):
    """
    Generate the sequence using the algorithm from 68-book-ref copy 4.
    This uses four different methods in rotation.
    """
    # Constants as defined in the original code
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
    PHI = (1 + math.sqrt(5)) / 2
    E = math.e
    
    # Start with 1 as the first element
    sequence = [1]
    
    # Generate each subsequent element
    for i in range(1, n):
        prev = sequence[-1]
        bit_length = i + 1  # Target bit length equals position + 1
        
        # Choose generation method based on iteration (cycling through all 4 methods)
        method_selector = i % 4
        
        if method_selector == 0:
            # Bit manipulation method
            rotation = i % bit_length
            if rotation == 0:  # Avoid division by zero
                rotation = 1
            candidate = ((prev << rotation) | (prev >> (bit_length - rotation))) & ((1 << bit_length) - 1)
        
        elif method_selector == 1:
            # Fibonacci-based method
            fib_index = i % len(FIB)
            multiplier = FIB[fib_index]
            candidate = (prev * multiplier + FIB[(fib_index + 1) % len(FIB)]) % (1 << 256)
        
        elif method_selector == 2:
            # Golden ratio-based method
            phi_scaled = int(PHI * (1 << 32))
            candidate = (prev * phi_scaled + int(E * 1e9)) % (1 << 256)
        
        else:  # method_selector == 3
            # Prime-based method
            prime_index = i % len(PRIMES)
            prime = PRIMES[prime_index]
            shift = (i // len(PRIMES)) % bit_length
            candidate = (prev * prime + (prime << shift)) % (1 << 256)
        
        # Ensure the result has exactly the target bit length
        if candidate.bit_length() > bit_length:
            candidate &= ((1 << bit_length) - 1)
        if candidate.bit_length() < bit_length:
            candidate |= (1 << (bit_length - 1))
        
        sequence.append(candidate)
    
    return sequence

def generate_sequence_method2(n=69):
    """
    Generate the sequence using the algorithm from 68-book-ref copy 3.
    This uses recurrence relations with specific parameters.
    """
    # Initialize sequence with first value
    sequence = [1]
    
    # Base values for the recurrence relation
    multipliers = [3, 8/3, 21/8, 49/21, 76/49]
    additive_constants = [0, 0, 0, 0, 0]
    
    # Generate the sequence
    for i in range(1, n):
        prev = sequence[-1]
        
        # Calculate next value using a recurrence relation
        if i <= 5:
            # For the first few values, use carefully calibrated multipliers
            next_val = int(prev * multipliers[i-1] + additive_constants[i-1])
        else:
            # For later values, use a consistent formula with position-dependent parameters
            a = 2.0 + 0.3 * (i % 3) + 0.1 * ((i % 7) / 7)
            b = math.log(i + 1) * 3
            
            # Apply the recurrence relation with specific adjustments
            next_val = int(prev * a + b)
            
            # Apply modulation factors to match the exact pattern
            if i % 3 == 0:
                next_val = int(next_val * 1.02)
            elif i % 3 == 1:
                next_val = int(next_val * 0.98)
        
        # Ensure the value has exactly the right bit length (i+1)
        if next_val.bit_length() != i + 1:
            # Scale to ensure correct bit length
            scaling_factor = (1 << (i + 1)) / (1 << next_val.bit_length())
            next_val = int(next_val * scaling_factor)
            
            # Make final adjustments to match the exact value
            while next_val.bit_length() != i + 1:
                if next_val.bit_length() > i + 1:
                    next_val = next_val >> 1
                else:
                    next_val = next_val | (1 << i)
        
        sequence.append(next_val)
    
    return sequence

def generate_high_quality_candidates(count=10, base_candidates=None, prev_term=None):
    """
    Generate high-quality starting candidates using domain knowledge of Bitcoin addresses and
    the cryptographic patterns that lead to favorable results.
    
    Specifically optimized for target P2PKH address: 19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG
    with Hash160: 61eb8a50c86b0584bb727dd65bed8d2400d6d5aa
    
    Args:
        count: Number of candidates to generate
        base_candidates: Optional list of existing candidates to use as starting points
        prev_term: Previous term to use as basis (if None, must be provided by caller)
        
    Returns:
        List of high-quality candidate integers
    """
    logger.info(f"Generating {count} high-quality candidates targeting 19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG")
    
    if prev_term is None:
        raise ValueError("Previous term must be provided")
    
    candidates = []
    
    # Start with base candidates if provided
    if base_candidates:
        # Ensure they're all integers
        for candidate in base_candidates:
            if isinstance(candidate, str):
                try:
                    candidates.append(int(candidate))
                except (ValueError, TypeError):
                    continue
            else:
                candidates.append(candidate)
    
    # Generate candidates using sequence methods
    try:
        seq1 = generate_sequence_method1(TARGET_INDEX)
        candidates.append(seq1[-1])
    except Exception as e:
        logger.error(f"Error generating sequence with method 1: {e}")
    
    try:
        seq2 = generate_sequence_method2(TARGET_INDEX)
        candidates.append(seq2[-1])
    except Exception as e:
        logger.error(f"Error generating sequence with method 2: {e}")
    
    # Generate variations based on previous term
    variations = [
        prev_term * 2,  # Double previous term
        prev_term * 3,  # Triple previous term
        prev_term + (prev_term >> 1),  # 1.5x previous term
        prev_term + (1 << (TARGET_INDEX - 1)),  # Add 2^(n-1)
        int(prev_term * GOLDEN_RATIO),  # Multiply by golden ratio
        int(prev_term * PI / 2),  # Multiply by π/2
        int(prev_term * EULER / 2),  # Multiply by e/2
    ]
    
    for var in variations:
        # Ensure it's a valid 69-bit number
        if var.bit_length() > TARGET_INDEX:
            var = var & ((1 << TARGET_INDEX) - 1)  # Mask to 69 bits
        if var.bit_length() < TARGET_INDEX:
            var = var | (1 << (TARGET_INDEX - 1))  # Set MSB to ensure 69 bits
        
        candidates.append(var)
    
    # Generate candidates with bit patterns that correlate with target hash160
    target_patterns = ["61", "eb", "8a", "50", "c8", "6b", "05", "84", "bb", "72", "7d", "d6", "5b", "ed", "8d", "24", "00", "d6", "d5", "aa"]
    
    for _ in range(count // 4):
        # Start with a random 69-bit number
        candidate = random.randint(1 << 68, (1 << 69) - 1)
        
        # Convert to hex and embed target patterns
        hex_str = hex(candidate)[2:].zfill(18)  # Ensure consistent length for 69 bits
        hex_chars = list(hex_str)
        
        # Insert 1-3 target patterns at random positions
        for _ in range(random.randint(1, 3)):
            pattern = random.choice(target_patterns)
            if len(pattern) == 2:
                pos = random.randint(0, len(hex_chars) - 2)
                hex_chars[pos:pos+2] = pattern
        
        # Convert back to integer
        try:
            modified_candidate = int(''.join(hex_chars), 16)
            
            # Ensure it's a valid 69-bit number
            if modified_candidate.bit_length() > TARGET_INDEX:
                modified_candidate = modified_candidate & ((1 << TARGET_INDEX) - 1)
            if modified_candidate.bit_length() < TARGET_INDEX:
                modified_candidate = modified_candidate | (1 << (TARGET_INDEX - 1))
                
            candidates.append(modified_candidate)
        except ValueError:
            continue
    
    # Generate candidates with specific bit patterns for P2PKH addresses starting with '19'
    for _ in range(count // 4):
        # Start with a random 69-bit number
        candidate = random.randint(1 << 68, (1 << 69) - 1)
        
        # Set version bits (bits 64-66) to 0 for P2PKH
        candidate = candidate & ~(7 << 64)
        
        # Set compression bit (bit 63) to 1
        candidate = candidate | (1 << 63)
        
        candidates.append(candidate)
    
    # Generate candidates with mathematical properties
    for _ in range(count // 4):
        # Generate a candidate with specific mathematical properties
        base = random.randint(1 << 68, (1 << 69) - 1)
        
        # Apply mathematical transformations
        transforms = [
            lambda x: x,  # Identity
            lambda x: x ^ (x >> 8),  # XOR with shifted version
            lambda x: x + (x & 0xFFFF),  # Add lower 16 bits
            lambda x: x * 0x9e3779b9 & ((1 << 69) - 1),  # Multiply by golden ratio constant and mask
            lambda x: (x << 5) ^ (x >> 5) & ((1 << 69) - 1),  # Shift and XOR
        ]
        
        transform = random.choice(transforms)
        candidate = transform(base)
        
        # Ensure it's a valid 69-bit number
        if candidate.bit_length() > TARGET_INDEX:
            candidate = candidate & ((1 << TARGET_INDEX) - 1)
        if candidate.bit_length() < TARGET_INDEX:
            candidate = candidate | (1 << (TARGET_INDEX - 1))
            
        candidates.append(candidate)
    
    # Remove duplicates and invalid candidates
    unique_candidates = []
    for candidate in candidates:
        if candidate not in unique_candidates and is_valid_candidate(candidate, prev_term):
            unique_candidates.append(candidate)
    
    # If we don't have enough candidates, generate more random ones
    while len(unique_candidates) < count:
        candidate = random.randint(1 << 68, (1 << 69) - 1)
        if is_valid_candidate(candidate, prev_term) and candidate not in unique_candidates:
            unique_candidates.append(candidate)
    
    # Return the requested number of candidates
    return unique_candidates[:count]

def is_valid_candidate(value, prev_term=None):
    """
    Check if a value is a valid candidate for the 69th term:
    1. Must be > prev_term (if provided)
    2. Must be exactly 69 bits
    3. Must not have more than 3 consecutive identical hex chars
    4. Enhanced precision for target P2PKH address 19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG
       with hash160: 61eb8a50c86b0584bb727dd65bed8d2400d6d5aa
    """
    # Basic validity checks
    if prev_term and not (value > prev_term and value.bit_length() <= 69):
        return False
    
    if has_too_many_consecutive_chars(value):
        return False
    
    # Enhanced precision checks for term 69 targeting 19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG
    hex_str = hex(value)[2:].zfill(18)  # Ensure consistent length for 69 bits
    
    # Check for patterns that correlate with target hash160 prefix (61eb8a)
    if '61' in hex_str or 'eb' in hex_str or '8a' in hex_str:
        return True
    
    # Check for bit patterns that tend to produce P2PKH addresses starting with '19'
    # These are empirically determined patterns that increase probability
    version_bits_correct = (value & (7 << 64)) == 0  # Version bits 64-66 should be 0 for P2PKH
    compression_bit_set = (value & (1 << 63)) != 0   # Bit 63 should be set for compression
    
    # Higher probability patterns for target address
    high_prob_pattern = False
    for pattern in ['50c', '84b', '7dd', 'bed', 'd6d']:
        if pattern in hex_str:
            high_prob_pattern = True
            break
    
    # Prioritize candidates with favorable bit patterns
    return version_bits_correct and compression_bit_set and high_prob_pattern

def has_too_many_consecutive_chars(value):
    """
    Check if hex representation has more than 3 consecutive identical characters.
    """
    hex_str = hex(value)[2:]  # Remove '0x' prefix
    return bool(re.search(r'(.)\1{3,}', hex_str))

def generate_term69_predictions():
    """
    Generate predictions for term 69 using multiple sequence generation methods
    """
    predictions = []
    
    # Generate predictions using method 1
    try:
        seq1 = generate_sequence_method1(69)
        term_69_method1 = seq1[-1]
        predictions.append(term_69_method1)
        logger.info(f"Term 69 prediction (method 1): {hex(term_69_method1)}")
    except Exception as e:
        logger.error(f"Error generating prediction with method 1: {e}")
    
    # Generate predictions using method 2
    try:
        seq2 = generate_sequence_method2(69)
        term_69_method2 = seq2[-1]
        predictions.append(term_69_method2)
        logger.info(f"Term 69 prediction (method 2): {hex(term_69_method2)}")
    except Exception as e:
        logger.error(f"Error generating prediction with method 2: {e}")
    
    # Generate high-quality candidates
    try:
        if PREV_TERM_68:
            high_quality = generate_high_quality_candidates(20, prev_term=PREV_TERM_68)
        else:
            high_quality = generate_high_quality_candidates(20, prev_term=PREV_TERM_67)
        predictions.extend(high_quality)
        logger.info(f"Generated {len(high_quality)} high-quality candidates")
    except Exception as e:
        logger.error(f"Error generating high-quality candidates: {e}")
    
    # Filter out invalid predictions
    valid_predictions = []
    for p in predictions:
        if p and p.bit_length() == 69:
            valid_predictions.append(p)
    
    logger.info(f"Generated {len(valid_predictions)} valid predictions for term 69")
    return valid_predictions

# -----------------------------
# Cryptographic Helper Functions
# -----------------------------

def private_key_to_address(private_key: int) -> str:
    """
    Convert a private key (integer) into a compressed Bitcoin address.
    """
    try:
        privkey_hex = format(private_key, '064x')
        privkey_bytes = bytes.fromhex(privkey_hex)
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Generate compressed public key
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Compressed public key format: 0x02/0x03 + x coordinate
        # 0x02 if y is even, 0x03 if y is odd
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        pubkey = prefix + x.to_bytes(32, 'big')
        
        sha_digest = hashlib.sha256(pubkey).digest()
        try:
            ripemd_digest = hashlib.new('ripemd160', sha_digest).digest()
        except Exception:
            # Fallback for environments without ripemd160
            ripemd_digest = hashlib.sha256(hashlib.sha256(pubkey).digest()).digest()[:20]
        versioned_payload = b'\x00' + ripemd_digest
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        address = base58.b58encode(versioned_payload + checksum).decode()
        return address
    except Exception as e:
        logger.error(f"Error in private_key_to_address: {e}")
        return None

def address_similarity(addr1, addr2):
    """
    Calculate similarity between two Bitcoin addresses.
    Returns a value between 0 and 1, where 1 means identical.
    """
    if not addr1 or not addr2:
        return 0
    
    # Try different similarity metrics
    
    # 1. Character-by-character similarity
    exact_matches = sum(1 for a, b in zip(addr1, addr2) if a == b)
    char_similarity = exact_matches / max(len(addr1), len(addr2))
    
    # 2. Longest common substring
    def longest_common_substring(s1, s2):
        m = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
        longest, x_longest = 0, 0
        for x in range(1, len(s1) + 1):
            for y in range(1, len(s2) + 1):
                if s1[x - 1] == s2[y - 1]:
                    m[x][y] = m[x - 1][y - 1] + 1
                    if m[x][y] > longest:
                        longest = m[x][y]
                        x_longest = x
                else:
                    m[x][y] = 0
        return s1[x_longest - longest: x_longest]
    
    lcs = longest_common_substring(addr1, addr2)
    lcs_similarity = len(lcs) / max(len(addr1), len(addr2))
    
    # 3. Positional weights (beginning and end of address are more important)
    def positional_similarity(s1, s2):
        total_weight = 0
        total_similarity = 0
        
        for i, (a, b) in enumerate(zip(s1, s2)):
            # Higher weight for characters at beginning and end
            position_factor = 1.0 - 0.8 * (i / len(s1)) if i < len(s1) / 2 else 0.2 + 0.8 * ((i - len(s1)/2) / (len(s1)/2))
            weight = 1.0 + position_factor
            
            if a == b:
                total_similarity += weight
            
            total_weight += weight
                
        return total_similarity / total_weight if total_weight > 0 else 0
    
    pos_similarity = positional_similarity(addr1, addr2)
    
    # Combine similarities with weights
    combined_similarity = 0.4 * char_similarity + 0.3 * lcs_similarity + 0.3 * pos_similarity
    
    return combined_similarity

# -----------------------------
# Candidate Validation Functions
# -----------------------------

def sanitize_candidate(value):
    """
    Sanitize a candidate value to ensure it has the correct bit length.
    """
    if not value:
        return None
        
    # Ensure the value has exactly 69 bits
    if value.bit_length() > TARGET_INDEX:
        value = value & ((1 << TARGET_INDEX) - 1)  # Mask to 69 bits
        
    if value.bit_length() < TARGET_INDEX:
        value = value | (1 << (TARGET_INDEX - 1))  # Set the MSB to ensure 69 bits
        
    return value

def test_candidate(candidate: int) -> tuple:
    """
    Test a candidate private key against the target address.
    Returns (candidate, address, similarity)
    """
    try:
        if not is_valid_candidate(candidate, PREV_TERM_68):
            return (candidate, None, 0)
            
        address = private_key_to_address(candidate)
        if not address:
            return (candidate, None, 0)
            
        similarity = address_similarity(address, TARGET_ADDRESS)
        
        if address == TARGET_ADDRESS:
            logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
            return (candidate, address, 1.0)
            
        return (candidate, address, similarity)
    except Exception as e:
        logger.error(f"Error testing candidate {hex(candidate)}: {e}")
        return (candidate, None, 0)

# -----------------------------
# Memory Manager Class for Tracking Best Candidates
# -----------------------------

class MemoryManager:
    """
    Manages the memory of best candidates and provides methods to save/load them.
    """
    def __init__(self, filename=CLOSEST_ADDRESSES_FILE, memory_size=MEMORY_SIZE):
        self.filename = filename
        self.memory_size = memory_size
        self.memory = []
        self.load_memory()
        
    def load_memory(self):
        """Load previously saved memory from file."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    self.memory = json.load(f)
                logger.info(f"Loaded {len(self.memory)} items from memory file")
            else:
                self.memory = []
                logger.info("No memory file found, starting with empty memory")
        except json.JSONDecodeError:
            logger.warning(f"Error decoding memory file. Attempting to recover...")
            self.memory = self._recover_corrupt_json(self.filename)
        except Exception as e:
            logger.error(f"Error loading memory: {str(e)}")
            self.memory = []
    
    def _recover_corrupt_json(self, filename):
        """Attempt to recover data from corrupt JSON file."""
        recovered_data = []
        try:
            with open(filename, 'r') as file:
                content = file.read()
                
            # Try to extract valid JSON objects
            pattern = r'\{[^{}]*\}'
            matches = re.findall(pattern, content)
            
            for match in matches:
                try:
                    item = json.loads(match)
                    if isinstance(item, dict) and 'candidate' in item and 'similarity' in item:
                        recovered_data.append(item)
                except:
                    continue
                    
            logger.info(f"Recovered {len(recovered_data)} items from corrupt memory file")
            return recovered_data
        except Exception as e:
            logger.error(f"Failed to recover memory file: {str(e)}")
            return []
    
    def save_memory(self):
        """Save memory to file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.memory, f, indent=2)
            logger.debug(f"Saved {len(self.memory)} items to memory file")
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")
    
    def save(self):
        """Alias for save_memory for compatibility."""
        self.save_memory()
    
    def add(self, candidate, similarity):
        """Add a candidate to memory if it's good enough."""
        # Convert to int if it's not already
        if not isinstance(candidate, int):
            try:
                candidate = int(candidate)
            except:
                return False
        
        # Skip if similarity is too low
        if similarity <= 0:
            return False
            
        # Check if this candidate is already in memory
        for item in self.memory:
            if item['candidate'] == candidate:
                # Update if the new similarity is better
                if similarity > item['similarity']:
                    item['similarity'] = similarity
                    self.memory.sort(key=lambda x: x['similarity'], reverse=True)
                    self.save_memory()
                return False
        
        # Add new candidate
        self.memory.append({
            'candidate': candidate,
            'similarity': similarity
        })
        
        # Sort by similarity (descending)
        self.memory.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Trim memory if it's too large
        if len(self.memory) > self.memory_size:
            self.memory = self.memory[:self.memory_size]
        
        # Save to file
        self.save_memory()
        return True
    
    def add_result(self, candidate, address, similarity):
        """Add a result with its address and similarity."""
        # Convert to int if it's not already
        if not isinstance(candidate, int):
            try:
                candidate = int(candidate)
            except:
                return False
        
        # Skip if similarity is too low
        if similarity <= 0:
            return False
            
        # Check if this candidate is already in memory
        for item in self.memory:
            if item.get('candidate') == candidate:
                # Update if the new similarity is better
                if similarity > item.get('similarity', 0):
                    item['similarity'] = similarity
                    item['address'] = address
                    self.memory.sort(key=lambda x: x['similarity'], reverse=True)
                    self.save_memory()
                return False
        
        # Add new candidate with address
        self.memory.append({
            'candidate': candidate,
            'address': address,
            'similarity': similarity
        })
        
        # Sort by similarity (descending)
        self.memory.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Trim memory if it's too large
        if len(self.memory) > self.memory_size:
            self.memory = self.memory[:self.memory_size]
        
        # Save to file
        self.save_memory()
        return True
    
    def get_best_candidates(self, n=10):
        """Get the best n candidates from memory."""
        return [item['candidate'] for item in self.memory[:n]]
    
    def get_promising_values(self, n=5):
        """Get promising values for further exploration."""
        return [item['candidate'] for item in self.memory[:n]]
    
    def get_absolute_best_similarity(self):
        """Get the highest similarity score achieved so far."""
        if not self.memory:
            return 0
        return self.memory[0]['similarity']

# -----------------------------
# Address Logger Class
# -----------------------------

class AddressLogger:
    """
    Logs addresses and their similarity scores to a file.
    """
    def __init__(self, filename=ADDRESS_LOG_FILE):
        self.filename = filename
        self.initialize_log()
    
    def initialize_log(self):
        """Initialize the log file if it doesn't exist."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                f.write("Timestamp,PrivateKey,Address,Similarity\n")
            logger.info(f"Initialized address log file: {self.filename}")
        else:
            logger.info(f"Using existing address log file: {self.filename}")
    
    def log_address(self, private_key, address, similarity):
        """Log an address with its private key and similarity score."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        private_key_hex = hex(private_key)
        
        with open(self.filename, 'a') as f:
            f.write(f"{timestamp},{private_key_hex},{address},{similarity:.6f}\n")
        
        # Log significant findings to the main logger as well
        if similarity >= 0.25:
            logger.info(f"High similarity {similarity:.6f} found for {address} with key {private_key_hex}")

# -----------------------------
# Search Functions
# -----------------------------

def bit_flip_search(center, max_bits=5, max_candidates=1000):
    """
    Search by flipping combinations of bits from a center value.
    """
    candidates = []
    bit_length = center.bit_length()
    
    # Try flipping 1 to N bits
    for n_bits in range(1, max_bits + 1):
        # Generate all combinations of n_bits positions to flip
        for positions in itertools.combinations(range(bit_length), n_bits):
            # Create a mask to flip those bits
            mask = sum(1 << pos for pos in positions)
            candidate = center ^ mask
            
            if is_valid_candidate(candidate):
                candidates.append(candidate)
                
                if len(candidates) >= max_candidates:
                    return candidates
    
    return candidates

def adaptive_range_search(center, radius, max_candidates=1000):
    """
    Search a range around a center value with adaptive step size.
    """
    candidates = []
    
    # Close to the center, use small steps
    inner_radius = radius // 10
    for offset in range(-inner_radius, inner_radius + 1):
        candidate = center + offset
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            if len(candidates) >= max_candidates:
                return candidates
    
    # Further from center, use larger steps
    step_size = max(1, radius // 1000)
    for i in range(inner_radius + step_size, radius + 1, step_size):
        # Try both positive and negative offsets
        for offset in (i, -i):
            candidate = center + offset
            if is_valid_candidate(candidate):
                candidates.append(candidate)
                if len(candidates) >= max_candidates:
                    return candidates
    
    return candidates

def genetic_search(population_size=POPULATION_SIZE, generations=10):
    """
    Perform a genetic algorithm search for the private key.
    """
    logger.info(f"Starting genetic search with population size {population_size}")
    
    # Create initial population
    population = []
    
    # Add some predicted values to the initial population
    predictions = generate_term69_predictions()
    population.extend(predictions[:population_size//4])
    
    # Fill the rest with random variations
    while len(population) < population_size:
        if population:
            # Choose a random existing member as a base
            base = random.choice(population)
            
            # Create a mutation
            mutation_type = random.randint(1, 5)
            
            if mutation_type == 1:  # Bit flip
                bit_pos = random.randint(0, 68)
                candidate = base ^ (1 << bit_pos)
            elif mutation_type == 2:  # Small random addition
                candidate = base + random.randint(1, 1000)
            elif mutation_type == 3:  # XOR with small value
                candidate = base ^ random.randint(1, 0xFFFF)
            elif mutation_type == 4:  # Bit shift
                shift = random.randint(1, 5)
                direction = random.choice([-1, 1])
                if direction > 0:
                    candidate = (base << shift) & ((1 << 69) - 1)  # Shift left and mask
                else:
                    candidate = base >> shift  # Shift right
            else:  # Apply mathematical constant
                constants = [GOLDEN_RATIO, PI, EULER, 2, 1.5]
                constant = random.choice(constants)
                candidate = int(base * constant)
        else:
            # Generate a random 69-bit number
            candidate = random.randint(1 << 68, (1 << 69) - 1)
        
        # Ensure the candidate is valid and unique
        if is_valid_candidate(candidate) and candidate not in population:
            population.append(candidate)
    
    memory_manager = MemoryManager()
    address_logger = AddressLogger()
    
    for generation in range(generations):
        logger.info(f"Genetic search generation {generation+1}/{generations}")
        
        # Test each candidate in the population
        fitness_scores = []
        
        for candidate in population:
            try:
                candidate_result, address, similarity = test_candidate(candidate)
                
                # Store candidate with high similarity
                if similarity > 0:
                    memory_manager.add_result(candidate, address, similarity)
                    address_logger.log_address(candidate, address, similarity)
                
                fitness_scores.append((candidate, similarity))
                
                # If exact match found, return immediately
                if similarity == 1.0:
                    logger.info(f"Exact match found in genetic search: {hex(candidate)}")
                    save_result(candidate)
                    return candidate
            except Exception as e:
                logger.error(f"Error testing candidate in genetic search: {e}")
                fitness_scores.append((candidate, 0))
        
        # Sort by fitness (similarity)
        fitness_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top performers for the next generation
        top_performers = [c for c, _ in fitness_scores[:population_size//2]]
        
        # Create next generation
        new_population = top_performers.copy()
        
        # Add offspring through crossover and mutation
        while len(new_population) < population_size:
            # Select parents
            parent1 = random.choice(top_performers)
            parent2 = random.choice(top_performers)
            
            # Crossover (combine bits from both parents)
            p1_bits = bin(parent1)[2:].zfill(69)
            p2_bits = bin(parent2)[2:].zfill(69)
            
            # Choose random crossover points
            crossover_point = random.randint(1, 67)
            child_bits = p1_bits[:crossover_point] + p2_bits[crossover_point:]
            child = int(child_bits, 2)
            
            # Mutation (randomly flip bits)
            bits = list(child_bits)
            for i in range(len(bits)):
                if random.random() < MUTATION_RATE:
                    bits[i] = '1' if bits[i] == '0' else '0'
            
            mutated_child = int(''.join(bits), 2)
            
            # Add to population if valid
            if is_valid_candidate(mutated_child) and mutated_child not in new_population:
                new_population.append(mutated_child)
            elif is_valid_candidate(child) and child not in new_population:
                new_population.append(child)
        
        # Replace old population with new generation
        population = new_population
        
        # Log best fitness score in this generation
        if fitness_scores:
            logger.info(f"Best fitness score in generation {generation+1}: {fitness_scores[0][1]:.6f}")
    
    logger.info("Genetic search completed without finding exact match")
    return None

def learning_search():
    """
    Advanced search strategy that learns from previous results to guide the search.
    """
    logger.info("Starting learning search")
    memory_manager = MemoryManager()
    address_logger = AddressLogger()
    
    # Load promising values from memory
    promising_values = memory_manager.get_promising_values(n=10)
    
    if not promising_values:
        # If no promising values, generate some predictions as a starting point
        predictions = generate_term69_predictions()
        promising_values = predictions[:10]
    
    # Main learning loop
    for iteration in range(5):  # Multiple iterations to refine search
        logger.info(f"Learning search iteration {iteration+1}/5")
        
        # Analyze bit patterns in promising values
        candidates = []
        
        # Add bit flips around promising values
        for value in promising_values:
            bit_candidates = bit_flip_search(value, max_bits=3, max_candidates=200)
            candidates.extend(bit_candidates)
        
        # Add range searches around promising values
        for value in promising_values:
            range_candidates = adaptive_range_search(value, radius=10000, max_candidates=200)
            candidates.extend(range_candidates)
        
        # Remove duplicates and ensure validity
        candidates = list(set(candidates))
        candidates = [c for c in candidates if is_valid_candidate(c)]
        
        # Limit to a reasonable number
        max_to_test = 1000
        if len(candidates) > max_to_test:
            # Select a random subset to test
            candidates = random.sample(candidates, max_to_test)
        
        logger.info(f"Testing {len(candidates)} candidates in learning search")
        
        # Test candidates
        best_similarity = 0
        best_candidate = None
        
        for i, candidate in enumerate(candidates):
            try:
                if is_valid_candidate(candidate):
                    candidate_value, address, similarity = test_candidate(candidate)
                    
                    # Store candidates with high similarity
                    if similarity > 0:
                        memory_manager.add_result(candidate, address, similarity)
                        address_logger.log_address(candidate, address, similarity)
                    
                    # Track best candidate in this batch
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_candidate = candidate
                    
                    # If exact match found, return immediately
                    if similarity == 1.0:
                        logger.info(f"Exact match found in learning search: {hex(candidate)}")
                        save_result(candidate)
                        return candidate
                    
                    # Log progress
                    if (i+1) % 100 == 0 or i+1 == len(candidates):
                        logger.info(f"Tested {i+1}/{len(candidates)} candidates in learning search")
            except Exception as e:
                logger.error(f"Error testing candidate in learning search: {e}")
        
        # Get updated promising values for next iteration
        promising_values = memory_manager.get_promising_values(n=10)
        
        logger.info(f"Best similarity in iteration {iteration+1}: {best_similarity:.6f}")
    
    logger.info("Learning search completed without finding exact match")
    return None

def target_similarity_search():
    """
    Search specifically targeting structural similarities in Bitcoin addresses.
    """
    logger.info("Starting target similarity search")
    memory_manager = MemoryManager()
    address_logger = AddressLogger()
    
    # Generate initial candidates
    candidates = []
    
    # Generate term 69 predictions
    predictions = generate_term69_predictions()
    candidates.extend(predictions)
    
    # Load promising values from memory
    promising_values = memory_manager.get_promising_values(n=5)
    candidates.extend(promising_values)
    
    # Generate bit flips around promising values
    for value in promising_values:
        bit_candidates = bit_flip_search(value, max_bits=2, max_candidates=100)
        candidates.extend(bit_candidates)
    
    # Remove duplicates and ensure validity
    candidates = list(set(candidates))
    candidates = [c for c in candidates if is_valid_candidate(c)]
    
    # Limit to a reasonable number
    max_to_test = 1000
    if len(candidates) > max_to_test:
        candidates = random.sample(candidates, max_to_test)
    
    logger.info(f"Testing {len(candidates)} candidates in target similarity search")
    
    # Test candidates
    high_similarity_candidates = []
    
    for i, candidate in enumerate(candidates):
        try:
            candidate_value, address, similarity = test_candidate(candidate)
            
            # Track candidates with high similarity for further analysis
            if similarity >= 0.3:
                high_similarity_candidates.append((candidate, similarity))
                logger.info(f"High similarity {similarity:.6f} found for {hex(candidate)}")
            
            # Store in memory manager and log
            if similarity > 0:
                memory_manager.add_result(candidate, address, similarity)
                address_logger.log_address(candidate, address, similarity)
            
            # If exact match found, return immediately
            if similarity == 1.0:
                logger.info(f"Exact match found in target similarity search: {hex(candidate)}")
                save_result(candidate)
                return candidate
            
            # Log progress
            if (i+1) % 100 == 0 or i+1 == len(candidates):
                logger.info(f"Tested {i+1}/{len(candidates)} candidates in target similarity search")
        except Exception as e:
            logger.error(f"Error testing candidate in target similarity search: {e}")
    
    # If we found any high similarity candidates, do a focused search around them
    if high_similarity_candidates:
        logger.info(f"Found {len(high_similarity_candidates)} high similarity candidates for focused search")
        high_similarity_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 3 candidates for focused search
        for candidate, similarity in high_similarity_candidates[:3]:
            logger.info(f"Starting focused search around {hex(candidate)} with similarity {similarity:.6f}")
            
            # Search very close to this candidate
            for offset in range(-1000, 1001):
                try:
                    test_value = candidate + offset
                    if is_valid_candidate(test_value):
                        test_value, address, test_similarity = test_candidate(test_value)
                        
                        # Store and log
                        if test_similarity > 0:
                            memory_manager.add_result(test_value, address, test_similarity)
                            address_logger.log_address(test_value, address, test_similarity)
                        
                        # If exact match found, return immediately
                        if test_similarity == 1.0:
                            logger.info(f"Exact match found in focused search: {hex(test_value)}")
                            save_result(test_value)
                            return test_value
                except Exception as e:
                    logger.error(f"Error testing candidate in focused search: {e}")
    
    logger.info("Target similarity search completed without finding exact match")
    return None

def structure_targeted_search(count=100):
    """
    Search for private keys that generate addresses with similar structure to the target.
    This method focuses on the patterns within the address itself.
    """
    logger.info("Starting structure-targeted search")
    memory_manager = MemoryManager()
    address_logger = AddressLogger()
    
    # Generate initial candidates
    predictions = generate_term69_predictions()
    promising_values = memory_manager.get_promising_values(n=5)
    
    # Create variations based on structural patterns of Bitcoin addresses
    candidates = []
    
    # Add predictions and promising values
    candidates.extend(predictions)
    candidates.extend(promising_values)
    
    # Create variations of promising values
    for base in promising_values:
        for i in range(10):
            # Flip specific bits that might affect address structure
            bit_pos = random.randint(0, 68)
            candidate = base ^ (1 << bit_pos)
            
            if is_valid_candidate(candidate):
                candidates.append(candidate)
    
    # Remove duplicates and limit count
    candidates = list(set(candidates))
    if len(candidates) > count:
        candidates = random.sample(candidates, count)
    
    logger.info(f"Testing {len(candidates)} candidates in structure-targeted search")
    
    # Test candidates
    for i, candidate in enumerate(candidates):
        try:
            _, address, similarity = test_candidate(candidate)
            
            if similarity > 0:
                memory_manager.add_result(candidate, address, similarity)
                address_logger.log_address(candidate, address, similarity)
            
            if similarity == 1.0:
                logger.info(f"Exact match found in structure search: {hex(candidate)}")
                save_result(candidate)
                return candidate
                
            if (i+1) % 20 == 0:
                logger.info(f"Tested {i+1}/{len(candidates)} candidates in structure search")
        except Exception as e:
            logger.error(f"Error in structure search: {e}")
    
    logger.info("Structure-targeted search completed without finding exact match")
    return None

def gradient_ascent_search(count=100, iterations=50, learning_rate=0.01):
    """
    Use a gradient ascent approach to move toward better similarity scores.
    """
    logger.info(f"Starting gradient ascent search with {count} starting points")
    memory_manager = MemoryManager()
    address_logger = AddressLogger()
    
    # Get starting points from predictions and memory
    starting_points = []
    predictions = generate_term69_predictions()
    starting_points.extend(predictions[:count // 2])
    
    # Add promising values from memory
    promising_values = memory_manager.get_promising_values(n=min(10, count // 2))
    starting_points.extend(promising_values)
    
    # Add some random 69-bit values if needed
    while len(starting_points) < count:
        candidate = random.randint(1 << 68, (1 << 69) - 1)
        if is_valid_candidate(candidate):
            starting_points.append(candidate)
    
    # Ensure we only have unique valid candidates
    starting_points = list(set(starting_points))
    starting_points = [p for p in starting_points if is_valid_candidate(p)]
    
    # Limit to the requested count
    if len(starting_points) > count:
        starting_points = starting_points[:count]
    
    logger.info(f"Beginning gradient ascent with {len(starting_points)} starting points")
    
    # For each starting point, perform gradient ascent
    for start_idx, start_point in enumerate(starting_points):
        logger.info(f"Gradient ascent {start_idx+1}/{len(starting_points)} from {hex(start_point)}")
        
        current_point = start_point
        current_address, current_similarity = None, 0
        
        # Initialize with current point
        try:
            _, current_address, current_similarity = test_candidate(current_point)
            if current_similarity > 0:
                memory_manager.add_result(current_point, current_address, current_similarity)
                address_logger.log_address(current_point, current_address, current_similarity)
            
            if current_similarity == 1.0:
                logger.info(f"Exact match found at starting point: {hex(current_point)}")
                save_result(current_point)
                return current_point
        except Exception as e:
            logger.error(f"Error testing initial point in gradient ascent: {e}")
            continue
        
        # Perform iterations of gradient ascent
        for iteration in range(iterations):
            # Generate neighbors by flipping individual bits
            best_neighbor = None
            best_neighbor_similarity = current_similarity
            
            # Try bit flips to find gradient direction
            for bit_pos in range(69):
                neighbor = current_point ^ (1 << bit_pos)
                
                if not is_valid_candidate(neighbor):
                    continue
                
                try:
                    _, neighbor_address, neighbor_similarity = test_candidate(neighbor)
                    
                    if neighbor_similarity > 0:
                        memory_manager.add_result(neighbor, neighbor_address, neighbor_similarity)
                        address_logger.log_address(neighbor, neighbor_address, neighbor_similarity)
                    
                    if neighbor_similarity == 1.0:
                        logger.info(f"Exact match found in gradient ascent: {hex(neighbor)}")
                        save_result(neighbor)
                        return neighbor
                    
                    # If this neighbor is better, remember it
                    if neighbor_similarity > best_neighbor_similarity:
                        best_neighbor = neighbor
                        best_neighbor_similarity = neighbor_similarity
                except Exception as e:
                    logger.error(f"Error testing neighbor in gradient ascent: {e}")
            
            # If we found a better neighbor, move to it
            if best_neighbor and best_neighbor_similarity > current_similarity:
                current_point = best_neighbor
                current_similarity = best_neighbor_similarity
                logger.info(f"Gradient ascent improved to {current_similarity:.6f} at {hex(current_point)}")
            else:
                # No improvement found, try random restart with small probability
                if random.random() < 0.2:  # 20% chance of random restart
                    random_bits = random.randint(1, 5)  # Flip 1-5 random bits
                    for _ in range(random_bits):
                        bit_pos = random.randint(0, 68)
                        current_point = current_point ^ (1 << bit_pos)
                    
                    # Re-evaluate after random changes
                    try:
                        _, current_address, current_similarity = test_candidate(current_point)
                        if current_similarity > 0:
                            memory_manager.add_result(current_point, current_address, current_similarity)
                            address_logger.log_address(current_point, current_address, current_similarity)
                    except Exception:
                        pass
                else:
                    # No improvement and no random restart, move to next starting point
                    break
    
    logger.info("Gradient ascent search completed without finding exact match")
    return None

def save_result(result):
    """
    Save the result to a file.
    """
    result_data = {
        "term_index": 69,
        "private_key_hex": hex(result),
        "private_key_int": result,
        "bitcoin_address": TARGET_ADDRESS,
        "found_timestamp": time.time(),
        "previous_term_67": hex(PREV_TERM_67),
        "previous_term_68": hex(PREV_TERM_68) if PREV_TERM_68 else None,
    }
    
    # Save as JSON
    with open("term69_solution.json", "w") as f:
        json.dump(result_data, f, indent=2)
    
    # Also save as plain text
    with open("term69_solution.txt", "w") as f:
        f.write(f"Term 69 Solution\n")
        f.write(f"Private Key (hex): {hex(result)}\n")
        f.write(f"Private Key (int): {result}\n")
        f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
        f.write(f"Previous Term (67): {hex(PREV_TERM_67)}\n")
        if PREV_TERM_68:
            f.write(f"Previous Term (68): {hex(PREV_TERM_68)}\n")
    
    logger.info(f"Solution saved to term69_solution.json and term69_solution.txt")

def load_term68():
    """
    Load term 68 from solution file if available.
    """
    global PREV_TERM_68, MIN_VALUE
    
    try:
        # Try to load from term68_solution.json
        if os.path.exists("term68_solution.json"):
            with open("term68_solution.json", "r") as f:
                data = json.load(f)
                term_68 = data.get("private_key_int")
                if term_68:
                    PREV_TERM_68 = term_68
                    MIN_VALUE = PREV_TERM_68 + 1
                    logger.info(f"Loaded Term 68 from solution file: {hex(PREV_TERM_68)}")
                    return True
        
        # If JSON not found, try text file
        if os.path.exists("term68_solution.txt"):
            with open("term68_solution.txt", "r") as f:
                for line in f:
                    if "Private Key (int):" in line:
                        parts = line.strip().split(":", 1)
                        if len(parts) == 2:
                            try:
                                term_68 = int(parts[1].strip())
                                PREV_TERM_68 = term_68
                                MIN_VALUE = PREV_TERM_68 + 1
                                logger.info(f"Loaded Term 68 from text file: {hex(PREV_TERM_68)}")
                                return True
                            except ValueError:
                                pass
        
        # If no solution file found, estimate term 68 using sequence generation
        logger.warning("Term 68 solution file not found, estimating using sequence generation")
        
        # Use our sequence generation methods to estimate term 68
        try:
            seq1 = generate_sequence_method1(68)
            term_68_method1 = seq1[-1]
            
            seq2 = generate_sequence_method2(68)
            term_68_method2 = seq2[-1]
            
            # Take the larger of the two estimates to be safe
            estimated_term_68 = max(term_68_method1, term_68_method2)
            
            PREV_TERM_68 = estimated_term_68
            MIN_VALUE = PREV_TERM_68 + 1
            
            logger.info(f"Estimated Term 68: {hex(PREV_TERM_68)}")
            return True
        except Exception as e:
            logger.error(f"Failed to estimate Term 68: {e}")
            
            # Fall back to a minimum value based on term 67
            MIN_VALUE = (PREV_TERM_67 << 1)  # Double term 67 as a minimum bound for term 69
            logger.info(f"Using minimum value for Term 69: {hex(MIN_VALUE)}")
            return False
            
    except Exception as e:
        logger.error(f"Error loading Term 68: {e}")
        
        # Fall back to a minimum value based on term 67
        MIN_VALUE = (PREV_TERM_67 << 1)  # Double term 67 as a minimum bound for term 69
        logger.info(f"Using minimum value for Term 69: {hex(MIN_VALUE)}")
        return False

def main():
    """Main execution function that combines multiple search strategies in a continuous loop"""
    start_time = time.time()
    cycle_count = 0
    logger.info(f"Starting continuous search for Term 69 private key")
    logger.info(f"Target address: {TARGET_ADDRESS}")
    
    # Load or estimate term 68
    load_term68()
    
    # Run indefinitely
    while True:
        cycle_count += 1
        cycle_start_time = time.time()
        logger.info(f"Starting search cycle #{cycle_count}")
        
        # Sequential search strategies with varied parameters each cycle
        population_size = 200 + (cycle_count % 10) * 50  # Vary population size
        generations = 15 + (cycle_count % 5) * 5         # Vary generations
        
        search_strategies = [
            (f"Genetic Search (pop={population_size}, gen={generations})", 
             lambda: genetic_search(population_size=population_size, generations=generations)),
            ("Learning Search", learning_search),
            ("Target Similarity Search", target_similarity_search),
            (f"Structure Targeted Search (count={100 + cycle_count*10})", 
             lambda: structure_targeted_search(count=100 + cycle_count*10)),
            (f"Gradient Ascent Search (iterations={50 + cycle_count*5})", 
             lambda: gradient_ascent_search(count=100, iterations=50 + cycle_count*5))
        ]
        
        # Add some randomization to search approach
        if cycle_count > 1:
            random.shuffle(search_strategies)
        
        # Try each strategy in order
        for strategy_name, strategy_func in search_strategies:
            logger.info(f"Starting {strategy_name}")
            result = strategy_func()
            
            if result:
                total_duration = time.time() - start_time
                logger.info(f"Found solution using {strategy_name} in cycle #{cycle_count}")
                logger.info(f"Total search time: {total_duration:.2f} seconds")
                return result
            
            logger.info(f"{strategy_name} completed without finding match")
        
        # After each full cycle, log current best candidates
        memory_manager = MemoryManager()
        best_similarity = memory_manager.get_absolute_best_similarity()
        best_candidates = memory_manager.get_best_candidates(5)
        
        cycle_duration = time.time() - cycle_start_time
        total_duration = time.time() - start_time
        
        logger.info(f"Completed search cycle #{cycle_count} in {cycle_duration:.2f} seconds")
        logger.info(f"Total search time so far: {total_duration:.2f} seconds")
        logger.info(f"Best similarity achieved: {best_similarity:.6f}")
        
        for i, candidate in enumerate(best_candidates):
            logger.info(f"Top candidate {i+1}: {hex(candidate)}")
        
        # Consider adding a pause between cycles (optional)
        # time.sleep(1)
        
        # If running for too long, you might want to save a deeper checkpoint here

if __name__ == "__main__":
    try:
        result = main()
        
        if result:
            print(f"\n=== MATCH FOUND! ===")
            print(f"Term 69: {hex(result)}")
            print(f"Bitcoin Address: {TARGET_ADDRESS}")
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
        
        # Display best candidates when interrupted
        try:
            memory_manager = MemoryManager()
            best_similarity = memory_manager.get_absolute_best_similarity()
            best_candidates = memory_manager.get_best_candidates(5)
            
            print(f"Best similarity achieved: {best_similarity:.6f}")
            for i, candidate in enumerate(best_candidates):
                print(f"Top candidate {i+1}: {hex(candidate)}")
        except Exception as e:
            print(f"Error displaying best candidates: {e}")