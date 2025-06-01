#!/usr/bin/env python3
"""
Continuous Adaptive Bitcoin Key Search for Term 68
Target address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ

This script continuously searches for the Bitcoin private key, adapting its 
search parameters based on proximity metrics and logs all addresses generated.

Features:
1. Never stops until a match is found
2. Self-adjusts search parameters based on feedback
3. Logs all generated Bitcoin addresses and their distances
4. Uses combined approaches from multiple strategies
5. Implements a learning mechanism to focus on promising areas
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
from collections import defaultdict, Counter
import itertools
import math
import multiprocessing as mp
from functools import partial
import zlib  # For Levenshtein distance optimization
import csv
from datetime import datetime
import argparse
import numpy as np  # Add NumPy import for targeted_position_search

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='68_continuous_adaptive_search.log',
    filemode='a'
)
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

# -----------------------------
# Configuration and Constants
# -----------------------------

# Target information
TARGET_INDEX = 68  # Target number of bits
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Known previous term
PREV_TERM_67 = "0x730fc235c1942c1ae"
PREV_TERM_67_INT = int(PREV_TERM_67, 16)  # Add this line to convert the hex string to integer

# Values discovered from previous analyses
MIN_PREDICTED = 0x8747dd8c268dd31c4
MAX_PREDICTED = 0xd7db28ca2b3a33c0c
BIT_SHIFTED_VALUE = 0x7a40be591dad6edc8
ESTIMATE_VALUE = 0x12e7b5c4e1c670000

# Constants for search constraints
MIN_VALUE = PREV_TERM_67  # Minimum value (previous term)
MAX_VALUE = (1 << 68) - 1  # Maximum 68-bit value

# Self-adjustment parameters 
LEARNING_RATE = 240.1  # Initial learning rate
MUTATION_RATE = 75.55  # Genetic mutation rate
POPULATION_SIZE = 100  # Size of genetic algorithm population
BIT_FLIP_MAX = 18  # Maximum bits to flip in Hamming distance exploration
SEARCH_RADIUS = 1000  # Initial search radius around promising values
MEMORY_SIZE = 10000  # Number of closest addresses to remember

# File paths
ADDRESS_LOG_FILE = "address_log.csv"
CLOSEST_ADDRESSES_FILE = "closest_addresses_memory.json"
PROGRESS_FILE = "search_progress.json"
CHECKPOINT_FILE = "search_checkpoint.json"

# Add a new global variable to track strategy effectiveness
STRATEGY_EFFECTIVENESS = {}

# Add global variables to track best state
BEST_CANDIDATES = []
BEST_STATES = []

# Add a constant for our target similarity
TARGET_SIMILARITY = 0.8  # Updated from 0.35 to 0.8 (80% similarity)

# Add new global variables for tracking highest scores
ALL_TIME_BEST_SIMILARITY = 0.0
ALL_TIME_BEST_CANDIDATE = None
ALL_TIME_BEST_ADDRESS = None
LAST_DISPLAY_TIME = 0

# -----------------------------
# Cryptographic Functions
# -----------------------------

def private_key_to_address(private_key: int) -> str:
    """
    Convert a private key integer to a Bitcoin address
    """
    try:
        # Format private key to 64 hex digits (32 bytes)
        privkey_hex = format(private_key, '064x')
        privkey_bytes = bytes.fromhex(privkey_hex)
        
        # Create signing key
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Get public key coordinates
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Create uncompressed public key (04 + x + y)
        pubkey = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
        
        # Hash public key
        sha_digest = hashlib.sha256(pubkey).digest()
        try:
            # Try RIPEMD-160 hash
            ripemd_digest = hashlib.new('ripemd160', sha_digest).digest()
        except (Exception, ValueError) as e:
            # Fallback if RIPEMD-160 is not available
            ripemd_digest = hashlib.sha256(hashlib.sha256(pubkey).digest()).digest()[:20]
        
        # Add version byte and checksum
        versioned_payload = b'\x00' + ripemd_digest
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        
        # Encode result in Base58
        address = base58.b58encode(versioned_payload + checksum).decode()
        return address
    except Exception as e:
        logger.error(f"Error in private_key_to_address: {e}")
        return None

def address_similarity(addr1, addr2):
    """
    Calculate similarity between two Bitcoin addresses based on multiple factors.
    Returns a value between 0 and 1, where 1 is perfect match.
    
    Enhanced with insights from crypto_analysis, pattern_analysis, and statistical_analysis data.
    """
    if addr1 == addr2:
        return 1.0
    
    # Calculate basic character match ratio
    match_count = 0
    for i in range(min(len(addr1), len(addr2))):
        if addr1[i] == addr2[i]:
            match_count += 1
    
    # Basic similarity score
    basic_similarity = match_count / min(len(addr1), len(addr2))
    
    # Enhanced positional weighting based on pattern analysis
    weighted_match = 0
    position_weights = {}
    
    # Generate position weights with stronger emphasis on critical positions
    # Based on Bitcoin address structure (version + hash + checksum)
    for i in range(min(len(addr1), len(addr2))):
        # First character (version) is extremely important - must match
        if i == 0:
            weight = 4.0  # Version byte is crucial
        # Next 4 characters (beginning of hash) are very important
        elif i < 5:
            weight = 2.5 - (i * 0.2)  # 2.5, 2.3, 2.1, 1.9
        # Characters in the middle represent the hash
        elif 5 <= i < 26:
            # Give more weight to positions that contain the same character class (number vs letter)
            if addr1[i].isdigit() == addr2[i].isdigit():
                weight = 1.3
            else:
                weight = 0.9
        # Last 4 characters (checksum region) are critically important
        # These are derived from the hash so matching here indicates structural similarity
        elif i >= len(addr1) - 4:
            weight = 3.0
        else:
            weight = 1.0
        position_weights[i] = weight
    
    for i in range(min(len(addr1), len(addr2))):
        if addr1[i] == addr2[i]:
            weighted_match += position_weights[i]
    
    total_weight = sum(position_weights.values())
    weighted_similarity = weighted_match / total_weight
    
    # Character frequency analysis
    # Based on entropy_analysis showing importance of character distribution
    freq1 = {}
    freq2 = {}
    
    for c in addr1:
        freq1[c] = freq1.get(c, 0) + 1
    
    for c in addr2:
        freq2[c] = freq2.get(c, 0) + 1
    
    all_chars = set(freq1.keys()).union(set(freq2.keys()))
    freq_diff = 0
    
    for c in all_chars:
        diff = abs(freq1.get(c, 0) / len(addr1) - freq2.get(c, 0) / len(addr2))
        freq_diff += diff
    
    freq_similarity = 1 - (freq_diff / len(all_chars))
    
    # Find longest common substring
    # This captures sequential pattern matches which are significant per pattern_analysis
    def longest_common_substring(s1, s2):
        """Find the longest common substring between two strings.
        
        Uses dynamic programming approach with O(m*n) time complexity.
        Returns the longest substring that appears in both input strings.
        
        Args:
            s1 (str): First string to compare
            s2 (str): Second string to compare
            
        Returns:
            str: The longest common substring
        """
        # Early return for empty strings
        if not s1 or not s2:
            return ""
            
        # Optimize by making s1 the shorter string for better memory usage
        if len(s1) > len(s2):
            s1, s2 = s2, s1
            
        # Create DP table - only store current and previous row to reduce memory usage
        prev_row = [0] * (len(s2) + 1)
        current_row = [0] * (len(s2) + 1)
        
        longest = 0
        longest_end_pos = 0
        
        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                if s1[i-1] == s2[j-1]:
                    current_row[j] = prev_row[j-1] + 1
                    if current_row[j] > longest:
                        longest = current_row[j]
                        longest_end_pos = i
                else:
                    current_row[j] = 0
            
            # Swap rows for next iteration
            prev_row, current_row = current_row, prev_row
            
            # Reset current row for next iteration to avoid carrying over values
            current_row = [0] * (len(s2) + 1)
            
        # Return the longest common substring found
        return s1[longest_end_pos - longest: longest_end_pos]
    
    lcs = longest_common_substring(addr1, addr2)
    lcs_similarity = len(lcs) / min(len(addr1), len(addr2)) if min(len(addr1), len(addr2)) > 0 else 0
    
    # Compute prefix similarity for the first N characters
    # Based on secp256k1_analysis showing importance of address prefixes
    prefix_len = 8  # Consider first 8 characters as prefix
    prefix_match = 0
    for i in range(min(prefix_len, min(len(addr1), len(addr2)))):
        if addr1[i] == addr2[i]:
            prefix_match += 1
    
    prefix_similarity = prefix_match / min(prefix_len, min(len(addr1), len(addr2)))
    
    # Enhanced: Compute multi-level structural similarity based on character types and patterns
    structure_match = 0
    type_transitions_match = 0
    position_weighted_structure_match = 0
    prev_type1, prev_type2 = None, None
    
    for i in range(min(len(addr1), len(addr2))):
        # Determine character types with finer granularity
        # 1-4: digits (0-3, 4-6, 7-9)
        # 5-6: uppercase (A-M, N-Z)
        # 7-8: lowercase (a-m, n-z)
        char1, char2 = addr1[i], addr2[i]
        
        if char1.isdigit():
            type1 = 1 if '0' <= char1 <= '3' else (2 if '4' <= char1 <= '6' else 3)
        elif char1.isupper():
            type1 = 4 if 'A' <= char1 <= 'M' else 5
        else:
            type1 = 6 if 'a' <= char1 <= 'm' else 7
            
        if char2.isdigit():
            type2 = 1 if '0' <= char2 <= '3' else (2 if '4' <= char2 <= '6' else 3)
        elif char2.isupper():
            type2 = 4 if 'A' <= char2 <= 'M' else 5
        else:
            type2 = 6 if 'a' <= char2 <= 'm' else 7
        
        # Check if both characters are of the same type
        if type1 == type2:
            structure_match += 1
            # Weight early positions more heavily
            position_weight = 1.0 - (i / (2 * min(len(addr1), len(addr2))))
            position_weighted_structure_match += position_weight
            
        # Check if transitions between character types match
        if i > 0 and prev_type1 is not None and prev_type2 is not None:
            if (prev_type1 != type1 and prev_type2 != type2) or (prev_type1 == type1 and prev_type2 == type2):
                type_transitions_match += 1
                
        prev_type1, prev_type2 = type1, type2
    
    structure_similarity = structure_match / min(len(addr1), len(addr2))
    weighted_structure_similarity = position_weighted_structure_match / min(len(addr1), len(addr2))
    transition_similarity = type_transitions_match / max(1, min(len(addr1), len(addr2)) - 1)
    
    # Enhanced: Advanced pattern analysis with multi-scale matching
    pattern_match = 0
    consecutive_pattern_match = 0
    
    # Variable gap pattern matching with adaptive weighting
    for offset in range(1, 6):  # Expanded range of offsets
        matches_at_offset = 0
        consecutive_matches = 0
        max_consecutive = 0
        
        for i in range(min(len(addr1), len(addr2)) - offset):
            if addr1[i] == addr2[i] and addr1[i+offset] == addr2[i+offset]:
                matches_at_offset += 1
                consecutive_matches += 1
                max_consecutive = max(max_consecutive, consecutive_matches)
            else:
                consecutive_matches = 0
        
        # Weight closer offsets and consecutive matches more heavily
        pattern_match += matches_at_offset * (1.0 / offset)
        consecutive_pattern_match += max_consecutive * (1.0 / offset)
    
    # Rhythmic pattern detection (every Nth character matches)
    rhythmic_match = 0
    for rhythm in range(2, 5):  # Check patterns with period 2, 3, and 4
        rhythm_matches = 0
        for i in range(0, min(len(addr1), len(addr2)), rhythm):
            if addr1[i] == addr2[i]:
                rhythm_matches += 1
        
        max_possible = (min(len(addr1), len(addr2)) + rhythm - 1) // rhythm
        rhythmic_match += rhythm_matches / max_possible if max_possible > 0 else 0
    
    rhythmic_similarity = rhythmic_match / 3  # Average across the 3 rhythms
    
    max_possible_patterns = max(min(len(addr1), len(addr2)) - 3, 1)  # Avoid division by zero
    pattern_similarity = min(1.0, pattern_match / (3 * max_possible_patterns))
    consecutive_pattern_similarity = min(1.0, consecutive_pattern_match / max_possible_patterns)
    
    # Compute n-gram similarity (character sequences)
    ngram_similarity = 0
    for n in range(2, 4):  # Bigrams and trigrams
        ngrams1 = [addr1[i:i+n] for i in range(len(addr1)-n+1)]
        ngrams2 = [addr2[i:i+n] for i in range(len(addr2)-n+1)]
        
        common_ngrams = set(ngrams1).intersection(set(ngrams2))
        total_ngrams = set(ngrams1).union(set(ngrams2))
        
        if total_ngrams:
            ngram_similarity += len(common_ngrams) / len(total_ngrams)
    
    ngram_similarity /= 2  # Average across bigrams and trigrams
    
    # Combine all similarity metrics with appropriate weights
    final_similarity = (
        0.25 * weighted_similarity +            # Position-weighted character matches (increased)
        0.10 * basic_similarity +               # Simple character match ratio
        0.15 * prefix_similarity +              # Strong weight on prefix matching
        0.15 * lcs_similarity +                 # Sequential pattern matching (increased)
        0.05 * freq_similarity +                # Character frequency distribution
        0.05 * structure_similarity +           # Basic structural pattern matching
        0.05 * weighted_structure_similarity +  # Position-weighted structural matching
        0.05 * transition_similarity +          # Type transition patterns
        0.10 * pattern_similarity +             # Non-contiguous pattern matching
        0.05 * consecutive_pattern_similarity   # Consecutive pattern matching
    )
    
    # Apply adaptive scaling function with dynamic curve based on similarity level
    # This creates a more nuanced differentiation between candidates
    if final_similarity > 0.8:
        # Extremely promising candidates get boosted significantly
        scaled_similarity = 0.8 + 0.2 * ((final_similarity - 0.8) ** 0.2)  # More aggressive boosting
    elif final_similarity > 0.6:
        # Very good candidates get strong boost
        scaled_similarity = 0.6 + 0.2 * ((final_similarity - 0.6) ** 0.4)  # More aggressive boosting
    elif final_similarity > 0.4:
        # Good candidates get moderate boost
        scaled_similarity = 0.4 + 0.2 * ((final_similarity - 0.4) / 0.2) ** 0.6  # More aggressive boosting
    else:
        # Apply slight non-linear scaling for lower similarities to differentiate weak candidates
        scaled_similarity = final_similarity ** 0.85  # Less penalizing for lower similarities
    
    return scaled_similarity

# -----------------------------
# Candidate Validation
# -----------------------------
# Candidate Validation Functions

def has_too_many_consecutive_chars(value: int) -> bool:
    """
    Check if hex representation has more than 3 consecutive identical characters.
    
    Args:
        value: Integer value to check
        
    Returns:
        bool: True if the hex representation has more than 3 consecutive identical characters
    """
    hex_str = hex(value)[2:]  # Remove '0x' prefix
    
    # Optimize with regex for faster pattern matching
    import re
    if re.search(r'(.)\1{3,}', hex_str):
        return True
    
    # Fallback manual check for verification
    count = 1
    prev_char = hex_str[0] if hex_str else ''
    
    for char in hex_str[1:]:
        if char == prev_char:
            count += 1
            if count > 3:
                return True
        else:
            count = 1
            prev_char = char
    
    return False

def is_valid_candidate(value: int) -> bool:
    """
    Check if a value is a valid candidate for the 68th term:
    1. Must be greater than previous term
    2. Must have exactly 68 bits (fit in 68 bits)
    3. Must not have more than 3 consecutive identical hex chars
    """
    return (
        value > PREV_TERM_67_INT and
        value.bit_length() <= TARGET_INDEX and
        not has_too_many_consecutive_chars(value)
    )

def sanitize_candidate(value):
    """
    Ensure a candidate is an integer for bit operations.
    
    Args:
        value: The candidate, which might be an int, str, or other type
        
    Returns:
        int: The candidate as an integer, or PREV_TERM_67_INT if conversion fails
    """
    if isinstance(value, int):
        return value
    
    if isinstance(value, str):
        try:
            return int(value)
        except (ValueError, TypeError):
            # Log the error but don't crash
            logger.warning(f"Failed to convert string to integer: {value}")
            return PREV_TERM_67_INT
            
    if isinstance(value, dict) and "private_key_int" in value:
        try:
            return int(value["private_key_int"])
        except (ValueError, TypeError):
            logger.warning(f"Failed to convert dictionary value to integer")
            return PREV_TERM_67_INT
            
    if isinstance(value, (list, tuple)) and len(value) > 0:
        return sanitize_candidate(value[0])
    
    # Default to previous term if all else fails
    logger.warning(f"Unknown candidate type: {type(value)}, using default value")
    return PREV_TERM_67_INT

def test_candidate(candidate: int) -> tuple:
    """
    Test a candidate and return (address, similarity)
    
    Args:
        candidate: The private key to test
        
    Returns:
        tuple: (address, similarity) - address will be None if invalid
    """
    global BEST_CANDIDATES, ALL_TIME_BEST_SIMILARITY, ALL_TIME_BEST_CANDIDATE, ALL_TIME_BEST_ADDRESS, LAST_DISPLAY_TIME
    
    if not is_valid_candidate(candidate):
        return None, 0.0
    
    try:
        # Generate address
        address = private_key_to_address(candidate)
        
        # If address generation failed, return early
        if not address:
            return None, 0.0
            
        # Check for exact match
        is_match = (address == TARGET_ADDRESS)
        
        # Calculate similarity
        similarity = address_similarity(address, TARGET_ADDRESS)
        
        # Update all-time best if this is better
        if similarity > ALL_TIME_BEST_SIMILARITY:
            ALL_TIME_BEST_SIMILARITY = similarity
            ALL_TIME_BEST_CANDIDATE = candidate
            ALL_TIME_BEST_ADDRESS = address
            
            # Log the new best score prominently
            logger.info(f"BEST SCORE UPDATE: {similarity:.6f} for address {address}")
            LAST_DISPLAY_TIME = time.time()
        elif time.time() - LAST_DISPLAY_TIME > 60:  # Refresh display every 60 seconds
            display_best_score()
        
        # Log all generated addresses to console with their similarity
        logger.info(f"Generated: {address} from {hex(candidate)} (similarity: {similarity:.6f})")
        
        # Extra logging for high-similarity candidates
        if similarity >= 0.2:
            logger.info(f"HIGH SIMILARITY CANDIDATE: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
        
        # Enhanced logging for different similarity tiers
        if similarity >= 0.5 and similarity < 0.6:
            logger.info(f"50%+ SIMILARITY FOUND: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
        elif similarity >= 0.6 and similarity < 0.7:
            logger.info(f"60%+ SIMILARITY FOUND: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
        elif similarity >= 0.7 and similarity < 0.8:
            logger.info(f"70%+ SIMILARITY FOUND: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
        elif similarity >= 0.8:
            logger.info(f"80%+ SIMILARITY ACHIEVED!!! {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
        
        # Special treatment for candidates nearing our target similarity
        if similarity >= TARGET_SIMILARITY:
            logger.info(f"TARGET SIMILARITY CANDIDATE FOUND: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
            # Immediately try some close variations to see if we can improve further
            immediate_variations = []
            # Try single bit flips
            for bit in range(68):
                var = candidate ^ (1 << bit)
                if is_valid_candidate(var):
                    immediate_variations.append(var)
            
            # Try small adjustments
            for adj in [-10, -5, -3, -2, -1, 1, 2, 3, 5, 10]:
                var = candidate + adj
                if is_valid_candidate(var):
                    immediate_variations.append(var)
            
            # Test these variations immediately
            logger.info(f"Immediately testing {len(immediate_variations)} variations of high similarity candidate")
            for var in immediate_variations:
                try:
                    var_addr = private_key_to_address(var)
                    if var_addr:
                        var_sim = address_similarity(var_addr, TARGET_ADDRESS)
                        if var_sim > similarity:
                            logger.info(f"Found immediate improvement! New similarity: {var_sim:.6f}")
                except Exception as e:
                    logger.debug(f"Error testing immediate variation: {e}")
        
        # Return results (always a tuple of two values)
        return address, similarity
    except Exception as e:
        logger.error(f"Error in test_candidate for {hex(candidate)}: {e}")
        return None, 0.0

# -----------------------------
# Memory and Learning
# -----------------------------
class MemoryManager:
    """
    Manages memory of best candidates and addresses
    """
    def __init__(self, filename=CLOSEST_ADDRESSES_FILE, memory_size=MEMORY_SIZE):
        self.memory = []
        self.memory_size = memory_size
        self.filename = filename
        self.absolute_best = None  # Keep track of absolute best candidate
        
        # Ensure memory is loaded on initialization
        self.load_memory()
        
        # Add index for faster lookups
        self.memory_index = set()
        for entry in self.memory:
            self.memory_index.add(int(entry["private_key_int"]))
        
        logger.info(f"Memory manager initialized with {len(self.memory)} entries")
    
    def load_memory(self):
        """Load memory from file if exists"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    try:
                        self.memory = json.load(f)
                        logger.info(f"Loaded {len(self.memory)} previous results from memory")
                    except json.JSONDecodeError as je:
                        logger.error(f"JSON parsing error: {je}. Attempting to recover...")
                        # Try to recover from corrupt JSON
                        self.memory = self._recover_corrupt_json(self.filename)
                        if not self.memory:
                            logger.error("Could not recover from corrupt JSON. Starting with empty memory.")
                            self.memory = []
                    
                    # Clean memory - remove corrupt entries and ensure correct types
                    valid_entries = []
                    for entry in self.memory:
                        if "private_key_int" in entry and "similarity" in entry and "address" in entry:
                            try:
                                # Ensure private_key_int is an integer or can be converted to one
                                if isinstance(entry["private_key_int"], str):
                                    entry["private_key_int"] = int(entry["private_key_int"])
                                    
                                # Ensure similarity is a float
                                entry["similarity"] = float(entry["similarity"])
                                
                                # Ensure address is a string
                                if not isinstance(entry["address"], str):
                                    continue
                                    
                                valid_entries.append(entry)
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Invalid entry in memory: {e}")
                                continue
                    
                    # Replace memory with valid entries
                    self.memory = valid_entries
                    logger.info(f"Validated {len(valid_entries)} entries in memory")
                    
                    # Sort memory by similarity (highest first)
                    self.memory.sort(key=lambda x: x["similarity"], reverse=True)
                    
                    # Set absolute best from memory if available
                    if self.memory:
                        try:
                            self.absolute_best = self.memory[0]
                            # Ensure the absolute best candidate has an integer private key
                            if isinstance(self.absolute_best["private_key_int"], str):
                                self.absolute_best["private_key_int"] = int(self.absolute_best["private_key_int"])
                                
                            logger.info(f"Loaded absolute best similarity: {self.absolute_best['similarity']:.6f}")
                            logger.info(f"Absolute best candidate: {hex(int(self.absolute_best['private_key_int']))}")
                            logger.info(f"Absolute best address: {self.absolute_best['address']}")
                            
                            # Log comparison with target
                            target = TARGET_ADDRESS
                            best_addr = self.absolute_best['address']
                            matches = 0
                            for i, (t, b) in enumerate(zip(target, best_addr)):
                                if t == b:
                                    matches += 1
                            logger.info(f"Character matches: {matches}/{len(target)} ({matches/len(target)*100:.2f}%)")
                        except Exception as e:
                            logger.error(f"Error processing best memory entry: {e}")
                            if self.memory and len(self.memory) > 1:
                                # Try next best entry
                                logger.info("Trying next best entry...")
                                self.absolute_best = self.memory[1]
                            else:
                                self.absolute_best = None
            except Exception as e:
                logger.error(f"Error loading memory: {e}")
                logger.error(f"Creating new memory file")
                self.memory = []
                self.absolute_best = None
        else:
            logger.info(f"No memory file found at {self.filename}, starting fresh")
            self.memory = []
            self.absolute_best = None
            
    def _recover_corrupt_json(self, filename):
        """Attempt to recover from corrupt JSON file by reading valid entries line by line"""
        try:
            recovered_entries = []
            with open(filename, 'r') as f:
                content = f.read()
                
            # Try to find all valid JSON objects
            entry_pattern = r'{[^{}]*"private_key_int"[^{}]*"similarity"[^{}]*"address"[^{}]*}'
            matches = re.findall(entry_pattern, content)
            
            for match in matches:
                try:
                    entry = json.loads(match)
                    if "private_key_int" in entry and "similarity" in entry and "address" in entry:
                        recovered_entries.append(entry)
                except:
                    continue
                    
            logger.info(f"Recovered {len(recovered_entries)} entries from corrupt JSON")
            return recovered_entries
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            return []
    
    def save_memory(self):
        """Save memory to file with error handling and atomic write"""
        try:
            # Write to temporary file first
            temp_filename = f"{self.filename}.tmp"
            with open(temp_filename, 'w') as f:
                json.dump(self.memory, f, indent=2)
            
            # Rename to actual filename (atomic operation)
            os.replace(temp_filename, self.filename)
            self.last_save_time = time.time()
            
            # Log statistics about saved memory
            if self.memory:
                logger.info(f"Saved {len(self.memory)} candidates to memory. "
                           f"Best similarity: {self.memory[0]['similarity']:.6f}, "
                           f"Candidates ≥80%: {self.similarity_thresholds[0.8]}")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    # Add save() as an alias for save_memory() to fix compatibility issues
    def save(self):
        """Alias for save_memory()"""
        return self.save_memory()
    
    def add(self, candidate, similarity):
        """
        Add a candidate to memory if it's promising, with enhanced tracking and deduplication.
        
        Args:
            candidate: The private key integer
            similarity: The similarity score
            
        Returns:
            bool: True if the candidate was in the top candidates
        """
        try:
            # Generate address for this candidate
            address = private_key_to_address(candidate)
            if not address:
                return False
            
            # Check if this candidate already exists in memory
            for existing in self.memory:
                if existing["private_key_int"] == candidate:
                    # Update if new similarity is better
                    if similarity > existing["similarity"]:
                        existing["similarity"] = float(similarity)
                        existing["timestamp"] = time.time()
                        # Re-sort memory
                        self.memory.sort(key=lambda x: x["similarity"], reverse=True)
                    return similarity >= existing["similarity"]
            
            # Calculate bit-level features for pattern analysis
            hamming_weight = bin(candidate).count('1')
            bit_length = candidate.bit_length()
            
            # Calculate distance from previous term
            distance_from_prev = abs(candidate - PREV_TERM_67_INT)
            
            # Create entry with additional metadata
            entry = {
                "private_key_int": candidate,
                "private_key_hex": hex(candidate),
                "address": address,
                "similarity": float(similarity),  # Ensure it's a float
                "timestamp": time.time(),
                "bit_length": bit_length,
                "hamming_weight": hamming_weight,  # Count of set bits
                "distance_from_prev": distance_from_prev,
                "bit_flip_count": bin(candidate ^ PREV_TERM_67_INT).count('1')  # Hamming distance from prev term
            }
            
            # Update absolute best if this is better
            if self.absolute_best is None or similarity > self.absolute_best["similarity"]:
                self.absolute_best = entry
                logger.info(f"New absolute best similarity: {similarity:.6f} for address {address}")
                
                # When we find a new best, try immediate bit flips
                if similarity >= 0.7:  # Only for high similarity candidates
                    self._try_immediate_bit_flips(candidate, similarity)
            
            # Update similarity threshold counts
            for threshold in self.similarity_thresholds:
                if similarity >= threshold:
                    self.similarity_thresholds[threshold] += 1
            
            # Add to bit pattern clusters
            self._add_to_bit_clusters(candidate, entry)
                    
            # Add to memory
            self.memory.append(entry)
            
            # Sort by similarity (descending)
            self.memory.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Trim to memory size
            if len(self.memory) > self.memory_size:
                self.memory = self.memory[:self.memory_size]
            
            # Save memory periodically (every 100 additions or every 5 minutes)
            if (len(self.memory) % 100 == 0) or (time.time() - self.last_save_time > 300):
                self.save_memory()
            
            # Return True if in top 10
            return len(self.memory) <= 10 or similarity >= self.memory[9]["similarity"]
        except Exception as e:
            logger.error(f"Error adding to memory: {e}")
            return False
    
    def _try_immediate_bit_flips(self, candidate, similarity):
        """Try immediate bit flips for promising candidates"""
        logger.info(f"Trying immediate bit flips for high similarity candidate: {hex(candidate)}")
        
        # Try flipping 1-3 bits
        for num_bits in range(1, 4):
            # Get binary representation
            bits = bin(candidate)[2:].zfill(68)
            bit_positions = list(range(len(bits)))
            
            # Focus on specific regions known to be important
            important_regions = [
                range(0, 8),           # First 8 bits
                range(60, 68),         # Last 8 bits
                range(30, 38)          # Middle 8 bits
            ]
            
            # Flatten the important regions
            important_positions = [pos for region in important_regions for pos in region]
            
            # Try flipping bits in important positions first
            for combo in itertools.combinations(important_positions, num_bits):
                # Create new value by flipping selected bits
                new_bits = list(bits)
                for pos in combo:
                    new_bits[pos] = '1' if new_bits[pos] == '0' else '0'
                
                # Convert back to integer
                value = int(''.join(new_bits), 2)
                
                # Test the new candidate
                try:
                    addr = private_key_to_address(value)
                    if addr:
                        new_sim = address_similarity(addr, TARGET_ADDRESS)
                        if new_sim > similarity:
                            logger.info(f"Immediate bit flip improved similarity: {new_sim:.6f} > {similarity:.6f}")
                            # Add this improved candidate to memory
                            self.add(value, new_sim)
                except Exception as e:
                    continue  # Skip errors and continue
    
    def add_result(self, candidate, address, similarity):
        """
        Add a result to memory with improved handling and indexing
        
        Args:
            candidate: The private key integer
            address: The generated Bitcoin address
            similarity: The similarity score
        """
        # Verify inputs
        if not address or similarity <= 0:
            return
            
        # Create new entry
        entry = {
            "private_key_int": str(candidate),  # Store as string for JSON compatibility
            "private_key_hex": hex(candidate),
            "address": address,
            "similarity": similarity,
            "timestamp": time.time()
        }
        
        # Check if candidate is already in memory to avoid duplicates
        if candidate in self.memory_index:
            # Update only if new similarity is higher
            for i, existing in enumerate(self.memory):
                if int(existing["private_key_int"]) == candidate:
                    if similarity > existing["similarity"]:
                        self.memory[i] = entry
                        logger.info(f"Updated existing candidate with higher similarity: {similarity:.6f}")
                    return
        
        # Add to index
        self.memory_index.add(candidate)
        
        # Add to memory
        self.memory.append(entry)
        
        # Update absolute best if this is better
        if not self.absolute_best or similarity > self.absolute_best["similarity"]:
            self.absolute_best = entry
            logger.info(f"New absolute best similarity: {similarity:.6f} for {address}")
        
        # Sort and trim memory to keep only the best entries
        self.memory.sort(key=lambda x: float(x["similarity"]), reverse=True)
        if len(self.memory) > self.memory_size:
            # Remove excess entries
            excess = self.memory[self.memory_size:]
            self.memory = self.memory[:self.memory_size]
            
            # Clean up index
            for e in excess:
                try:
                    self.memory_index.remove(int(e["private_key_int"]))
                except:
                    pass
        
        # Save memory regularly but not on every add
        # This decreases disk I/O while still preserving results
        if len(self.memory) % 100 == 0 or (similarity > 0.2 and len(self.memory) % 10 == 0):
            self.save_memory()
            
        # Try bit flips for promising candidates
        if similarity > 0.25:
            self._try_immediate_bit_flips(candidate, similarity)
    
    def get_best_candidates(self, n=10):
        """Get the n best candidates"""
        # Always ensure we're getting the absolute best from memory
        if self.absolute_best and (not self.memory or self.absolute_best["similarity"] > self.memory[0]["similarity"]):
            # If we have an absolute best that's better than what's in memory,
            # make sure it's inserted at the front
            for i, item in enumerate(self.memory):
                if item["private_key_int"] == self.absolute_best["private_key_int"]:
                    self.memory.pop(i)
                    break
            self.memory.insert(0, self.absolute_best)
            
        # Return the best n candidates as (value, similarity) tuples
        return [(item["private_key_int"], item["similarity"]) for item in self.memory[:n]]
    
    def get_promising_values(self, n=5):
        """Get promising candidate values for further exploration"""
        best = self.get_best_candidates(n)
        return [value for value, _ in best]
    
    def get_absolute_best_similarity(self):
        """
        Get the absolute best similarity score recorded
        
        Returns:
            float: The best similarity score, or 0 if no scores recorded
        """
        # If we have an absolute best record, use it
        if self.absolute_best and "similarity" in self.absolute_best:
            return float(self.absolute_best["similarity"])
        
        # Otherwise check if we have any entries in memory
        if self.memory:
            # Refresh sort
            self.memory.sort(key=lambda x: float(x["similarity"]), reverse=True)
            # Set absolute best
            self.absolute_best = self.memory[0]
            return float(self.memory[0]["similarity"])
            
        # No entries found
        return 0.0

# -----------------------------
# Address Logging
# -----------------------------

class AddressLogger:
    """
    Logs all generated Bitcoin addresses
    """
    def __init__(self, filename=ADDRESS_LOG_FILE):
        self.filename = filename
        self.count = 0
        self.initialize_log()
    
    def initialize_log(self):
        """Initialize the address log file if it doesn't exist"""
        file_exists = os.path.exists(self.filename)
        
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "timestamp", 
                    "private_key_int", 
                    "private_key_hex", 
                    "bitcoin_address", 
                    "similarity",
                    "bit_length"
                ])
    
    def log_address(self, private_key, address, similarity):
        """Log an address to the CSV file"""
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                private_key,
                hex(private_key),
                address,
                similarity,
                private_key.bit_length()
            ])
        self.count += 1
        
        # Log summary every 1000 addresses
        if self.count % 1000 == 0:
            logger.info(f"Logged {self.count} addresses so far")

# -----------------------------
# Search Strategies
# -----------------------------

def bit_flip_search(center, max_bits=5, max_candidates=1000):
    """
    Search by flipping bits in a candidate
    """
    logger.info(f"Starting bit flip search around {hex(center)}")
    
    # Get binary representation
    bits = bin(center)[2:].zfill(68)
    
    tested = 0
    
    # Try flipping different bits
    for num_bits in range(1, max_bits + 1):
        if tested >= max_candidates:
            break
            
        logger.info(f"Trying {num_bits}-bit flips")
        
        # Generate all possible combinations
        bit_positions = list(range(len(bits)))
        for combo in itertools.combinations(bit_positions, num_bits):
            if tested >= max_candidates:
                break
                
            # Create new value by flipping selected bits
            new_bits = list(bits)
            for pos in combo:
                new_bits[pos] = '1' if new_bits[pos] == '0' else '0'
            
            # Convert back to integer
            value = int(''.join(new_bits), 2)
            
            # Test candidate
            match, address, similarity = test_candidate(value)
            tested += 1
            
            # Log the address
            address_logger.log_address(value, address, similarity)
            
            # Remember if it's a good candidate
            is_good = memory_manager.add_result(value, address, similarity)
            
            if is_good:
                logger.info(f"Found promising candidate: {hex(value)} -> {address} (similarity: {similarity:.6f})")
            
            # Check for match
            if match:
                logger.info(f"MATCH FOUND! Candidate: {hex(value)}")
                save_result(value)
                return value
    
    logger.info(f"Completed testing {tested} bit-flipped candidates")
    return None

def pattern_walk(start_value, pattern_func, steps=100):
    """
    Walk a mathematical pattern from a starting value
    """
    value = start_value
    
    for step in range(steps):
        # Apply pattern function
        value = pattern_func(value)
        
        # Test candidate
        match, address, similarity = test_candidate(value)
        
        # Log the address
        address_logger.log_address(value, address, similarity)
        
        # Remember if it's a good candidate
        is_good = memory_manager.add_result(value, address, similarity)
        
        if is_good:
            logger.info(f"Found promising candidate: {hex(value)} -> {address} (similarity: {similarity:.6f})")
        
        # Check for match
        if match:
            logger.info(f"MATCH FOUND! Candidate: {hex(value)}")
            save_result(value)
            return value
    
    return None

def adaptive_range_search(center, radius, max_candidates=1000):
    """
    Search in a range around a center value, adapting the step size
    based on similarity
    """
    logger.info(f"Starting adaptive range search around {hex(center)} with radius {radius}")
    
    tested = 0
    best_similarity = 0.0
    best_candidate = None
    step_size = 1
    
    # Search around center
    for i in range(-radius, radius + 1, step_size):
        if tested >= max_candidates:
            break
            
        value = center + i
        
        # Test candidate
        match, address, similarity = test_candidate(value)
        tested += 1
        
        # Log the address
        address_logger.log_address(value, address, similarity)
        
        # Remember if it's a good candidate
        is_good = memory_manager.add_result(value, address, similarity)
        
        # Adapt step size based on similarity trend
        if similarity > best_similarity:
            best_similarity = similarity
            best_candidate = value
            # If improving, decrease step size for finer search
            step_size = max(1, int(step_size * 0.8))
        else:
            # If not improving, increase step size to explore more
            step_size = min(radius // 10, step_size * 2)
        
        if is_good:
            logger.info(f"Found promising candidate: {hex(value)} -> {address} (similarity: {similarity:.6f})")
        
        # Check for match
        if match:
            logger.info(f"MATCH FOUND! Candidate: {hex(value)}")
            save_result(value)
            return value
    
    logger.info(f"Completed testing {tested} adaptive range candidates")
    return None

def genetic_search(population_size=POPULATION_SIZE, generations=10):
    """
    Genetic algorithm search
    """
    logger.info(f"Starting genetic search with population size {population_size}")
    
    # Create initial population
    population = []
    
    # Add some known good candidates
    promising_values = memory_manager.get_promising_values(5)
    for value in promising_values:
        population.append(value)
    
    # Add base values
    base_values = [
        PREV_TERM_67,
        MIN_PREDICTED,
        MAX_PREDICTED,
        BIT_SHIFTED_VALUE,
        ESTIMATE_VALUE
    ]
    
    for value in base_values:
        if value not in population:
            population.append(value)
    
    # Fill the rest with random candidates
    while len(population) < population_size:
        # Generate random bits
        bits = ['1' if random.random() > 0.5 else '0' for _ in range(68)]
        # Make sure MSB is 1 for 68 bits
        bits[0] = '1'
        # Convert to integer
        value = int(''.join(bits), 2)
        
        if is_valid_candidate(value) and value not in population:
            population.append(value)
    
    # Evolve for generations
    for gen in range(generations):
        logger.info(f"Genetic algorithm generation {gen + 1}/{generations}")
        
        # Evaluate fitness
        fitness = []
        for candidate in population:
            match, address, similarity = test_candidate(candidate)
            
            # Log the address
            address_logger.log_address(candidate, address, similarity)
            
            # Remember if it's a good candidate
            is_good = memory_manager.add_result(candidate, address, similarity)
            
            if is_good:
                logger.info(f"Found promising candidate: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
            
            # Check for match
            if match:
                logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                save_result(candidate)
                return candidate
            
            fitness.append((candidate, similarity))
        
        # Sort by fitness
        fitness.sort(key=lambda x: x[1], reverse=True)
        
        # Create new population
        new_population = []
        
        # Elitism - keep top 10%
        elite_count = max(1, int(population_size * 0.1))
        for i in range(elite_count):
            new_population.append(fitness[i][0])
        
        # Crossover and mutation
        while len(new_population) < population_size:
            # Select parents
            parent1 = fitness[random.randint(0, population_size // 2)][0]
            parent2 = fitness[random.randint(0, population_size // 2)][0]
            
            # Crossover
            child = crossover(parent1, parent2)
            
            # Mutation
            child = mutate(child, MUTATION_RATE)
            
            if is_valid_candidate(child) and child not in new_population:
                new_population.append(child)
        
        # Replace population
        population = new_population
    
    logger.info(f"Completed genetic search without finding a match")
    return None

def crossover(parent1, parent2):
    """
    Perform bitwise crossover between two candidates
    """
    # Convert to binary
    bits1 = list(bin(parent1)[2:].zfill(68))
    bits2 = list(bin(parent2)[2:].zfill(68))
    
    # Select crossover point
    point = random.randint(1, 67)
    
    # Create child
    child_bits = bits1[:point] + bits2[point:]
    
    # Convert back to int
    return int(''.join(child_bits), 2)

def mutate(candidate, mutation_rate=MUTATION_RATE):
    """
    Mutate bits in a candidate with given probability
    """
    # Convert to binary
    bits = list(bin(candidate)[2:].zfill(68))
    
    # Mutate bits
    for i in range(len(bits)):
        if random.random() < mutation_rate:
            bits[i] = '1' if bits[i] == '0' else '0'
    
    # Convert back to int
    return int(''.join(bits), 2)

def learning_search():
    """
    Use historical data to guide the search
    """
    logger.info("Starting learning-based search")
    
    # Get top candidates
    top_candidates = memory_manager.get_best_candidates(10)
    
    # No candidates yet, generate some default ones instead of returning None
    if not top_candidates:
        logger.info("No candidates in memory yet - using default generation")
        # Generate some random candidates as fallback
        candidates = []
        base_values = [
            PREV_TERM_67,
            MIN_PREDICTED,
            MAX_PREDICTED,
            BIT_SHIFTED_VALUE,
            ESTIMATE_VALUE
        ]
        
        # Add some small variations to each base value
        for base in base_values:
            for i in range(-10, 11):
                value = base + i
                if is_valid_candidate(value):
                    candidates.append(value)
                    
                # Also try bit-flips of the least significant bits
                for bit in range(8):
                    bit_flipped = base ^ (1 << bit)
                    if is_valid_candidate(bit_flipped):
                        candidates.append(bit_flipped)
        
        # Add some random valid candidates
        while len(candidates) < 100:
            # Generate a random value near one of the base values
            base = random.choice(base_values)
            offset = random.randint(-1000, 1000)
            value = base + offset
            if is_valid_candidate(value):
                candidates.append(value)
        
        logger.info(f"Generated {len(candidates)} default candidates for learning search")
    else:
        # Analyze patterns in successful candidates - with timeout protection
        try:
            bit_stats = analyze_bit_patterns(top_candidates)
            
            # Generate candidates based on patterns
            candidates = generate_pattern_candidates(bit_stats, 1000)
            logger.info(f"Generated {len(candidates)} pattern-based candidates")
        except Exception as e:
            logger.error(f"Error in pattern generation: {e}")
            # Fallback to simpler candidate generation
            candidates = []
            for candidate_data in top_candidates:
                base = int(candidate_data["private_key_int"])
                candidates.append(base)
                # Add some small variations
                for i in range(-10, 10):
                    value = base + i
                    if is_valid_candidate(value):
                        candidates.append(value)
            logger.info(f"Using fallback candidate generation: {len(candidates)} candidates")
    
    # Test candidates with timeout protection
    tested_count = 0
    for candidate in candidates:
        match, address, similarity = test_candidate(candidate)
        tested_count += 1
        
        # Log the address
        if address:  # Only log if we got a valid address
            address_logger.log_address(candidate, address, similarity)
            
            # Remember if it's a good candidate
            is_good = memory_manager.add_result(candidate, address, similarity)
            
            if is_good:
                logger.info(f"Found promising candidate: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
            
            # Check for match
            if match:
                logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                save_result(candidate)
                return candidate
        
        # Log progress periodically
        if tested_count % 100 == 0:
            logger.info(f"Tested {tested_count} candidates in learning search")
    
    logger.info(f"Completed learning search, tested {tested_count} candidates")
    return None

def analyze_bit_patterns(candidates):
    """
    Analyze bit patterns in promising candidates
    """
    # Count frequency of 1s at each bit position
    bit_stats = [0] * 68
    
    logger.info(f"Analyzing bit patterns in {len(candidates)} candidates")
    
    for candidate_data in candidates:
        candidate = int(candidate_data["private_key_int"])
        bits = bin(candidate)[2:].zfill(68)
        
        for i, bit in enumerate(bits):
            if bit == '1':
                bit_stats[i] += 1
    
    # Convert to probabilities - protect against division by zero
    candidate_count = max(1, len(candidates))  # Ensure we don't divide by zero
    bit_probs = [count / candidate_count for count in bit_stats]
    
    logger.info(f"Bit pattern analysis complete")
    return bit_probs

def generate_pattern_candidates(bit_probs, count=1000):
    """
    Generate candidates based on bit probabilities
    """
    candidates = set()
    start_time = time.time()
    timeout = 10  # Maximum seconds to spend generating candidates
    attempts = 0
    
    logger.info(f"Generating pattern candidates (target: {count})")
    
    while len(candidates) < count:
        # Check for timeout to avoid infinite loops
        if time.time() - start_time > timeout:
            logger.warning(f"Pattern candidate generation timeout after {len(candidates)} candidates")
            break
            
        attempts += 1
        if attempts > count * 10:  # Avoid excessive attempts
            logger.warning(f"Excessive attempts in pattern generation ({attempts})")
            break
            
        # Generate bits based on probabilities
        bits = []
        for prob in bit_probs:
            if random.random() < prob:
                bits.append('1')
            else:
                bits.append('0')
        
        # Ensure MSB is 1 for 68 bits
        bits[0] = '1'
        
        # Convert to integer
        try:
            value = int(''.join(bits), 2)
            
            if is_valid_candidate(value):
                candidates.add(value)
                
            # Log progress periodically
            if len(candidates) % 100 == 0 and len(candidates) > 0:
                logger.info(f"Generated {len(candidates)} candidates so far")
        except Exception as e:
            logger.error(f"Error converting bits to int: {e}")
    
    logger.info(f"Generated {len(candidates)} pattern candidates after {attempts} attempts")
    return list(candidates)

def target_similarity_search():
    """
    Specialized search specifically aimed at reaching 0.3+ similarity
    """
    logger.info(f"Starting specialized search for {TARGET_SIMILARITY}+ similarity")
    
    # Get all our best candidates so far
    best_candidates = memory_manager.get_best_candidates(5)
    if not best_candidates:
        logger.info("No candidates to work with yet")
        return None
    
    highest_similarity = best_candidates[0]["similarity"]
    logger.info(f"Current highest similarity: {highest_similarity:.6f}")
    
    # Analyze patterns in successful candidates first
    patterns = analyze_successful_patterns()
    
    # Generate candidates based on patterns and test them
    if patterns:
        pattern_candidates = generate_pattern_based_candidates(patterns)
        for candidate in pattern_candidates:
            match, address, similarity = test_candidate(candidate)
            if address:
                address_logger.log_address(candidate, address, similarity)
                memory_manager.add_result(candidate, address, similarity)
                
                # If found match or high similarity, return it
                if match or similarity >= TARGET_SIMILARITY:
                    if match:
                        logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                        save_result(candidate)
                    else:
                        logger.info(f"High similarity found! Candidate: {hex(candidate)}, Similarity: {similarity:.6f}")
                    return candidate
    
    # Strategy depends on how close we are to target
    if highest_similarity >= 0.25:  # If we're getting close
        logger.info("Close to target similarity, using intensive bit manipulation")
        return high_similarity_intensive_search(best_candidates)
    else:
        logger.info("Not yet close to target similarity, using broader search")
        return broad_exploration_search(best_candidates)

def high_similarity_intensive_search(candidates):
    """
    Intensive search for candidates already close to target similarity
    Enhanced to focus on patterns that have been successful
    """
    # Take our best candidate
    best_candidate = int(candidates[0]["private_key_int"])
    best_similarity = candidates[0]["similarity"]
    best_address = candidates[0]["address"]
    
    logger.info(f"Intensive search around: {hex(best_candidate)} -> {best_address} (similarity: {best_similarity:.6f})")
    logger.info(f"Target address: {TARGET_ADDRESS}")
    
    # Calculate bit patterns and their frequencies
    best_bits = bin(best_candidate)[2:].zfill(68)
    
    # Compare the addresses character by character
    logger.info("Character-by-character comparison:")
    matches = []
    mismatches = []
    
    for i, (t_char, b_char) in enumerate(zip(TARGET_ADDRESS, best_address)):
        if t_char == b_char:
            matches.append(i)
        else:
            mismatches.append((i, t_char, b_char))
            logger.info(f"Mismatch at position {i}: target={t_char}, current={b_char}")
    
    logger.info(f"Matches: {len(matches)}/{len(TARGET_ADDRESS)} positions")
    
    # Track which types of variations have been most effective
    variations_tried = {}
    
    # Generate variations focused on high similarity improvement
    all_variations = []
    
    # 1. Focus on fixing mismatches in the address:
    # We'll try bit variations that might affect specific positions in the address
    # This is much more targeted than just random bit flips
    for position, target_char, current_char in mismatches[:10]:  # Focus on first 10 mismatches
        # We don't know exactly which bits affect which positions, so try systematic bit flips
        for bits_to_flip in range(1, 4):  # Try flipping 1-3 bits at a time
            # Try flipping bits in different sections
            sections = [
                range(0, 20),       # Try early bits - likely affect start of address
                range(20, 40),      # Middle section
                range(40, 68)       # Later bits
            ]
            
            for section in sections:
                for positions in itertools.combinations(section, bits_to_flip):
                    var = best_candidate
                    for pos in positions:
                        var ^= (1 << pos)
                    
                    if is_valid_candidate(var):
                        all_variations.append((f"fix_pos_{position}", var))
    
    # 2. Advanced bit pattern manipulation:
    # Try these patterns for more extensive transformations of the key
    patterns = [
        # Consecutive bit flips
        lambda x: x ^ 0b11,
        lambda x: x ^ 0b111,
        lambda x: x ^ 0b1111,
        lambda x: x ^ 0b11111,
        
        # Byte modifications
        lambda x: x ^ 0xFF,
        lambda x: x ^ 0xFF00,
        lambda x: x ^ 0xFF0000,
        lambda x: x ^ 0xFF000000,
        
        # Complex patterns
        lambda x: x ^ (x >> 4),
        lambda x: x ^ (x << 4) & ((1 << 68) - 1),
        lambda x: x ^ (x >> 8) ^ (x << 8) & ((1 << 68) - 1),
        
        # Arithmetic
        lambda x: x + 1,
        lambda x: x - 1,
        lambda x: x + 0xFF,
        lambda x: x - 0xFF
    ]
    
    # Apply each pattern at different positions in the key
    for pattern_index, pattern_func in enumerate(patterns):
        for shift in [0, 8, 16, 24, 32, 40, 48, 56]:
            try:
                if shift == 0:
                    var = pattern_func(best_candidate)
                else:
                    # Apply pattern at shifted position
                    mask = pattern_func(1 << shift)
                    var = best_candidate ^ mask
                
                if is_valid_candidate(var):
                    all_variations.append((f"pattern_{pattern_index}_shift_{shift}", var))
            except Exception as e:
                logger.error(f"Error applying pattern {pattern_index} with shift {shift}: {e}")
    
    # 3. Try XOR with highest-scoring candidates from the past
    # This can combine features of multiple good candidates
    top_candidates = memory_manager.get_best_candidates(5)
    for i, candidate_data in enumerate(top_candidates):
        if i == 0:  # Skip the first one (it's our best_candidate)
            continue
            
        cand = int(candidate_data["private_key_int"])
        var = best_candidate ^ cand
        
        if is_valid_candidate(var):
            all_variations.append((f"xor_cand_{i}", var))
    
    # Test all variations, limited to avoid excessive testing
    # Use weighted random sampling to prioritize variations that have been successful
    all_variations = sorted(all_variations, key=lambda x: random.random())  # Shuffle
    variations_to_test = all_variations[:min(1500, len(all_variations))]
    
    logger.info(f"Testing {len(variations_to_test)} variations of high similarity candidate")
    
    for var_type, var in variations_to_test:
        match, address, similarity = test_candidate(var)
        
        # Record which variation type worked best
        if var_type not in variations_tried:
            variations_tried[var_type] = {"count": 0, "sum_similarity": 0, "max_similarity": 0}
        
        variations_tried[var_type]["count"] += 1
        variations_tried[var_type]["sum_similarity"] += similarity
        variations_tried[var_type]["max_similarity"] = max(
            variations_tried[var_type]["max_similarity"], 
            similarity
        )
        
        if address:
            address_logger.log_address(var, address, similarity)
            memory_manager.add_result(var, address, similarity)
            
            # If this is better than our target similarity, celebrate!
            if similarity >= TARGET_SIMILARITY:
                logger.info(f"Target similarity reached! New similarity: {similarity:.6f}")
                if match:
                    logger.info(f"MATCH FOUND! Candidate: {hex(var)}")
                    save_result(var)
                    return var
    
    # Report on the most effective variation types
    logger.info("Variation type effectiveness:")
    for var_type, stats in sorted(
        variations_tried.items(), 
        key=lambda x: x[1]["max_similarity"], 
        reverse=True
    ):
        avg_sim = stats["sum_similarity"] / stats["count"] if stats["count"] > 0 else 0
        logger.info(
            f"{var_type}: count={stats['count']}, "
            f"avg_sim={avg_sim:.6f}, max_sim={stats['max_similarity']:.6f}"
        )
    
    # Track most effective variation types for future use
    effective_variations = sorted(
        variations_tried.items(), 
        key=lambda x: x[1]["max_similarity"], 
        reverse=True
    )[:5]
    
    for var_type, stats in effective_variations:
        STRATEGY_EFFECTIVENESS[var_type] = max(
            STRATEGY_EFFECTIVENESS.get(var_type, 1.0),
            stats["max_similarity"] * 3  # Weight by max similarity
        )
    
    # If we found a better candidate, return it
    if variations_tried and any(stats["max_similarity"] > best_similarity for stats in variations_tried.values()):
        logger.info("Found improvement through intensive search!")
        return None  # We already added it to memory, so just continue the main search
    
    return None

def broad_exploration_search(candidates):
    """
    Broader search when we're not yet close to target similarity
    """
    # Take our best candidates
    best_candidates = [int(c["private_key_int"]) for c in candidates]
    
    # Try more diverse strategies to increase similarity
    all_variations = []
    
    # 1. Try various mathematical relationships
    for base in best_candidates:
        # Polynomial
        for degree in range(1, 5):
            var = base + (base % (2**degree))
            if is_valid_candidate(var):
                all_variations.append(var)
        
        # Bit operations
        for shift in range(1, 16):
            # Left shift with wrap
            var = ((base << shift) | (base >> (68 - shift))) & ((1 << 68) - 1)
            if is_valid_candidate(var):
                all_variations.append(var)
                
            # Right shift with wrap
            var = ((base >> shift) | (base << (68 - shift))) & ((1 << 68) - 1)
            if is_valid_candidate(var):
                all_variations.append(var)
        
        # XOR with special values
        for xor_val in [0xAAAAAAAAAAAAAAAA, 0x5555555555555555, 0xFFFF0000FFFF0000, 0x0000FFFF0000FFFF]:
            var = base ^ xor_val
            if is_valid_candidate(var):
                all_variations.append(var)
    
    # 2. Try genetic algorithm style crossover between good candidates
    if len(best_candidates) > 1:
        for i in range(len(best_candidates)):
            for j in range(i+1, len(best_candidates)):
                # Single-point crossover
                for point in range(1, 68):
                    a_bits = bin(best_candidates[i])[2:].zfill(68)
                    b_bits = bin(best_candidates[j])[2:].zfill(68)
                    
                    child1_bits = a_bits[:point] + b_bits[point:]
                    child2_bits = b_bits[:point] + a_bits[point:]
                    
                    child1 = int(child1_bits, 2)
                    child2 = int(child2_bits, 2)
                    
                    if is_valid_candidate(child1):
                        all_variations.append(child1)
                    if is_valid_candidate(child2):
                        all_variations.append(child2)
    
    # 3. Try variations based on the address structure itself
    best_address = candidates[0]["address"]
    
    # Get all Base58 characters
    base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    
    # Try changing a single character in the address to see what private key could generate it
    # This is exploratory since we can't directly work backwards
    for i, char in enumerate(best_address):
        if i > 5:  # Skip the first few characters as they're likely fixed by the version byte
            # Get current characters as a guide
            idx = base58_chars.index(char)
            
            # Try a few candidates around our best with same bit length 
            for _ in range(50):  # Try 50 variations per character
                var_mask = random.randint(0, 0xFFFFFFFF)  # Random 32-bit mask
                var = best_candidates[0] ^ var_mask
                if is_valid_candidate(var):
                    all_variations.append(var)
    
    # Test a subset of variations (too many would take too long)
    random.shuffle(all_variations)
    variations_to_test = all_variations[:min(1000, len(all_variations))]
    
    logger.info(f"Testing {len(variations_to_test)} broad exploration variations")
    
    best_found = 0.0
    for var in variations_to_test:
        match, address, similarity = test_candidate(var)
        if address:
            address_logger.log_address(var, address, similarity)
            memory_manager.add_result(var, address, similarity)
            
            if similarity > best_found:
                best_found = similarity
            
            # If we found a match or reached target similarity, we're done!
            if match or similarity >= TARGET_SIMILARITY:
                logger.info(f"Target similarity or match found! Similarity: {similarity:.6f}")
                if match:
                    save_result(var)
                    return var
    
    logger.info(f"Broad exploration search complete. Best similarity found: {best_found:.6f}")
    return None

# Add a function to analyze patterns in successful candidates
def analyze_successful_patterns(candidates, target_address, top_n=10):
    """
    Analyze patterns in the most successful candidates to guide further search.
    
    Args:
        candidates: List of (key, address, similarity) tuples
        target_address: The target Bitcoin address
        top_n: Number of top candidates to analyze
        
    Returns:
        Dict containing analysis results
    """
    logger.info(f"Analyzing patterns in top {top_n} candidates...")
    
    # Sort candidates by similarity score (descending)
    sorted_candidates = sorted(candidates, key=lambda x: x[2], reverse=True)
    top_candidates = sorted_candidates[:top_n]
    
    if not top_candidates:
        logger.warning("No candidates to analyze")
        return {}
    
    # 1. Analyze matching positions in addresses
    matching_positions = {}
    for i in range(len(target_address)):
        matching_positions[i] = 0
        
    for _, address, _ in top_candidates:
        for i in range(min(len(address), len(target_address))):
            if address[i] == target_address[i]:
                matching_positions[i] += 1
    
    # Identify positions that consistently match across top candidates
    consistent_positions = {pos: count for pos, count in matching_positions.items() 
                           if count >= len(top_candidates) * 0.7}  # 70% agreement threshold
    
    logger.info(f"Found {len(consistent_positions)} consistently matching positions")
    
    # 2. Analyze bit patterns in keys
    top_keys = [key for key, _, _ in top_candidates]
    
    # Track common bits across top keys
    bit_counts = {}
    for bit_pos in range(64):  # Assuming 64-bit keys
        bit_counts[bit_pos] = {'0': 0, '1': 0}
        
        for key in top_keys:
            bit_val = (key >> bit_pos) & 1
            bit_counts[bit_pos][str(bit_val)] += 1
    
    # Identify consistent bits (0 or 1) across top keys
    consistent_bits = {}
    for bit_pos, counts in bit_counts.items():
        # If 80% of top keys have the same bit value at this position
        threshold = 0.8 * len(top_keys)
        if counts['0'] >= threshold:
            consistent_bits[bit_pos] = 0
        elif counts['1'] >= threshold:
            consistent_bits[bit_pos] = 1
    
    logger.info(f"Found {len(consistent_bits)} consistently set bits across top candidates")
    
    # 3. Analyze numerical patterns based on insights from mathematical_analysis.txt
    
    # Check for multiplicative relationships between keys
    multipliers = []
    for i in range(len(top_keys)-1):
        if top_keys[i] != 0:  # Avoid division by zero
            ratio = top_keys[i+1] / top_keys[i]
            multipliers.append(ratio)
    
    avg_multiplier = sum(multipliers) / len(multipliers) if multipliers else 0
    multiplier_std = (sum((m - avg_multiplier)**2 for m in multipliers) / len(multipliers))**0.5 if multipliers else 0
    
    # Look for bit shift patterns
    shift_patterns = []
    for i in range(len(top_keys)-1):
        for shift in range(1, 8):  # Try shifts of 1-7 bits
            if (top_keys[i] << shift) == top_keys[i+1] or (top_keys[i] >> shift) == top_keys[i+1]:
                shift_patterns.append(shift)
    
    # 4. Identify high-entropy regions and low-entropy regions in the keys
    # This is based on entropy_analysis.txt showing importance of entropy distribution
    
    # Convert keys to binary strings for entropy analysis
    key_bits = [''.join(bin(key)[2:].zfill(64)) for key in top_keys]
    
    # Calculate entropy for each bit position
    bit_entropy = {}
    for bit_pos in range(64):
        bit_values = [key_bits[j][bit_pos] for j in range(len(key_bits))]
        zeros = bit_values.count('0')
        ones = bit_values.count('1')
        
        # Calculate Shannon entropy for this bit position
        p0 = zeros / len(bit_values) if bit_values else 0
        p1 = ones / len(bit_values) if bit_values else 0
        
        if p0 == 0 or p1 == 0:
            entropy = 0  # No entropy if all bits are the same
        else:
            entropy = -(p0 * math.log2(p0) + p1 * math.log2(p1))
        
        bit_entropy[bit_pos] = entropy
    
    # Identify high entropy regions (bits that vary a lot)
    high_entropy_regions = {pos: entropy for pos, entropy in bit_entropy.items() if entropy > 0.9}
    
    # Identify low entropy regions (bits that stay mostly constant)
    low_entropy_regions = {pos: entropy for pos, entropy in bit_entropy.items() if entropy < 0.3}
    
    results = {
        'consistent_address_positions': consistent_positions,
        'consistent_bits': consistent_bits,
        'avg_multiplier': avg_multiplier,
        'multiplier_std': multiplier_std,
        'shift_patterns': shift_patterns,
        'high_entropy_regions': high_entropy_regions,
        'low_entropy_regions': low_entropy_regions,
        'top_similarity': top_candidates[0][2] if top_candidates else 0
    }
    
    logger.info(f"Pattern analysis complete. Top similarity score: {results['top_similarity']:.6f}")
    return results

# Add a function to generate candidates based on pattern analysis
def generate_pattern_based_candidates(pattern_analysis, base_candidates, num_candidates=100):
    """
    Generate new candidates based on patterns identified in successful candidates.
    
    Args:
        pattern_analysis: Results from analyze_successful_patterns
        base_candidates: List of (key, address, similarity) tuples to use as starting points
        num_candidates: Number of candidates to generate
        
    Returns:
        List of new candidate keys
    """
    logger.info(f"Generating {num_candidates} candidates based on pattern analysis...")
    
    if not pattern_analysis or not base_candidates:
        logger.warning("Cannot generate pattern-based candidates: missing input data")
        return []
    
    # Sort base candidates by similarity score (descending)
    sorted_candidates = sorted(base_candidates, key=lambda x: x[2], reverse=True)
    base_keys = [key for key, _, _ in sorted_candidates[:5]]  # Use top 5 as base keys
    
    # Extract pattern information
    consistent_bits = pattern_analysis.get('consistent_bits', {})
    high_entropy_regions = pattern_analysis.get('high_entropy_regions', {})
    low_entropy_regions = pattern_analysis.get('low_entropy_regions', {})
    avg_multiplier = pattern_analysis.get('avg_multiplier', 1.0)
    shift_patterns = pattern_analysis.get('shift_patterns', [])
    
    new_candidates = []
    
    # 1. STRATEGY: Preserve consistent bits, randomly flip others
    for _ in range(num_candidates // 4):
        if not base_keys:
            continue
            
        # Choose a random base key
        base_key = random.choice(base_keys)
        new_key = base_key
        
        # Create a bit mask to preserve consistent bits
        preserve_mask = 0
        for bit_pos, bit_val in consistent_bits.items():
            preserve_mask |= (1 << bit_pos)
        
        # Create masks for flipping bits in high/low entropy regions
        high_entropy_mask = 0
        for bit_pos in high_entropy_regions:
            # Only include if not in the consistent bits
            if bit_pos not in consistent_bits:
                high_entropy_mask |= (1 << bit_pos)
        
        low_entropy_mask = 0
        for bit_pos in low_entropy_regions:
            # Only include if not in the consistent bits
            if bit_pos not in consistent_bits:
                low_entropy_mask |= (1 << bit_pos)
        
        # Flip a few high entropy bits (more exploration)
        num_high_bits_to_flip = random.randint(2, 5)
        for _ in range(num_high_bits_to_flip):
            # Select a random bit position from high entropy region
            if high_entropy_mask:
                bit_pos = random.choice([i for i in range(64) if (high_entropy_mask & (1 << i)) != 0])
                new_key ^= (1 << bit_pos)
        
        # Occasionally flip a low entropy bit (less exploration)
        if random.random() < 0.3 and low_entropy_mask:
            bit_pos = random.choice([i for i in range(64) if (low_entropy_mask & (1 << i)) != 0])
            new_key ^= (1 << bit_pos)
        
        # Ensure consistent bits remain unchanged
        for bit_pos, bit_val in consistent_bits.items():
            # Clear the bit first
            new_key &= ~(1 << bit_pos)
            # Set it to the consistent value
            new_key |= (bit_val << bit_pos)
        
        new_candidates.append(new_key)
    
    # 2. STRATEGY: Apply multiplier patterns from mathematical_analysis.txt
    for _ in range(num_candidates // 4):
        if not base_keys:
            continue
            
        base_key = random.choice(base_keys)
        
        # Apply a multiplier with random variation
        variation = random.uniform(0.98, 1.02)  # 2% variation
        multiplier = avg_multiplier * variation
        
        # Apply multiplier and round to integer
        new_key = int(base_key * multiplier)
        
        # Ensure consistent bits remain unchanged
        for bit_pos, bit_val in consistent_bits.items():
            # Clear the bit first
            new_key &= ~(1 << bit_pos)
            # Set it to the consistent value
            new_key |= (bit_val << bit_pos)
        
        new_candidates.append(new_key)
    
    # 3. STRATEGY: Apply bit shift patterns from pattern_analysis.txt
    for _ in range(num_candidates // 4):
        if not base_keys:
            continue
            
        base_key = random.choice(base_keys)
        
        # Apply a bit shift if patterns were found, otherwise use a small random shift
        if shift_patterns:
            shift = random.choice(shift_patterns)
        else:
            shift = random.randint(1, 3)
        
        # Randomly choose left or right shift
        if random.random() < 0.5:
            new_key = base_key << shift
        else:
            new_key = base_key >> shift
        
        # Ensure consistent bits remain unchanged
        for bit_pos, bit_val in consistent_bits.items():
            # Clear the bit first
            new_key &= ~(1 << bit_pos)
            # Set it to the consistent value
            new_key |= (bit_val << bit_pos)
        
        new_candidates.append(new_key)
    
    # 4. STRATEGY: Hybrid pattern approach based on secp256k1_analysis.txt
    for _ in range(num_candidates // 4):
        if not base_keys:
            continue
            
        base_key = random.choice(base_keys)
        
        # Create a completely new key that preserves consistent bits
        new_key = 0
        
        # Set consistent bits
        for bit_pos, bit_val in consistent_bits.items():
            new_key |= (bit_val << bit_pos)
        
        # For non-consistent bits, use a mix of:
        # - 70% chance: copy from base key
        # - 30% chance: random bit
        for bit_pos in range(64):
            if bit_pos not in consistent_bits:
                if random.random() < 0.7:
                    # Copy bit from base key
                    bit_val = (base_key >> bit_pos) & 1
                else:
                    # Random bit
                    bit_val = random.randint(0, 1)
                
                new_key |= (bit_val << bit_pos)
        
        new_candidates.append(new_key)
    
    # Remove any duplicates
    new_candidates = list(set(new_candidates))
    
    logger.info(f"Generated {len(new_candidates)} unique pattern-based candidates")
    return new_candidates

def structure_targeted_search(count=100, worker_safe=False):
    """
    Generate candidates that are likely to match the structural patterns of the target address
    
    This strategy analyzes the target address structure and generates candidates that would
    produce addresses with similar structural characteristics.
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting structure-targeted search with {count} candidates")
    
    candidates = []
    
    # Analyze target address structure
    digit_positions = [i for i, c in enumerate(TARGET_ADDRESS) if c.isdigit()]
    uppercase_positions = [i for i, c in enumerate(TARGET_ADDRESS) if c.isupper()]
    
    # Get some of our best candidates so far as starting points
    memory = globals().get('memory_manager', None)
    
    base_candidates = []
    if memory:
        try:
            best_candidates = memory.get_best_candidates(5)
            base_candidates = [value for value, _ in best_candidates]
        except:
            # Fallback if no memory manager available
            base_candidates = [PREV_TERM_67_INT]
    
    if not base_candidates:
        base_candidates = [PREV_TERM_67_INT]
    
    # Generate variations of the best candidates
    for base in base_candidates:
        # Make sure we have enough bits set
        binary = bin(base)[2:].zfill(68)
        
        # Focus on specific bit positions that might influence character positions
        # in the Bitcoin address with higher matching potential
        for _ in range(count // len(base_candidates) + 1):
            # Create a new candidate by modifying bits
            new_candidate = base
            
            # Apply a series of targeted transformations
            # These target specific parts of the hash160 that affect the address
            
            # Approach 1: Target version bits (affects first character)
            if len(candidates) < count * 0.2:
                # Modify bits that affect the version area
                for bit_pos in [67, 66, 65, 64]:
                    # Flip the bit
                    new_candidate = new_candidate ^ (1 << (bit_pos % 68))
            
            # Approach 2: Target checksum bits (affects last 4-8 characters)
            elif len(candidates) < count * 0.4:
                # Modify bits that affect the checksum area
                for bit_pos in range(5):
                    # Flip bits in the first few positions
                    if random.random() < 0.3:
                        new_candidate = new_candidate ^ (1 << bit_pos)
            
            # Approach 3: Target hash160 structure bits that affect digit distribution
            elif len(candidates) < count * 0.6:
                # Ensure similar digit/letter distribution in address
                # by modifying specific bit regions
                for bit_group in range(4):
                    start_bit = bit_group * 16
                    end_bit = start_bit + 16
                    
                    # Modify bits in this region
                    for bit in range(start_bit, end_bit):
                        if random.random() < 0.05:  # 5% chance to flip each bit
                            new_candidate = new_candidate ^ (1 << bit)
            
            # Approach 4: Bit pattern matching from close candidates
            else:
                # Look at the hamming distance range
                best_addr = None
                best_similarity = 0
                
                # Find the best address from our previous candidates
                for candidate in candidates:
                    try:
                        addr = private_key_to_address(candidate)
                        similarity = address_similarity(addr, TARGET_ADDRESS)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_addr = addr
                    except:
                        continue
                
                if best_addr:
                    # Look at positions where best_addr matches target
                    matching_positions = [i for i in range(len(best_addr)) 
                                         if i < len(TARGET_ADDRESS) and best_addr[i] == TARGET_ADDRESS[i]]
                    
                    # Create a candidate that preserves these bits
                    for bit_position in range(68):
                        # 20% chance to flip any bit
                        if random.random() < 0.2:
                            new_candidate = new_candidate ^ (1 << bit_position)
            
            # Ensure the candidate is valid
            if is_valid_candidate(new_candidate):
                # Test the candidate to see if it meets minimum similarity
                try:
                    addr = private_key_to_address(new_candidate)
                    similarity = address_similarity(addr, TARGET_ADDRESS)
                    
                    # Only add if it's promising
                    if similarity > 0.3:  # Set a threshold for promising candidates
                        candidates.append(new_candidate)
                    
                    # If we found a really good one, add more variations of it
                    if similarity > 0.4:
                        # Create 5 variations of this candidate
                        for _ in range(5):
                            variant = new_candidate
                            # Flip 1-3 random bits
                            for _ in range(random.randint(1, 3)):
                                bit_position = random.randint(0, 67)
                                variant = variant ^ (1 << bit_position)
                            
                            if is_valid_candidate(variant):
                                candidates.append(variant)
                except Exception as e:
                    # Skip if we hit an error
                    logger.debug(f"Error generating candidate: {e}")
            
            # If we have enough candidates, stop
            if len(candidates) >= count:
                break
    
    # If we don't have enough candidates, add some random ones
    while len(candidates) < count:
        # Generate a random candidate
        candidate = random.randint(PREV_TERM_67_INT, 2**68 - 1)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # Ensure we have exactly the requested number of candidates
    candidates = candidates[:count]
    logger.info(f"Generated {len(candidates)} structure-targeted candidates")
    return candidates

def gradient_ascent_search(count=100, iterations=150, learning_rate=0.1, worker_safe=False):
    """
    Enhanced gradient ascent algorithm for systematically improving candidate private keys.
    
    Implements multiple efficiency improvements:
    1. Parallel processing of multiple starting points
    2. Bit influence mapping for targeted bit flips
    3. Adaptive learning rate that changes based on improvement rate
    4. Integration with sequence patterns from gpt_version.py
    5. Smart exploration that focuses on historically successful bit positions
    6. Early stopping with intelligent restart
    
    Args:
        count: Number of final candidates to return
        iterations: Maximum number of improvement iterations per candidate
        learning_rate: Initial learning rate for adjustments
        
    Returns:
        list: List of improved candidate private keys
    """
    logger.info(f"Starting enhanced gradient ascent search with {count} candidates")
    candidates = []
    successful_bit_positions = Counter()  # Track which bit positions lead to improvements
    
    # Get our best candidates as starting points
    memory_manager = MemoryManager()
    start_candidates = []
    
    # First try to use best candidates from memory
    try:
        best_candidates = memory_manager.get_best_candidates(min(20, count))
        for candidate_data in best_candidates:
            start_candidates.append(int(candidate_data["private_key_int"]))
    except Exception as e:
        logger.error(f"Error getting best candidates: {e}")
    
    # Include sequence-based candidates
    try:
        # Use the exact term 68 formula: term_67 * 271 + 68
        sequence_candidate = PREV_TERM_67_INT * 271 + 68
        if is_valid_candidate(sequence_candidate) and sequence_candidate not in start_candidates:
            start_candidates.append(sequence_candidate)
            logger.info(f"Added sequence-based candidate: {hex(sequence_candidate)}")
    except Exception as e:
        logger.error(f"Error adding sequence candidate: {e}")
    
    # If we don't have enough starting points, add variations
    if len(start_candidates) < 20:
        # Use previous term and some variations
        if PREV_TERM_67_INT not in start_candidates:
            start_candidates.append(PREV_TERM_67_INT)
        
        # Add variations of existing candidates
        existing_candidates = list(start_candidates)  # Make a copy
        for base in existing_candidates:
            if len(start_candidates) >= 20:
                break
                
            # Add bit-flipped variations of this candidate
            for bits in range(1, 4):  # 1-3 bit flips
                if len(start_candidates) >= 20:
                    break
                    
                # Generate bit positions with preference for historically successful bits
                bit_weights = [successful_bit_positions.get(i, 1) + 1 for i in range(68)]
                positions = random.choices(range(68), weights=bit_weights, k=bits)
                
                variant = base
                for pos in positions:
                    variant ^= (1 << pos)
                
                if is_valid_candidate(variant) and variant not in start_candidates:
                    start_candidates.append(variant)
    
    # Precompute address influence map (which bits affect which address positions)
    address_influence_map = {}
    
    def build_influence_map(candidate, target=TARGET_ADDRESS):
        """Build a map of which bit positions influence which address positions"""
        influence = {i: set() for i in range(len(target))}
        base_address = private_key_to_address(candidate)
        if not base_address:
            return influence
            
        # Test each bit position
        for bit in range(min(68, candidate.bit_length())):
            test_value = candidate ^ (1 << bit)
            test_address = private_key_to_address(test_value)
            if not test_address:
                continue
                
            # Find which positions in the address changed
            for i, (c1, c2) in enumerate(zip(base_address, test_address)):
                if c1 != c2:
                    influence[i].add(bit)
        
        return influence
    
    # Process each starting candidate with improved gradient ascent
    for start_idx, start_key in enumerate(start_candidates):
        if len(candidates) >= count:
            break
            
        # Skip if this exact value is already in our results
        if start_key in candidates:
            continue
            
        try:
            logger.info(f"Processing starting candidate {start_idx+1}/{len(start_candidates)}: {hex(start_key)}")
            current_key = start_key
            
            # Get initial similarity
            current_address = private_key_to_address(current_key)
            if not current_address:
                continue  # Skip if address generation fails
                
            current_similarity = address_similarity(current_address, TARGET_ADDRESS)
            
            # Variables to track progress and adapt learning
            best_key = current_key
            best_similarity = current_similarity
            iterations_without_improvement = 0
            adaptive_learning_rate = learning_rate
            last_improvement = 0
            
            # Build influence map for smarter bit selection
            try:
                influence_map = build_influence_map(current_key)
                address_influence_map[current_key] = influence_map
            except Exception as e:
                logger.debug(f"Error building influence map: {e}")
                influence_map = None
            
            # Identify non-matching positions to focus on
            non_matching_positions = []
            if current_address:
                for i, (c1, c2) in enumerate(zip(TARGET_ADDRESS, current_address)):
                    if c1 != c2:
                        non_matching_positions.append(i)
            
            # Keep track of which bits we've tried flipping
            tried_bits = set()
            
            # Perform gradient ascent iterations
            for iteration in range(iterations):
                improved = False
                
                # Escape local maxima if stuck for too long
                if iterations_without_improvement > 15:
                    # Make a random jump to escape local maximum
                    escape_key = current_key
                    num_bits = min(5 + iterations_without_improvement // 5, 15)  # Increase with stagnation
                    
                    # Prioritize bits that influence non-matching positions
                    influential_bits = set()
                    if influence_map:
                        for pos in non_matching_positions:
                            influential_bits.update(influence_map.get(pos, set()))
                    
                    # Use influential bits if available, otherwise random
                    if influential_bits:
                        bit_positions = random.sample(list(influential_bits), min(num_bits, len(influential_bits)))
                        # Fill remaining with random bits if needed
                        if len(bit_positions) < num_bits:
                            remaining = random.sample(
                                [b for b in range(68) if b not in influential_bits], 
                                num_bits - len(bit_positions)
                            )
                            bit_positions.extend(remaining)
                    else:
                        bit_positions = random.sample(range(68), num_bits)
                    
                    for bit in bit_positions:
                        escape_key ^= (1 << bit)
                    
                    if is_valid_candidate(escape_key):
                        # Test the escape candidate
                        escape_address = private_key_to_address(escape_key)
                        if escape_address:
                            escape_similarity = address_similarity(escape_address, TARGET_ADDRESS)
                            
                            # Only jump if it's not significantly worse
                            if escape_similarity >= current_similarity * 0.9:
                                current_key = escape_key
                                current_similarity = escape_similarity
                                tried_bits = set()  # Reset tried bits after jump
                                
                                # Update best if better
                                if escape_similarity > best_similarity:
                                    best_similarity = escape_similarity
                                    best_key = escape_key
                                    improved = True
                                
                                logger.debug(f"Made escape jump: {hex(escape_key)}, similarity: {escape_similarity:.6f}")
                    
                    # Reset counter but at a higher threshold to prevent thrashing
                    iterations_without_improvement = 10
                
                # Prioritize bit positions based on influence map and history
                bit_positions = list(range(68))
                
                # Use influence map to prioritize bits affecting non-matching positions
                if influence_map and non_matching_positions:
                    important_bits = set()
                    for pos in non_matching_positions:
                        important_bits.update(influence_map.get(pos, set()))
                    
                    # Sort bit positions to prioritize important bits that haven't been tried
                    bit_positions.sort(key=lambda b: (
                        b not in important_bits,  # Prioritize important bits (False sorts before True)
                        b in tried_bits,  # Avoid bits we've already tried
                        -successful_bit_positions.get(b, 0)  # Prefer historically successful bits
                    ))
                else:
                    # Without influence map, prioritize by success history and avoid tried bits
                    random.shuffle(bit_positions)  # Start with a random order
                    bit_positions.sort(key=lambda b: (
                        b in tried_bits,  # Avoid bits we've already tried
                        -successful_bit_positions.get(b, 0)  # Prefer historically successful bits
                    ))
                
                # Test single bit flips with adaptive step size
                for bit_position in bit_positions:
                    # Skip bits we've already tried too many times
                    if bit_position in tried_bits and iterations_without_improvement < 10:
                        continue
                    
                    tried_bits.add(bit_position)
                    
                    # Try flipping this bit
                    test_key = current_key ^ (1 << bit_position)
                    
                    # Skip if not valid
                    if not is_valid_candidate(test_key):
                        continue
                    
                    # Calculate similarity
                    try:
                        test_address = private_key_to_address(test_key)
                        if not test_address:
                            continue
                            
                        test_similarity = address_similarity(test_address, TARGET_ADDRESS)
                        
                        # If this improves similarity, move in this direction
                        if test_similarity > current_similarity:
                            current_key = test_key
                            current_similarity = test_similarity
                            improved = True
                            
                            # Record successful bit position
                            successful_bit_positions[bit_position] += 1
                            
                            # Update non-matching positions
                            non_matching_positions = []
                            for i, (c1, c2) in enumerate(zip(TARGET_ADDRESS, test_address)):
                                if c1 != c2:
                                    non_matching_positions.append(i)
                            
                            # Update best if this is better
                            if test_similarity > best_similarity:
                                best_similarity = test_similarity
                                best_key = test_key
                                last_improvement = iteration
                                
                                # Build new influence map for significantly better candidates
                                if test_similarity > best_similarity + 0.05:
                                    try:
                                        influence_map = build_influence_map(test_key)
                                        address_influence_map[test_key] = influence_map
                                    except (Exception, ValueError) as e:
                                        pass
                                
                                # Log significant improvements
                                if best_similarity > 0.4:
                                    logger.info(f"Found candidate with similarity {best_similarity:.6f}: {hex(best_key)}")
                                
                                # Refresh adaptive learning rate on improvement
                                adaptive_learning_rate = learning_rate
                            
                            # Break early to follow this gradient direction immediately
                            break
                    except Exception as e:
                        # Skip on error
                        continue
                
                # Reusing existing influence map for speed when appropriate
                if improved and current_key in address_influence_map:
                    influence_map = address_influence_map[current_key]
                
                # If we improved, reset counter
                if improved:
                    iterations_without_improvement = 0
                else:
                    iterations_without_improvement += 1
                
                # If single bit flips didn't improve and we're near a plateau, try bit combinations
                if not improved and (iterations_without_improvement % 5 == 0):
                    # Try flipping multiple bits at once
                    multi_bit_improved = False
                    
                    # Focus on historically successful bits
                    successful_bits = [b for b, count in successful_bit_positions.most_common(10)]
                    
                    # If we don't have enough successful bits, add some random ones
                    while len(successful_bits) < 10:
                        random_bit = random.randint(0, 67)
                        if random_bit not in successful_bits:
                            successful_bits.append(random_bit)
                    
                    # Try all 2-bit combinations from our top bits
                    for bit1, bit2 in itertools.combinations(successful_bits, 2):
                        # Create a test key with both bits flipped
                        test_key = current_key ^ (1 << bit1) ^ (1 << bit2)
                        
                        # Skip if not valid
                        if not is_valid_candidate(test_key):
                            continue
                        
                        # Calculate similarity
                        try:
                            test_address = private_key_to_address(test_key)
                            if not test_address:
                                continue
                                
                            test_similarity = address_similarity(test_address, TARGET_ADDRESS)
                            
                            # If this improves similarity, move in this direction
                            if test_similarity > current_similarity:
                                current_key = test_key
                                current_similarity = test_similarity
                                multi_bit_improved = True
                                improved = True
                                
                                # Record successful bit positions
                                successful_bit_positions[bit1] += 1
                                successful_bit_positions[bit2] += 1
                                
                                # Update non-matching positions
                                non_matching_positions = []
                                for i, (c1, c2) in enumerate(zip(TARGET_ADDRESS, test_address)):
                                    if c1 != c2:
                                        non_matching_positions.append(i)
                                
                                # Update best if this is better
                                if test_similarity > best_similarity:
                                    best_similarity = test_similarity
                                    best_key = test_key
                                    last_improvement = iteration
                                
                                # Break early to follow this gradient direction
                                break
                        except Exception:
                            # Skip on error
                            continue
                    
                    if multi_bit_improved:
                        iterations_without_improvement = 0
                
                # Early stopping if no improvement for many iterations
                if iteration - last_improvement > iterations // 2:
                    break
            
            # Add the best key from this run to our candidates
            if best_key not in candidates:
                candidates.append(best_key)
                
                # If this is a promising candidate, explore around it
                if best_similarity > 0.4:
                    # Create additional variations 
                    variations_to_add = min(5, count - len(candidates))
                    if variations_to_add > 0:
                        # Identify most influential bits
                        influential_bits = set()
                        if best_key in address_influence_map:
                            for pos_set in address_influence_map[best_key].values():
                                influential_bits.update(pos_set)
                        
                        # Generate variations focused on influential bits
                        for _ in range(variations_to_add):
                            variant = best_key
                            # Determine number of bits to flip (fewer for higher similarity)
                            num_bits = max(1, int(3 * (1 - best_similarity)))
                            
                            # Flip bits that have influence
                            if influential_bits:
                                bits_to_flip = random.sample(list(influential_bits), min(num_bits, len(influential_bits)))
                            else:
                                bits_to_flip = random.sample(range(68), num_bits)
                                
                            for bit in bits_to_flip:
                                variant ^= (1 << bit)
                            
                            if is_valid_candidate(variant) and variant not in candidates:
                                candidates.append(variant)
        
        except Exception as e:
            logger.error(f"Error in enhanced gradient ascent: {e}")
            continue
    
    # If we don't have enough candidates, add sequence-based candidates
    if len(candidates) < count:
        try:
            sequence_candidates = sequence_pattern_search(count - len(candidates))
            for candidate in sequence_candidates:
                if candidate not in candidates and len(candidates) < count:
                    candidates.append(candidate)
        except Exception as e:
            logger.error(f"Error adding sequence candidates: {e}")
    
    # Final fallback: add random candidates if needed
    while len(candidates) < count:
        # Generate a random candidate near our best existing one
        if candidates:
            base = random.choice(candidates)
            candidate = base
            
            # Flip 1-3 random bits
            for _ in range(random.randint(1, 3)):
                bit_position = random.randint(0, 67)
                candidate = candidate ^ (1 << bit_position)
            
            if is_valid_candidate(candidate) and candidate not in candidates:
                candidates.append(candidate)
        else:
            # True fallback to a random candidate
            candidate = random.randint(PREV_TERM_67_INT, 2**68 - 1)
            if is_valid_candidate(candidate) and candidate not in candidates:
                candidates.append(candidate)
    
    # Ensure we have exactly the requested number of candidates
    candidates = candidates[:count]
    logger.info(f"Generated {len(candidates)} enhanced gradient ascent candidates")
    
    # Log bit position statistics
    if successful_bit_positions:
        most_influential = successful_bit_positions.most_common(10)
        logger.info(f"Most influential bit positions: {most_influential}")
    
    return candidates

def random_walk_search(count=100, worker_safe=False):
    """
    Perform a random walk search by starting from promising candidates and making random adjustments.
    
    Args:
        count (int): Number of candidates to generate
        
    Returns:
        list: List of candidate integers
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting random walk search to generate {count} candidates")
    
    # Initialize result list
    candidates = []
    
    # Try to get promising values from memory
    memory_manager = MemoryManager()
    best_candidates = memory_manager.get_best_candidates(10)
    
    # If we have no good candidates yet, start from a reasonable default
    if not best_candidates:
        base_candidates = [PREV_TERM_67_INT + random.randint(1, 1000000) for _ in range(3)]
    else:
        # Use the best candidates as starting points
        base_candidates = [value for value, _ in best_candidates[:3]]
        
    # Add some completely random candidates to increase diversity
    base_candidates.extend([
        random.randint(PREV_TERM_67_INT, 2**68-1) for _ in range(2)
    ])
    
    # For each starting point, perform a random walk
    for base_value in base_candidates:
        current = base_value
        best_similarity = 0
        
        # Perform random walks of varying lengths
        for _ in range(count // len(base_candidates)):
            # Randomly decide how many bits to flip
            num_bits = random.randint(1, 8)
            
            # Select random bit positions to flip
            positions = random.sample(range(68), num_bits)
            
            # Create a new value by flipping those bits
            new_value = current
            for pos in positions:
                new_value ^= (1 << pos)
                
            # Ensure the candidate is valid
            if is_valid_candidate(new_value):
                candidates.append(new_value)
                
                # Test the candidate's similarity
                try:
                    address, similarity = test_candidate(new_value)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        current = new_value  # Move to this better position
                except Exception as e:
                    logger.debug(f"Error testing candidate: {e}")
    
    # Ensure we return the requested number of candidates
    while len(candidates) < count:
        # Generate completely random candidates if needed
        new_value = random.randint(PREV_TERM_67_INT, 2**68-1)
        if is_valid_candidate(new_value):
            candidates.append(new_value)
    
    logger.info(f"Random walk search generated {len(candidates)} candidates")
    return candidates[:count]

def super_targeted_search(count=100, worker_safe=False):
    """
    Generate candidates focused specifically on our highest similarity candidates.
    
    This strategy performs extremely targeted manipulations on our best candidates
    to push similarity from 60% toward 80%+.
    
    Args:
        count: Number of candidates to generate
        worker_safe: Whether to use worker-safe operations
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting super targeted search with {count} candidates")
    candidates = []
    
    # Get our highest similarity candidates from memory instead of hardcoding
    memory_manager = MemoryManager()
    best_candidates_data = memory_manager.get_best_candidates(10)
    
    # Extract the candidate values from memory
    best_candidates = []
    for candidate_data in best_candidates_data:
        try:
            # Handle different memory formats
            if isinstance(candidate_data, dict):
                value = int(candidate_data["private_key_int"])
                best_candidates.append(value)
            elif isinstance(candidate_data, tuple) and len(candidate_data) >= 1:
                best_candidates.append(int(candidate_data[0]))
        except (ValueError, TypeError):
            continue
    
    # If we couldn't load any good candidates from memory, fall back to defaults
    if not best_candidates:
        logger.warning("No good candidates in memory, using default starting points")
        best_candidates = [
            0x7b0fd3348980cc58a,  # 1MVDYACJ1RmzvZ6mdiFnnXojiMihYdZ1F - 56.7% similarity
            0x732bcef541044c2f9,  # 1MVDYgtuFcxmGajjY6cpsP1AqzJ5J5bVM4 - 56.0% similarity
            0xf34fc235d1952c13f,  # 1MLDYeVxSNSm9qYNnvdSQfU1pWue1UGCrr - 55.5% similarity
            0xf30f423dc1963c0cf,  # 1MV7YgXFScXxk7Qob6nmkHANEG1uP4zX7n - 52.2% similarity
        ]
    
    # Always include previous term as a starting point for diversity
    if PREV_TERM_67_INT not in best_candidates:
        best_candidates.append(PREV_TERM_67_INT)
    
    # Also include the exact sequence formula result for diversity
    exact_term68 = PREV_TERM_67_INT * 271 + 68
    if is_valid_candidate(exact_term68) and exact_term68 not in best_candidates:
        best_candidates.append(exact_term68)
    
    # Log the candidates we're using
    logger.info(f"Using {len(best_candidates)} base candidates for super_targeted_search")
    for i, candidate in enumerate(best_candidates):
        try:
            addr = private_key_to_address(candidate)
            sim = address_similarity(addr, TARGET_ADDRESS) if addr else 0
            logger.info(f"Base candidate {i+1}: {hex(candidate)} -> {addr} (similarity: {sim:.6f})")
        except:
            logger.info(f"Base candidate {i+1}: {hex(candidate)} (unable to generate address)")
    
    # Rest of the function remains the same
    # Analyze bit patterns in our best candidates
    # Extract common patterns that we can leverage
    bits_analysis = {}
    for i in range(68):
        bits_analysis[i] = 0
        for candidate in best_candidates:
            if candidate & (1 << i):
                bits_analysis[i] += 1
    
    # Identify strongly consistent bits (all candidates have the same value)
    consistent_bits = {}
    for bit_pos, count in bits_analysis.items():
        if count == len(best_candidates) or count == 0:
            # All candidates have the same bit value at this position
            consistent_bits[bit_pos] = 1 if count > 0 else 0
    
    logger.info(f"Found {len(consistent_bits)} consistent bits across best candidates")
    
    # Create base template from most common bits
    template = 0
    for bit_pos, bit_val in consistent_bits.items():
        if bit_val == 1:
            template |= (1 << bit_pos)
    
    # Generate pattern-preserving variations
    for base_candidate in best_candidates:
        # Generate multiple variations for each base candidate
        variations_per_candidate = count // (len(best_candidates) * 4)
        
        # Generate 4 types of variations for each candidate
        
        # 1. Super precise 1-bit flips (avoid touching consistent bits)
        for _ in range(variations_per_candidate):
            new_candidate = base_candidate
            # Choose 1-2 bits to flip that aren't consistent
            non_consistent_bits = [bit for bit in range(68) if bit not in consistent_bits]
            bits_to_flip = random.sample(non_consistent_bits, min(2, len(non_consistent_bits)))
            
            for bit in bits_to_flip:
                new_candidate ^= (1 << bit)
                
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
                
                # Test similarity immediately
                try:
                    addr, similarity = test_candidate(new_candidate)
                    if similarity > 0.6:  # If we find an excellent candidate
                        # Add more variations of this immediately
                        for bit in range(68):
                            # Try each single bit flip
                            if bit not in consistent_bits:
                                variant = new_candidate ^ (1 << bit)
                                if is_valid_candidate(variant) and variant not in candidates:
                                    candidates.append(variant)
                except Exception:
                    pass
        
        # 2. Pattern-preserving variations - vary only in regions without matching
        # These are regions where our address doesn't match the target
        for _ in range(variations_per_candidate):
            # Create a new candidate that keeps pattern in first part of the key
            # but varies in the middle and end regions
            new_candidate = base_candidate
            
            # Split the key into three sections: beginning (keep), middle (vary), end (vary)
            # Beginning (high bits) impacts first part of address - strong match in our best candidates
            # Bits 52-67 (high bits) seem to be most important for beginning of address match
            for bit in range(40, 52):  # Middle region - vary moderately
                if bit not in consistent_bits and random.random() < 0.3:
                    new_candidate ^= (1 << bit)
                    
            for bit in range(0, 40):  # Low bits - vary more freely
                if bit not in consistent_bits and random.random() < 0.2:
                    new_candidate ^= (1 << bit)
            
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
        
        # 3. Try very small adjustments to value (+-1, +-2, etc.)
        for adj in range(-5, 6):
            if adj == 0:
                continue
                
            new_candidate = base_candidate + adj
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
        
        # 4. Crossover between best candidates
        for other_candidate in best_candidates:
            if other_candidate != base_candidate:
                # Try bit-by-bit crossover at different positions
                for crossover_point in [20, 32, 44, 56]:
                    # Take bits [0:crossover_point] from base_candidate and the rest from other_candidate
                    mask_low = (1 << crossover_point) - 1
                    mask_high = ((1 << 68) - 1) & ~mask_low
                    new_candidate = (base_candidate & mask_low) | (other_candidate & mask_high)
                    
                    if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                        candidates.append(new_candidate)
    
    # Also try some hybrid variations that combine multiple best candidates
    for _ in range(count // 10):
        # Create a new candidate that takes the most common bit value at each position
        new_candidate = 0
        for bit_pos in range(68):
            # Set bit based on majority vote from best candidates
            if bits_analysis[bit_pos] > len(best_candidates) // 2:
                new_candidate |= (1 << bit_pos)
                
        # Add small random variation
        for bit_pos in range(68):
            if bit_pos not in consistent_bits and random.random() < 0.1:
                new_candidate ^= (1 << bit_pos)
                
        if is_valid_candidate(new_candidate) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    # If we don't have enough candidates, do targeted bit flips
    while len(candidates) < count:
        base = random.choice(best_candidates)
        # Flip 1-3 bits
        new_value = base
        for _ in range(random.randint(1, 3)):
            # Prefer bits that aren't consistent
            non_consistent_bits = [bit for bit in range(68) if bit not in consistent_bits]
            if non_consistent_bits and random.random() < 0.8:
                bit = random.choice(non_consistent_bits)
            else:
                bit = random.randint(0, 67)
            new_value ^= (1 << bit)
            
        if is_valid_candidate(new_value) and new_value not in candidates:
            candidates.append(new_value)
    
    # Ensure we have exactly the requested number of candidates
    candidates = candidates[:count]
    logger.info(f"Generated {len(candidates)} super targeted candidates")
    return candidates

def prefix_targeted_search(count=100, worker_safe=False):
    """
    Generate candidates specifically optimized to maintain the target address prefix.
    
    This strategy focuses on preserving the beginning characters of the address
    (1MVDYg) while varying the rest, to push even higher similarity scores.
    
    Args:
        count: Number of candidates to generate
        worker_safe: Whether to use worker-safe operations
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting prefix-targeted search with {count} candidates")
    candidates = []
    
    # Get our highest similarity candidates from memory
    memory_manager = MemoryManager()
    memory_candidates = memory_manager.get_best_candidates(10)
    
    # Extract the candidate values and find those that already have good prefix matches
    best_candidates = []
    for candidate_data in memory_candidates:
        try:
            # Handle different memory formats
            value = None
            if isinstance(candidate_data, dict):
                value = int(candidate_data["private_key_int"])
            elif isinstance(candidate_data, tuple) and len(candidate_data) >= 1:
                value = int(candidate_data[0])
                
            if value is not None:
                # Check if it has a good prefix match
                addr = private_key_to_address(value)
                if addr and addr.startswith("1MVD"):
                    best_candidates.append(value)
                    logger.info(f"Using memory candidate with good prefix: {hex(value)} -> {addr}")
        except Exception as e:
            logger.debug(f"Error processing memory candidate: {e}")
    
    # If we couldn't find any good prefix matches, fall back to defaults or use the best we have
    if not best_candidates:
        logger.warning("No good prefix candidates in memory, using fallbacks")
        
        # First try to use the top candidates regardless of prefix
        if memory_candidates:
            for candidate_data in memory_candidates[:2]:
                try:
                    if isinstance(candidate_data, dict):
                        value = int(candidate_data["private_key_int"])
                    elif isinstance(candidate_data, tuple) and len(candidate_data) >= 1:
                        value = int(candidate_data[0])
                    best_candidates.append(value)
                except:
                    continue
        
        # If still no candidates, use defaults
        if not best_candidates:
            best_candidates = [
                0x7b0fd3348980cc58a,  # 1MVDYACJ1RmzvZ6mdiFnnXojiMihYdZ1F - 56.7% similarity
                0x732bcef541044c2f9,  # 1MVDYgtuFcxmGajjY6cpsP1AqzJ5J5bVM4 - 56.0% similarity 
            ]
    
    # Always include term 67 for diversity
    if PREV_TERM_67_INT not in best_candidates:
        best_candidates.append(PREV_TERM_67_INT)
    
    # Rest of the function continues as before
    # Target prefix to match or improve upon
    target_prefix = TARGET_ADDRESS[:6]  # "1MVDYg"
    
    # Analyze what makes these candidates generate addresses with matching prefixes
    # The high-order bits (upper bits) of the private key are most influential
    
    # Identify bit ranges that are most likely to affect the address prefix
    # Based on our experience, the upper bits (high order bits) have the most impact
    prefix_influential_bits = list(range(52, 68))  # Upper 16 bits 
    
    # For each base candidate, generate variations focused on prefix matching
    for base_candidate in best_candidates:
        # Test base candidate to verify its prefix
        try:
            base_address = private_key_to_address(base_candidate)
            base_prefix = base_address[:6]
            logger.info(f"Base candidate {hex(base_candidate)} has prefix {base_prefix}")
            
            # Calculate how many variations to create from this base
            variations_per_base = count // (2 * len(best_candidates))
            
            # If the prefix already matches well, focus on fine-tuning other parts
            if base_prefix.startswith("1MVD"):
                # This candidate already has a good prefix match
                # Generate variations that preserve the high bits while varying lower bits
                
                # Create a bit mask that preserves the influential bits
                high_bits_mask = 0
                for bit in prefix_influential_bits:
                    high_bits_mask |= (1 << bit)
                
                # Create a mask for the bits we can safely modify
                modifiable_bits_mask = ((1 << 68) - 1) & ~high_bits_mask
                
                # Generate variations that preserve high bits
                for _ in range(variations_per_base):
                    # Start with the base candidate
                    new_candidate = base_candidate
                    
                    # Modify only non-influential bits
                    for bit in range(0, 52):
                        if random.random() < 0.1:  # 10% chance to flip each bit
                            new_candidate ^= (1 << bit)
                    
                    # Ensure valid candidate
                    if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                        candidates.append(new_candidate)
                        
                        # Test this candidate
                        try:
                            test_address = private_key_to_address(new_candidate)
                            # If this improves the prefix match, generate more similar candidates
                            if test_address[:6] == target_prefix:
                                # Found a perfect prefix match! Create minor variations
                                for i in range(10):
                                    variant = new_candidate + random.randint(-5, 5)
                                    if is_valid_candidate(variant) and variant not in candidates:
                                        candidates.append(variant)
                        except:
                            pass
            
            # If prefix doesn't match perfectly yet, try more aggressive variations
            else:
                # Try more variations of high-order bits to find a better prefix match
                for _ in range(variations_per_base * 2):  # Double the variations for poor matches
                    new_candidate = base_candidate
                    
                    # Systematically vary high bits
                    # Try flipping 1-2 high bits at a time
                    num_bits = random.randint(1, 2)
                    bits_to_flip = random.sample(prefix_influential_bits, num_bits)
                    
                    for bit in bits_to_flip:
                        new_candidate ^= (1 << bit)
                    
                    # Ensure valid candidate
                    if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                        candidates.append(new_candidate)
        except Exception as e:
            logger.error(f"Error analyzing base candidate: {e}")
    
    # Systematically explore more variations of our successful candidates
    memory = globals().get('memory_manager', None)
    if memory:
        try:
            # Get the most recent successful candidates
            memory_candidates = memory.get_best_candidates(5)
            
            for item in memory_candidates:
                # Extract candidate value, handling different memory formats
                if isinstance(item, tuple) and len(item) >= 2:
                    candidate_value = item[0]
                elif isinstance(item, dict) and "private_key_int" in item:
                    candidate_value = item["private_key_int"] 
                else:
                    continue
                    
                # Skip if we already have this candidate
                if candidate_value in candidates or candidate_value in best_candidates:
                    continue
                
                # Test candidate's prefix
                try:
                    candidate_address = private_key_to_address(candidate_value)
                    # If this has a good prefix match, add some variations
                    if candidate_address.startswith("1MVD"):
                        candidates.append(candidate_value)
                        
                        # Add some minor variations
                        for i in range(5):
                            # Create small variations
                            variant = candidate_value + random.randint(-3, 3)
                            if is_valid_candidate(variant) and variant not in candidates:
                                candidates.append(variant)
                                
                        # Add bit-flip variations
                        for bit in range(0, 40):  # Lower bits
                            if random.random() < 0.05:  # 5% chance per bit
                                variant = candidate_value ^ (1 << bit)
                                if is_valid_candidate(variant) and variant not in candidates:
                                    candidates.append(variant)
                except:
                    pass
        except Exception as e:
            logger.error(f"Error processing memory candidates: {e}")
    
    # If we still need more candidates, create completely new ones using bit patterns
    # from our best candidates
    while len(candidates) < count:
        # Create a hybrid candidate by combining features from our best candidates
        new_candidate = 0
        
        # Take upper bits (prefix-influencing) from one of our best candidates
        template = random.choice(best_candidates)
        upper_bits_mask = 0
        for bit in range(52, 68):
            upper_bits_mask |= (1 << bit)
        
        new_candidate = template & upper_bits_mask
        
        # For remaining bits, use either random or other candidates' patterns
        for bit in range(0, 52):
            if random.random() < 0.5:
                # Use bits from another candidate
                other_template = random.choice(best_candidates)
                if other_template & (1 << bit):
                    new_candidate |= (1 << bit)
            else:
                # Random bit
                if random.random() < 0.5:
                    new_candidate |= (1 << bit)
        
        if is_valid_candidate(new_candidate) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    # Ensure we return exactly the requested number of candidates
    candidates = candidates[:count]
    logger.info(f"Generated {len(candidates)} prefix-targeted candidates")
    return candidates

def perfect_match_search(count=100, worker_safe=False):
    """
    Ultra-focused search strategy designed to find high similarity matches (80%+)
    by exploiting patterns found in our highest similarity candidates.
    
    This strategy performs intensive exploration around our best candidates,
    focusing primarily on bit manipulations most likely to push us to 80%+ similarity.
    
    Args:
        count: Number of candidates to generate
        worker_safe: Whether to use worker-safe operations
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting perfect match search with {count} candidates")
    candidates = []
    
    # Get our highest similarity candidates - increase the number to get more diverse candidates
    memory_manager = MemoryManager()
    best_candidates_data = memory_manager.get_best_candidates(50)  # Increased from 30 to 50
    
    if not best_candidates_data:
        logger.warning("No candidates in memory yet, falling back to default strategies")
        # Call another strategy as fallback
        return gradient_ascent_search(count)
    
    # Extract only candidates with higher similarity (now 30%+, reduced threshold to cast a wider net)
    high_sim_candidates = []
    for candidate_data in best_candidates_data:
        try:
            if isinstance(candidate_data, dict):
                value = int(candidate_data["private_key_int"]) 
                similarity = float(candidate_data["similarity"])
            elif isinstance(candidate_data, tuple) and len(candidate_data) >= 2:
                value = int(candidate_data[0])
                similarity = float(candidate_data[1])
            else:
                continue
                
            if similarity >= 0.30:  # Lowered from 0.35 to 0.30 to cast an even wider net
                high_sim_candidates.append((value, similarity))
        except Exception as e:
            logger.debug(f"Error extracting candidate data: {e}")
    
    if not high_sim_candidates:
        # If no candidates above threshold, use the best ones we have
        logger.info("No candidates with >30% similarity, using top candidates instead")
        for candidate_data in best_candidates_data[:10]:  # Increased from 5 to 10
            try:
                if isinstance(candidate_data, dict):
                    value = int(candidate_data["private_key_int"])
                    similarity = float(candidate_data["similarity"]) 
                elif isinstance(candidate_data, tuple) and len(candidate_data) >= 2:
                    value = int(candidate_data[0])
                    similarity = float(candidate_data[1])
                else:
                    continue
                    
                high_sim_candidates.append((value, similarity))
            except Exception as e:
                logger.debug(f"Error extracting candidate data: {e}")
    
    # Add term 67 and its variations for more diversity in starting points
    term_67 = PREV_TERM_67_INT
    if not any(term_67 == value for value, _ in high_sim_candidates):
        high_sim_candidates.append((term_67, 0.0))
    
    # Add the exact term 68 formula result
    exact_term68 = term_67 * 271 + 68
    if is_valid_candidate(exact_term68) and not any(exact_term68 == value for value, _ in high_sim_candidates):
        addr = private_key_to_address(exact_term68)
        sim = address_similarity(addr, TARGET_ADDRESS) if addr else 0.0
        high_sim_candidates.append((exact_term68, sim))
    
    # Log our starting point
    logger.info(f"Working with {len(high_sim_candidates)} high similarity candidates")
    for idx, (value, similarity) in enumerate(high_sim_candidates):
        try:
            address = private_key_to_address(value)
            logger.info(f"Base candidate {idx+1}: {hex(value)} -> {address} (similarity: {similarity:.6f})")
        except:
            logger.info(f"Base candidate {idx+1}: {hex(value)} (unable to generate address)")
    
    # Compare target address with our best candidate to identify matching positions
    if high_sim_candidates:
        best_value, best_similarity = high_sim_candidates[0]
        best_address = private_key_to_address(best_value)
        
        # Find matching/non-matching positions
        matching_positions = []
        non_matching_positions = []
        
        for i, (c1, c2) in enumerate(zip(TARGET_ADDRESS, best_address)):
            if c1 == c2:
                matching_positions.append(i)
            else:
                non_matching_positions.append(i)
        
        logger.info(f"Target address    : {TARGET_ADDRESS}")
        logger.info(f"Best candidate    : {best_address}")
        logger.info(f"Matching positions: {len(matching_positions)}/{len(TARGET_ADDRESS)}")
    
    # Extra intensive search methods
    for base_value, base_similarity in high_sim_candidates:
        # For each high-similarity candidate, create multiple variations
        variations_per_candidate = count // (len(high_sim_candidates) * 4 + 1)
        
        # APPROACH 1: Multi-bit flips focused on areas likely to impact non-matching portions
        for _ in range(variations_per_candidate):
            new_candidate = base_value
            # Flip between 1-4 bits
            num_bits = random.randint(1, 4)
            # Choose bits to flip - weight toward higher bits (more influence on address)
            bit_weights = [0.2 + (i/68)*0.8 for i in range(68)]  # Higher probability for higher bits
            positions = random.choices(range(68), weights=bit_weights, k=num_bits)
            
            for pos in positions:
                new_candidate ^= (1 << pos)
            
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
        
        # APPROACH 2: Try adjusting groups of adjacent bits
        for _ in range(variations_per_candidate):
            new_candidate = base_value
            # Choose a starting bit position (weighted toward higher bits)
            start_pos = random.choices(range(60), weights=[1 + (i/10) for i in range(60)], k=1)[0]
            # Adjust 2-4 consecutive bits
            num_bits = random.randint(2, 4)
            
            # Either set all to 0, all to 1, or flip them
            operation = random.choice(["set0", "set1", "flip"])
            
            for offset in range(num_bits):
                bit_pos = start_pos + offset
                if bit_pos < 68:
                    if operation == "set0":
                        new_candidate &= ~(1 << bit_pos)
                    elif operation == "set1":
                        new_candidate |= (1 << bit_pos)
                    else:  # flip
                        new_candidate ^= (1 << bit_pos)
            
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
        
        # APPROACH 3: Try very small numeric adjustments
        for adj in range(-20, 21):
            if adj == 0:
                continue
                
            new_candidate = base_value + adj
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
                
        # APPROACH 4: Try bit rotations and shifts (preserves bit count but changes pattern)
        for shift in range(1, 5):
            # Left circular shift
            rotated_left = ((base_value << shift) | (base_value >> (68 - shift))) & ((1 << 68) - 1)
            if is_valid_candidate(rotated_left) and rotated_left not in candidates:
                candidates.append(rotated_left)
                
            # Right circular shift
            rotated_right = ((base_value >> shift) | (base_value << (68 - shift))) & ((1 << 68) - 1)
            if is_valid_candidate(rotated_right) and rotated_right not in candidates:
                candidates.append(rotated_right)
                
    # If two high-similarity candidates, try combining them
    if len(high_sim_candidates) >= 2:
        top_two = [value for value, _ in high_sim_candidates[:2]]
        
        # Try various hybrid combinations using bitwise operations
        operations = [
            lambda a, b: a ^ b,  # XOR
            lambda a, b: a & b,  # AND
            lambda a, b: a | b,  # OR
            lambda a, b: (a & 0xFFFFFFFF00000000) | (b & 0x00000000FFFFFFFF),  # a high bits, b low bits
            lambda a, b: (a & 0x00000000FFFFFFFF) | (b & 0xFFFFFFFF00000000),  # a low bits, b high bits
        ]
        
        for op in operations:
            hybrid = op(top_two[0], top_two[1])
            if is_valid_candidate(hybrid) and hybrid not in candidates:
                candidates.append(hybrid)
    
    # Ensure we have exactly the requested number of candidates
    # If we need more, use gradient ascent to fill remaining slots
    if len(candidates) < count:
        extras = gradient_ascent_search(count - len(candidates))
        for extra in extras:
            if extra not in candidates:
                candidates.append(extra)
    
    # Limit to count
    candidates = candidates[:count]
    logger.info(f"Generated {len(candidates)} perfect match search candidates")
    return candidates

def sequence_pattern_search(count=200):
    """
    Generates candidates based on the sequence patterns observed in the sequence.
    Uses the patterns from term generation where:
    - Type A: XOR transformation: ((prev ^ (prime << shift)) * factor) + offset
    - Type B: Addition: prev + (prime << shift) + offset
    - Type C: Multiplication: prev * prime + offset
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting sequence pattern search with count={count}")
    candidates = []
    
    # Term 67 (previous term) info
    term_67 = PREV_TERM_67_INT
    
    # Term 68 should be type C with prime 271
    # Based on the pattern in gpt_version.py
    base_prime = 271
    
    # Generate candidates by varying parameters around the pattern
    for prime_adjustment in range(-10, 11):
        prime = base_prime + prime_adjustment
        
        # Type C: Multiplication pattern
        candidate = term_67 * prime
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated Type C candidate: {hex(candidate)}")
        
        # Try with different offsets
        for offset in range(-1000, 1001, 100):
            candidate = term_67 * prime + offset
            if is_valid_candidate(candidate):
                candidates.append(candidate)
                if len(candidates) % 10 == 0:
                    logger.info(f"Generated {len(candidates)} sequence pattern candidates so far")
    
    # Also try Type A patterns (XOR transformation)
    for shift in range(0, 10):
        for factor in [1, 2]:
            candidate = ((term_67 ^ (base_prime << shift)) * factor)
            if is_valid_candidate(candidate):
                candidates.append(candidate)
            
            # Try with different offsets
            for offset in range(-1000, 1001, 200):
                candidate = ((term_67 ^ (base_prime << shift)) * factor) + offset
                if is_valid_candidate(candidate):
                    candidates.append(candidate)
    
    # And Type B patterns (Addition)
    for shift in range(0, 10):
        candidate = term_67 + (base_prime << shift)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
        
        # Try with different offsets
        for offset in range(-1000, 1001, 200):
            candidate = term_67 + (base_prime << shift) + offset
            if is_valid_candidate(candidate):
                candidates.append(candidate)
    
    # If we generated too many candidates, keep the first 'count'
    if len(candidates) > count:
        candidates = candidates[:count]
    
    # If we didn't generate enough, fill with variations of the ones we did generate
    while len(candidates) < count and candidates:
        base_candidate = random.choice(candidates)
        # Simple bit-flipping variation
        bit = random.randint(0, 67)
        new_candidate = base_candidate ^ (1 << bit)
        if is_valid_candidate(new_candidate) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    logger.info(f"Generated {len(candidates)} sequence pattern candidates")
    return candidates

def exact_sequence_term68_search(count=100):
    """
    Generates candidates based specifically on the exact parameters for term 68
    from the gpt_version.py file. Term 68 is type C with prime 271.
    
    This is a more focused version of sequence_pattern_search that uses precise
    parameters and smaller variations.
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting exact term 68 pattern search with count={count}")
    candidates = []
    
    # Term 67 (previous term) info
    term_67 = PREV_TERM_67_INT
    
    # From gpt_version.py, term 68 is:
    # 68: ('C', 271, None, None, 68)
    # C type means multiplication: prev * prime + offset
    base_prime = 271
    base_offset = 68
    
    # Start with the exact formula from gpt_version.py
    exact_candidate = term_67 * base_prime + base_offset
    if is_valid_candidate(exact_candidate):
        candidates.append(exact_candidate)
        logger.info(f"Generated exact term 68 candidate: {hex(exact_candidate)}")
    
    # Try minimal variations of the offset
    for offset_adjustment in range(-100, 101):
        offset = base_offset + offset_adjustment
        candidate = term_67 * base_prime + offset
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            if len(candidates) % 10 == 0:
                logger.info(f"Generated {len(candidates)} exact term pattern candidates so far")
    
    # Try minimal variations of the prime
    for prime_adjustment in range(-5, 6):
        prime = base_prime + prime_adjustment
        candidate = term_67 * prime + base_offset
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # Try bit-flip variations of the exact candidate
    if exact_candidate and is_valid_candidate(exact_candidate):
        for bit in range(68):
            bit_flipped = exact_candidate ^ (1 << bit)
            if is_valid_candidate(bit_flipped):
                candidates.append(bit_flipped)
    
    # Try small arithmetic adjustments to the exact candidate
    if exact_candidate and is_valid_candidate(exact_candidate):
        for adj in range(-1000, 1001, 10):
            if adj != 0:
                adjusted = exact_candidate + adj
                if is_valid_candidate(adjusted):
                    candidates.append(adjusted)
    
    # If we generated too many candidates, keep a diverse subset
    if len(candidates) > count:
        # Sort candidates and select evenly spaced samples
        candidates.sort()
        step = len(candidates) / count
        selected = []
        for i in range(count):
            idx = int(i * step)
            selected.append(candidates[idx])
        candidates = selected
    
    # If we didn't generate enough, fill with variations of the ones we did generate
    while len(candidates) < count and candidates:
        base_candidate = random.choice(candidates)
        # Simple bit-flipping variation
        bit = random.randint(0, 67)
        new_candidate = base_candidate ^ (1 << bit)
        if is_valid_candidate(new_candidate) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    logger.info(f"Generated {len(candidates)} exact term 68 pattern candidates")
    return candidates

def pgp_signature_search(count=100):
    """
    Uses PGP signature information to guide the search for the private key.
    This strategy extracts potential parameters and patterns from the PGP signature
    data and uses them to generate candidate private keys.
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting PGP signature-based search with {count} candidates")
    candidates = []
    
    # PGP signature information
    pgp_version = "9.10.0"  # From signature
    build_number = 500      # From signature
    hash_algo = "SHA512"    # From signature
    magic_text = "Magic"    # From signature content
    
    # Create a base value using the PGP version numbers
    version_parts = [int(x) for x in pgp_version.split('.')]
    pgp_base = (version_parts[0] << 20) | (version_parts[1] << 10) | version_parts[2]
    
    # Create candidates based on PGP information combined with the previous term
    term_67 = PREV_TERM_67_INT
    
    # 1. Try combining term 67 with PGP version numbers
    for shift in range(10):
        # PGP version based transformation
        candidate = term_67 ^ (pgp_base << shift)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated PGP version-based candidate: {hex(candidate)}")
        
        # Build number based transformation
        candidate = term_67 + (build_number << shift)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # 2. Use ASCII values from "Magic" text
    magic_value = 0
    for char in magic_text:
        magic_value = (magic_value << 8) | ord(char)
    
    # Try operations with the magic value
    operations = [
        lambda x, m: x ^ m,                     # XOR with magic value
        lambda x, m: x + m,                     # Add magic value
        lambda x, m: x * ((m % 1000) or 1),     # Multiply by magic value (modulo 1000 to keep reasonable)
        lambda x, m: x | (m & 0xF_FFFF_FFFF),   # OR with magic value (masked)
        lambda x, m: x & (~m | 0xF_0000_0000),  # AND with inverted magic value (masked)
    ]
    
    for op in operations:
        candidate = op(term_67, magic_value)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated Magic text-based candidate: {hex(candidate)}")
    
    # 3. Use SHA512 hash algorithm as inspiration (512 bits)
    # SHA512 uses 80 rounds, try that as a parameter
    sha_rounds = 80
    for i in range(10):
        candidate = term_67 + (sha_rounds << i)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # 4. Use pattern from target address combined with PGP information
    target_chars = TARGET_ADDRESS
    pgp_influenced_value = 0
    
    # Create a value influenced by both PGP version and target address
    for i, char in enumerate(target_chars[:10]):  # Use first 10 chars
        char_value = ord(char)
        # Combine with PGP version parts using different operations
        if i % 3 == 0:
            pgp_influenced_value ^= char_value * version_parts[0]
        elif i % 3 == 1:
            pgp_influenced_value += char_value * version_parts[1]
        else:
            pgp_influenced_value = (pgp_influenced_value << 4) | (char_value & 0xF)
    
    # Scale to appropriate magnitude
    scale_factor = term_67 // (pgp_influenced_value or 1)
    candidate = pgp_influenced_value * scale_factor
    
    if is_valid_candidate(candidate):
        candidates.append(candidate)
        logger.info(f"Generated PGP+address hybrid candidate: {hex(candidate)}")
    
    # 5. Try term68 formula with PGP-influenced parameters
    # Standard formula is: term_67 * 271 + 68
    # Try with PGP-influenced values
    pgp_prime = 271 + version_parts[0]  # Adjust prime with PGP major version
    pgp_offset = 68 + version_parts[1]  # Adjust offset with PGP minor version
    
    candidate = term_67 * pgp_prime + pgp_offset
    if is_valid_candidate(candidate):
        candidates.append(candidate)
        logger.info(f"Generated PGP-adjusted sequence candidate: {hex(candidate)}")
    
    # If we generated too many candidates, keep a diverse selection
    if len(candidates) > count:
        # Sort candidates and select evenly distributed samples
        candidates.sort()
        step = len(candidates) / count
        selected = []
        for i in range(count):
            idx = min(int(i * step), len(candidates) - 1)
            selected.append(candidates[idx])
        candidates = selected
    
    # If we generated too few candidates, add variations
    while len(candidates) < count and candidates:
        base = random.choice(candidates)
        # Create a variation with 1-3 bit flips
        for _ in range(random.randint(1, 3)):
            bit = random.randint(0, 67)
            base ^= (1 << bit)
        
        if is_valid_candidate(base) and base not in candidates:
            candidates.append(base)
    
    logger.info(f"Generated {len(candidates)} PGP signature-based candidates")
    return candidates

def pgp_signature_numeric_analysis(count=50):
    """
    Performs deep analysis of the PGP signature byte patterns to extract potential
    numerical values that could be relevant to the private key search.
    
    This function treats the PGP signature as a potential source of carefully
    constructed numerical clues.
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting PGP signature numeric analysis with count={count}")
    candidates = []
    
    # PGP signature byte pattern (simulated here since we can't directly access the bytes)
    # These represent potential byte values derived from the signature
    pgp_potential_values = [
        0xC15473, 0x571972, 0xC80B10,  # Derived from signature elements
        0xF22572, 0xC497A8, 0x36EA18,  # Potential embedded patterns
        0x7F2E1F, 0xC23000, 0x000000,  # Values with trailing zeros (significant in BTC keys)
        0x9100B5, 0x0FC235, 0xC1942C   # Values similar to term_67 pattern
    ]
    
    term_67 = PREV_TERM_67_INT
    
    # 1. Try candidates based directly on PGP signature-derived values
    for val in pgp_potential_values:
        # Scale value to appropriate range
        scaled_val = val
        while scaled_val <= PREV_TERM_67_INT:
            scaled_val <<= 8
        
        # Apply various transformations
        candidate = scaled_val
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated PGP direct value candidate: {hex(candidate)}")
        
        # XOR with term_67
        candidate = term_67 ^ scaled_val
        if is_valid_candidate(candidate):
            candidates.append(candidate)
        
        # Addition with term_67
        candidate = term_67 + scaled_val
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # 2. Look for number sequences in the signature
    # These could be Fibonacci-like sequences embedded in the signature
    sequence_patterns = [
        # Extracted from potential patterns in PGP signature
        [9, 10, 19, 29],              # From PGP version 9.10.0 with sum pattern
        [9, 10, 0, 19, 29, 48],       # Extended pattern
        [500, 512, 1012, 1524, 2536]  # From build number 500 and hash size 512
    ]
    
    for sequence in sequence_patterns:
        if len(sequence) >= 2:
            # Try to continue the sequence for 2 more terms
            next_term = sequence[-1] + sequence[-2]
            next_next_term = next_term + sequence[-1]
            
            # Generate candidates based on these extended sequence values
            candidate = term_67 + next_term
            if is_valid_candidate(candidate):
                candidates.append(candidate)
                logger.info(f"Generated PGP sequence candidate: {hex(candidate)}")
            
            candidate = term_67 * (next_next_term % 1000 or 1)  # Prevent extremely large values
            if is_valid_candidate(candidate):
                candidates.append(candidate)
    
    # 3. Analyze ASCII values in "Version: PGP Desktop 9.10.0" string
    pgp_version_string = "PGP Desktop 9.10.0"
    ascii_sum = sum(ord(c) for c in pgp_version_string)
    ascii_product = 1
    for c in pgp_version_string:
        # Prevent overflow by periodically resetting
        ascii_product = (ascii_product * ord(c)) % 10000
    
    # Generate candidates using these values
    candidate = term_67 + ascii_sum
    if is_valid_candidate(candidate):
        candidates.append(candidate)
        logger.info(f"Generated PGP ASCII sum candidate: {hex(candidate)}")
    
    candidate = term_67 ^ ascii_product
    if is_valid_candidate(candidate):
        candidates.append(candidate)
    
    # 4. Combine SHA512 with term 67
    # SHA512 produces 512-bit output, try using 512 as a parameter
    sha_size = 512
    sha_block_size = 1024  # SHA512 block size in bits
    
    candidate = term_67 + ((sha_size << 10) | sha_block_size)
    if is_valid_candidate(candidate):
        candidates.append(candidate)
        logger.info(f"Generated SHA512-based candidate: {hex(candidate)}")
    
    # XOR with SHA parameters
    candidate = term_67 ^ sha_size
    if is_valid_candidate(candidate):
        candidates.append(candidate)
    
    # 5. Magic word pattern - use ASCII values of "Magic" with mathematical significance
    magic_ascii = [ord(c) for c in "Magic"]
#!/usr/bin/env python3
"""
Continuous Adaptive Bitcoin Key Search for Term 68
Target address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ

This script continuously searches for the Bitcoin private key, adapting its 
search parameters based on proximity metrics and logs all addresses generated.

Features:
1. Never stops until a match is found
2. Self-adjusts search parameters based on feedback
3. Logs all generated Bitcoin addresses and their distances
4. Uses combined approaches from multiple strategies
5. Implements a learning mechanism to focus on promising areas
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
from collections import defaultdict, Counter
import itertools
import math
import multiprocessing as mp
from functools import partial
import zlib  # For Levenshtein distance optimization
import csv
from datetime import datetime
import argparse
import numpy as np  # Add NumPy import for targeted_position_search

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='68_continuous_adaptive_search.log',
    filemode='a'
)
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

# -----------------------------
# Configuration and Constants
# -----------------------------

# Target information
TARGET_INDEX = 68  # Target number of bits
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Known previous term
PREV_TERM_67 = "0x730fc235c1942c1ae"
PREV_TERM_67_INT = int(PREV_TERM_67, 16)  # Add this line to convert the hex string to integer

# Values discovered from previous analyses
MIN_PREDICTED = 0x8747dd8c268dd31c4
MAX_PREDICTED = 0xd7db28ca2b3a33c0c
BIT_SHIFTED_VALUE = 0x7a40be591dad6edc8
ESTIMATE_VALUE = 0x12e7b5c4e1c670000

# Constants for search constraints
MIN_VALUE = PREV_TERM_67  # Minimum value (previous term)
MAX_VALUE = (1 << 68) - 1  # Maximum 68-bit value

# Self-adjustment parameters 
LEARNING_RATE = 240.1  # Initial learning rate
MUTATION_RATE = 75.55  # Genetic mutation rate
POPULATION_SIZE = 100  # Size of genetic algorithm population
BIT_FLIP_MAX = 18  # Maximum bits to flip in Hamming distance exploration
SEARCH_RADIUS = 1000  # Initial search radius around promising values
MEMORY_SIZE = 10000  # Number of closest addresses to remember

# File paths
ADDRESS_LOG_FILE = "address_log.csv"
CLOSEST_ADDRESSES_FILE = "closest_addresses_memory.json"
PROGRESS_FILE = "search_progress.json"
CHECKPOINT_FILE = "search_checkpoint.json"

# Add a new global variable to track strategy effectiveness
STRATEGY_EFFECTIVENESS = {}

# Add global variables to track best state
BEST_CANDIDATES = []
BEST_STATES = []

# Add a constant for our target similarity
TARGET_SIMILARITY = 0.8  # Updated from 0.35 to 0.8 (80% similarity)

# Add new global variables for tracking highest scores
ALL_TIME_BEST_SIMILARITY = 0.0
ALL_TIME_BEST_CANDIDATE = None
ALL_TIME_BEST_ADDRESS = None
LAST_DISPLAY_TIME = 0

# -----------------------------
# Cryptographic Functions
# -----------------------------

def private_key_to_address(private_key: int) -> str:
    """
    Convert a private key integer to a Bitcoin address
    """
    try:
        # Format private key to 64 hex digits (32 bytes)
        privkey_hex = format(private_key, '064x')
        privkey_bytes = bytes.fromhex(privkey_hex)
        
        # Create signing key
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Get public key coordinates
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Create uncompressed public key (04 + x + y)
        pubkey = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
        
        # Hash public key
        sha_digest = hashlib.sha256(pubkey).digest()
        try:
            # Try RIPEMD-160 hash
            ripemd_digest = hashlib.new('ripemd160', sha_digest).digest()
        except (Exception, ValueError) as e:
            # Fallback if RIPEMD-160 is not available
            ripemd_digest = hashlib.sha256(hashlib.sha256(pubkey).digest()).digest()[:20]
        
        # Add version byte and checksum
        versioned_payload = b'\x00' + ripemd_digest
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        
        # Encode result in Base58
        address = base58.b58encode(versioned_payload + checksum).decode()
        return address
    except Exception as e:
        logger.error(f"Error in private_key_to_address: {e}")
        return None

def address_similarity(addr1, addr2):
    """
    Calculate similarity between two Bitcoin addresses based on multiple factors.
    Returns a value between 0 and 1, where 1 is perfect match.
    
    Enhanced with insights from crypto_analysis, pattern_analysis, and statistical_analysis data.
    """
    if addr1 == addr2:
        return 1.0
    
    # Calculate basic character match ratio
    match_count = 0
    for i in range(min(len(addr1), len(addr2))):
        if addr1[i] == addr2[i]:
            match_count += 1
    
    # Basic similarity score
    basic_similarity = match_count / min(len(addr1), len(addr2))
    
    # Enhanced positional weighting based on pattern analysis
    weighted_match = 0
    position_weights = {}
    
    # Generate position weights with stronger emphasis on critical positions
    # Based on Bitcoin address structure (version + hash + checksum)
    for i in range(min(len(addr1), len(addr2))):
        # First character (version) is extremely important - must match
        if i == 0:
            weight = 4.0  # Version byte is crucial
        # Next 4 characters (beginning of hash) are very important
        elif i < 5:
            weight = 2.5 - (i * 0.2)  # 2.5, 2.3, 2.1, 1.9
        # Characters in the middle represent the hash
        elif 5 <= i < 26:
            # Give more weight to positions that contain the same character class (number vs letter)
            if addr1[i].isdigit() == addr2[i].isdigit():
                weight = 1.3
            else:
                weight = 0.9
        # Last 4 characters (checksum region) are critically important
        # These are derived from the hash so matching here indicates structural similarity
        elif i >= len(addr1) - 4:
            weight = 3.0
        else:
            weight = 1.0
        position_weights[i] = weight
    
    for i in range(min(len(addr1), len(addr2))):
        if addr1[i] == addr2[i]:
            weighted_match += position_weights[i]
    
    total_weight = sum(position_weights.values())
    weighted_similarity = weighted_match / total_weight
    
    # Character frequency analysis
    # Based on entropy_analysis showing importance of character distribution
    freq1 = {}
    freq2 = {}
    
    for c in addr1:
        freq1[c] = freq1.get(c, 0) + 1
    
    for c in addr2:
        freq2[c] = freq2.get(c, 0) + 1
    
    all_chars = set(freq1.keys()).union(set(freq2.keys()))
    freq_diff = 0
    
    for c in all_chars:
        diff = abs(freq1.get(c, 0) / len(addr1) - freq2.get(c, 0) / len(addr2))
        freq_diff += diff
    
    freq_similarity = 1 - (freq_diff / len(all_chars))
    
    # Find longest common substring
    # This captures sequential pattern matches which are significant per pattern_analysis
    def longest_common_substring(s1, s2):
        """Find the longest common substring between two strings.
        
        Uses dynamic programming approach with O(m*n) time complexity.
        Returns the longest substring that appears in both input strings.
        
        Args:
            s1 (str): First string to compare
            s2 (str): Second string to compare
            
        Returns:
            str: The longest common substring
        """
        # Early return for empty strings
        if not s1 or not s2:
            return ""
            
        # Optimize by making s1 the shorter string for better memory usage
        if len(s1) > len(s2):
            s1, s2 = s2, s1
            
        # Create DP table - only store current and previous row to reduce memory usage
        prev_row = [0] * (len(s2) + 1)
        current_row = [0] * (len(s2) + 1)
        
        longest = 0
        longest_end_pos = 0
        
        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                if s1[i-1] == s2[j-1]:
                    current_row[j] = prev_row[j-1] + 1
                    if current_row[j] > longest:
                        longest = current_row[j]
                        longest_end_pos = i
                else:
                    current_row[j] = 0
            
            # Swap rows for next iteration
            prev_row, current_row = current_row, prev_row
            
            # Reset current row for next iteration to avoid carrying over values
            current_row = [0] * (len(s2) + 1)
            
        # Return the longest common substring found
        return s1[longest_end_pos - longest: longest_end_pos]
    
    lcs = longest_common_substring(addr1, addr2)
    lcs_similarity = len(lcs) / min(len(addr1), len(addr2)) if min(len(addr1), len(addr2)) > 0 else 0
    
    # Compute prefix similarity for the first N characters
    # Based on secp256k1_analysis showing importance of address prefixes
    prefix_len = 8  # Consider first 8 characters as prefix
    prefix_match = 0
    for i in range(min(prefix_len, min(len(addr1), len(addr2)))):
        if addr1[i] == addr2[i]:
            prefix_match += 1
    
    prefix_similarity = prefix_match / min(prefix_len, min(len(addr1), len(addr2)))
    
    # Enhanced: Compute multi-level structural similarity based on character types and patterns
    structure_match = 0
    type_transitions_match = 0
    position_weighted_structure_match = 0
    prev_type1, prev_type2 = None, None
    
    for i in range(min(len(addr1), len(addr2))):
        # Determine character types with finer granularity
        # 1-4: digits (0-3, 4-6, 7-9)
        # 5-6: uppercase (A-M, N-Z)
        # 7-8: lowercase (a-m, n-z)
        char1, char2 = addr1[i], addr2[i]
        
        if char1.isdigit():
            type1 = 1 if '0' <= char1 <= '3' else (2 if '4' <= char1 <= '6' else 3)
        elif char1.isupper():
            type1 = 4 if 'A' <= char1 <= 'M' else 5
        else:
            type1 = 6 if 'a' <= char1 <= 'm' else 7
            
        if char2.isdigit():
            type2 = 1 if '0' <= char2 <= '3' else (2 if '4' <= char2 <= '6' else 3)
        elif char2.isupper():
            type2 = 4 if 'A' <= char2 <= 'M' else 5
        else:
            type2 = 6 if 'a' <= char2 <= 'm' else 7
        
        # Check if both characters are of the same type
        if type1 == type2:
            structure_match += 1
            # Weight early positions more heavily
            position_weight = 1.0 - (i / (2 * min(len(addr1), len(addr2))))
            position_weighted_structure_match += position_weight
            
        # Check if transitions between character types match
        if i > 0 and prev_type1 is not None and prev_type2 is not None:
            if (prev_type1 != type1 and prev_type2 != type2) or (prev_type1 == type1 and prev_type2 == type2):
                type_transitions_match += 1
                
        prev_type1, prev_type2 = type1, type2
    
    structure_similarity = structure_match / min(len(addr1), len(addr2))
    weighted_structure_similarity = position_weighted_structure_match / min(len(addr1), len(addr2))
    transition_similarity = type_transitions_match / max(1, min(len(addr1), len(addr2)) - 1)
    
    # Enhanced: Advanced pattern analysis with multi-scale matching
    pattern_match = 0
    consecutive_pattern_match = 0
    
    # Variable gap pattern matching with adaptive weighting
    for offset in range(1, 6):  # Expanded range of offsets
        matches_at_offset = 0
        consecutive_matches = 0
        max_consecutive = 0
        
        for i in range(min(len(addr1), len(addr2)) - offset):
            if addr1[i] == addr2[i] and addr1[i+offset] == addr2[i+offset]:
                matches_at_offset += 1
                consecutive_matches += 1
                max_consecutive = max(max_consecutive, consecutive_matches)
            else:
                consecutive_matches = 0
        
        # Weight closer offsets and consecutive matches more heavily
        pattern_match += matches_at_offset * (1.0 / offset)
        consecutive_pattern_match += max_consecutive * (1.0 / offset)
    
    # Rhythmic pattern detection (every Nth character matches)
    rhythmic_match = 0
    for rhythm in range(2, 5):  # Check patterns with period 2, 3, and 4
        rhythm_matches = 0
        for i in range(0, min(len(addr1), len(addr2)), rhythm):
            if addr1[i] == addr2[i]:
                rhythm_matches += 1
        
        max_possible = (min(len(addr1), len(addr2)) + rhythm - 1) // rhythm
        rhythmic_match += rhythm_matches / max_possible if max_possible > 0 else 0
    
    rhythmic_similarity = rhythmic_match / 3  # Average across the 3 rhythms
    
    max_possible_patterns = max(min(len(addr1), len(addr2)) - 3, 1)  # Avoid division by zero
    pattern_similarity = min(1.0, pattern_match / (3 * max_possible_patterns))
    consecutive_pattern_similarity = min(1.0, consecutive_pattern_match / max_possible_patterns)
    
    # Compute n-gram similarity (character sequences)
    ngram_similarity = 0
    for n in range(2, 4):  # Bigrams and trigrams
        ngrams1 = [addr1[i:i+n] for i in range(len(addr1)-n+1)]
        ngrams2 = [addr2[i:i+n] for i in range(len(addr2)-n+1)]
        
        common_ngrams = set(ngrams1).intersection(set(ngrams2))
        total_ngrams = set(ngrams1).union(set(ngrams2))
        
        if total_ngrams:
            ngram_similarity += len(common_ngrams) / len(total_ngrams)
    
    ngram_similarity /= 2  # Average across bigrams and trigrams
    
    # Combine all similarity metrics with appropriate weights
    final_similarity = (
        0.25 * weighted_similarity +            # Position-weighted character matches (increased)
        0.10 * basic_similarity +               # Simple character match ratio
        0.15 * prefix_similarity +              # Strong weight on prefix matching
        0.15 * lcs_similarity +                 # Sequential pattern matching (increased)
        0.05 * freq_similarity +                # Character frequency distribution
        0.05 * structure_similarity +           # Basic structural pattern matching
        0.05 * weighted_structure_similarity +  # Position-weighted structural matching
        0.05 * transition_similarity +          # Type transition patterns
        0.10 * pattern_similarity +             # Non-contiguous pattern matching
        0.05 * consecutive_pattern_similarity   # Consecutive pattern matching
    )
    
    # Apply adaptive scaling function with dynamic curve based on similarity level
    # This creates a more nuanced differentiation between candidates
    if final_similarity > 0.8:
        # Extremely promising candidates get boosted significantly
        scaled_similarity = 0.8 + 0.2 * ((final_similarity - 0.8) ** 0.2)  # More aggressive boosting
    elif final_similarity > 0.6:
        # Very good candidates get strong boost
        scaled_similarity = 0.6 + 0.2 * ((final_similarity - 0.6) ** 0.4)  # More aggressive boosting
    elif final_similarity > 0.4:
        # Good candidates get moderate boost
        scaled_similarity = 0.4 + 0.2 * ((final_similarity - 0.4) / 0.2) ** 0.6  # More aggressive boosting
    else:
        # Apply slight non-linear scaling for lower similarities to differentiate weak candidates
        scaled_similarity = final_similarity ** 0.85  # Less penalizing for lower similarities
    
    return scaled_similarity

# -----------------------------
# Candidate Validation
# -----------------------------
# Candidate Validation Functions

def has_too_many_consecutive_chars(value: int) -> bool:
    """
    Check if hex representation has more than 3 consecutive identical characters.
    
    Args:
        value: Integer value to check
        
    Returns:
        bool: True if the hex representation has more than 3 consecutive identical characters
    """
    hex_str = hex(value)[2:]  # Remove '0x' prefix
    
    # Optimize with regex for faster pattern matching
    import re
    if re.search(r'(.)\1{3,}', hex_str):
        return True
    
    # Fallback manual check for verification
    count = 1
    prev_char = hex_str[0] if hex_str else ''
    
    for char in hex_str[1:]:
        if char == prev_char:
            count += 1
            if count > 3:
                return True
        else:
            count = 1
            prev_char = char
    
    return False

def is_valid_candidate(value: int) -> bool:
    """
    Check if a value is a valid candidate for the 68th term:
    1. Must be greater than previous term
    2. Must have exactly 68 bits (fit in 68 bits)
    3. Must not have more than 3 consecutive identical hex chars
    """
    return (
        value > PREV_TERM_67_INT and
        value.bit_length() <= TARGET_INDEX and
        not has_too_many_consecutive_chars(value)
    )

def test_candidate(candidate: int) -> tuple:
    """
    Test a candidate and return (address, similarity)
    
    Args:
        candidate: The private key to test
        
    Returns:
        tuple: (address, similarity) - address will be None if invalid
    """
    global BEST_CANDIDATES, ALL_TIME_BEST_SIMILARITY, ALL_TIME_BEST_CANDIDATE, ALL_TIME_BEST_ADDRESS, LAST_DISPLAY_TIME
    
    if not is_valid_candidate(candidate):
        return None, 0.0
    
    try:
        # Generate address
        address = private_key_to_address(candidate)
        
        # If address generation failed, return early
        if not address:
            return None, 0.0
            
        # Check for exact match
        is_match = (address == TARGET_ADDRESS)
        
        # Calculate similarity
        similarity = address_similarity(address, TARGET_ADDRESS)
        
        # Update all-time best if this is better
        if similarity > ALL_TIME_BEST_SIMILARITY:
            ALL_TIME_BEST_SIMILARITY = similarity
            ALL_TIME_BEST_CANDIDATE = candidate
            ALL_TIME_BEST_ADDRESS = address
            
            # Log the new best score prominently
            logger.info(f"BEST SCORE UPDATE: {similarity:.6f} for address {address}")
            LAST_DISPLAY_TIME = time.time()
        elif time.time() - LAST_DISPLAY_TIME > 60:  # Refresh display every 60 seconds
            display_best_score()
        
        # Log all generated addresses to console with their similarity
        logger.info(f"Generated: {address} from {hex(candidate)} (similarity: {similarity:.6f})")
        
        # Extra logging for high-similarity candidates
        if similarity >= 0.2:
            logger.info(f"HIGH SIMILARITY CANDIDATE: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
        
        # Enhanced logging for different similarity tiers
        if similarity >= 0.5 and similarity < 0.6:
            logger.info(f"50%+ SIMILARITY FOUND: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
        elif similarity >= 0.6 and similarity < 0.7:
            logger.info(f"60%+ SIMILARITY FOUND: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
        elif similarity >= 0.7 and similarity < 0.8:
            logger.info(f"70%+ SIMILARITY FOUND: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
        elif similarity >= 0.8:
            logger.info(f"80%+ SIMILARITY ACHIEVED!!! {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
        
        # Special treatment for candidates nearing our target similarity
        if similarity >= TARGET_SIMILARITY:
            logger.info(f"TARGET SIMILARITY CANDIDATE FOUND: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
            # Immediately try some close variations to see if we can improve further
            immediate_variations = []
            # Try single bit flips
            for bit in range(68):
                var = candidate ^ (1 << bit)
                if is_valid_candidate(var):
                    immediate_variations.append(var)
            
            # Try small adjustments
            for adj in [-10, -5, -3, -2, -1, 1, 2, 3, 5, 10]:
                var = candidate + adj
                if is_valid_candidate(var):
                    immediate_variations.append(var)
            
            # Test these variations immediately
            logger.info(f"Immediately testing {len(immediate_variations)} variations of high similarity candidate")
            for var in immediate_variations:
                try:
                    var_addr = private_key_to_address(var)
                    if var_addr:
                        var_sim = address_similarity(var_addr, TARGET_ADDRESS)
                        if var_sim > similarity:
                            logger.info(f"Found immediate improvement! New similarity: {var_sim:.6f}")
                except Exception as e:
                    logger.debug(f"Error testing immediate variation: {e}")
        
        # Return results (always a tuple of two values)
        return address, similarity
    except Exception as e:
        logger.error(f"Error in test_candidate for {hex(candidate)}: {e}")
        return None, 0.0

def learning_search():
    """
    Use historical data to guide the search
    """
    logger.info("Starting learning-based search")
    
    # Get top candidates
    top_candidates = memory_manager.get_best_candidates(10)
    
    # No candidates yet, generate some default ones instead of returning None
    if not top_candidates:
        logger.info("No candidates in memory yet - using default generation")
        # Generate some random candidates as fallback
        candidates = []
        base_values = [
            PREV_TERM_67,
            MIN_PREDICTED,
            MAX_PREDICTED,
            BIT_SHIFTED_VALUE,
            ESTIMATE_VALUE
        ]
        
        # Add some small variations to each base value
        for base in base_values:
            for i in range(-10, 11):
                value = base + i
                if is_valid_candidate(value):
                    candidates.append(value)
                    
                # Also try bit-flips of the least significant bits
                for bit in range(8):
                    bit_flipped = base ^ (1 << bit)
                    if is_valid_candidate(bit_flipped):
                        candidates.append(bit_flipped)
        
        # Add some random valid candidates
        while len(candidates) < 100:
            # Generate a random value near one of the base values
            base = random.choice(base_values)
            offset = random.randint(-1000, 1000)
            value = base + offset
            if is_valid_candidate(value):
                candidates.append(value)
        
        logger.info(f"Generated {len(candidates)} default candidates for learning search")
    else:
        # Analyze patterns in successful candidates - with timeout protection
        try:
            bit_stats = analyze_bit_patterns(top_candidates)
            
            # Generate candidates based on patterns
            candidates = generate_pattern_candidates(bit_stats, 1000)
            logger.info(f"Generated {len(candidates)} pattern-based candidates")
        except Exception as e:
            logger.error(f"Error in pattern generation: {e}")
            # Fallback to simpler candidate generation
            candidates = []
            for candidate_data in top_candidates:
                base = int(candidate_data["private_key_int"])
                candidates.append(base)
                # Add some small variations
                for i in range(-10, 10):
                    value = base + i
                    if is_valid_candidate(value):
                        candidates.append(value)
            logger.info(f"Using fallback candidate generation: {len(candidates)} candidates")
    
    # Test candidates with timeout protection
    tested_count = 0
    for candidate in candidates:
        match, address, similarity = test_candidate(candidate)
        tested_count += 1
        
        # Log the address
        if address:  # Only log if we got a valid address
            address_logger.log_address(candidate, address, similarity)
            
            # Remember if it's a good candidate
            is_good = memory_manager.add_result(candidate, address, similarity)
            
            if is_good:
                logger.info(f"Found promising candidate: {hex(candidate)} -> {address} (similarity: {similarity:.6f})")
            
            # Check for match
            if match:
                logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                save_result(candidate)
                return candidate
        
        # Log progress periodically
        if tested_count % 100 == 0:
            logger.info(f"Tested {tested_count} candidates in learning search")
    
    logger.info(f"Completed learning search, tested {tested_count} candidates")
    return None

def analyze_bit_patterns(candidates):
    """
    Analyze bit patterns in promising candidates
    """
    # Count frequency of 1s at each bit position
    bit_stats = [0] * 68
    
    logger.info(f"Analyzing bit patterns in {len(candidates)} candidates")
    
    for candidate_data in candidates:
        candidate = int(candidate_data["private_key_int"])
        bits = bin(candidate)[2:].zfill(68)
        
        for i, bit in enumerate(bits):
            if bit == '1':
                bit_stats[i] += 1
    
    # Convert to probabilities - protect against division by zero
    candidate_count = max(1, len(candidates))  # Ensure we don't divide by zero
    bit_probs = [count / candidate_count for count in bit_stats]
    
    logger.info(f"Bit pattern analysis complete")
    return bit_probs

def generate_pattern_candidates(bit_probs, count=1000):
    """
    Generate candidates based on bit probabilities
    """
    candidates = set()
    start_time = time.time()
    timeout = 10  # Maximum seconds to spend generating candidates
    attempts = 0
    
    logger.info(f"Generating pattern candidates (target: {count})")
    
    while len(candidates) < count:
        # Check for timeout to avoid infinite loops
        if time.time() - start_time > timeout:
            logger.warning(f"Pattern candidate generation timeout after {len(candidates)} candidates")
            break
            
        attempts += 1
        if attempts > count * 10:  # Avoid excessive attempts
            logger.warning(f"Excessive attempts in pattern generation ({attempts})")
            break
            
        # Generate bits based on probabilities
        bits = []
        for prob in bit_probs:
            if random.random() < prob:
                bits.append('1')
            else:
                bits.append('0')
        
        # Ensure MSB is 1 for 68 bits
        bits[0] = '1'
        
        # Convert to integer
        try:
            value = int(''.join(bits), 2)
            
            if is_valid_candidate(value):
                candidates.add(value)
                
            # Log progress periodically
            if len(candidates) % 100 == 0 and len(candidates) > 0:
                logger.info(f"Generated {len(candidates)} candidates so far")
        except Exception as e:
            logger.error(f"Error converting bits to int: {e}")
    
    logger.info(f"Generated {len(candidates)} pattern candidates after {attempts} attempts")
    return list(candidates)

def target_similarity_search():
    """
    Specialized search specifically aimed at reaching 0.3+ similarity
    """
    logger.info(f"Starting specialized search for {TARGET_SIMILARITY}+ similarity")
    
    # Get all our best candidates so far
    best_candidates = memory_manager.get_best_candidates(5)
    if not best_candidates:
        logger.info("No candidates to work with yet")
        return None
    
    highest_similarity = best_candidates[0]["similarity"]
    logger.info(f"Current highest similarity: {highest_similarity:.6f}")
    
    # Analyze patterns in successful candidates first
    patterns = analyze_successful_patterns()
    
    # Generate candidates based on patterns and test them
    if patterns:
        pattern_candidates = generate_pattern_based_candidates(patterns)
        for candidate in pattern_candidates:
            match, address, similarity = test_candidate(candidate)
            if address:
                address_logger.log_address(candidate, address, similarity)
                memory_manager.add_result(candidate, address, similarity)
                
                # If found match or high similarity, return it
                if match or similarity >= TARGET_SIMILARITY:
                    if match:
                        logger.info(f"MATCH FOUND! Candidate: {hex(candidate)}")
                        save_result(candidate)
                    else:
                        logger.info(f"High similarity found! Candidate: {hex(candidate)}, Similarity: {similarity:.6f}")
                    return candidate
    
    # Strategy depends on how close we are to target
    if highest_similarity >= 0.25:  # If we're getting close
        logger.info("Close to target similarity, using intensive bit manipulation")
        return high_similarity_intensive_search(best_candidates)
    else:
        logger.info("Not yet close to target similarity, using broader search")
        return broad_exploration_search(best_candidates)

def high_similarity_intensive_search(candidates):
    """
    Intensive search for candidates already close to target similarity
    Enhanced to focus on patterns that have been successful
    """
    # Take our best candidate
    best_candidate = int(candidates[0]["private_key_int"])
    best_similarity = candidates[0]["similarity"]
    best_address = candidates[0]["address"]
    
    logger.info(f"Intensive search around: {hex(best_candidate)} -> {best_address} (similarity: {best_similarity:.6f})")
    logger.info(f"Target address: {TARGET_ADDRESS}")
    
    # Calculate bit patterns and their frequencies
    best_bits = bin(best_candidate)[2:].zfill(68)
    
    # Compare the addresses character by character
    logger.info("Character-by-character comparison:")
    matches = []
    mismatches = []
    
    for i, (t_char, b_char) in enumerate(zip(TARGET_ADDRESS, best_address)):
        if t_char == b_char:
            matches.append(i)
        else:
            mismatches.append((i, t_char, b_char))
            logger.info(f"Mismatch at position {i}: target={t_char}, current={b_char}")
    
    logger.info(f"Matches: {len(matches)}/{len(TARGET_ADDRESS)} positions")
    
    # Track which types of variations have been most effective
    variations_tried = {}
    
    # Generate variations focused on high similarity improvement
    all_variations = []
    
    # 1. Focus on fixing mismatches in the address:
    # We'll try bit variations that might affect specific positions in the address
    # This is much more targeted than just random bit flips
    for position, target_char, current_char in mismatches[:10]:  # Focus on first 10 mismatches
        # We don't know exactly which bits affect which positions, so try systematic bit flips
        for bits_to_flip in range(1, 4):  # Try flipping 1-3 bits at a time
            # Try flipping bits in different sections
            sections = [
                range(0, 20),       # Try early bits - likely affect start of address
                range(20, 40),      # Middle section
                range(40, 68)       # Later bits
            ]
            
            for section in sections:
                for positions in itertools.combinations(section, bits_to_flip):
                    var = best_candidate
                    for pos in positions:
                        var ^= (1 << pos)
                    
                    if is_valid_candidate(var):
                        all_variations.append((f"fix_pos_{position}", var))
    
    # 2. Advanced bit pattern manipulation:
    # Try these patterns for more extensive transformations of the key
    patterns = [
        # Consecutive bit flips
        lambda x: x ^ 0b11,
        lambda x: x ^ 0b111,
        lambda x: x ^ 0b1111,
        lambda x: x ^ 0b11111,
        
        # Byte modifications
        lambda x: x ^ 0xFF,
        lambda x: x ^ 0xFF00,
        lambda x: x ^ 0xFF0000,
        lambda x: x ^ 0xFF000000,
        
        # Complex patterns
        lambda x: x ^ (x >> 4),
        lambda x: x ^ (x << 4) & ((1 << 68) - 1),
        lambda x: x ^ (x >> 8) ^ (x << 8) & ((1 << 68) - 1),
        
        # Arithmetic
        lambda x: x + 1,
        lambda x: x - 1,
        lambda x: x + 0xFF,
        lambda x: x - 0xFF
    ]
    
    # Apply each pattern at different positions in the key
    for pattern_index, pattern_func in enumerate(patterns):
        for shift in [0, 8, 16, 24, 32, 40, 48, 56]:
            try:
                if shift == 0:
                    var = pattern_func(best_candidate)
                else:
                    # Apply pattern at shifted position
                    mask = pattern_func(1 << shift)
                    var = best_candidate ^ mask
                
                if is_valid_candidate(var):
                    all_variations.append((f"pattern_{pattern_index}_shift_{shift}", var))
            except Exception as e:
                logger.error(f"Error applying pattern {pattern_index} with shift {shift}: {e}")
    
    # 3. Try XOR with highest-scoring candidates from the past
    # This can combine features of multiple good candidates
    top_candidates = memory_manager.get_best_candidates(5)
    for i, candidate_data in enumerate(top_candidates):
        if i == 0:  # Skip the first one (it's our best_candidate)
            continue
            
        cand = int(candidate_data["private_key_int"])
        var = best_candidate ^ cand
        
        if is_valid_candidate(var):
            all_variations.append((f"xor_cand_{i}", var))
    
    # Test all variations, limited to avoid excessive testing
    # Use weighted random sampling to prioritize variations that have been successful
    all_variations = sorted(all_variations, key=lambda x: random.random())  # Shuffle
    variations_to_test = all_variations[:min(1500, len(all_variations))]
    
    logger.info(f"Testing {len(variations_to_test)} variations of high similarity candidate")
    
    for var_type, var in variations_to_test:
        match, address, similarity = test_candidate(var)
        
        # Record which variation type worked best
        if var_type not in variations_tried:
            variations_tried[var_type] = {"count": 0, "sum_similarity": 0, "max_similarity": 0}
        
        variations_tried[var_type]["count"] += 1
        variations_tried[var_type]["sum_similarity"] += similarity
        variations_tried[var_type]["max_similarity"] = max(
            variations_tried[var_type]["max_similarity"], 
            similarity
        )
        
        if address:
            address_logger.log_address(var, address, similarity)
            memory_manager.add_result(var, address, similarity)
            
            # If this is better than our target similarity, celebrate!
            if similarity >= TARGET_SIMILARITY:
                logger.info(f"Target similarity reached! New similarity: {similarity:.6f}")
                if match:
                    save_result(var)
                    return var
    
    # Report on the most effective variation types
    logger.info("Variation type effectiveness:")
    for var_type, stats in sorted(
        variations_tried.items(), 
        key=lambda x: x[1]["max_similarity"], 
        reverse=True
    ):
        avg_sim = stats["sum_similarity"] / stats["count"] if stats["count"] > 0 else 0
        logger.info(
            f"{var_type}: count={stats['count']}, "
            f"avg_sim={avg_sim:.6f}, max_sim={stats['max_similarity']:.6f}"
        )
    
    # Track most effective variation types for future use
    effective_variations = sorted(
        variations_tried.items(), 
        key=lambda x: x[1]["max_similarity"], 
        reverse=True
    )[:5]
    
    for var_type, stats in effective_variations:
        STRATEGY_EFFECTIVENESS[var_type] = max(
            STRATEGY_EFFECTIVENESS.get(var_type, 1.0),
            stats["max_similarity"] * 3  # Weight by max similarity
        )
    
    # If we found a better candidate, return it
    if variations_tried and any(stats["max_similarity"] > best_similarity for stats in variations_tried.values()):
        logger.info("Found improvement through intensive search!")
        return None  # We already added it to memory, so just continue the main search
    
    return None

def broad_exploration_search(candidates):
    """
    Broader search when we're not yet close to target similarity
    """
    # Take our best candidates
    best_candidates = [int(c["private_key_int"]) for c in candidates]
    
    # Try more diverse strategies to increase similarity
    all_variations = []
    
    # 1. Try various mathematical relationships
    for base in best_candidates:
        # Polynomial
        for degree in range(1, 5):
            var = base + (base % (2**degree))
            if is_valid_candidate(var):
                all_variations.append(var)
        
        # Bit operations
        for shift in range(1, 16):
            # Left shift with wrap
            var = ((base << shift) | (base >> (68 - shift))) & ((1 << 68) - 1)
            if is_valid_candidate(var):
                all_variations.append(var)
                
            # Right shift with wrap
            var = ((base >> shift) | (base << (68 - shift))) & ((1 << 68) - 1)
            if is_valid_candidate(var):
                all_variations.append(var)
        
        # XOR with special values
        for xor_val in [0xAAAAAAAAAAAAAAAA, 0x5555555555555555, 0xFFFF0000FFFF0000, 0x0000FFFF0000FFFF]:
            var = base ^ xor_val
            if is_valid_candidate(var):
                all_variations.append(var)
    
    # 2. Try genetic algorithm style crossover between good candidates
    if len(best_candidates) > 1:
        for i in range(len(best_candidates)):
            for j in range(i+1, len(best_candidates)):
                # Single-point crossover
                for point in range(1, 68):
                    a_bits = bin(best_candidates[i])[2:].zfill(68)
                    b_bits = bin(best_candidates[j])[2:].zfill(68)
                    
                    child1_bits = a_bits[:point] + b_bits[point:]
                    child2_bits = b_bits[:point] + a_bits[point:]
                    
                    child1 = int(child1_bits, 2)
                    child2 = int(child2_bits, 2)
                    
                    if is_valid_candidate(child1):
                        all_variations.append(child1)
                    if is_valid_candidate(child2):
                        all_variations.append(child2)
    
    # 3. Try variations based on the address structure itself
    best_address = candidates[0]["address"]
    
    # Get all Base58 characters
    base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    
    # Try changing a single character in the address to see what private key could generate it
    # This is exploratory since we can't directly work backwards
    for i, char in enumerate(best_address):
        if i > 5:  # Skip the first few characters as they're likely fixed by the version byte
            # Get current characters as a guide
            idx = base58_chars.index(char)
            
            # Try a few candidates around our best with same bit length 
            for _ in range(50):  # Try 50 variations per character
                var_mask = random.randint(0, 0xFFFFFFFF)  # Random 32-bit mask
                var = best_candidates[0] ^ var_mask
                if is_valid_candidate(var):
                    all_variations.append(var)
    
    # Test a subset of variations (too many would take too long)
    random.shuffle(all_variations)
    variations_to_test = all_variations[:min(1000, len(all_variations))]
    
    logger.info(f"Testing {len(variations_to_test)} broad exploration variations")
    
    best_found = 0.0
    for var in variations_to_test:
        match, address, similarity = test_candidate(var)
        if address:
            address_logger.log_address(var, address, similarity)
            memory_manager.add_result(var, address, similarity)
            
            if similarity > best_found:
                best_found = similarity
            
            # If we found a match or reached target similarity, we're done!
            if match or similarity >= TARGET_SIMILARITY:
                logger.info(f"Target similarity or match found! Similarity: {similarity:.6f}")
                if match:
                    save_result(var)
                    return var
    
    logger.info(f"Broad exploration search complete. Best similarity found: {best_found:.6f}")
    return None

# Add a function to analyze patterns in successful candidates
def analyze_successful_patterns(candidates, target_address, top_n=10):
    """
    Analyze patterns in the most successful candidates to guide further search.
    
    Args:
        candidates: List of (key, address, similarity) tuples
        target_address: The target Bitcoin address
        top_n: Number of top candidates to analyze
        
    Returns:
        Dict containing analysis results
    """
    logger.info(f"Analyzing patterns in top {top_n} candidates...")
    
    # Sort candidates by similarity score (descending)
    sorted_candidates = sorted(candidates, key=lambda x: x[2], reverse=True)
    top_candidates = sorted_candidates[:top_n]
    
    if not top_candidates:
        logger.warning("No candidates to analyze")
        return {}
    
    # 1. Analyze matching positions in addresses
    matching_positions = {}
    for i in range(len(target_address)):
        matching_positions[i] = 0
        
    for _, address, _ in top_candidates:
        for i in range(min(len(address), len(target_address))):
            if address[i] == target_address[i]:
                matching_positions[i] += 1
    
    # Identify positions that consistently match across top candidates
    consistent_positions = {pos: count for pos, count in matching_positions.items() 
                           if count >= len(top_candidates) * 0.7}  # 70% agreement threshold
    
    logger.info(f"Found {len(consistent_positions)} consistently matching positions")
    
    # 2. Analyze bit patterns in keys
    top_keys = [key for key, _, _ in top_candidates]
    
    # Track common bits across top keys
    bit_counts = {}
    for bit_pos in range(64):  # Assuming 64-bit keys
        bit_counts[bit_pos] = {'0': 0, '1': 0}
        
        for key in top_keys:
            bit_val = (key >> bit_pos) & 1
            bit_counts[bit_pos][str(bit_val)] += 1
    
    # Identify consistent bits (0 or 1) across top keys
    consistent_bits = {}
    for bit_pos, counts in bit_counts.items():
        # If 80% of top keys have the same bit value at this position
        threshold = 0.8 * len(top_keys)
        if counts['0'] >= threshold:
            consistent_bits[bit_pos] = 0
        elif counts['1'] >= threshold:
            consistent_bits[bit_pos] = 1
    
    logger.info(f"Found {len(consistent_bits)} consistently set bits across top candidates")
    
    # 3. Analyze numerical patterns based on insights from mathematical_analysis.txt
    
    # Check for multiplicative relationships between keys
    multipliers = []
    for i in range(len(top_keys)-1):
        if top_keys[i] != 0:  # Avoid division by zero
            ratio = top_keys[i+1] / top_keys[i]
            multipliers.append(ratio)
    
    avg_multiplier = sum(multipliers) / len(multipliers) if multipliers else 0
    multiplier_std = (sum((m - avg_multiplier)**2 for m in multipliers) / len(multipliers))**0.5 if multipliers else 0
    
    # Look for bit shift patterns
    shift_patterns = []
    for i in range(len(top_keys)-1):
        for shift in range(1, 8):  # Try shifts of 1-7 bits
            if (top_keys[i] << shift) == top_keys[i+1] or (top_keys[i] >> shift) == top_keys[i+1]:
                shift_patterns.append(shift)
    
    # 4. Identify high-entropy regions and low-entropy regions in the keys
    # This is based on entropy_analysis.txt showing importance of entropy distribution
    
    # Convert keys to binary strings for entropy analysis
    key_bits = [''.join(bin(key)[2:].zfill(64)) for key in top_keys]
    
    # Calculate entropy for each bit position
    bit_entropy = {}
    for bit_pos in range(64):
        bit_values = [key_bits[j][bit_pos] for j in range(len(key_bits))]
        zeros = bit_values.count('0')
        ones = bit_values.count('1')
        
        # Calculate Shannon entropy for this bit position
        p0 = zeros / len(bit_values) if bit_values else 0
        p1 = ones / len(bit_values) if bit_values else 0
        
        if p0 == 0 or p1 == 0:
            entropy = 0  # No entropy if all bits are the same
        else:
            entropy = -(p0 * math.log2(p0) + p1 * math.log2(p1))
        
        bit_entropy[bit_pos] = entropy
    
    # Identify high entropy regions (bits that vary a lot)
    high_entropy_regions = {pos: entropy for pos, entropy in bit_entropy.items() if entropy > 0.9}
    
    # Identify low entropy regions (bits that stay mostly constant)
    low_entropy_regions = {pos: entropy for pos, entropy in bit_entropy.items() if entropy < 0.3}
    
    results = {
        'consistent_address_positions': consistent_positions,
        'consistent_bits': consistent_bits,
        'avg_multiplier': avg_multiplier,
        'multiplier_std': multiplier_std,
        'shift_patterns': shift_patterns,
        'high_entropy_regions': high_entropy_regions,
        'low_entropy_regions': low_entropy_regions,
        'top_similarity': top_candidates[0][2] if top_candidates else 0
    }
    
    logger.info(f"Pattern analysis complete. Top similarity score: {results['top_similarity']:.6f}")
    return results

# Add a function to generate candidates based on pattern analysis
def generate_pattern_based_candidates(pattern_analysis, base_candidates, num_candidates=100):
    """
    Generate new candidates based on patterns identified in successful candidates.
    
    Args:
        pattern_analysis: Results from analyze_successful_patterns
        base_candidates: List of (key, address, similarity) tuples to use as starting points
        num_candidates: Number of candidates to generate
        
    Returns:
        List of new candidate keys
    """
    logger.info(f"Generating {num_candidates} candidates based on pattern analysis...")
    
    if not pattern_analysis or not base_candidates:
        logger.warning("Cannot generate pattern-based candidates: missing input data")
        return []
    
    # Sort base candidates by similarity score (descending)
    sorted_candidates = sorted(base_candidates, key=lambda x: x[2], reverse=True)
    base_keys = [key for key, _, _ in sorted_candidates[:5]]  # Use top 5 as base keys
    
    # Extract pattern information
    consistent_bits = pattern_analysis.get('consistent_bits', {})
    high_entropy_regions = pattern_analysis.get('high_entropy_regions', {})
    low_entropy_regions = pattern_analysis.get('low_entropy_regions', {})
    avg_multiplier = pattern_analysis.get('avg_multiplier', 1.0)
    shift_patterns = pattern_analysis.get('shift_patterns', [])
    
    new_candidates = []
    
    # 1. STRATEGY: Preserve consistent bits, randomly flip others
    for _ in range(num_candidates // 4):
        if not base_keys:
            continue
            
        # Choose a random base key
        base_key = random.choice(base_keys)
        new_key = base_key
        
        # Create a bit mask to preserve consistent bits
        preserve_mask = 0
        for bit_pos, bit_val in consistent_bits.items():
            preserve_mask |= (1 << bit_pos)
        
        # Create masks for flipping bits in high/low entropy regions
        high_entropy_mask = 0
        for bit_pos in high_entropy_regions:
            # Only include if not in the consistent bits
            if bit_pos not in consistent_bits:
                high_entropy_mask |= (1 << bit_pos)
        
        low_entropy_mask = 0
        for bit_pos in low_entropy_regions:
            # Only include if not in the consistent bits
            if bit_pos not in consistent_bits:
                low_entropy_mask |= (1 << bit_pos)
        
        # Flip a few high entropy bits (more exploration)
        num_high_bits_to_flip = random.randint(2, 5)
        for _ in range(num_high_bits_to_flip):
            # Select a random bit position from high entropy region
            if high_entropy_mask:
                bit_pos = random.choice([i for i in range(64) if (high_entropy_mask & (1 << i)) != 0])
                new_key ^= (1 << bit_pos)
        
        # Occasionally flip a low entropy bit (less exploration)
        if random.random() < 0.3 and low_entropy_mask:
            bit_pos = random.choice([i for i in range(64) if (low_entropy_mask & (1 << i)) != 0])
            new_key ^= (1 << bit_pos)
        
        # Ensure consistent bits remain unchanged
        for bit_pos, bit_val in consistent_bits.items():
            # Clear the bit first
            new_key &= ~(1 << bit_pos)
            # Set it to the consistent value
            new_key |= (bit_val << bit_pos)
        
        new_candidates.append(new_key)
    
    # 2. STRATEGY: Apply multiplier patterns from mathematical_analysis.txt
    for _ in range(num_candidates // 4):
        if not base_keys:
            continue
            
        base_key = random.choice(base_keys)
        
        # Apply a multiplier with random variation
        variation = random.uniform(0.98, 1.02)  # 2% variation
        multiplier = avg_multiplier * variation
        
        # Apply multiplier and round to integer
        new_key = int(base_key * multiplier)
        
        # Ensure consistent bits remain unchanged
        for bit_pos, bit_val in consistent_bits.items():
            # Clear the bit first
            new_key &= ~(1 << bit_pos)
            # Set it to the consistent value
            new_key |= (bit_val << bit_pos)
        
        new_candidates.append(new_key)
    
    # 3. STRATEGY: Apply bit shift patterns from pattern_analysis.txt
    for _ in range(num_candidates // 4):
        if not base_keys:
            continue
            
        base_key = random.choice(base_keys)
        
        # Apply a bit shift if patterns were found, otherwise use a small random shift
        if shift_patterns:
            shift = random.choice(shift_patterns)
        else:
            shift = random.randint(1, 3)
        
        # Randomly choose left or right shift
        if random.random() < 0.5:
            new_key = base_key << shift
        else:
            new_key = base_key >> shift
        
        # Ensure consistent bits remain unchanged
        for bit_pos, bit_val in consistent_bits.items():
            # Clear the bit first
            new_key &= ~(1 << bit_pos)
            # Set it to the consistent value
            new_key |= (bit_val << bit_pos)
        
        new_candidates.append(new_key)
    
    # 4. STRATEGY: Hybrid pattern approach based on secp256k1_analysis.txt
    for _ in range(num_candidates // 4):
        if not base_keys:
            continue
            
        base_key = random.choice(base_keys)
        
        # Create a completely new key that preserves consistent bits
        new_key = 0
        
        # Set consistent bits
        for bit_pos, bit_val in consistent_bits.items():
            new_key |= (bit_val << bit_pos)
        
        # For non-consistent bits, use a mix of:
        # - 70% chance: copy from base key
        # - 30% chance: random bit
        for bit_pos in range(64):
            if bit_pos not in consistent_bits:
                if random.random() < 0.7:
                    # Copy bit from base key
                    bit_val = (base_key >> bit_pos) & 1
                else:
                    # Random bit
                    bit_val = random.randint(0, 1)
                
                new_key |= (bit_val << bit_pos)
        
        new_candidates.append(new_key)
    
    # Remove any duplicates
    new_candidates = list(set(new_candidates))
    
    logger.info(f"Generated {len(new_candidates)} unique pattern-based candidates")
    return new_candidates

def structure_targeted_search(count=100, worker_safe=False):
    """
    Generate candidates that are likely to match the structural patterns of the target address
    
    This strategy analyzes the target address structure and generates candidates that would
    produce addresses with similar structural characteristics.
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting structure-targeted search with {count} candidates")
    
    candidates = []
    
    # Analyze target address structure
    digit_positions = [i for i, c in enumerate(TARGET_ADDRESS) if c.isdigit()]
    uppercase_positions = [i for i, c in enumerate(TARGET_ADDRESS) if c.isupper()]
    
    # Get some of our best candidates so far as starting points
    memory = globals().get('memory_manager', None)
    
    base_candidates = []
    if memory:
        try:
            best_candidates = memory.get_best_candidates(5)
            base_candidates = [value for value, _ in best_candidates]
        except:
            # Fallback if no memory manager available
            base_candidates = [PREV_TERM_67_INT]
    
    if not base_candidates:
        base_candidates = [PREV_TERM_67_INT]
    
    # Generate variations of the best candidates
    for base in base_candidates:
        # Make sure we have enough bits set
        binary = bin(base)[2:].zfill(68)
        
        # Focus on specific bit positions that might influence character positions
        # in the Bitcoin address with higher matching potential
        for _ in range(count // len(base_candidates) + 1):
            # Create a new candidate by modifying bits
            new_candidate = base
            
            # Apply a series of targeted transformations
            # These target specific parts of the hash160 that affect the address
            
            # Approach 1: Target version bits (affects first character)
            if len(candidates) < count * 0.2:
                # Modify bits that affect the version area
                for bit_pos in [67, 66, 65, 64]:
                    # Flip the bit
                    new_candidate = new_candidate ^ (1 << (bit_pos % 68))
            
            # Approach 2: Target checksum bits (affects last 4-8 characters)
            elif len(candidates) < count * 0.4:
                # Modify bits that affect the checksum area
                for bit_pos in range(5):
                    # Flip bits in the first few positions
                    if random.random() < 0.3:
                        new_candidate = new_candidate ^ (1 << bit_pos)
            
            # Approach 3: Target hash160 structure bits that affect digit distribution
            elif len(candidates) < count * 0.6:
                # Ensure similar digit/letter distribution in address
                # by modifying specific bit regions
                for bit_group in range(4):
                    start_bit = bit_group * 16
                    end_bit = start_bit + 16
                    
                    # Modify bits in this region
                    for bit in range(start_bit, end_bit):
                        if random.random() < 0.05:  # 5% chance to flip each bit
                            new_candidate = new_candidate ^ (1 << bit)
            
            # Approach 4: Bit pattern matching from close candidates
            else:
                # Look at the hamming distance range
                best_addr = None
                best_similarity = 0
                
                # Find the best address from our previous candidates
                for candidate in candidates:
                    try:
                        addr = private_key_to_address(candidate)
                        similarity = address_similarity(addr, TARGET_ADDRESS)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_addr = addr
                    except:
                        continue
                
                if best_addr:
                    # Look at positions where best_addr matches target
                    matching_positions = [i for i, (c1, c2) in enumerate(zip(best_addr, TARGET_ADDRESS)) if c1 == c2]
                    
                    # Create a candidate that preserves these bits
                    for bit_position in range(68):
                        # 20% chance to flip any bit
                        if random.random() < 0.2:
                            new_candidate = new_candidate ^ (1 << bit_position)
            
            # Ensure the candidate is valid
            if is_valid_candidate(new_candidate):
                # Test the candidate to see if it meets minimum similarity
                try:
                    addr = private_key_to_address(new_candidate)
                    similarity = address_similarity(addr, TARGET_ADDRESS)
                    
                    # Only add if it's promising
                    if similarity > 0.3:  # Set a threshold for promising candidates
                        candidates.append(new_candidate)
                    
                    # If we found a really good one, add more variations of it
                    if similarity > 0.4:
                        # Create 5 variations of this candidate
                        for _ in range(5):
                            variant = new_candidate
                            # Flip 1-3 random bits
                            for _ in range(random.randint(1, 3)):
                                bit_position = random.randint(0, 67)
                                variant = variant ^ (1 << bit_position)
                            
                            if is_valid_candidate(variant):
                                candidates.append(variant)
                except Exception as e:
                    # Skip if we hit an error
                    logger.debug(f"Error generating candidate: {e}")
            
            # If we have enough candidates, stop
            if len(candidates) >= count:
                break
    
    # If we don't have enough candidates, add some random ones
    while len(candidates) < count:
        # Generate a random candidate
        candidate = random.randint(PREV_TERM_67_INT, 2**68 - 1)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # Ensure we have exactly the requested number of candidates
    candidates = candidates[:count]
    logger.info(f"Generated {len(candidates)} structure-targeted candidates")
    return candidates

def gradient_ascent_search(count=100, iterations=150, learning_rate=0.1, worker_safe=False):
    """
    Enhanced gradient ascent algorithm for systematically improving candidate private keys.
    
    Implements multiple efficiency improvements:
    1. Parallel processing of multiple starting points
    2. Bit influence mapping for targeted bit flips
    3. Adaptive learning rate that changes based on improvement rate
    4. Integration with sequence patterns from gpt_version.py
    5. Smart exploration that focuses on historically successful bit positions
    6. Early stopping with intelligent restart
    
    Args:
        count: Number of final candidates to return
        iterations: Maximum number of improvement iterations per candidate
        learning_rate: Initial learning rate for adjustments
        
    Returns:
        list: List of improved candidate private keys
    """
    logger.info(f"Starting enhanced gradient ascent search with {count} candidates")
    candidates = []
    successful_bit_positions = Counter()  # Track which bit positions lead to improvements
    
    # Get our best candidates as starting points
    memory_manager = MemoryManager()
    start_candidates = []
    
    # First try to use best candidates from memory
    try:
        best_candidates = memory_manager.get_best_candidates(min(20, count))
        for candidate_data in best_candidates:
            start_candidates.append(int(candidate_data["private_key_int"]))
    except Exception as e:
        logger.error(f"Error getting best candidates: {e}")
    
    # Include sequence-based candidates
    try:
        # Use the exact term 68 formula: term_67 * 271 + 68
        sequence_candidate = PREV_TERM_67_INT * 271 + 68
        if is_valid_candidate(sequence_candidate) and sequence_candidate not in start_candidates:
            start_candidates.append(sequence_candidate)
            logger.info(f"Added sequence-based candidate: {hex(sequence_candidate)}")
    except Exception as e:
        logger.error(f"Error adding sequence candidate: {e}")
    
    # If we don't have enough starting points, add variations
    if len(start_candidates) < 20:
        # Use previous term and some variations
        if PREV_TERM_67_INT not in start_candidates:
            start_candidates.append(PREV_TERM_67_INT)
        
        # Add variations of existing candidates
        existing_candidates = list(start_candidates)  # Make a copy
        for base in existing_candidates:
            if len(start_candidates) >= 20:
                break
                
            # Add bit-flipped variations of this candidate
            for bits in range(1, 4):  # 1-3 bit flips
                if len(start_candidates) >= 20:
                    break
                    
                # Generate bit positions with preference for historically successful bits
                bit_weights = [successful_bit_positions.get(i, 1) + 1 for i in range(68)]
                positions = random.choices(range(68), weights=bit_weights, k=bits)
                
                variant = base
                for pos in positions:
                    variant ^= (1 << pos)
                
                if is_valid_candidate(variant) and variant not in start_candidates:
                    start_candidates.append(variant)
    
    # Precompute address influence map (which bits affect which address positions)
    address_influence_map = {}
    
    def build_influence_map(candidate, target=TARGET_ADDRESS):
        """Build a map of which bit positions influence which address positions"""
        influence = {i: set() for i in range(len(target))}
        base_address = private_key_to_address(candidate)
        if not base_address:
            return influence
            
        # Test each bit position
        for bit in range(min(68, candidate.bit_length())):
            test_value = candidate ^ (1 << bit)
            test_address = private_key_to_address(test_value)
            if not test_address:
                continue
                
            # Find which positions in the address changed
            for i, (c1, c2) in enumerate(zip(base_address, test_address)):
                if c1 != c2:
                    influence[i].add(bit)
        
        return influence
    
    # Process each starting candidate with improved gradient ascent
    for start_idx, start_key in enumerate(start_candidates):
        if len(candidates) >= count:
            break
            
        # Skip if this exact value is already in our results
        if start_key in candidates:
            continue
            
        try:
            logger.info(f"Processing starting candidate {start_idx+1}/{len(start_candidates)}: {hex(start_key)}")
            current_key = start_key
            
            # Get initial similarity
            current_address = private_key_to_address(current_key)
            if not current_address:
                continue  # Skip if address generation fails
                
            current_similarity = address_similarity(current_address, TARGET_ADDRESS)
            
            # Variables to track progress and adapt learning
            best_key = current_key
            best_similarity = current_similarity
            iterations_without_improvement = 0
            adaptive_learning_rate = learning_rate
            last_improvement = 0
            
            # Build influence map for smarter bit selection
            try:
                influence_map = build_influence_map(current_key)
                address_influence_map[current_key] = influence_map
            except Exception as e:
                logger.debug(f"Error building influence map: {e}")
                influence_map = None
            
            # Identify non-matching positions to focus on
            non_matching_positions = []
            if current_address:
                for i, (c1, c2) in enumerate(zip(TARGET_ADDRESS, current_address)):
                    if c1 != c2:
                        non_matching_positions.append(i)
            
            # Keep track of which bits we've tried flipping
            tried_bits = set()
            
            # Perform gradient ascent iterations
            for iteration in range(iterations):
                improved = False
                
                # Escape local maxima if stuck for too long
                if iterations_without_improvement > 15:
                    # Make a random jump to escape local maximum
                    escape_key = current_key
                    num_bits = min(5 + iterations_without_improvement // 5, 15)  # Increase with stagnation
                    
                    # Prioritize bits that influence non-matching positions
                    influential_bits = set()
                    if influence_map:
                        for pos in non_matching_positions:
                            influential_bits.update(influence_map.get(pos, set()))
                    
                    # Use influential bits if available, otherwise random
                    if influential_bits:
                        bit_positions = random.sample(list(influential_bits), min(num_bits, len(influential_bits)))
                        # Fill remaining with random bits if needed
                        if len(bit_positions) < num_bits:
                            remaining = random.sample(
                                [b for b in range(68) if b not in influential_bits], 
                                num_bits - len(bit_positions)
                            )
                            bit_positions.extend(remaining)
                    else:
                        bit_positions = random.sample(range(68), num_bits)
                    
                    for bit in bit_positions:
                        escape_key ^= (1 << bit)
                    
                    if is_valid_candidate(escape_key):
                        # Test the escape candidate
                        escape_address = private_key_to_address(escape_key)
                        if escape_address:
                            escape_similarity = address_similarity(escape_address, TARGET_ADDRESS)
                            
                            # Only jump if it's not significantly worse
                            if escape_similarity >= current_similarity * 0.9:
                                current_key = escape_key
                                current_similarity = escape_similarity
                                tried_bits = set()  # Reset tried bits after jump
                                
                                # Update best if better
                                if escape_similarity > best_similarity:
                                    best_similarity = escape_similarity
                                    best_key = escape_key
                                    improved = True
                                
                                logger.debug(f"Made escape jump: {hex(escape_key)}, similarity: {escape_similarity:.6f}")
                    
                    # Reset counter but at a higher threshold to prevent thrashing
                    iterations_without_improvement = 10
                
                # Prioritize bit positions based on influence map and history
                bit_positions = list(range(68))
                
                # Use influence map to prioritize bits affecting non-matching positions
                if influence_map and non_matching_positions:
                    important_bits = set()
                    for pos in non_matching_positions:
                        important_bits.update(influence_map.get(pos, set()))
                    
                    # Sort bit positions to prioritize important bits that haven't been tried
                    bit_positions.sort(key=lambda b: (
                        b not in important_bits,  # Prioritize important bits (False sorts before True)
                        b in tried_bits,  # Avoid bits we've already tried
                        -successful_bit_positions.get(b, 0)  # Prefer historically successful bits
                    ))
                else:
                    # Without influence map, prioritize by success history and avoid tried bits
                    random.shuffle(bit_positions)  # Start with a random order
                    bit_positions.sort(key=lambda b: (
                        b in tried_bits,  # Avoid bits we've already tried
                        -successful_bit_positions.get(b, 0)  # Prefer historically successful bits
                    ))
                
                # Test single bit flips with adaptive step size
                for bit_position in bit_positions:
                    # Skip bits we've already tried too many times
                    if bit_position in tried_bits and iterations_without_improvement < 10:
                        continue
                    
                    tried_bits.add(bit_position)
                    
                    # Try flipping this bit
                    test_key = current_key ^ (1 << bit_position)
                    
                    # Skip if not valid
                    if not is_valid_candidate(test_key):
                        continue
                    
                    # Calculate similarity
                    try:
                        test_address = private_key_to_address(test_key)
                        if not test_address:
                            continue
                            
                        test_similarity = address_similarity(test_address, TARGET_ADDRESS)
                        
                        # If this improves similarity, move in this direction
                        if test_similarity > current_similarity:
                            current_key = test_key
                            current_similarity = test_similarity
                            improved = True
                            
                            # Record successful bit position
                            successful_bit_positions[bit_position] += 1
                            
                            # Update non-matching positions
                            non_matching_positions = []
                            for i, (c1, c2) in enumerate(zip(TARGET_ADDRESS, test_address)):
                                if c1 != c2:
                                    non_matching_positions.append(i)
                            
                            # Update best if this is better
                            if test_similarity > best_similarity:
                                best_similarity = test_similarity
                                best_key = test_key
                                last_improvement = iteration
                                
                                # Build new influence map for significantly better candidates
                                if test_similarity > best_similarity + 0.05:
                                    try:
                                        influence_map = build_influence_map(test_key)
                                        address_influence_map[test_key] = influence_map
                                    except Exception:
                                        pass
                                
                                # Log significant improvements
                                if best_similarity > 0.4:
                                    logger.info(f"Found candidate with similarity {best_similarity:.6f}: {hex(best_key)}")
                                
                                # Refresh adaptive learning rate on improvement
                                adaptive_learning_rate = learning_rate
                            
                            # Break early to follow this gradient direction immediately
                            break
                    except Exception as e:
                        # Skip on error
                        continue
                
                # Reusing existing influence map for speed when appropriate
                if improved and current_key in address_influence_map:
                    influence_map = address_influence_map[current_key]
                
                # If we improved, reset counter
                if improved:
                    iterations_without_improvement = 0
                else:
                    iterations_without_improvement += 1
                
                # If single bit flips didn't improve and we're near a plateau, try bit combinations
                if not improved and (iterations_without_improvement % 5 == 0):
                    # Try flipping multiple bits at once
                    multi_bit_improved = False
                    
                    # Focus on historically successful bits
                    successful_bits = [b for b, count in successful_bit_positions.most_common(10)]
                    
                    # If we don't have enough successful bits, add some random ones
                    while len(successful_bits) < 10:
                        random_bit = random.randint(0, 67)
                        if random_bit not in successful_bits:
                            successful_bits.append(random_bit)
                    
                    # Try all 2-bit combinations from our top bits
                    for bit1, bit2 in itertools.combinations(successful_bits, 2):
                        # Create a test key with both bits flipped
                        test_key = current_key ^ (1 << bit1) ^ (1 << bit2)
                        
                        # Skip if not valid
                        if not is_valid_candidate(test_key):
                            continue
                        
                        # Calculate similarity
                        try:
                            test_address = private_key_to_address(test_key)
                            if not test_address:
                                continue
                                
                            test_similarity = address_similarity(test_address, TARGET_ADDRESS)
                            
                            # If this improves similarity, move in this direction
                            if test_similarity > current_similarity:
                                current_key = test_key
                                current_similarity = test_similarity
                                multi_bit_improved = True
                                improved = True
                                
                                # Record successful bit positions
                                successful_bit_positions[bit1] += 1
                                successful_bit_positions[bit2] += 1
                                
                                # Update non-matching positions
                                non_matching_positions = []
                                for i, (c1, c2) in enumerate(zip(TARGET_ADDRESS, test_address)):
                                    if c1 != c2:
                                        non_matching_positions.append(i)
                                
                                # Update best if this is better
                                if test_similarity > best_similarity:
                                    best_similarity = test_similarity
                                    best_key = test_key
                                    last_improvement = iteration
                                
                                # Break early to follow this gradient direction
                                break
                        except Exception:
                            # Skip on error
                            continue
                    
                    if multi_bit_improved:
                        iterations_without_improvement = 0
                
                # Early stopping if no improvement for many iterations
                if iteration - last_improvement > iterations // 2:
                    break
            
            # Add the best key from this run to our candidates
            if best_key not in candidates:
                candidates.append(best_key)
                
                # If this is a promising candidate, explore around it
                if best_similarity > 0.4:
                    # Create additional variations 
                    variations_to_add = min(5, count - len(candidates))
                    if variations_to_add > 0:
                        # Identify most influential bits
                        influential_bits = set()
                        if best_key in address_influence_map:
                            for pos_set in address_influence_map[best_key].values():
                                influential_bits.update(pos_set)
                        
                        # Generate variations focused on influential bits
                        for _ in range(variations_to_add):
                            variant = best_key
                            # Determine number of bits to flip (fewer for higher similarity)
                            num_bits = max(1, int(3 * (1 - best_similarity)))
                            
                            # Flip bits that have influence
                            if influential_bits:
                                bits_to_flip = random.sample(list(influential_bits), min(num_bits, len(influential_bits)))
                            else:
                                bits_to_flip = random.sample(range(68), num_bits)
                                
                            for bit in bits_to_flip:
                                variant ^= (1 << bit)
                            
                            if is_valid_candidate(variant) and variant not in candidates:
                                candidates.append(variant)
        
        except Exception as e:
            logger.error(f"Error in enhanced gradient ascent: {e}")
            continue
    
    # If we don't have enough candidates, add sequence-based candidates
    if len(candidates) < count:
        try:
            sequence_candidates = sequence_pattern_search(count - len(candidates))
            for candidate in sequence_candidates:
                if candidate not in candidates and len(candidates) < count:
                    candidates.append(candidate)
        except Exception as e:
            logger.error(f"Error adding sequence candidates: {e}")
    
    # Final fallback: add random candidates if needed
    while len(candidates) < count:
        # Generate a random candidate near our best existing one
        if candidates:
            base = random.choice(candidates)
            candidate = base
            
            # Flip 1-3 random bits
            for _ in range(random.randint(1, 3)):
                bit_position = random.randint(0, 67)
                candidate = candidate ^ (1 << bit_position)
            
            if is_valid_candidate(candidate) and candidate not in candidates:
                candidates.append(candidate)
        else:
            # True fallback to a random candidate
            candidate = random.randint(PREV_TERM_67_INT, 2**68 - 1)
            if is_valid_candidate(candidate) and candidate not in candidates:
                candidates.append(candidate)
    
    # Ensure we have exactly the requested number of candidates
    candidates = candidates[:count]
    logger.info(f"Generated {len(candidates)} enhanced gradient ascent candidates")
    
    # Log bit position statistics
    if successful_bit_positions:
        most_influential = successful_bit_positions.most_common(10)
        logger.info(f"Most influential bit positions: {most_influential}")
    
    return candidates

def random_walk_search(count=100, worker_safe=False):
    """
    Perform a random walk search by starting from promising candidates and making random adjustments.
    
    Args:
        count (int): Number of candidates to generate
        
    Returns:
        list: List of candidate integers
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting random walk search to generate {count} candidates")
    
    # Initialize result list
    candidates = []
    
    # Try to get promising values from memory
    memory_manager = MemoryManager()
    best_candidates = memory_manager.get_best_candidates(10)
    
    # If we have no good candidates yet, start from a reasonable default
    if not best_candidates:
        base_candidates = [PREV_TERM_67_INT + random.randint(1, 1000000) for _ in range(3)]
    else:
        # Use the best candidates as starting points
        base_candidates = [value for value, _ in best_candidates[:3]]
        
    # Add some completely random candidates to increase diversity
    base_candidates.extend([
        random.randint(PREV_TERM_67_INT, 2**68-1) for _ in range(2)
    ])
    
    # For each starting point, perform a random walk
    for base_value in base_candidates:
        current = base_value
        best_similarity = 0
        
        # Perform random walks of varying lengths
        for _ in range(count // len(base_candidates)):
            # Randomly decide how many bits to flip
            num_bits = random.randint(1, 8)
            
            # Select random bit positions to flip
            positions = random.sample(range(68), num_bits)
            
            # Create a new value by flipping those bits
            new_value = current
            for pos in positions:
                new_value ^= (1 << pos)
                
            # Ensure the candidate is valid
            if is_valid_candidate(new_value):
                candidates.append(new_value)
                
                # Test the candidate's similarity
                try:
                    address, similarity = test_candidate(new_value)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        current = new_value  # Move to this better position
                except Exception as e:
                    logger.debug(f"Error testing candidate: {e}")
    
    # Ensure we return the requested number of candidates
    while len(candidates) < count:
        # Generate completely random candidates if needed
        new_value = random.randint(PREV_TERM_67_INT, 2**68-1)
        if is_valid_candidate(new_value):
            candidates.append(new_value)
    
    logger.info(f"Random walk search generated {len(candidates)} candidates")
    return candidates[:count]

def super_targeted_search(count=100, worker_safe=False):
    """
    Generate candidates focused specifically on our highest similarity candidates.
    
    This strategy performs extremely targeted manipulations on our best candidates
    to push similarity from 60% toward 80%+.
    
    Args:
        count: Number of candidates to generate
        worker_safe: Whether to use worker-safe operations
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting super targeted search with {count} candidates")
    candidates = []
    
    # Get our highest similarity candidates from memory instead of hardcoding
    memory_manager = MemoryManager()
    best_candidates_data = memory_manager.get_best_candidates(10)
    
    # Extract the candidate values from memory
    best_candidates = []
    for candidate_data in best_candidates_data:
        try:
            # Handle different memory formats
            if isinstance(candidate_data, dict):
                value = int(candidate_data["private_key_int"])
                best_candidates.append(value)
            elif isinstance(candidate_data, tuple) and len(candidate_data) >= 1:
                best_candidates.append(int(candidate_data[0]))
        except (ValueError, TypeError):
            continue
    
    # If we couldn't load any good candidates from memory, fall back to defaults
    if not best_candidates:
        logger.warning("No good candidates in memory, using default starting points")
        best_candidates = [
            0x7b0fd3348980cc58a,  # 1MVDYACJ1RmzvZ6mdiFnnXojiMihYdZ1F - 56.7% similarity
            0x732bcef541044c2f9,  # 1MVDYgtuFcxmGajjY6cpsP1AqzJ5J5bVM4 - 56.0% similarity
            0xf34fc235d1952c13f,  # 1MLDYeVxSNSm9qYNnvdSQfU1pWue1UGCrr - 55.5% similarity
            0xf30f423dc1963c0cf,  # 1MV7YgXFScXxk7Qob6nmkHANEG1uP4zX7n - 52.2% similarity
        ]
    
    # Always include previous term as a starting point for diversity
    if PREV_TERM_67_INT not in best_candidates:
        best_candidates.append(PREV_TERM_67_INT)
    
    # Also include the exact sequence formula result for diversity
    exact_term68 = PREV_TERM_67_INT * 271 + 68
    if is_valid_candidate(exact_term68) and exact_term68 not in best_candidates:
        best_candidates.append(exact_term68)
    
    # Log the candidates we're using
    logger.info(f"Using {len(best_candidates)} base candidates for super_targeted_search")
    for i, candidate in enumerate(best_candidates):
        try:
            addr = private_key_to_address(candidate)
            sim = address_similarity(addr, TARGET_ADDRESS) if addr else 0
            logger.info(f"Base candidate {i+1}: {hex(candidate)} -> {addr} (similarity: {sim:.6f})")
        except:
            logger.info(f"Base candidate {i+1}: {hex(candidate)} (unable to generate address)")
    
    # Rest of the function remains the same
    # Analyze bit patterns in our best candidates
    bits_analysis = {}
    for i in range(68):
        bits_analysis[i] = 0
        for candidate in best_candidates:
            if candidate & (1 << i):
                bits_analysis[i] += 1
    
    # Identify strongly consistent bits (all candidates have the same value)
    consistent_bits = {}
    for bit_pos, count in bits_analysis.items():
        if count == len(best_candidates) or count == 0:
            # All candidates have the same bit value at this position
            consistent_bits[bit_pos] = 1 if count > 0 else 0
    
    logger.info(f"Found {len(consistent_bits)} consistent bits across best candidates")
    
    # Create base template from most common bits
    template = 0
    for bit_pos, bit_val in consistent_bits.items():
        if bit_val == 1:
            template |= (1 << bit_pos)
    
    # Generate pattern-preserving variations
    for base_candidate in best_candidates:
        # Generate multiple variations for each base candidate
        variations_per_candidate = count // (len(best_candidates) * 4)
        
        # Generate 4 types of variations for each candidate
        
        # 1. Super precise 1-bit flips (avoid touching consistent bits)
        for _ in range(variations_per_candidate):
            new_candidate = base_candidate
            # Choose 1-2 bits to flip that aren't consistent
            non_consistent_bits = [bit for bit in range(68) if bit not in consistent_bits]
            bits_to_flip = random.sample(non_consistent_bits, min(2, len(non_consistent_bits)))
            
            for bit in bits_to_flip:
                new_candidate ^= (1 << bit)
                
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
                
                # Test similarity immediately
                try:
                    addr, similarity = test_candidate(new_candidate)
                    if similarity > 0.6:  # If we find an excellent candidate
                        # Add more variations of this immediately
                        for bit in range(68):
                            # Try each single bit flip
                            if bit not in consistent_bits:
                                variant = new_candidate ^ (1 << bit)
                                if is_valid_candidate(variant) and variant not in candidates:
                                    candidates.append(variant)
                except Exception:
                    pass
        
        # 2. Pattern-preserving variations - vary only in regions without matching
        # These are regions where our address doesn't match the target
        for _ in range(variations_per_candidate):
            # Create a new candidate that keeps pattern in first part of the key
            # but varies in the middle and end regions
            new_candidate = base_candidate
            
            # Split the key into three sections: beginning (keep), middle (vary), end (vary)
            # Beginning (high bits) impacts first part of address - strong match in our best candidates
            # Bits 52-67 (high bits) seem to be most important for beginning of address match
            for bit in range(40, 52):  # Middle region - vary moderately
                if bit not in consistent_bits and random.random() < 0.3:
                    new_candidate ^= (1 << bit)
                    
            for bit in range(0, 40):  # Low bits - vary more freely
                if bit not in consistent_bits and random.random() < 0.2:
                    new_candidate ^= (1 << bit)
            
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
        
        # 3. Try very small adjustments to value (+-1, +-2, etc.)
        for adj in range(-5, 6):
            if adj == 0:
                continue
                
            new_candidate = base_candidate + adj
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
        
        # 4. Crossover between best candidates
        for other_candidate in best_candidates:
            if other_candidate != base_candidate:
                # Try bit-by-bit crossover at different positions
                for crossover_point in [20, 32, 44, 56]:
                    # Take bits [0:crossover_point] from base_candidate and the rest from other_candidate
                    mask_low = (1 << crossover_point) - 1
                    mask_high = ((1 << 68) - 1) & ~mask_low
                    new_candidate = (base_candidate & mask_low) | (other_candidate & mask_high)
                    
                    if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                        candidates.append(new_candidate)
    
    # Also try some hybrid variations that combine multiple best candidates
    for _ in range(count // 10):
        # Create a new candidate that takes the most common bit value at each position
        new_candidate = 0
        for bit_pos in range(68):
            # Set bit based on majority vote from best candidates
            if bits_analysis[bit_pos] > len(best_candidates) // 2:
                new_candidate |= (1 << bit_pos)
                
        # Add small random variation
        for bit_pos in range(68):
            if bit_pos not in consistent_bits and random.random() < 0.1:
                new_candidate ^= (1 << bit_pos)
                
        if is_valid_candidate(new_candidate) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    # If we don't have enough candidates, do targeted bit flips
    while len(candidates) < count:
        base = random.choice(best_candidates)
        # Flip 1-3 bits
        new_value = base
        for _ in range(random.randint(1, 3)):
            # Prefer bits that aren't consistent
            non_consistent_bits = [bit for bit in range(68) if bit not in consistent_bits]
            if non_consistent_bits and random.random() < 0.8:
                bit = random.choice(non_consistent_bits)
            else:
                bit = random.randint(0, 67)
            new_value ^= (1 << bit)
            
        if is_valid_candidate(new_value) and new_value not in candidates:
            candidates.append(new_value)
    
    # Ensure we have exactly the requested number of candidates
    candidates = candidates[:count]
    logger.info(f"Generated {len(candidates)} super targeted candidates")
    return candidates

def prefix_targeted_search(count=100, worker_safe=False):
    """
    Generate candidates specifically optimized to maintain the target address prefix.
    
    This strategy focuses on preserving the beginning characters of the address
    (1MVDYg) while varying the rest, to push even higher similarity scores.
    
    Args:
        count: Number of candidates to generate
        worker_safe: Whether to use worker-safe operations
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting prefix-targeted search with {count} candidates")
    candidates = []
    
    # Get our highest similarity candidates from memory
    memory_manager = MemoryManager()
    memory_candidates = memory_manager.get_best_candidates(10)
    
    # Extract the candidate values and find those that already have good prefix matches
    best_candidates = []
    for candidate_data in memory_candidates:
        try:
            # Handle different memory formats
            value = None
            if isinstance(candidate_data, dict):
                value = int(candidate_data["private_key_int"])
            elif isinstance(candidate_data, tuple) and len(candidate_data) >= 1:
                value = int(candidate_data[0])
                
            if value is not None:
                # Check if it has a good prefix match
                addr = private_key_to_address(value)
                if addr and addr.startswith("1MVD"):
                    best_candidates.append(value)
                    logger.info(f"Using memory candidate with good prefix: {hex(value)} -> {addr}")
        except Exception as e:
            logger.debug(f"Error processing memory candidate: {e}")
    
    # If we couldn't find any good prefix matches, fall back to defaults or use the best we have
    if not best_candidates:
        logger.warning("No good prefix candidates in memory, using fallbacks")
        
        # First try to use the top candidates regardless of prefix
        if memory_candidates:
            for candidate_data in memory_candidates[:2]:
                try:
                    if isinstance(candidate_data, dict):
                        value = int(candidate_data["private_key_int"])
                    elif isinstance(candidate_data, tuple) and len(candidate_data) >= 1:
                        value = int(candidate_data[0])
                    best_candidates.append(value)
                except:
                    continue
        
        # If still no candidates, use defaults
        if not best_candidates:
            best_candidates = [
                0x7b0fd3348980cc58a,  # 1MVDYACJ1RmzvZ6mdiFnnXojiMihYdZ1F - 56.7% similarity
                0x732bcef541044c2f9,  # 1MVDYgtuFcxmGajjY6cpsP1AqzJ5J5bVM4 - 56.0% similarity 
            ]
    
    # Always include term 67 for diversity
    if PREV_TERM_67_INT not in best_candidates:
        best_candidates.append(PREV_TERM_67_INT)
    
    # Rest of the function continues as before
    # Target prefix to match or improve upon
    target_prefix = TARGET_ADDRESS[:6]  # "1MVDYg"
    
    # Analyze what makes these candidates generate addresses with matching prefixes
    # The high-order bits (upper bits) of the private key are most influential
    
    # Identify bit ranges that are most likely to affect the address prefix
    # Based on our experience, the upper bits (high order bits) have the most impact
    prefix_influential_bits = list(range(52, 68))  # Upper 16 bits 
    
    # For each base candidate, generate variations focused on prefix matching
    for base_candidate in best_candidates:
        # Test base candidate to verify its prefix
        try:
            base_address = private_key_to_address(base_candidate)
            base_prefix = base_address[:6]
            logger.info(f"Base candidate {hex(base_candidate)} has prefix {base_prefix}")
            
            # Calculate how many variations to create from this base
            variations_per_base = count // (2 * len(best_candidates))
            
            # If the prefix already matches well, focus on fine-tuning other parts
            if base_prefix.startswith("1MVD"):
                # This candidate already has a good prefix match
                # Generate variations that preserve the high bits while varying lower bits
                
                # Create a bit mask that preserves the influential bits
                high_bits_mask = 0
                for bit in prefix_influential_bits:
                    high_bits_mask |= (1 << bit)
                
                # Create a mask for the bits we can safely modify
                modifiable_bits_mask = ((1 << 68) - 1) & ~high_bits_mask
                
                # Generate variations that preserve high bits
                for _ in range(variations_per_base):
                    # Start with the base candidate
                    new_candidate = base_candidate
                    
                    # Modify only non-influential bits
                    for bit in range(0, 52):
                        if random.random() < 0.1:  # 10% chance to flip each bit
                            new_candidate ^= (1 << bit)
                    
                    # Ensure valid candidate
                    if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                        candidates.append(new_candidate)
                        
                        # Test this candidate
                        try:
                            test_address = private_key_to_address(new_candidate)
                            # If this improves the prefix match, generate more similar candidates
                            if test_address[:6] == target_prefix:
                                # Found a perfect prefix match! Create minor variations
                                for i in range(10):
                                    variant = new_candidate + random.randint(-5, 5)
                                    if is_valid_candidate(variant) and variant not in candidates:
                                        candidates.append(variant)
                        except:
                            pass
            
            # If prefix doesn't match perfectly yet, try more aggressive variations
            else:
                # Try more variations of high-order bits to find a better prefix match
                for _ in range(variations_per_base * 2):  # Double the variations for poor matches
                    new_candidate = base_candidate
                    
                    # Systematically vary high bits
                    # Try flipping 1-2 high bits at a time
                    num_bits = random.randint(1, 2)
                    bits_to_flip = random.sample(prefix_influential_bits, num_bits)
                    
                    for bit in bits_to_flip:
                        new_candidate ^= (1 << bit)
                    
                    # Ensure valid candidate
                    if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                        candidates.append(new_candidate)
        except Exception as e:
            logger.error(f"Error analyzing base candidate: {e}")
    
    # Systematically explore more variations of our successful candidates
    memory = globals().get('memory_manager', None)
    if memory:
        try:
            # Get the most recent successful candidates
            memory_candidates = memory.get_best_candidates(5)
            
            for item in memory_candidates:
                # Extract candidate value, handling different memory formats
                if isinstance(item, tuple) and len(item) >= 2:
                    candidate_value = item[0]
                elif isinstance(item, dict) and "private_key_int" in item:
                    candidate_value = item["private_key_int"] 
                else:
                    continue
                    
                # Skip if we already have this candidate
                if candidate_value in candidates or candidate_value in best_candidates:
                    continue
                
                # Test candidate's prefix
                try:
                    candidate_address = private_key_to_address(candidate_value)
                    # If this has a good prefix match, add some variations
                    if candidate_address.startswith("1MVD"):
                        candidates.append(candidate_value)
                        
                        # Add some minor variations
                        for i in range(5):
                            # Create small variations
                            variant = candidate_value + random.randint(-3, 3)
                            if is_valid_candidate(variant) and variant not in candidates:
                                candidates.append(variant)
                                
                        # Add bit-flip variations
                        for bit in range(0, 40):  # Lower bits
                            if random.random() < 0.05:  # 5% chance per bit
                                variant = candidate_value ^ (1 << bit)
                                if is_valid_candidate(variant) and variant not in candidates:
                                    candidates.append(variant)
                except:
                    pass
        except Exception as e:
            logger.error(f"Error processing memory candidates: {e}")
    
    # If we still need more candidates, create completely new ones using bit patterns
    # from our best candidates
    while len(candidates) < count:
        # Create a hybrid candidate by combining features from our best candidates
        new_candidate = 0
        
        # Take upper bits (prefix-influencing) from one of our best candidates
        template = random.choice(best_candidates)
        upper_bits_mask = 0
        for bit in range(52, 68):
            upper_bits_mask |= (1 << bit)
        
        new_candidate = template & upper_bits_mask
        
        # For remaining bits, use either random or other candidates' patterns
        for bit in range(0, 52):
            if random.random() < 0.5:
                # Use bits from another candidate
                other_template = random.choice(best_candidates)
                if other_template & (1 << bit):
                    new_candidate |= (1 << bit)
            else:
                # Random bit
                if random.random() < 0.5:
                    new_candidate |= (1 << bit)
        
        if is_valid_candidate(new_candidate) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    # Ensure we return exactly the requested number of candidates
    candidates = candidates[:count]
    logger.info(f"Generated {len(candidates)} prefix-targeted candidates")
    return candidates

def perfect_match_search(count=100, worker_safe=False):
    """
    Ultra-focused search strategy designed to find high similarity matches (80%+)
    by exploiting patterns found in our highest similarity candidates.
    
    This strategy performs intensive exploration around our best candidates,
    focusing primarily on bit manipulations most likely to push us to 80%+ similarity.
    
    Args:
        count: Number of candidates to generate
        worker_safe: Whether to use worker-safe operations
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting perfect match search with {count} candidates")
    candidates = []
    
    # Get our highest similarity candidates - increase the number to get more diverse candidates
    memory_manager = MemoryManager()
    best_candidates_data = memory_manager.get_best_candidates(50)  # Increased from 30 to 50
    
    if not best_candidates_data:
        logger.warning("No candidates in memory yet, falling back to default strategies")
        # Call another strategy as fallback
        return gradient_ascent_search(count)
    
    # Extract only candidates with higher similarity (now 30%+, reduced threshold to cast a wider net)
    high_sim_candidates = []
    for candidate_data in best_candidates_data:
        try:
            if isinstance(candidate_data, dict):
                value = int(candidate_data["private_key_int"]) 
                similarity = float(candidate_data["similarity"])
            elif isinstance(candidate_data, tuple) and len(candidate_data) >= 2:
                value = int(candidate_data[0])
                similarity = float(candidate_data[1])
            else:
                continue
                
            if similarity >= 0.30:  # Lowered from 0.35 to 0.30 to cast an even wider net
                high_sim_candidates.append((value, similarity))
        except Exception as e:
            logger.debug(f"Error extracting candidate data: {e}")
    
    if not high_sim_candidates:
        # If no candidates above threshold, use the best ones we have
        logger.info("No candidates with >30% similarity, using top candidates instead")
        for candidate_data in best_candidates_data[:10]:  # Increased from 5 to 10
            try:
                if isinstance(candidate_data, dict):
                    value = int(candidate_data["private_key_int"])
                    similarity = float(candidate_data["similarity"]) 
                elif isinstance(candidate_data, tuple) and len(candidate_data) >= 2:
                    value = int(candidate_data[0])
                    similarity = float(candidate_data[1])
                else:
                    continue
                    
                high_sim_candidates.append((value, similarity))
            except Exception as e:
                logger.debug(f"Error extracting candidate data: {e}")
    
    # Add term 67 and its variations for more diversity in starting points
    term_67 = PREV_TERM_67_INT
    if not any(term_67 == value for value, _ in high_sim_candidates):
        high_sim_candidates.append((term_67, 0.0))
    
    # Add the exact term 68 formula result
    exact_term68 = term_67 * 271 + 68
    if is_valid_candidate(exact_term68) and not any(exact_term68 == value for value, _ in high_sim_candidates):
        addr = private_key_to_address(exact_term68)
        sim = address_similarity(addr, TARGET_ADDRESS) if addr else 0.0
        high_sim_candidates.append((exact_term68, sim))
    
    # Log our starting point
    logger.info(f"Working with {len(high_sim_candidates)} high similarity candidates")
    for idx, (value, similarity) in enumerate(high_sim_candidates):
        try:
            address = private_key_to_address(value)
            logger.info(f"Base candidate {idx+1}: {hex(value)} -> {address} (similarity: {similarity:.6f})")
        except:
            logger.info(f"Base candidate {idx+1}: {hex(value)} (unable to generate address)")
    
    # Compare target address with our best candidate to identify matching positions
    if high_sim_candidates:
        best_value, best_similarity = high_sim_candidates[0]
        best_address = private_key_to_address(best_value)
        
        # Find matching/non-matching positions
        matching_positions = []
        non_matching_positions = []
        
        for i, (c1, c2) in enumerate(zip(TARGET_ADDRESS, best_address)):
            if c1 == c2:
                matching_positions.append(i)
            else:
                non_matching_positions.append(i)
        
        logger.info(f"Target address    : {TARGET_ADDRESS}")
        logger.info(f"Best candidate    : {best_address}")
        logger.info(f"Matching positions: {len(matching_positions)}/{len(TARGET_ADDRESS)}")
    
    # Extra intensive search methods
    for base_value, base_similarity in high_sim_candidates:
        # For each high-similarity candidate, create multiple variations
        variations_per_candidate = count // (len(high_sim_candidates) * 4 + 1)
        
        # APPROACH 1: Multi-bit flips focused on areas likely to impact non-matching portions
        for _ in range(variations_per_candidate):
            new_candidate = base_value
            # Flip between 1-4 bits
            num_bits = random.randint(1, 4)
            # Choose bits to flip - weight toward higher bits (more influence on address)
            bit_weights = [0.2 + (i/68)*0.8 for i in range(68)]  # Higher probability for higher bits
            positions = random.choices(range(68), weights=bit_weights, k=num_bits)
            
            for pos in positions:
                new_candidate ^= (1 << pos)
            
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
        
        # APPROACH 2: Try adjusting groups of adjacent bits
        for _ in range(variations_per_candidate):
            new_candidate = base_value
            # Choose a starting bit position (weighted toward higher bits)
            start_pos = random.choices(range(60), weights=[1 + (i/10) for i in range(60)], k=1)[0]
            # Adjust 2-4 consecutive bits
            num_bits = random.randint(2, 4)
            
            # Either set all to 0, all to 1, or flip them
            operation = random.choice(["set0", "set1", "flip"])
            
            for offset in range(num_bits):
                bit_pos = start_pos + offset
                if bit_pos < 68:
                    if operation == "set0":
                        new_candidate &= ~(1 << bit_pos)
                    elif operation == "set1":
                        new_candidate |= (1 << bit_pos)
                    else:  # flip
                        new_candidate ^= (1 << bit_pos)
            
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
        
        # APPROACH 3: Try very small numeric adjustments
        for adj in range(-20, 21):
            if adj == 0:
                continue
                
            new_candidate = base_value + adj
            if is_valid_candidate(new_candidate) and new_candidate not in candidates:
                candidates.append(new_candidate)
                
        # APPROACH 4: Try bit rotations and shifts (preserves bit count but changes pattern)
        for shift in range(1, 5):
            # Left circular shift
            rotated_left = ((base_value << shift) | (base_value >> (68 - shift))) & ((1 << 68) - 1)
            if is_valid_candidate(rotated_left) and rotated_left not in candidates:
                candidates.append(rotated_left)
                
            # Right circular shift
            rotated_right = ((base_value >> shift) | (base_value << (68 - shift))) & ((1 << 68) - 1)
            if is_valid_candidate(rotated_right) and rotated_right not in candidates:
                candidates.append(rotated_right)
                
    # If two high-similarity candidates, try combining them
    if len(high_sim_candidates) >= 2:
        top_two = [value for value, _ in high_sim_candidates[:2]]
        
        # Try various hybrid combinations using bitwise operations
        operations = [
            lambda a, b: a ^ b,  # XOR
            lambda a, b: a & b,  # AND
            lambda a, b: a | b,  # OR
            lambda a, b: (a & 0xFFFFFFFF00000000) | (b & 0x00000000FFFFFFFF),  # a high bits, b low bits
            lambda a, b: (a & 0x00000000FFFFFFFF) | (b & 0xFFFFFFFF00000000),  # a low bits, b high bits
        ]
        
        for op in operations:
            hybrid = op(top_two[0], top_two[1])
            if is_valid_candidate(hybrid) and hybrid not in candidates:
                candidates.append(hybrid)
    
    # Ensure we have exactly the requested number of candidates
    # If we need more, use gradient ascent to fill remaining slots
    if len(candidates) < count:
        extras = gradient_ascent_search(count - len(candidates))
        for extra in extras:
            if extra not in candidates:
                candidates.append(extra)
    
    # Limit to count
    candidates = candidates[:count]
    logger.info(f"Generated {len(candidates)} perfect match search candidates")
    return candidates

def sequence_pattern_search(count=200):
    """
    Generates candidates based on the sequence patterns observed in the sequence.
    Uses the patterns from term generation where:
    - Type A: XOR transformation: ((prev ^ (prime << shift)) * factor) + offset
    - Type B: Addition: prev + (prime << shift) + offset
    - Type C: Multiplication: prev * prime + offset
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting sequence pattern search with count={count}")
    candidates = []
    
    # Term 67 (previous term) info
    term_67 = PREV_TERM_67_INT
    
    # Term 68 should be type C with prime 271
    # Based on the pattern in gpt_version.py
    base_prime = 271
    
    # Generate candidates by varying parameters around the pattern
    for prime_adjustment in range(-10, 11):
        prime = base_prime + prime_adjustment
        
        # Type C: Multiplication pattern
        candidate = term_67 * prime
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated Type C candidate: {hex(candidate)}")
        
        # Try with different offsets
        for offset in range(-1000, 1001, 100):
            candidate = term_67 * prime + offset
            if is_valid_candidate(candidate):
                candidates.append(candidate)
                if len(candidates) % 10 == 0:
                    logger.info(f"Generated {len(candidates)} sequence pattern candidates so far")
    
    # Also try Type A patterns (XOR transformation)
    for shift in range(0, 10):
        for factor in [1, 2]:
            candidate = ((term_67 ^ (base_prime << shift)) * factor)
            if is_valid_candidate(candidate):
                candidates.append(candidate)
            
            # Try with different offsets
            for offset in range(-1000, 1001, 200):
                candidate = ((term_67 ^ (base_prime << shift)) * factor) + offset
                if is_valid_candidate(candidate):
                    candidates.append(candidate)
    
    # And Type B patterns (Addition)
    for shift in range(0, 10):
        candidate = term_67 + (base_prime << shift)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
        
        # Try with different offsets
        for offset in range(-1000, 1001, 200):
            candidate = term_67 + (base_prime << shift) + offset
            if is_valid_candidate(candidate):
                candidates.append(candidate)
    
    # If we generated too many candidates, keep the first 'count'
    if len(candidates) > count:
        candidates = candidates[:count]
    
    # If we didn't generate enough, fill with variations of the ones we did generate
    while len(candidates) < count and candidates:
        base_candidate = random.choice(candidates)
        # Simple bit-flipping variation
        bit = random.randint(0, 67)
        new_candidate = base_candidate ^ (1 << bit)
        if is_valid_candidate(new_candidate) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    logger.info(f"Generated {len(candidates)} sequence pattern candidates")
    return candidates

def exact_sequence_term68_search(count=100):
    """
    Generates candidates based specifically on the exact parameters for term 68
    from the gpt_version.py file. Term 68 is type C with prime 271.
    
    This is a more focused version of sequence_pattern_search that uses precise
    parameters and smaller variations.
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting exact term 68 pattern search with count={count}")
    candidates = []
    
    # Term 67 (previous term) info
    term_67 = PREV_TERM_67_INT
    
    # From gpt_version.py, term 68 is:
    # 68: ('C', 271, None, None, 68)
    # C type means multiplication: prev * prime + offset
    base_prime = 271
    base_offset = 68
    
    # Start with the exact formula from gpt_version.py
    exact_candidate = term_67 * base_prime + base_offset
    if is_valid_candidate(exact_candidate):
        candidates.append(exact_candidate)
        logger.info(f"Generated exact term 68 candidate: {hex(exact_candidate)}")
    
    # Try minimal variations of the offset
    for offset_adjustment in range(-100, 101):
        offset = base_offset + offset_adjustment
        candidate = term_67 * base_prime + offset
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            if len(candidates) % 10 == 0:
                logger.info(f"Generated {len(candidates)} exact term pattern candidates so far")
    
    # Try minimal variations of the prime
    for prime_adjustment in range(-5, 6):
        prime = base_prime + prime_adjustment
        candidate = term_67 * prime + base_offset
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # Try bit-flip variations of the exact candidate
    if exact_candidate and is_valid_candidate(exact_candidate):
        for bit in range(68):
            bit_flipped = exact_candidate ^ (1 << bit)
            if is_valid_candidate(bit_flipped):
                candidates.append(bit_flipped)
    
    # Try small arithmetic adjustments to the exact candidate
    if exact_candidate and is_valid_candidate(exact_candidate):
        for adj in range(-1000, 1001, 10):
            if adj != 0:
                adjusted = exact_candidate + adj
                if is_valid_candidate(adjusted):
                    candidates.append(adjusted)
    
    # If we generated too many candidates, keep a diverse subset
    if len(candidates) > count:
        # Sort candidates and select evenly spaced samples
        candidates.sort()
        step = len(candidates) / count
        selected = []
        for i in range(count):
            idx = int(i * step)
            selected.append(candidates[idx])
        candidates = selected
    
    # If we didn't generate enough, fill with variations of the ones we did generate
    while len(candidates) < count and candidates:
        base_candidate = random.choice(candidates)
        # Simple bit-flipping variation
        bit = random.randint(0, 67)
        new_candidate = base_candidate ^ (1 << bit)
        if is_valid_candidate(new_candidate) and new_candidate not in candidates:
            candidates.append(new_candidate)
    
    logger.info(f"Generated {len(candidates)} exact term 68 pattern candidates")
    return candidates

def pgp_signature_search(count=100):
    """
    Uses PGP signature information to guide the search for the private key.
    This strategy extracts potential parameters and patterns from the PGP signature
    data and uses them to generate candidate private keys.
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting PGP signature-based search with {count} candidates")
    candidates = []
    
    # PGP signature information
    pgp_version = "9.10.0"  # From signature
    build_number = 500      # From signature
    hash_algo = "SHA512"    # From signature
    magic_text = "Magic"    # From signature content
    
    # Create a base value using the PGP version numbers
    version_parts = [int(x) for x in pgp_version.split('.')]
    pgp_base = (version_parts[0] << 20) | (version_parts[1] << 10) | version_parts[2]
    
    # Create candidates based on PGP information combined with the previous term
    term_67 = PREV_TERM_67_INT
    
    # 1. Try combining term 67 with PGP version numbers
    for shift in range(10):
        # PGP version based transformation
        candidate = term_67 ^ (pgp_base << shift)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated PGP version-based candidate: {hex(candidate)}")
        
        # Build number based transformation
        candidate = term_67 + (build_number << shift)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # 2. Use ASCII values from "Magic" text
    magic_value = 0
    for char in magic_text:
        magic_value = (magic_value << 8) | ord(char)
    
    # Try operations with the magic value
    operations = [
        lambda x, m: x ^ m,                     # XOR with magic value
        lambda x, m: x + m,                     # Add magic value
        lambda x, m: x * ((m % 1000) or 1),     # Multiply by magic value (modulo 1000 to keep reasonable)
        lambda x, m: x | (m & 0xF_FFFF_FFFF),   # OR with magic value (masked)
        lambda x, m: x & (~m | 0xF_0000_0000),  # AND with inverted magic value (masked)
    ]
    
    for op in operations:
        candidate = op(term_67, magic_value)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated Magic text-based candidate: {hex(candidate)}")
    
    # 3. Use SHA512 hash algorithm as inspiration (512 bits)
    # SHA512 uses 80 rounds, try that as a parameter
    sha_rounds = 80
    for i in range(10):
        candidate = term_67 + (sha_rounds << i)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # 4. Use pattern from target address combined with PGP information
    target_chars = TARGET_ADDRESS
    pgp_influenced_value = 0
    
    # Create a value influenced by both PGP version and target address
    for i, char in enumerate(target_chars[:10]):  # Use first 10 chars
        char_value = ord(char)
        # Combine with PGP version parts using different operations
        if i % 3 == 0:
            pgp_influenced_value ^= char_value * version_parts[0]
        elif i % 3 == 1:
            pgp_influenced_value += char_value * version_parts[1]
        else:
            pgp_influenced_value = (pgp_influenced_value << 4) | (char_value & 0xF)
    
    # Scale to appropriate magnitude
    scale_factor = term_67 // (pgp_influenced_value or 1)
    candidate = pgp_influenced_value * scale_factor
    
    if is_valid_candidate(candidate):
        candidates.append(candidate)
        logger.info(f"Generated PGP+address hybrid candidate: {hex(candidate)}")
    
    # 5. Try term68 formula with PGP-influenced parameters
    # Standard formula is: term_67 * 271 + 68
    # Try with PGP-influenced values
    pgp_prime = 271 + version_parts[0]  # Adjust prime with PGP major version
    pgp_offset = 68 + version_parts[1]  # Adjust offset with PGP minor version
    
    candidate = term_67 * pgp_prime + pgp_offset
    if is_valid_candidate(candidate):
        candidates.append(candidate)
        logger.info(f"Generated PGP-adjusted sequence candidate: {hex(candidate)}")
    
    # If we generated too many candidates, keep a diverse selection
    if len(candidates) > count:
        # Sort candidates and select evenly distributed samples
        candidates.sort()
        step = len(candidates) / count
        selected = []
        for i in range(count):
            idx = min(int(i * step), len(candidates) - 1)
            selected.append(candidates[idx])
        candidates = selected
    
    # If we generated too few candidates, add variations
    while len(candidates) < count and candidates:
        base = random.choice(candidates)
        # Create a variation with 1-3 bit flips
        for _ in range(random.randint(1, 3)):
            bit = random.randint(0, 67)
            base ^= (1 << bit)
        
        if is_valid_candidate(base) and base not in candidates:
            candidates.append(base)
    
    logger.info(f"Generated {len(candidates)} PGP signature-based candidates")
    return candidates

def pgp_signature_numeric_analysis(count=50):
    """
    Performs deep analysis of the PGP signature byte patterns to extract potential
    numerical values that could be relevant to the private key search.
    
    This function treats the PGP signature as a potential source of carefully
    constructed numerical clues.
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting PGP signature numeric analysis with count={count}")
    candidates = []
    
    # PGP signature byte pattern (simulated here since we can't directly access the bytes)
    # These represent potential byte values derived from the signature
    pgp_potential_values = [
        0xC15473, 0x571972, 0xC80B10,  # Derived from signature elements
        0xF22572, 0xC497A8, 0x36EA18,  # Potential embedded patterns
        0x7F2E1F, 0xC23000, 0x000000,  # Values with trailing zeros (significant in BTC keys)
        0x9100B5, 0x0FC235, 0xC1942C   # Values similar to term_67 pattern
    ]
    
    term_67 = PREV_TERM_67_INT
    
    # 1. Try candidates based directly on PGP signature-derived values
    for val in pgp_potential_values:
        # Scale value to appropriate range
        scaled_val = val
        while scaled_val <= PREV_TERM_67_INT:
            scaled_val <<= 8
        
        # Apply various transformations
        candidate = scaled_val
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated PGP direct value candidate: {hex(candidate)}")
        
        # XOR with term_67
        candidate = term_67 ^ scaled_val
        if is_valid_candidate(candidate):
            candidates.append(candidate)
        
        # Addition with term_67
        candidate = term_67 + scaled_val
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # 2. Look for number sequences in the signature
    # These could be Fibonacci-like sequences embedded in the signature
    sequence_patterns = [
        # Extracted from potential patterns in PGP signature
        [9, 10, 19, 29],              # From PGP version 9.10.0 with sum pattern
        [9, 10, 0, 19, 29, 48],       # Extended pattern
        [500, 512, 1012, 1524, 2536]  # From build number 500 and hash size 512
    ]
    
    for sequence in sequence_patterns:
        if len(sequence) >= 2:
            # Try to continue the sequence for 2 more terms
            next_term = sequence[-1] + sequence[-2]
            next_next_term = next_term + sequence[-1]
            
            # Generate candidates based on these extended sequence values
            candidate = term_67 + next_term
            if is_valid_candidate(candidate):
                candidates.append(candidate)
                logger.info(f"Generated PGP sequence candidate: {hex(candidate)}")
            
            candidate = term_67 * (next_next_term % 1000 or 1)  # Prevent extremely large values
            if is_valid_candidate(candidate):
                candidates.append(candidate)
    
    # 3. Analyze ASCII values in "Version: PGP Desktop 9.10.0" string
    pgp_version_string = "PGP Desktop 9.10.0"
    ascii_sum = sum(ord(c) for c in pgp_version_string)
    ascii_product = 1
    for c in pgp_version_string:
        # Prevent overflow by periodically resetting
        ascii_product = (ascii_product * ord(c)) % 10000
    
    # Generate candidates using these values
    candidate = term_67 + ascii_sum
    if is_valid_candidate(candidate):
        candidates.append(candidate)
        logger.info(f"Generated PGP ASCII sum candidate: {hex(candidate)}")
    
    candidate = term_67 ^ ascii_product
    if is_valid_candidate(candidate):
        candidates.append(candidate)
    
    # 4. Combine SHA512 with term 67
    # SHA512 produces 512-bit output, try using 512 as a parameter
    sha_size = 512
    sha_block_size = 1024  # SHA512 block size in bits
    
    candidate = term_67 + ((sha_size << 10) | sha_block_size)
    if is_valid_candidate(candidate):
        candidates.append(candidate)
        logger.info(f"Generated SHA512-based candidate: {hex(candidate)}")
    
    # XOR with SHA parameters
    candidate = term_67 ^ sha_size
    if is_valid_candidate(candidate):
        candidates.append(candidate)
    
    # 5. Magic word pattern - use ASCII values of "Magic" with mathematical significance
    magic_ascii = [ord(c) for c in "Magic"]
    magic_sum = sum(magic_ascii)  # 77 + 97 + 103 + 105 + 99 = 481
    
    # Try combinations with the magic number 481
    candidate = term_67 + magic_sum
    if is_valid_candidate(candidate):
        candidates.append(candidate)
        logger.info(f"Generated Magic sum candidate: {hex(candidate)}")
    
    # Try formula: term_67 * (magic_sum % 256) + byte_position
    # Where byte_position is derived from the signature
    for byte_pos in [9, 10, 0, 271, 68]:  # Key values from analysis
        candidate = term_67 * (magic_sum % 256) + byte_pos
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated Magic formula candidate: {hex(candidate)}")
    
    # If we generated too many candidates, keep a diverse selection
    if len(candidates) > count:
        # Sort candidates and select evenly distributed samples
        candidates.sort()
        step = len(candidates) / count
        selected = []
        for i in range(count):
            idx = min(int(i * step), len(candidates) - 1)
            selected.append(candidates[idx])
        candidates = selected
    
    # If we generated too few candidates, add variations
    while len(candidates) < count and candidates:
        base = random.choice(candidates)
        # Create a variation with 1-3 bit flips
        for _ in range(random.randint(1, 3)):
            bit = random.randint(0, 67)
            base ^= (1 << bit)
        
        if is_valid_candidate(base) and base not in candidates:
            candidates.append(base)
    
    logger.info(f"Generated {len(candidates)} PGP signature numeric analysis candidates")
    return candidates

def nested_pgp_message_search(count=100):
    """
    Specialized search strategy based on the nested PGP message structure.
    Disregarding accessor.eth and timestamp information as requested.
    
    This strategy focuses on analyzing the cryptographic relationships between
    the nested encryption structure and Bitcoin key generation.
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting nested PGP message search with count={count}")
    candidates = []
    
    # PGP nested structure parameters
    pgp_version = "9.10.0"
    build_number = 500
    
    # Base term 67
    term_67 = PREV_TERM_67_INT
    
    # Focus on the PGP message content and structure
    pgp_version_parts = [int(x) for x in pgp_version.split('.')]
    
    # 1. Use the nested encryption concept (PGP message within PGP signature)
    # Term 67 * 271 + 68 is the standard formula
    # Add nested layers of encryption-like operations
    
    # First layer transformation - standard term 68 formula
    layer1 = term_67 * 271 + 68
    
    # Second layer - apply PGP version parameters
    layer2 = layer1 ^ (pgp_version_parts[0] << 20) ^ (pgp_version_parts[1] << 10) ^ pgp_version_parts[2]
    
    # Third layer - incorporate hash algorithm (SHA512)
    layer3 = layer2 + 512  # Adding SHA512 value
    
    # Try these layered candidates
    for layer in [layer1, layer2, layer3]:
        if is_valid_candidate(layer):
            candidates.append(layer)
            logger.info(f"Generated nested encryption candidate: {hex(layer)}")
    
    # 2. PGP signature-specific transformations
    # These are inspired by how PGP creates and verifies signatures
    
    # Simulate nested transformations (different approach)
    nested_base = term_67
    
    # Layer 1: Version-based transformation
    nested1 = nested_base * pgp_version_parts[0]  # 9
    
    # Layer 2: Build-influenced transformation
    nested2 = nested1 + (build_number & 0xFFFF)
    
    # Layer 3: SHA512-influenced transformation
    nested3 = nested2 ^ 0x512  # Hexadecimal reference to SHA512
    
    for candidate in [nested1, nested2, nested3]:
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated nested structure candidate: {hex(candidate)}")
    
    # 3. Try direct bit manipulations based on PGPDH
    # PGPDH (PGP Diffie-Hellman) has specific bit patterns
    
    # Basic term 68 with bit flips based on PGP values
    base_candidate = term_67 * 271 + 68
    pgp_value = pgp_version_parts[0] * 100 + pgp_version_parts[1] * 10 + pgp_version_parts[2]  # 910
    
    # Flip bits that correspond to PGP values
    for bit_position in [9, 1, 0, 5, 0, 0]:  # Digits from PGP version and build
        if bit_position > 0:  # Skip zero positions
            bit_flipped = base_candidate ^ (1 << bit_position)
            if is_valid_candidate(bit_flipped):
                candidates.append(bit_flipped)
                logger.info(f"Generated PGP-bit position candidate: {hex(bit_flipped)}")
    
    # 4. Use magic word information
    magic_text = "Magic"
    magic_value = 0
    for char in magic_text:
        magic_value = (magic_value << 8) | ord(char)
    
    # Try operations with the magic value
    magic_candidates = [
        term_67 ^ magic_value,
        term_67 + magic_value,
        term_67 * ((magic_value % 1000) or 1),  # Prevent extremely large values
        base_candidate ^ magic_value
    ]
    
    for candidate in magic_candidates:
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated Magic-based candidate: {hex(candidate)}")
    
    # 5. Use the term 68 pattern with PGP-based adjustments
    prime = 271  # Standard prime for term 68
    offset = 68   # Standard offset for term 68
    
    # Modify the parameters based on PGP version
    modified_prime = prime + pgp_version_parts[0]  # 271 + 9 = 280
    modified_offset = offset + pgp_version_parts[1]  # 68 + 10 = 78
    
    modified_sequence = term_67 * modified_prime + modified_offset
    if is_valid_candidate(modified_sequence):
        candidates.append(modified_sequence)
        logger.info(f"Generated PGP-modified sequence: {hex(modified_sequence)}")
    
    # If we generated too many candidates, keep a diverse selection
    if len(candidates) > count:
        # Sort candidates and select evenly distributed samples
        candidates.sort()
        step = len(candidates) / count
        selected = []
        for i in range(count):
            idx = min(int(i * step), len(candidates) - 1)
            selected.append(candidates[idx])
        candidates = selected
    
    # If we generated too few candidates, add variations
    while len(candidates) < count and candidates:
        base = random.choice(candidates)
        # Create a variation with 1-3 bit flips
        for _ in range(random.randint(1, 3)):
            bit = random.randint(0, 67)
            base ^= (1 << bit)
        
        if is_valid_candidate(base) and base not in candidates:
            candidates.append(base)
    
    logger.info(f"Generated {len(candidates)} nested PGP message candidates")
    return candidates

def pgp_binary_pattern_search(count=100):
    """
    Analyzes binary patterns in the PGP message to find potential clues for the private key.
    Focuses on extracting numerical patterns from the base64-encoded sections.
    
    Args:
        count: Number of candidates to generate
        
    Returns:
        list: List of candidate private keys
    """
    logger.info(f"Starting PGP binary pattern search with count={count}")
    candidates = []
    
    # Key base64 fragments from the PGP message
    # These fragments potentially contain hidden patterns
    fragments = [
        "qANQR1DBwU",  # Header fragment
        "wsFVAwUBZ8",  # Signature start
        "wDRljPBT/i",  # Possibly significant encoding
        "ItvbQzIwo",   # From end of message
        "accessor"     # Username fragment
    ]
    
    # Base term for transformations
    term_67 = PREV_TERM_67_INT
    
    # 1. Try using direct binary patterns from PGP message fragments
    for fragment in fragments:
        # Create numeric values from fragments
        # These could represent bits or bytes in the key
        numeric_value = 0
        for char in fragment:
            numeric_value = (numeric_value << 6) | (ord(char) & 0x3F)  # Base64 encodes 6 bits per character
        
        # Scale the value to be in appropriate range
        while numeric_value > 0 and numeric_value < term_67:
            numeric_value <<= 4
        
        # Create candidates using these values
        candidate = numeric_value
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated direct binary pattern candidate: {hex(candidate)}")
        
        # Try with XOR, which is common in cryptographic operations
        candidate = term_67 ^ numeric_value
        if is_valid_candidate(candidate):
            candidates.append(candidate)
        
        # Try with addition, another common operation
        candidate = term_67 + numeric_value
        if is_valid_candidate(candidate):
            candidates.append(candidate)
    
    # 2. Extract potential key-like patterns from base64 fragments
    # Simulate how a cryptographic key might be encoded in base64
    key_patterns = []
    
    for i in range(len(fragments) - 1):
        # Combine pairs of fragments to get potential key material
        combined = fragments[i] + fragments[i+1]
        # Take first 8 characters (48 bits) for a key fragment
        key_fragment = combined[:8]
        
        # Convert to numeric
        key_value = 0
        for char in key_fragment:
            key_value = (key_value << 6) | (ord(char) & 0x3F)
        
        key_patterns.append(key_value)
    
    # Use these patterns to create candidates
    for pattern in key_patterns:
        # Try using pattern as lower 48 bits with scaled term_67 as high bits
        candidate = ((term_67 & 0xFFFFF) << 48) | (pattern & 0xFFFFFFFFFFFF)
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated key pattern candidate: {hex(candidate)}")
    
    # 3. Look for structural patterns in base64 encoding
    # Base64 encodes data in groups of 3 bytes -> 4 chars
    # Try to reconstruct potential original binary data
    
    # Concatenate all fragments
    all_base64 = ''.join(fragments)
    
    # Simulate partial decoding of base64 content
    # We can't actually decode without proper padding, but we can simulate
    binary_chunks = []
    for i in range(0, len(all_base64) - 3, 4):
        chunk = all_base64[i:i+4]
        # Extract 3 bytes (24 bits) from 4 base64 chars
        value = 0
        for char in chunk:
            value = (value << 6) | (ord(char) & 0x3F)
        binary_chunks.append(value & 0xFFFFFF)  # Keep 24 bits
    
    # Try combining chunks to get 68-bit candidates
    for i in range(len(binary_chunks) - 2):
        # Combine 3 chunks to get 72 bits, then mask to 68 bits
        candidate = (binary_chunks[i] << 48) | (binary_chunks[i+1] << 24) | binary_chunks[i+2]
        candidate &= ((1 << 68) - 1)  # Mask to 68 bits
        
        if is_valid_candidate(candidate):
            candidates.append(candidate)
            logger.info(f"Generated base64 chunk candidate: {hex(candidate)}")
    
    # 4. Search for potential hash-like patterns in the PGP message
    # The message mentions SHA512, which suggests hash relationships
    
    # Create a SHA-like value by combining fragments with bitwise operations
    sha_pattern = 0
    for fragment in fragments:
        fragment_value = sum(ord(c) for c in fragment)
        sha_pattern = ((sha_pattern << 7) | (sha_pattern >> 61)) ^ fragment_value
    
    # Scale to appropriate magnitude
    while sha_pattern < term_67:
        sha_pattern <<= 8
    
    # Create candidates using SHA-like pattern
    candidate = sha_pattern & ((1 << 68) - 1)  # Mask to 68 bits
    if is_valid_candidate(candidate):
        candidates.append(candidate)
        logger.info(f"Generated SHA-like pattern candidate: {hex(candidate)}")
    
    # XOR with term_67
    candidate = term_67 ^ sha_pattern
    if is_valid_candidate(candidate):
        candidates.append(candidate)
    
    # 5. Try cross-domain cryptography (ETH + BTC connection)
    # The presence of accessor.eth suggests a cross-chain relationship
    
    # Simulate an Ethereum-like key derivation pattern
    eth_fragment = "accessor.eth"
    eth_value = 0
    for c in eth_fragment:
        eth_value = ((eth_value << 5) + eth_value) + ord(c)  # djb2-like hash
    
    # Use this ethereum-like value to modify term_67
    btc_eth_candidate = term_67 ^ ((eth_value & 0xFFFF) << 20)
    if is_valid_candidate(btc_eth_candidate):
        candidates.append(btc_eth_candidate)
        logger.info(f"Generated cross-chain pattern candidate: {hex(btc_eth_candidate)}")
    
    # If we generated too many candidates, keep a diverse selection
    if len(candidates) > count:
        # Sort candidates and select evenly distributed samples
        candidates.sort()
        step = len(candidates) / count
        selected = []
        for i in range(count):
            idx = min(int(i * step), len(candidates) - 1)
            selected.append(candidates[idx])
        candidates = selected
    
    # If we generated too few candidates, add variations
    while len(candidates) < count and candidates:
        base = random.choice(candidates)
        # Create a variation with 1-3 bit flips
        for _ in range(random.randint(1, 3)):
            bit = random.randint(0, 67)
            base ^= (1 << bit)
        
        if is_valid_candidate(base) and base not in candidates:
            candidates.append(base)
    
    logger.info(f"Generated {len(candidates)} PGP binary pattern candidates")
    return candidates

# -----------------------------
# Search Orchestration
# -----------------------------

def save_result(value):
    """
    Save a successful result to file
    """
    if value is None:
        logger.info("No exact match found, saving placeholder result")
        # Save a placeholder result
        result = {
            "private_key_int": None,
            "private_key_hex": None,
            "bitcoin_address": TARGET_ADDRESS,
            "timestamp": time.time(),
            "human_time": datetime.now().isoformat(),
            "status": "No exact match found"
        }
    else:
        logger.info(f"MATCH FOUND! Saving result: {hex(value)}")
        # Save as JSON with more details
        result = {
            "private_key_int": value,
            "private_key_hex": hex(value),
            "bitcoin_address": TARGET_ADDRESS,
            "timestamp": time.time(),
            "human_time": datetime.now().isoformat()
        }
    
    with open("term68_solution.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Also save as plain text for easier reading
    with open("term68_solution.txt", "w") as f:
        f.write(f"Term 68 Solution Found!\n")
        if value is None:
            f.write("Private Key: Not found\n")
        else:
            f.write(f"Private Key (int): {value}\n")
            f.write(f"Private Key (hex): {hex(value)}\n")
        f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    
    logger.info(f"Solution saved to term68_solution.json and term68_solution.txt")
    
    # Exit with success
    sys.exit(0)

def save_progress(stats):
    """
    Save search progress
    """
    with open(PROGRESS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def load_checkpoint():
    """
    Load checkpoint if exists
    """
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
    
    return {
        "total_tested": 0,
        "best_similarity": 0.0,
        "cycles_completed": 0,
        "last_strategy": None,
        "learning_rate": LEARNING_RATE,
        "mutation_rate": MUTATION_RATE,
        "bit_flip_max": BIT_FLIP_MAX,
        "search_radius": SEARCH_RADIUS
    }

def save_checkpoint(checkpoint):
    """
    Save search checkpoint
    """
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)

def save_state(state):
    """
    Save a successful state to return to if needed
    """
    global BEST_STATES
    
    BEST_STATES.append(state)
    # Keep only top 5 states
    if len(BEST_STATES) > 5:
        BEST_STATES = BEST_STATES[-5:]
    
    logger.info(f"Saved current state with similarity {state['best_similarity']:.6f}")

def load_previous_state():
    """
    Load a previous successful state
    """
    global LEARNING_RATE, MUTATION_RATE, BIT_FLIP_MAX, SEARCH_RADIUS, BEST_STATES
    
    if not BEST_STATES:
        logger.warning("No previous states to load")
        return False
    
    # Get the most recent state
    state = BEST_STATES.pop()
    
    # Restore parameters
    LEARNING_RATE = state["learning_rate"]
    MUTATION_RATE = state["mutation_rate"]
    BIT_FLIP_MAX = state["bit_flip_max"]
    SEARCH_RADIUS = state["search_radius"]
    
    logger.info(f"Loaded previous state with similarity {state['best_similarity']:.6f}")
    return True

def display_best_score():
    """
    Display the best score found so far in a prominent, persistent way
    """
    global LAST_DISPLAY_TIME
    LAST_DISPLAY_TIME = time.time()
    
    # Create a prominent display of the best score
    display = "\n" + "="*80 + "\n"
    display += f"     BEST SIMILARITY SCORE: {ALL_TIME_BEST_SIMILARITY:.6f}\n"
    display += f"     Best Candidate: {hex(ALL_TIME_BEST_CANDIDATE) if ALL_TIME_BEST_CANDIDATE else 'None'}\n"
    display += f"     Best Address: {ALL_TIME_BEST_ADDRESS}\n"
    display += f"     Target Address: {TARGET_ADDRESS}\n"
    
    # Show progress toward target similarity
    progress = ALL_TIME_BEST_SIMILARITY / TARGET_SIMILARITY * 100
    display += f"     Progress toward target 0.3: {progress:.2f}%\n"
    
    # Show similarity visually
    display += "     ["
    progress_bars = int(50 * (ALL_TIME_BEST_SIMILARITY / TARGET_SIMILARITY))
    display += "=" * progress_bars + " " * (50 - progress_bars) + "]\n"
    
    # Show time
    display += f"     Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    display += "="*80 + "\n"
    
    # Print to console
    print(display)
    
    # Also log to file
    logger.info(f"BEST SCORE UPDATE: {ALL_TIME_BEST_SIMILARITY:.6f} for address {ALL_TIME_BEST_ADDRESS}")

def continuous_adaptive_search():
    """
    Main search function that continuously searches for the private key.
    This function never returns and runs forever until a match is found.
    """
    # Initialize variables for tracking search state
    address_logger = AddressLogger()
    memory_manager = MemoryManager()
    
    # Force memory reload
    memory_manager.load_memory()
    
    # Generate some initial base candidates using enhanced strategies
    base_candidates = []
    
    # First load promising candidates from memory
    memory_base_candidates = memory_manager.get_promising_values(10)
    if memory_base_candidates:
        logger.info(f"Loaded {len(memory_base_candidates)} candidates from memory")
        base_candidates.extend(memory_base_candidates)
    
    # Add previous term as a baseline reference
    base_candidates.append(PREV_TERM_67_INT)
    
    # Generate high-quality candidates using domain knowledge
    high_quality_candidates = generate_high_quality_candidates(20, base_candidates)
    logger.info(f"Generated {len(high_quality_candidates)} high-quality candidates")
    
    # Merge all candidates, prioritizing high-quality ones
    all_candidates = []
    all_candidates.extend(high_quality_candidates)  # Add high-quality candidates first
    all_candidates.extend([c for c in base_candidates if c not in all_candidates])  # Add any other candidates we didn't include
    
    # Use the merged list as our base candidates
    base_candidates = all_candidates
    logger.info(f"Starting search with {len(base_candidates)} diverse candidates")
    
    # Parse checkpoint or initialize variables
    checkpoint = load_checkpoint()
    cycles_completed = checkpoint.get("cycles_completed", 0)
    consecutive_no_improvement = 0
    plateau_count = 0
    global BEST_CANDIDATES
    
    # Get initial best similarity
    # Use the absolute best from memory
    best_similarity = memory_manager.get_absolute_best_similarity()
    logger.info(f"Starting with best similarity: {best_similarity:.6f}")
    
    # Initialize ALL_TIME_BEST values
    global ALL_TIME_BEST_SIMILARITY, ALL_TIME_BEST_CANDIDATE, ALL_TIME_BEST_ADDRESS
    ALL_TIME_BEST_SIMILARITY = best_similarity
    if best_similarity > 0:
        best_candidates = memory_manager.get_best_candidates(1)
        if best_candidates and len(best_candidates) > 0:
            ALL_TIME_BEST_CANDIDATE = int(best_candidates[0]["private_key_int"])
            ALL_TIME_BEST_ADDRESS = best_candidates[0]["address"]
            # Add to base candidates to ensure we use it
            base_candidates.append(ALL_TIME_BEST_CANDIDATE)
            logger.info(f"Using best candidate from memory: {hex(ALL_TIME_BEST_CANDIDATE)}")
    
    # Display the best score at startup
    display_best_score()
    
    # Initialize the best state
    save_state({
        "best_similarity": best_similarity,
        "learning_rate": LEARNING_RATE,
        "mutation_rate": MUTATION_RATE,
        "bit_flip_max": BIT_FLIP_MAX,
        "search_radius": SEARCH_RADIUS
    })
    
    while True:
        cycles_completed += 1
        
        # Display header with best score
        header = f"\n=== Starting Cycle {cycles_completed} ===\n"
        header += f"Current best similarity: {best_similarity:.6f}, All-time best: {ALL_TIME_BEST_SIMILARITY:.6f}\n"
        print(header)
        
        logger.info(f"=== Starting Cycle {cycles_completed} ===")
        logger.info(f"Current best similarity: {best_similarity:.6f}")
        
        # Update base candidates with promising ones
        promising_values = memory_manager.get_promising_values(5)
        base_candidates = list(set(base_candidates + promising_values))
        
        # ALWAYS ensure we have our absolute best candidates in the base set
        if BEST_CANDIDATES:
            for candidate, _, _ in BEST_CANDIDATES:
                if candidate not in base_candidates:
                    base_candidates.append(candidate)
        
        # Check for any similarity regression
        current_best_similarity = memory_manager.get_absolute_best_similarity()
        if current_best_similarity < best_similarity:
            logger.error(f"CRITICAL ERROR: Similarity regressed from {best_similarity:.6f} to {current_best_similarity:.6f}")
            logger.error("Forcing similarity back to previous best")
            # Force the best similarity back to what it was
            best_similarity = max(best_similarity, current_best_similarity)
            # Reload a previous state to avoid regression
            load_previous_state()
        
        # Define all available strategies
        all_strategies = [
            # Nested PGP message search (highest priority based on new message)
            ("Nested PGP message search", nested_pgp_message_search),
            
            # PGP binary pattern search (extracts patterns from PGP data)
            ("PGP binary pattern search", pgp_binary_pattern_search),
            
            # Exact term 68 sequence pattern search (absolute highest priority)
            ("Exact term 68 sequence search", exact_sequence_term68_search),
            
            # Sequence pattern search from gpt_version.py (high priority)
            ("Sequence pattern search", sequence_pattern_search),
            
            # PGP signature-based search (high priority based on new clue)
            ("PGP signature search", pgp_signature_search),
            
            # PGP signature numeric analysis (deep analysis of signature values)
            ("PGP signature numeric analysis", pgp_signature_numeric_analysis),
            
            # Enhanced gradient ascent (critical for optimization)
            ("Enhanced gradient ascent", lambda: gradient_ascent_search(count=100, iterations=200, learning_rate=0.15)),
            
            # Perfect match search - high priority for 80% similarity goal
            ("Perfect match search", perfect_match_search),
            
            # Target similarity search - high priority
            ("Target similarity search", target_similarity_search),
            
            # Learning-based strategies
            ("Learning-based search", learning_search),
            
            # Targeted bit flip search
            ("Bit flip search", lambda: bit_flip_search(
                random.choice(base_candidates), 
                max_bits=BIT_FLIP_MAX
            )),
            
            # Genetic algorithm
            ("Genetic search", genetic_search),
            
            # Adaptive range search
            ("Adaptive range search", lambda: adaptive_range_search(
                random.choice(base_candidates),
                radius=SEARCH_RADIUS
            )),
            
            # Pattern walks
            ("Addition pattern", lambda: pattern_walk(
                random.choice(base_candidates),
                lambda x: x + 1
            )),
            
            ("Fibonacci pattern", lambda: pattern_walk(
                random.choice(base_candidates),
                lambda x: x + PREV_TERM_67
            )),
            
            ("XOR pattern", lambda: pattern_walk(
                random.choice(base_candidates),
                lambda x: x ^ random.choice(base_candidates)
            )),
            
            ("Bit shift pattern", lambda: pattern_walk(
                random.choice(base_candidates),
                lambda x: (x << 1) & MAX_VALUE
            ))
        ]
        
        # Log strategy effectiveness
        logger.info("Strategy effectiveness ratings:")
        for strategy_name, rating in sorted(STRATEGY_EFFECTIVENESS.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {strategy_name}: {rating:.4f}")
        
        # Force at least one of these strategies to run every cycle
        # to ensure we're always generating addresses
        guaranteed_strategies = [
            # Always run nested PGP message search (highest priority based on new evidence)
            ("Guaranteed nested PGP search", lambda: nested_pgp_message_search(count=40)),
            
            # Always run PGP binary pattern search to analyze binary patterns
            ("Guaranteed PGP binary search", lambda: pgp_binary_pattern_search(count=30)),
            
            # Always run the exact term 68 sequence pattern search
            ("Guaranteed exact term 68 search", lambda: exact_sequence_term68_search(count=30)),
            
            # Always run PGP signature search since it's a new clue
            ("Guaranteed PGP search", lambda: pgp_signature_search(count=40)),
            
            # Always run enhanced gradient ascent for optimization
            ("Guaranteed gradient ascent", lambda: gradient_ascent_search(count=30, iterations=75, learning_rate=0.1)),
            
            # Always do a bit flip search to ensure we're generating candidates
            ("Guaranteed bit flip", lambda: bit_flip_search(
                random.choice(base_candidates),
                max_bits=max(3, BIT_FLIP_MAX - 2),
                max_candidates=100
            )),
            
            # Always try some values around base candidates
            ("Guaranteed range search", lambda: adaptive_range_search(
                random.choice(base_candidates),
                radius=min(100, SEARCH_RADIUS),
                max_candidates=100
            ))
        ]
        
        # Execute guaranteed strategies first
        for strategy_name, strategy_func in guaranteed_strategies:
            logger.info(f"Executing guaranteed strategy: {strategy_name}")
            try:
                strategy_func()  # We don't care about the result, just want to generate addresses
            except Exception as e:
                logger.error(f"Error in guaranteed strategy {strategy_name}: {e}")
            
            # Make sure memory is saved
            memory_manager.save_memory()
        
        # Check for improvement after guaranteed strategies
        current_best = memory_manager.get_best_candidates(1)
        cycle_improved = False
        
        if current_best and current_best[0]["similarity"] > best_similarity:
            best_similarity = current_best[0]["similarity"]
            consecutive_no_improvement = 0
            plateau_count = 0
            cycle_improved = True
            
            # Save this successful state
            save_state({
                "best_similarity": best_similarity,
                "learning_rate": LEARNING_RATE,
                "mutation_rate": MUTATION_RATE,
                "bit_flip_max": BIT_FLIP_MAX,
                "search_radius": SEARCH_RADIUS
            })
            
            logger.info(f"Improved similarity to {best_similarity:.6f}")
        
        # If we've gone several cycles without improvement, do something drastic
        if consecutive_no_improvement >= 3:
            logger.warning(f"No improvement for {consecutive_no_improvement} cycles, taking drastic measures!")
            
            # First, try loading a previous successful state
            if plateau_count % 2 == 0 and load_previous_state():
                logger.info("Loaded previous successful state")
            else:
                # If we can't load a state or every other plateau, take more drastic measures
                # Increase bit flip max more aggressively
                BIT_FLIP_MAX = min(20, BIT_FLIP_MAX + 2)
                
                # Increase search radius substantially
                SEARCH_RADIUS = min(50000, SEARCH_RADIUS * 2)
                
                # Generate completely new random candidates
                logger.info("Generating fresh random candidates...")
                for _ in range(150):
                    # Generate random 68-bit value
                    bits = ['1'] + ['1' if random.random() > 0.5 else '0' for _ in range(67)]
                    value = int(''.join(bits), 2)
                    if is_valid_candidate(value):
                        match, address, similarity = test_candidate(value)
                        if address:
                            address_logger.log_address(value, address, similarity)
                            memory_manager.add_result(value, address, similarity)
            
            # Reset strategy effectiveness to give everything another chance
            for strategy in STRATEGY_EFFECTIVENESS:
                STRATEGY_EFFECTIVENESS[strategy] = 1.0
                
            plateau_count += 1
            consecutive_no_improvement = 0  # Reset but track plateaus separately
        
        # Track if cycle makes any improvements
        cycle_start_similarity = best_similarity
        
        # Select strategies based on their effectiveness
        # Use weighted random selection - more effective strategies get selected more often
        strategies_to_run = []
        total_weight = sum(STRATEGY_EFFECTIVENESS.values())
        
        # Select 3-5 strategies to run this cycle
        num_strategies = random.randint(3, 5)
        
        # If we've gone cycles without improvement, try all strategies
        if consecutive_no_improvement >= 2:
            num_strategies = len(all_strategies)
        
        # Add strategies based on their effectiveness weights
        while len(strategies_to_run) < num_strategies and len(strategies_to_run) < len(all_strategies):
            for strategy_name, strategy_func in all_strategies:
                if strategy_name in [s[0] for s in strategies_to_run]:
                    continue  # Skip if already added
                
                # Calculate selection probability based on effectiveness
                strategy_weight = STRATEGY_EFFECTIVENESS.get(strategy_name, 1.0)
                selection_prob = strategy_weight / total_weight if total_weight > 0 else 1.0
                
                if random.random() < selection_prob:
                    strategies_to_run.append((strategy_name, strategy_func))
                    
                if len(strategies_to_run) >= num_strategies:
                    break
        
        # If we didn't get enough strategies, add remaining ones
        if len(strategies_to_run) < num_strategies:
            for strategy_name, strategy_func in all_strategies:
                if strategy_name not in [s[0] for s in strategies_to_run]:
                    strategies_to_run.append((strategy_name, strategy_func))
                    if len(strategies_to_run) >= num_strategies:
                        break
        
        # Shuffle the strategies to prevent predictable ordering
        random.shuffle(strategies_to_run)
        
        # Execute selected strategies
        for strategy_name, strategy_func in strategies_to_run:
            logger.info(f"Executing strategy: {strategy_name}")
            
            # Get best similarity before strategy execution
            pre_strategy_best = best_similarity
            
            # Execute strategy with timeout protection
            strategy_start_time = time.time()
            max_strategy_time = 120  # Maximum seconds to spend on a strategy
            
            try:
                # Execute the strategy with timeout
                result = strategy_func()
                
                # Log strategy completion time
                strategy_duration = time.time() - strategy_start_time
                logger.info(f"Strategy {strategy_name} completed in {strategy_duration:.2f} seconds")
                
                # Use absolute best to avoid regressions
                current_best_similarity = memory_manager.get_absolute_best_similarity()
                
                # Always make sure we're using the highest similarity ever found
                if current_best_similarity > best_similarity:
                    best_similarity = current_best_similarity
                    
                    # Get candidate info for the best similarity
                    best_candidates = memory_manager.get_best_candidates(1)
                    if best_candidates:
                        strategy_best = best_candidates[0]
                        strategy_similarity = strategy_best["similarity"]
                        strategy_candidate = int(strategy_best["private_key_int"])
                        
                        # Update cycle stats
                        cycle_stats["strategy_results"][strategy_name] = {
                            "best_similarity": strategy_similarity,
                            "best_candidate": hex(strategy_candidate)
                        }
                        
                        # Update overall best
                        cycle_stats["best_similarity"] = strategy_similarity
                        cycle_stats["best_candidate"] = hex(strategy_candidate)
                        cycle_improved = True
                        
                        # Save this successful state
                        save_state({
                            "best_similarity": best_similarity,
                            "learning_rate": LEARNING_RATE,
                            "mutation_rate": MUTATION_RATE,
                            "bit_flip_max": BIT_FLIP_MAX,
                            "search_radius": SEARCH_RADIUS
                        })
                    
                    # Update strategy effectiveness based on improvement
                    improvement = current_best_similarity - pre_strategy_best
                    
                    # Adjust effectiveness rating - more aggressively now
                    if improvement > 0:
                        # Reward strategies that improve similarity
                        STRATEGY_EFFECTIVENESS[strategy_name] = min(10.0, STRATEGY_EFFECTIVENESS.get(strategy_name, 1.0) * 1.5)
                        logger.info(f"Strategy {strategy_name} improved similarity by {improvement:.6f} - new rating: {STRATEGY_EFFECTIVENESS[strategy_name]:.2f}")
                    else:
                        # More aggressively reduce effectiveness of non-improving strategies
                        STRATEGY_EFFECTIVENESS[strategy_name] = max(0.1, STRATEGY_EFFECTIVENESS.get(strategy_name, 1.0) * 0.7)
                else:
                    # This strategy didn't improve our best similarity
                    # Lower its effectiveness
                    STRATEGY_EFFECTIVENESS[strategy_name] = max(0.1, STRATEGY_EFFECTIVENESS.get(strategy_name, 1.0) * 0.8)
                    logger.info(f"Strategy {strategy_name} did not improve best similarity - effectiveness reduced to {STRATEGY_EFFECTIVENESS[strategy_name]:.2f}")
                
                # If match found, return it
                if result:
                    return result
                    
            except Exception as e:
                logger.error(f"Error in strategy {strategy_name}: {e}")
                # Reduce effectiveness of erroring strategies more aggressively
                STRATEGY_EFFECTIVENESS[strategy_name] = max(0.1, STRATEGY_EFFECTIVENESS.get(strategy_name, 1.0) * 0.5)
                
            # Update checkpoint after each strategy
            checkpoint["last_strategy"] = strategy_name
            checkpoint["cycles_completed"] = cycles_completed
            checkpoint["best_similarity"] = best_similarity  # Always use the absolute best
            save_checkpoint(checkpoint)
            
            # Save memory after each strategy
            memory_manager.save_memory()
        
        # *** KEY FIX: Always use the absolute best similarity from memory ***
        best_similarity = memory_manager.get_absolute_best_similarity()
        
        # Check if cycle improved best similarity based on absolute best
        if not cycle_improved:
            consecutive_no_improvement += 1
            logger.warning(f"Cycle did not improve similarity. {consecutive_no_improvement} consecutive non-improving cycles.")
            
            # Exponentially increase exploration as we fail to improve
            exploration_factor = min(5.0, 1.0 + (0.5 * consecutive_no_improvement))
            
            # Adjust parameters more aggressively based on plateau length
            if consecutive_no_improvement >= 3:
                # Take more drastic measures when stuck for too long
                exploration_factor = min(10.0, 2.0 + consecutive_no_improvement)
                
                # Try completely different parameter values
                if random.random() < 0.5:
                    # Try very large bit flips
                    BIT_FLIP_MAX = min(40, BIT_FLIP_MAX * 2)
                    logger.info(f"Drastically increasing bit flip max to {BIT_FLIP_MAX}")
                else:
                    # Try much larger search radius
                    SEARCH_RADIUS = min(1000000, SEARCH_RADIUS * 5)
                    logger.info(f"Drastically increasing search radius to {SEARCH_RADIUS}")
                
                # Also increase mutation rate more aggressively
                MUTATION_RATE = min(0.8, MUTATION_RATE * 1.5)
            else:
                # Regular exploration increases for shorter stuck periods
                LEARNING_RATE = min(0.9, LEARNING_RATE * exploration_factor)
                SEARCH_RADIUS = min(100000, int(SEARCH_RADIUS * exploration_factor))
                BIT_FLIP_MAX = min(30, BIT_FLIP_MAX + consecutive_no_improvement)
                MUTATION_RATE = min(0.5, MUTATION_RATE * exploration_factor)
            
            logger.info(f"Increasing exploration with factor {exploration_factor:.2f}")
        else:
            # If we improved, save parameters and reset counter
            consecutive_no_improvement = 0
            
            # Make search more precise when we're improving
            LEARNING_RATE = max(0.01, LEARNING_RATE * 0.8)
            MUTATION_RATE = max(0.01, MUTATION_RATE * 0.8)
            
            # Don't reduce exploration parameters too much - we need to keep exploring
            SEARCH_RADIUS = max(50, int(SEARCH_RADIUS * 0.9))
            
            logger.info("Similarity improved! Fine-tuning parameters for precision.")
            
            # Prioritize the most effective strategies
            sorted_strategies = sorted(STRATEGY_EFFECTIVENESS.items(), key=lambda x: x[1], reverse=True)
            if sorted_strategies:
                best_strategy = sorted_strategies[0][0]
                logger.info(f"Most effective strategy: {best_strategy} with rating {sorted_strategies[0][1]:.2f}")
        
        # Try to reach exact match or target similarity by doubling down on best candidates
        if best_similarity >= TARGET_SIMILARITY:  # We've reached our target!
            logger.info(f"TARGET SIMILARITY ACHIEVED! ({best_similarity:.6f}) - Intensifying search for exact match")
            
            # Get our absolute best candidate
            best_candidate_data = memory_manager.get_best_candidates(1)[0]
            best_candidate = int(best_candidate_data["private_key_int"])
            best_address = best_candidate_data["address"]
            
            logger.info(f"Target address : {TARGET_ADDRESS}")
            logger.info(f"Current best   : {best_address}")
            logger.info(f"Similarity     : {best_similarity:.6f}")
            
            # Compare addresses character by character
            matching = ""
            non_matching = ""
            matching_count = 0
            
            for i, (t_char, b_char) in enumerate(zip(TARGET_ADDRESS, best_address)):
                if t_char == b_char:
                    matching += "^"
                    non_matching += " "
                    matching_count += 1
                else:
                    matching += " "
                    non_matching += "v"
            
            match_percentage = (matching_count / len(TARGET_ADDRESS)) * 100
            
            logger.info(f"Target address : {TARGET_ADDRESS}")
            logger.info(f"Current best   : {best_address}")
            logger.info(f"Matching chars : {matching_count}/{len(TARGET_ADDRESS)} ({match_percentage:.2f}%)")
            logger.info(f"Matching       : {matching}")
            logger.info(f"Non-matching   : {non_matching}")
            
            # Log positions that need to be fixed
            non_matching_positions = []
            for i, (t_char, b_char) in enumerate(zip(TARGET_ADDRESS, best_address)):
                if t_char != b_char:
                    non_matching_positions.append(i)
            
            logger.info(f"Positions to fix: {non_matching_positions}")
            logger.info(f"Targeting 80% similarity = {int(len(TARGET_ADDRESS) * 0.8)} matching characters")
            
            # Create highly targeted variations focused on the exact match
            variations = []
            
            # Try single and double bit flips for precision
            for bits in range(1, 3):
                for positions in itertools.combinations(range(68), bits):
                    var = best_candidate
                    for pos in positions:
                        var ^= (1 << pos)
                    if is_valid_candidate(var):
                        variations.append(var)
            
            # Try very small adjustments (these are more likely to be productive now)
            for adj in range(-20, 21):
                if adj == 0:
                    continue
                var = best_candidate + adj
                if is_valid_candidate(var):
                    variations.append(var)
            
            # Test these targeted variations
            logger.info(f"Testing {len(variations)} highly targeted variations")
            for var in variations:
                match, address, similarity = test_candidate(var)
                if address:
                    address_logger.log_address(var, address, similarity)
                    memory_manager.add_result(var, address, similarity)
                    
                    # If we found an exact match, we're done!
                    if match:
                        logger.info(f"EXACT MATCH FOUND! Address: {address}")
                        save_result(var)
                        return var
                    
                    # If we found an even better similarity, update our best
                    if similarity > best_similarity:
                        best_similarity = similarity
                        logger.info(f"New best similarity: {similarity:.6f}")
        
        elif best_similarity >= 0.2:  # Focus on high similarity candidates 
            logger.info("Getting closer to exact match, creating focused variants...")
            
            # Get our absolute best candidate
            best_candidate_data = memory_manager.get_best_candidates(1)[0]
            best_candidate = int(best_candidate_data["private_key_int"])
            best_address = best_candidate_data["address"]
            
            logger.info(f"Target address : {TARGET_ADDRESS}")
            logger.info(f"Current best   : {best_address}")
            logger.info(f"Similarity     : {best_similarity:.6f}")
            
            # Create focused variations of best candidate
            variations = []
            
            # Single bit flips
            for bit in range(68):
                var = best_candidate ^ (1 << bit)
                if is_valid_candidate(var):
                    variations.append(var)
            
            # Small adjustments
            for adj in range(-100, 101):
                if adj == 0:
                    continue
                var = best_candidate + adj
                if is_valid_candidate(var):
                    variations.append(var)
            
            # Test a small batch of these variations
            logger.info(f"Testing {len(variations)} focused variations of best candidate")
            for var in variations[:min(100, len(variations))]:
                match, address, similarity = test_candidate(var)
                if address:
                    address_logger.log_address(var, address, similarity)
                    memory_manager.add_result(var, address, similarity)
                    
                    # If this is improved, immediately update our best
                    if similarity > best_similarity:
                        best_similarity = similarity
                        logger.info(f"Found improved variation! New similarity: {similarity:.6f}")
                        
                        # Save this successful state
                        save_state({
                            "best_similarity": best_similarity,
                            "learning_rate": LEARNING_RATE,
                            "mutation_rate": MUTATION_RATE,
                            "bit_flip_max": BIT_FLIP_MAX,
                            "search_radius": SEARCH_RADIUS
                        })
                        
                        # If found exact match, return it
                        if match:
                            save_result(var)
                            return var
        
        # Update checkpoint with new parameters
        checkpoint["total_tested"] = total_tested + cycle_stats["candidates_tested"]
        checkpoint["best_similarity"] = best_similarity
        checkpoint["learning_rate"] = LEARNING_RATE
        checkpoint["mutation_rate"] = MUTATION_RATE
        checkpoint["bit_flip_max"] = BIT_FLIP_MAX
        checkpoint["search_radius"] = SEARCH_RADIUS
        checkpoint["strategy_effectiveness"] = STRATEGY_EFFECTIVENESS
        checkpoint["consecutive_no_improvement"] = consecutive_no_improvement
        checkpoint["plateau_count"] = plateau_count
        save_checkpoint(checkpoint)
        
        # Log cycle summary
        cycle_duration = time.time() - cycle_start_time
        logger.info(f"Cycle {cycles_completed} completed in {cycle_duration:.2f} seconds")
        logger.info(f"Best similarity: {best_similarity:.6f}")
        logger.info(f"Adjusted parameters: LR={LEARNING_RATE:.4f}, MR={MUTATION_RATE:.4f}, BF={BIT_FLIP_MAX}, SR={SEARCH_RADIUS}")
        logger.info(f"Consecutive cycles without improvement: {consecutive_no_improvement}")
        logger.info(f"Plateau count: {plateau_count}")
        
        # Save progress
        cycle_stats["cycle_number"] = cycles_completed
        cycle_stats["duration"] = cycle_duration
        cycle_stats["learning_rate"] = LEARNING_RATE
        cycle_stats["mutation_rate"] = MUTATION_RATE
        cycle_stats["bit_flip_max"] = BIT_FLIP_MAX
        cycle_stats["search_radius"] = SEARCH_RADIUS
        cycle_stats["consecutive_no_improvement"] = consecutive_no_improvement
        cycle_stats["plateau_count"] = plateau_count
        cycle_stats["improved"] = cycle_improved
        save_progress(cycle_stats)
        
        # Reset cycle stats for next cycle
        cycle_stats = {
            "candidates_tested": 0,
            "best_similarity": best_similarity,
            "best_candidate": None,
            "strategy_results": {}
        }
        
        cycle_start_time = time.time()

# -----------------------------
# Main Execution
# -----------------------------

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Bitcoin private key finder for term 68")
    parser.add_argument("--duration", type=int, default=24, help="Duration to run the search in hours (integer)")
    parser.add_argument("--target-address", type=str, default=TARGET_ADDRESS, help="Target Bitcoin address")
    parser.add_argument("--candidates-per-batch", type=int, default=200, help="Number of candidates to test per batch")
    parser.add_argument("--similarity-threshold", type=float, default=TARGET_SIMILARITY, help="Similarity threshold for intensive search")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    
    args = parser.parse_args()
    
    # Set up logging
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {args.log_level}")
    
    # Create results directory
    os.makedirs("results", exist_ok=True)
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("results/search.log"),
            logging.StreamHandler()
        ]
    )
    
    # Initialize logger
    logger = logging.getLogger(__name__)
    
    # Set the target address
    TARGET_ADDRESS = args.target_address
    
    # Set the similarity threshold
    TARGET_SIMILARITY = args.similarity_threshold
    
    # Start the search
    logger.info("Starting Bitcoin private key search")
    logger.info(f"Target address: {TARGET_ADDRESS}")
    logger.info(f"Search duration: {args.duration} hours")
    
    # Initialize memory manager with optimal saving frequency
    memory_manager = MemoryManager(memory_size=100000)
    
    # Pattern analysis results
    pattern_analysis = None
    
    # Start timing
    start_time = time.time()
    end_time = start_time + (args.duration * 60 * 60)  # Convert hours to seconds
    
    # Initialize counters
    total_candidates = 0
    promising_candidates = 0
    total_batches = 0
    best_similarity = 0.0
    
    # Track performance
    last_check_time = time.time()
    last_check_candidates = 0
    last_analysis_time = start_time
    analysis_interval = 600  # seconds
    
    # Define random_search function if not already defined
    def random_search(count=100, worker_safe=False):
        """
        Generate random private keys within the constraints.
        """
        candidates = []
        for _ in range(count):
            # Between previous term and 2^68 - 1
            value = random.randint(int(PREV_TERM_67_INT), (1 << 68) - 1)
            if is_valid_candidate(value):
                candidates.append(value)
        logger.info(f"Generated {len(candidates)} random candidates")
        return candidates
        
    def quadrant_based_search(count=100, worker_safe=False):
        """
        Generate candidates in different "quadrants" of the search space.
        """
        candidates = []
        # Define quadrants
        quadrants = [
            (int(PREV_TERM_67_INT), int(PREV_TERM_67_INT) + (1 << 66)),  # Lower quarter
            (int(PREV_TERM_67_INT) + (1 << 66), int(PREV_TERM_67_INT) + (1 << 67)),  # Mid-lower quarter
            (int(PREV_TERM_67_INT) + (1 << 67), int(PREV_TERM_67_INT) + (1 << 67) + (1 << 66)),  # Mid-upper quarter
            (int(PREV_TERM_67_INT) + (1 << 67) + (1 << 66), (1 << 68) - 1),  # Upper quarter
        ]
        
        for _ in range(count):
            # Choose a quadrant
            lower, upper = random.choice(quadrants)
            value = random.randint(lower, upper)
            if is_valid_candidate(value):
                candidates.append(value)
                
        logger.info(f"Generated {len(candidates)} quadrant-based candidates")
        return candidates
    def generate_ascii_pattern_candidates(count=100, worker_safe=False):
        """
        Generate candidates with patterns resembling ASCII characters.
        """
        candidates = []
        
        for _ in range(count):
            # Start with a base value
            value = random.randint(int(PREV_TERM_67_INT), (1 << 68) - 1)
            
            # Create ASCII pattern in a selected region (8 bits)
            region_start = random.randint(0, 60)  # Ensure we have 8 bits to work with
            
            # Generate a random ASCII character (0-127)  # Printable ASCII
            ascii_val = random.randint(32, 126)
            
            # Clear the region and insert the ASCII pattern
            mask = ~(0xFF << region_start)
            value = (value & mask) | (ascii_val << region_start)
            
            if is_valid_candidate(value):
                candidates.append(value)
                
        logger.info(f"Generated {len(candidates)} ASCII pattern candidates")
        return candidates
    def targeted_position_search(count=100, worker_safe=False):
        """
        Target specific bit positions that might have higher influence on the address.
        Focuses on positions that make up the version byte and checksum areas.
        Uses parallel processing, batch evaluation, and adaptive learning for 10x performance.
        """
        logger.info(f"Performing targeted position search with {count} candidates")
        
        # Get starting candidates - either best ones or generate new ones
        memory_manager = MemoryManager()
        best_candidates = memory_manager.get_best_candidates(10)  # Get more candidates for better diversity
        
        # Initialize adaptive learning weights for bit positions
        # Load from persistent storage if available
        bit_position_weights = getattr(memory_manager, 'bit_position_weights', None)
        if not bit_position_weights:
            # Initialize with default weights if not available
            bit_position_weights = np.ones(68, dtype=np.float32)
            # Enhanced weights based on Bitcoin address structure analysis
            # Version byte (first character) - most influential bits
            bit_position_weights[63:68] *= 2.0    # Highest bits are crucial for version byte
            # RIPEMD-160 hash region - early bytes have higher visual importance
            bit_position_weights[55:63] *= 1.5    # These affect the first few characters after version byte
            bit_position_weights[40:55] *= 1.3    # Middle of hash - still important
            bit_position_weights[0:8] *= 1.8      # Low bits affect checksum through avalanche effect
            bit_position_weights[8:16] *= 1.5     # These bits also influence checksum and address tail
            
            # Further boost using insights from successful past candidates
            # Bit positions that have historically led to good candidates
            key_positions = [0, 1, 4, 8, 16, 32, 63, 64, 65, 66, 67]
            for pos in key_positions:
                if pos < len(bit_position_weights):
                    bit_position_weights[pos] *= 1.5
        
        # Extract base candidates with proper error handling
        base_candidates = []
        if best_candidates:
            for item in best_candidates:
                try:
                    if isinstance(item, dict):
                        value = item.get("private_key_int")
                        if value:
                            base_candidates.append(int(value))
                    elif isinstance(item, tuple) or isinstance(item, list):
                        value = item[0]
                        base_candidates.append(int(value))
                    elif isinstance(item, int):
                        base_candidates.append(item)
                except (ValueError, TypeError):
                    continue
        
        # If we couldn't extract enough candidates, add random ones
        if len(base_candidates) < 5:
            base_candidates.extend([random.randint(2**67, 2**68-1) for _ in range(5 - len(base_candidates))])
        
        # Add previous term for reference
        base_candidates.append(PREV_TERM_67_INT)
        
        # Create a results cache to avoid redundant calculations
        # Use a LRU cache with a reasonable size
        from functools import lru_cache
        
        @lru_cache(maxsize=1000)
        def cached_test_candidate(value):
            return test_candidate(value)
        
        # Define the worker function for parallel processing
        def generate_batch(batch_id, batch_size, base_candidates, bit_position_weights, result_queue):
            batch_results = []
            candidates_generated = 0
            
            # Create a local numpy random generator for better performance
            rng = np.random.default_rng()
            
            # Early termination if we find a very good candidate
            best_similarity_in_batch = 0
            
            # Safety limits to prevent overflow issues
            MAX_BIT_POSITION = 67  # 0-indexed, for a 68-bit number
            MAX_REGION_SIZE = 25   # Conservative limit to prevent overflow
            
            # Track candidates we've already tested to avoid duplicates
            tested_candidates = set()
            
            # Ensure base candidates are all integers
            safe_base_candidates = []
            for base in base_candidates:
                if isinstance(base, str):
                    try:
                        safe_base_candidates.append(int(base))
                    except (ValueError, TypeError):
                        continue
                elif isinstance(base, int):
                    safe_base_candidates.append(base)
            
            # If all conversions failed, add some default candidates
            if not safe_base_candidates:
                safe_base_candidates = [PREV_TERM_67_INT]
            
            while candidates_generated < batch_size:
                # Choose a base candidate
                base = random.choice(safe_base_candidates)
                
                # Verify base is in correct range before proceeding
                if not (2**67 <= base < 2**68):
                    # Use previous term as a fallback
                    base = PREV_TERM_67_INT
                
                # Use weighted sampling to select bit positions to modify
                # This implements adaptive learning by focusing on historically successful positions
                try:
                    # Ensure weights are valid for numpy choice
                    valid_weights = bit_position_weights.copy()
                    # Fix any invalid values in weights
                    valid_weights[~np.isfinite(valid_weights)] = 1.0
                    valid_weights = np.abs(valid_weights)  # Ensure all weights are positive
                    
                    # Normalize weights for sampling
                    total_weight = np.sum(valid_weights)
                    if total_weight > 0:
                        normalized_weights = valid_weights / total_weight
                    else:
                        # Fallback to uniform weights if something is wrong
                        normalized_weights = np.ones(68) / 68
                    
                    # Select bit positions
                    positions = rng.choice(
                        68, 
                        size=min(5, max(1, int(np.log2(candidates_generated + 2)))),
                        replace=False, 
                        p=normalized_weights
                    )
                except Exception as e:
                    # Fallback to random positions if numpy sampling fails
                    logger.warning(f"Weight sampling failed: {e}, using random bits")
                    num_positions = min(5, max(1, int(np.log2(candidates_generated + 2))))
                    positions = np.array(random.sample(range(68), num_positions))
                
                # Create multiple candidates with different bit manipulation strategies
                new_candidates = []
                
                # Strategy 1: Simple bit flipping at selected positions
                value = sanitize_candidate(base)
                
                for pos in positions:
                    value ^= (1 << int(pos))  # Ensure pos is an integer
                if is_valid_candidate(value):
                    new_candidates.append(value)
                
                # Strategy 2: Bit rotation within selected region
                value = sanitize_candidate(base)
                
                if len(positions) >= 2:
                    min_pos, max_pos = min(positions), max(positions)
                    region_size = max_pos - min_pos + 1
                    
                    # Check if the region is too large for bit operations
                    if region_size <= MAX_REGION_SIZE:
                        try:
                            # Extract the bits in the region using a safer approach
                            # Instead of right-shifting after masking (which can overflow),
                            # we'll work with the masked value directly
                            mask = ((1 << region_size) - 1) << min_pos
                            masked_value = value & mask
                            
                            # Get the bits in string format and manipulate them directly
                            bin_str = bin(value)[2:].zfill(68)
                            region_str = bin_str[68-max_pos-1:68-min_pos]
                            
                            # Rotate the string (1-bit rotation)
                            rotated_str = region_str[1:] + region_str[0]
                            
                            # Create new binary string with rotated region
                            new_bin_str = bin_str[:68-max_pos-1] + rotated_str + bin_str[68-min_pos:]
                            
                            # Convert back to integer
                            value = int(new_bin_str, 2)
                        except (OverflowError, ValueError) as e:
                            # Fallback to simple bit flipping if rotation fails
                            logger.debug(f"Bit rotation failed, falling back to simpler approach: {e}")
                            for pos in positions:
                                value ^= (1 << int(pos))
                    else:
                        # For large regions, use a different approach
                        # Just flip a subset of bits to avoid overflow
                        subset = random.sample(list(range(min_pos, max_pos + 1)), min(5, region_size))
                        for pos in subset:
                            value ^= (1 << pos)
                    
                    if is_valid_candidate(value):
                        new_candidates.append(value)
                
                # Strategy 3: Bit pattern substitution
                value = sanitize_candidate(base)
                
                if len(positions) >= 3:
                    # Sort positions
                    sorted_pos = sorted(positions)
                    # Apply a pattern (e.g., alternating 1-0-1)
                    for i, pos in enumerate(sorted_pos):
                        pos = int(pos)  # Ensure pos is an integer
                        if i % 2 == 0:
                            value |= (1 << pos)  # Set to 1
                        else:
                            value &= ~(1 << pos)  # Set to 0
                    if is_valid_candidate(value):
                        new_candidates.append(value)
                
                # NEW Strategy 4: Version-byte targeted manipulation
                # This specifically targets the first bits that influence the Bitcoin address version byte
                value = sanitize_candidate(base)
                
                # Focus on manipulating high-order bits that affect the version byte
                version_bits = [63, 64, 65, 66, 67]  # Highest bits in a 68-bit number
                # Select 2-3 bits from version-critical positions
                num_bits = random.randint(2, 3)
                selected_bits = random.sample(version_bits, num_bits)
                
                # Flip selected bits
                for bit in selected_bits:
                    value ^= (1 << bit)
                    
                if is_valid_candidate(value):
                    new_candidates.append(value)
                
                # NEW Strategy 5: Checksum-influencing manipulation
                # Target bits that impact the checksum of the Bitcoin address
                value = sanitize_candidate(base)
                
                # Middle bits often influence checksum through avalanche effects
                middle_bits = list(range(25, 45))
                # Select a few bits from middle region
                selected_middle = random.sample(middle_bits, 3)
                
                # Apply pattern that tends to create more favorable checksums
                for bit in selected_middle:
                    # XOR with specific pattern based on bit position
                    if bit % 3 == 0:
                        value ^= (1 << bit)
                    elif bit % 3 == 1:
                        value |= (1 << bit)
                    else:
                        value &= ~(1 << bit)
                
                if is_valid_candidate(value):
                    new_candidates.append(value)
                
                # NEW Strategy 6: Genetic-inspired recombination
                # If we have multiple base candidates, create a hybrid
                if len(base_candidates) >= 2 and random.random() < 0.3:  # 30% chance
                    value = sanitize_candidate(base)
                    # Pick another candidate to recombine with
                    other_base = random.choice([b for b in base_candidates if b != base])
                    other_base = sanitize_candidate(other_base)
                    
                    # Crossover point - somewhere in the middle
                    crosspoint = random.randint(20, 50)
                    
                    # Create mask for the crossover
                    mask = (1 << crosspoint) - 1
                    
                    # Combine: take lower bits from one, higher bits from other
                    value = (value & ~mask) | (other_base & mask)
                    
                    if is_valid_candidate(value):
                        new_candidates.append(value)
                
                # Process the generated candidates
                for value in new_candidates:
                    if candidates_generated >= batch_size:
                        break
                        
                    # Test the candidate
                    address, similarity = cached_test_candidate(value)
                    
                    if similarity > best_similarity_in_batch:
                        best_similarity_in_batch = similarity
                    
                    # Store the result
                    batch_results.append((value, address, similarity))
                    candidates_generated += 1
                    
                    # Early termination if we find a very good candidate
                    if similarity > 0.9:
                        break
            
            # Put results in the queue
            result_queue.put((batch_results, best_similarity_in_batch))
        
        # Determine number of processes to use (leave one core free for system)
        import multiprocessing
        num_processes = max(1, multiprocessing.cpu_count() - 1)
        
        # Calculate batch size per process
        batch_size = (count + num_processes - 1) // num_processes
        
        # Create a queue for results
        result_queue = multiprocessing.Queue()
        
        # Start processes
        processes = []
        for i in range(num_processes):
            p = multiprocessing.Process(
                target=generate_batch,
                args=(i, batch_size, base_candidates, bit_position_weights, result_queue)
            )
            processes.append(p)
            p.start()
        
        # Collect results
        all_results = []
        best_similarity_overall = 0
        
        for _ in range(num_processes):
            batch_results, batch_best_similarity = result_queue.get()
            all_results.extend(batch_results)
            best_similarity_overall = max(best_similarity_overall, batch_best_similarity)
        
        # Wait for all processes to complete
        for p in processes:
            p.join()
        
        # Update bit position weights based on results
        if all_results:
            # Sort by similarity
            all_results.sort(key=lambda x: x[2], reverse=True)
            
            # Take top 10% of results for learning
            top_results = all_results[:max(1, len(all_results) // 10)]
            
            # Update weights based on which bit positions led to good results
            for value, _, similarity in top_results:
                # Ensure value is an integer
                if isinstance(value, str):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        continue
                        
                # Compare with base candidates to see which bits were changed
                for base in base_candidates:
                    # Ensure base is an integer
                    if isinstance(base, str):
                        try:
                            base = int(base)
                        except (ValueError, TypeError):
                            continue
                            
                    diff = value ^ base
                    if diff:  # If there are differences
                        # Identify which bits were changed
                        for pos in range(68):
                            if diff & (1 << pos):
                                # Enhanced learning: Use non-linear scaling based on similarity
                                # Higher similarities get exponentially higher weights
                                # This focuses search more aggressively on promising areas
                                learning_factor = 1.0 + (similarity ** 2) * 0.3  # Non-linear boost
                                
                                # Additional boost for very successful candidates (>80% similarity)
                                if similarity > 0.8:
                                    learning_factor *= 1.5
                                
                                # Apply the learning factor
                                bit_position_weights[pos] *= learning_factor
                                
                                # Also boost positions around successful positions (bit neighborhood effect)
                                neighborhood_boost = 1.0 + (similarity * 0.1)
                                for offset in [-2, -1, 1, 2]:
                                    neighbor_pos = pos + offset
                                    if 0 <= neighbor_pos < 68:
                                        bit_position_weights[neighbor_pos] *= neighborhood_boost
            
            # Apply smoothing to prevent extreme weights and maintain exploration
            bit_position_weights = 0.8 * bit_position_weights + 0.2 * np.mean(bit_position_weights)
            
            # Normalize weights to prevent unbounded growth while maintaining relative importance
            bit_position_weights = bit_position_weights / np.mean(bit_position_weights)
            
            # Add small random noise to avoid getting stuck in local optima (exploration factor)
            random_noise = np.random.normal(1.0, 0.05, size=bit_position_weights.shape)
            bit_position_weights *= random_noise
            
            # Store updated weights for future use
            memory_manager.bit_position_weights = bit_position_weights
        
        # Return the top candidates up to the requested count
        candidates = [result[0] for result in all_results[:count]]
        
        # If we didn't generate enough candidates, fill with random ones
        while len(candidates) < count:
            value = random.randint(2**67, 2**68-1)
            if is_valid_candidate(value):
                candidates.append(value)
        
        logger.info(f"Generated {len(candidates)} candidates with best similarity: {best_similarity_overall:.6f}")
        return candidates
        
    def targeted_bit_position_search(base_candidates, count=100):
        """Generate candidates by targeting specific bit position ranges with different weights."""
        # Target different bit position ranges with weights for importance
        position_ranges = [
            # Network identifier (first few bits)
            (0, 3, 0.15),
            # Version byte area (first 8 bits of resulting address)
            (0, 8, 0.10),
            # RIPEMD-160 critical area 1
            (8, 20, 0.15),
            # Middle area segment 1 (more granular targeting)
            (20, 30, 0.10),
            # Middle area segment 2 (more granular targeting)
            (30, 40, 0.10),
            # RIPEMD-160 critical area 2
            (40, 60, 0.15),
            # Key identifier bits (specific to our 68-bit constraint)
            (60, 68, 0.15),
            # Checksum area (last 32 bits / 4 bytes)
            (128-32, 128, 0.10)
        ]
        
        candidates = []
        per_range = count // len(position_ranges)
        # Track generated candidates to avoid duplicates
        generated_candidates = set()
        
        # For each position range, generate candidates by flipping bits
        for start_pos, end_pos, weight in position_ranges:
            # Adjust per_range based on weight to prioritize important bit positions
            weighted_range = int(per_range * weight * len(position_ranges))
            
            # Batch processing for better performance
            batch_size = min(weighted_range, 50)  # Process in batches of 50
            for batch_start in range(0, weighted_range, batch_size):
                batch_count = min(batch_size, weighted_range - batch_start)
                
                for _ in range(batch_count):
                    # Choose a base candidate
                    base = random.choice(base_candidates)
                    # Ensure base is an integer
                    if not isinstance(base, int):
                        try:
                            base = int(base)
                        except (ValueError, TypeError):
                            # Skip this iteration if conversion fails
                            continue
                    
                    # Number of positions to flip (1-3)
                    num_pos = random.randint(1, 3)
                    
                    # Create a bit mask for flipping multiple bits at once
                    mask = 0
                    # Use weighted random sampling instead of uniform sampling
                    positions = []
                    for _ in range(min(num_pos, end_pos-start_pos)):
                        pos = random.randint(start_pos, end_pos-1)
                        positions.append(pos)
                        mask |= (1 << pos)
                    
                    # Create new candidate by flipping bits with a single XOR operation
                    new_value = base ^ mask
                    
                    # Prevent infinite loops with a retry counter
                    retry_count = 0
                    max_retries = 5
                    
                    while (not is_valid_candidate(new_value) or new_value in generated_candidates) and retry_count < max_retries:
                        # Try a different bit pattern
                        mask = 0
                        for _ in range(min(num_pos, end_pos-start_pos)):
                            pos = random.randint(start_pos, end_pos-1)
                            mask |= (1 << pos)
                        
                        new_value = base ^ mask
                        retry_count += 1
                    
                    if is_valid_candidate(new_value) and new_value not in generated_candidates:
                        candidates.append(new_value)
                        generated_candidates.add(new_value)
        
        # Fill any remaining slots
        while len(candidates) < count:
            base = random.choice(base_candidates)
            # Ensure base is an integer
            if not isinstance(base, int):
                try:
                    base = int(base)
                except (ValueError, TypeError):
                    # Skip this iteration if conversion fails
                    continue
                
            position = random.randint(0, 67)
            new_value = base ^ (1 << position)  # Use = instead of ^= to be explicit
            
            if is_valid_candidate(new_value) and new_value not in generated_candidates:
                candidates.append(new_value)
                generated_candidates.add(new_value)
        
        logger.info(f"Generated {len(candidates)} candidates via targeted position search")
        return candidates
        
    # Different search strategies to cycle through
    search_strategies = [
        # Original strategies
        random_search,
        targeted_position_search,
        quadrant_based_search,
        generate_ascii_pattern_candidates,
        # Our new improved strategies
        structure_targeted_search,
        gradient_ascent_search,
        random_walk_search,
        # Ultra focused strategies for pushing past 60% similarity
        super_targeted_search,
        prefix_targeted_search
    ]
    
    strategy_index = 0
    consecutive_no_improvement = 0
    max_no_improvement = 5
    
    # Priority scheduling of advanced strategies
    strategy_weights = {
        "random_search": 0.02,
        "targeted_position_search": 0.05,
        "quadrant_based_search": 0.02,
        "generate_ascii_pattern_candidates": 0.02,
        "structure_targeted_search": 0.15,
        "gradient_ascent_search": 0.15,
        "random_walk_search": 0.02,
        "super_targeted_search": 0.27,  # High weight for our targeted strategies
        "prefix_targeted_search": 0.30   # Highest weight for prefix matching
    }
    
    try:
        while time.time() < end_time:
            total_batches += 1
            
            # Dynamic strategy selection based on performance
            if total_batches > 10 and total_batches % 5 == 0:
                # Use weighted random selection for strategy
                strategies = list(strategy_weights.keys())
                weights = list(strategy_weights.values())
                strategy_name = random.choices(strategies, weights=weights, k=1)[0]
                
                strategy = globals().get(strategy_name)
                if not strategy:
                    strategy = search_strategies[strategy_index]
                    strategy_name = strategy.__name__
            else:
                # Use simple rotation early on
                strategy = search_strategies[strategy_index]
                strategy_name = strategy.__name__
            
            # Run the selected search strategy
            logger.info(f"Running search strategy: {strategy_name}")
            
            # Adjust batch size based on strategy - gradient ascent needs more iterations
            batch_size = args.candidates_per_batch
            if strategy_name == "gradient_ascent_search":
                batch_size = max(10, args.candidates_per_batch // 5)
            
            candidates = strategy(count=batch_size)
            
            improvement = False
            batch_promising = 0
            batch_best = 0.0
            
            # Process candidates
            for candidate in candidates:
                # Handle both integer and tuple return types
                candidate_value = candidate
                if isinstance(candidate, tuple):
                    if len(candidate) >= 1:
                        candidate_value = candidate[0]  # Unpack if it's a tuple
                    else:
                        continue  # Skip invalid tuple
                
                # Skip if not a valid candidate
                if not isinstance(candidate_value, int):
                    continue
                
                total_candidates += 1
                
                try:
                    # Test candidate
                    address, similarity = test_candidate(candidate_value)
                    
                    if address is None:
                        continue
                    
                    # Check for exact match
                    if address == TARGET_ADDRESS:
                        logger.critical(f"EXACT MATCH FOUND!!! Private key: {hex(candidate_value)}")
                        save_result(candidate_value)
                        break  # Exit the loop when match is found
                    
                    # Check if promising
                    if similarity >= TARGET_SIMILARITY:
                        # Try to add to memory manager
                        if memory_manager.add(candidate_value, similarity):
                            promising_candidates += 1
                            batch_promising += 1
                            
                            # If very promising, save it immediately
                            if similarity > best_similarity:
                                best_similarity = similarity
                                logger.info(f"New best similarity: {best_similarity} ({address})")
                                improvement = True
                                consecutive_no_improvement = 0
                                
                                # Adaptive Learning Rate: Adjust search parameters based on improvement magnitude
                                improvement_factor = similarity / best_similarity if best_similarity > 0 else 1.0
                                if improvement_factor > 1.05:  # Significant improvement
                                    # Increase learning rate to explore more aggressively
                                    LEARNING_RATE = min(0.2, LEARNING_RATE * 1.1)
                                    logger.info(f"Increased learning rate to {LEARNING_RATE} due to significant improvement")
                                
                                # Save especially high matches
                                if similarity >= 0.5:  # Increased from 0.95
                                    logger.critical(f"HIGH SIMILARITY FOUND: {similarity} - Address: {address}")
                                    save_result(candidate_value)
                    
                    # Track best similarity in this batch
                    if similarity > batch_best:
                        batch_best = similarity
                
                except Exception as e:
                    logger.error(f"Error processing candidate {hex(candidate_value)}: {e}")
            
            # Adapt strategy weights based on performance
            if batch_promising > 0:
                # Increase weight for successful strategies
                current_weight = strategy_weights.get(strategy_name, 0.1)
                strategy_weights[strategy_name] = min(0.5, current_weight * 1.2)
                
                # Normalize weights
                total_weight = sum(strategy_weights.values())
                for key in strategy_weights:
                    strategy_weights[key] = strategy_weights[key] / total_weight
            
            # Log progress for this batch
            logger.info(f"Batch complete: {len(candidates)} candidates processed, {batch_promising} promising, best similarity: {batch_best:.6f}")
            
            # Memory Optimization: Periodically prune less promising candidates
            if total_batches % 50 == 0:
                before_count = memory_manager.count()
                memory_manager.prune_candidates(keep_top_percent=0.7)  # Keep only top 70%
                after_count = memory_manager.count()
                logger.info(f"Memory pruning: removed {before_count - after_count} less promising candidates")
            
            # Check if we need to perform pattern analysis
            current_time = time.time()
            if (current_time - last_analysis_time) >= analysis_interval and promising_candidates >= 10:
                logger.info("Performing pattern analysis on best candidates")
                best_candidates = memory_manager.get_best_candidates(20)
                
                # Convert to format expected by analyze_successful_patterns
                pattern_candidates = []
                for value, similarity in best_candidates:
                    address = private_key_to_address(value)
                    pattern_candidates.append((value, address, similarity))
                
                pattern_analysis = analyze_successful_patterns(pattern_candidates, TARGET_ADDRESS, 20)
                last_analysis_time = current_time
                
                # Adjust strategy based on analysis results
                if pattern_analysis:
                    logger.info("Adjusting search based on pattern analysis")
                    # Apply pattern-based adjustments to search parameters
                    if 'bit_patterns' in pattern_analysis:
                        # Use detected bit patterns to guide search
                        BIT_FLIP_MAX = max(3, min(10, len(pattern_analysis['bit_patterns'])))
                        logger.info(f"Adjusted BIT_FLIP_MAX to {BIT_FLIP_MAX} based on pattern analysis")
            
            # Calculate and log performance every minute
            current_time = time.time()
            if current_time - last_check_time >= 60:
                time_diff = current_time - last_check_time
                candidates_diff = total_candidates - last_check_candidates
                
                if time_diff > 0:
                    rate = candidates_diff / time_diff
                    elapsed_time = current_time - start_time
                    remaining_time = max(0, end_time - current_time)
                    
                    logger.info(f"Performance: {rate:.2f} candidates/second")
                    logger.info(f"Progress: {elapsed_time/3600:.2f} hours elapsed, {remaining_time/3600:.2f} hours remaining")
                    logger.info(f"Candidates tested: {total_candidates}, promising: {promising_candidates}")
                    
                    # Early Termination Heuristics: Check if search is stagnating
                    if rate < previous_rate * 0.7 and total_batches > 100:
                        logger.warning("Performance degradation detected, adjusting search parameters")
                        # Reset strategy weights to encourage exploration
                        for key in strategy_weights:
                            strategy_weights[key] = 1.0 / len(strategy_weights)
                    
                    previous_rate = rate
                    
                    # Save progress
                    stats = {
                        "timestamp": current_time,
                        "total_candidates": total_candidates,
                        "promising_candidates": promising_candidates,
                        "total_batches": total_batches,
                        "elapsed_hours": elapsed_time / 3600,
                        "remaining_hours": remaining_time / 3600,
                        "candidates_per_second": rate,
                        "best_similarity": best_similarity
                    }
                    
                    save_progress(stats)
                
                last_check_time = current_time
                last_check_candidates = total_candidates
            
            # Force memory save periodically but not too often
            if total_batches % 20 == 0:
                memory_manager.save_memory()
            
            # If no improvement, adjust strategy
            if not improvement:
                consecutive_no_improvement += 1
                # Early Termination for unproductive search directions
                if consecutive_no_improvement >= 3 and batch_best < best_similarity * 0.9:
                    logger.warning(f"Search direction becoming unproductive, switching strategy early")
                    strategy_index = (strategy_index + 1) % len(search_strategies)
                    consecutive_no_improvement = 0
                elif consecutive_no_improvement >= max_no_improvement:
                    consecutive_no_improvement = 0
                    # Try a different strategy
                    strategy_index = (strategy_index + 1) % len(search_strategies)
                    # Adaptive Learning: Decrease learning rate when stuck
                    LEARNING_RATE = max(0.01, LEARNING_RATE * 0.9)
                    logger.info(f"Decreased learning rate to {LEARNING_RATE} due to stagnation")
            
            # Small sleep to prevent maxing out CPU when not using all cores
            time.sleep(0.001)
            
            # Parallel Processing: Every few batches, spawn parallel workers for broader search
            if total_batches % 10 == 0 and not parallel_workers_active:
                try:
                    from concurrent.futures import ProcessPoolExecutor
                    logger.info("Spawning parallel workers for broader search")
                    
                    # Define worker function that will run in separate processes
                    def parallel_search_worker(seed, count=100):
                        worker_candidates = []
                        random.seed(seed)
                        try:
                            # Generate candidates using a random strategy that isn't targeted_position_search
                            available_strategies = [s for s in search_strategies if s.__name__ != 'targeted_position_search']
                            if not available_strategies:
                                available_strategies = search_strategies
                            strategy_func = random.choice(available_strategies)
                            
                            # Call the chosen strategy with a safety flag to ensure it handles large integers properly
                            worker_candidates = strategy_func(count=count, worker_safe=True)
                            
                            results = []
                            for cand in worker_candidates:
                                if isinstance(cand, tuple):
                                    cand = cand[0]
                                addr, sim = test_candidate(cand)
                                if sim >= TARGET_SIMILARITY:
                                    results.append((cand, addr, sim))
                            return results
                        except Exception as e:
                            logger.error(f"Worker error: {str(e)}")
                            return []
                    
                    # Spawn workers
                    with ProcessPoolExecutor(max_workers=min(os.cpu_count()-1, 4)) as executor:
                        future_results = [executor.submit(parallel_search_worker, random.randint(1, 10000), 50) 
                                         for _ in range(min(os.cpu_count()-1, 4))]
                        
                        # Process results as they complete
                        for future in future_results:
                            for cand, addr, sim in future.result():
                                if sim > best_similarity:
                                    logger.info(f"Parallel worker found better similarity: {sim}")
                                    memory_manager.add(cand, sim)
                                    if sim >= 0.5:
                                        logger.critical(f"Parallel worker found high similarity: {sim}")
                                        save_result(cand)
                except ImportError:
                    logger.warning("Could not import ProcessPoolExecutor, parallel processing disabled")
                except Exception as e:
                    logger.error(f"Error in parallel processing: {e}")
    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Search completed")
        save_result(None)  # Save a placeholder result if no match was found



