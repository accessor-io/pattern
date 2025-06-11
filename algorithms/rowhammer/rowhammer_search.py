#!/usr/bin/env python3
"""
RowHammer-Inspired Search for Term 68
Target address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ

This script implements a search approach inspired by the RowHammer memory 
vulnerability to find the Bitcoin private key for Term 68. RowHammer is a hardware 
vulnerability where repeatedly accessing certain memory rows causes bit flips
in adjacent rows due to electrical interference.

Based on insights from the Hammulator framework (https://dramsec.ethz.ch/papers/hammulator.pdf)
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import os
import json
import logging
import random
import itertools
import traceback
import sys
from datetime import datetime
import numpy as np
import struct
from collections import deque  # For tracking recently tested candidates
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import pickle

# Setup logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rowhammer_search.log'),
        logging.StreamHandler(sys.stdout)  # Also output to console
    ]
)
logger = logging.getLogger(__name__)

# Target information
TARGET_INDEX = 68
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Known previous term
PREV_TERM_67 = "0x730fc235c1942c1ae"
PREV_TERM_67_INT = int(PREV_TERM_67, 16)

# Values discovered from previous analyses
ESTIMATE_VALUE = 0x734fc235c1940c1af  # Updated based on best result from debug

# Constants for RowHammer simulation (based on Hammulator paper)
HAMMER_ITERATIONS = 1000  # Number of simulated row hammer attempts
ADJACENT_INFLUENCE = 3    # Number of adjacent bits that might be affected
ACTIVATION_THRESHOLD = 100  # Minimum hammers needed for bit flips
MAX_FLIPS_PER_HAMMER = 3   # Max bit flips per hammer operation
FLIP_PROBABILITY = 0.05    # Probability of a bit flip occurring once threshold is reached

# File paths
RESULT_FILE = "term68_rowhammer_result.json"
CLOSEST_ADDRESSES = "rowhammer_closest_addresses.json"
PROGRESS_FILE = "rowhammer_progress.json"
TESTED_CANDIDATES_FILE = "tested_candidates.json"  # New file to track tested candidates

# Continuous search parameters
SAVE_INTERVAL = 5  # Save progress every 5 iterations
ADAPTATION_INTERVAL = 10  # Adapt parameters every 10 iterations
MAX_RECENT_CANDIDATES = 10000  # Maximum number of recent candidates to track for avoiding repetition

# Global candidate tracking
recent_candidates = deque(maxlen=MAX_RECENT_CANDIDATES)  # Store recently tested candidates to avoid repetition
unique_candidates_count = 0  # Track unique candidates tested
total_candidates_count = 0  # Track total candidates tested

# Add new constants for sequence-based patterns
SEQUENCE_PATTERNS = {
    "consecutive": [1, 2, 4, 8, 16, 32],  # Powers of 2
    "fibonacci": [1, 1, 2, 3, 5, 8, 13, 21],  # Fibonacci sequence
    "prime": [2, 3, 5, 7, 11, 13, 17, 19],  # Prime numbers
    "hamming": [1, 2, 4, 8, 16, 32, 64]  # Hamming weight sequence
}

# Add new constants for pattern-based bit manipulation
BIT_PATTERNS = {
    "consecutive_zeros": [1, 2, 4, 4, 3, 1, 1, 5, 2, 1, 4, 1, 5, 1, 1, 1],
    "consecutive_ones": [3, 2, 6, 1, 2, 1, 3, 2, 1, 1, 1, 2, 2, 1, 3],
    "xor_masks": {
        "min": 0xf4481fb9e719ff06a,
        "max": 0xa4d4eaffeaae1fda2,
        "shifted": 0x94f7c6cdc3942c66
    }
}

class LearningSystem:
    """
    Self-learning system to analyze and adapt search patterns
    """
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.training_data = []
        self.training_labels = []
        self.pattern_history = []
        self.successful_patterns = []
        self.model_file = "rowhammer_learning_model.pkl"
        self.scaler_file = "rowhammer_scaler.pkl"
        self.load_model()
    
    def load_model(self):
        """Load previously trained model if available"""
        try:
            if os.path.exists(self.model_file) and os.path.exists(self.scaler_file):
                self.model = joblib.load(self.model_file)
                self.scaler = joblib.load(self.scaler_file)
                logger.info("Loaded previously trained learning model")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def save_model(self):
        """Save the current model state"""
        try:
            joblib.dump(self.model, self.model_file)
            joblib.dump(self.scaler, self.scaler_file)
            logger.info("Saved learning model state")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def extract_features(self, candidate, pattern_used, similarity):
        """Extract features from a candidate for learning"""
        bits = [int(b) for b in bin(candidate)[2:].zfill(68)]
        features = [
            sum(bits),  # Hamming weight
            sum(1 for i in range(len(bits)-1) if bits[i] != bits[i+1]),  # Bit transitions
            len([i for i in range(len(bits)-1) if bits[i] == 0 and bits[i+1] == 0]),  # Consecutive zeros
            len([i for i in range(len(bits)-1) if bits[i] == 1 and bits[i+1] == 1]),  # Consecutive ones
            similarity,  # Address similarity
            pattern_used,  # Pattern used (encoded)
            candidate % 4,  # Last 2 bits
            (candidate >> 32) % 4,  # Middle bits
            (candidate >> 64) % 4   # First bits
        ]
        return features
    
    def update(self, candidate, pattern_used, similarity, success):
        """Update the learning system with new data"""
        features = self.extract_features(candidate, pattern_used, similarity)
        self.training_data.append(features)
        self.training_labels.append(1 if success else 0)
        
        # Store pattern information
        self.pattern_history.append({
            "pattern": pattern_used,
            "similarity": similarity,
            "success": success,
            "timestamp": time.time()
        })
        
        # Keep only recent history
        if len(self.pattern_history) > 1000:
            self.pattern_history = self.pattern_history[-1000:]
        
        # Update successful patterns
        if success:
            self.successful_patterns.append({
                "pattern": pattern_used,
                "similarity": similarity,
                "features": features,
                "timestamp": time.time()
            })
        
        # Retrain model periodically
        if len(self.training_data) >= 100:
            self.train()
    
    def train(self):
        """Train the model on collected data"""
        if len(self.training_data) < 10:
            return
            
        try:
            X = np.array(self.training_data)
            y = np.array(self.training_labels)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            logger.info("Retrained learning model")
            
            # Save updated model
            self.save_model()
        except Exception as e:
            logger.error(f"Error training model: {e}")
    
    def predict_success_probability(self, candidate, pattern_used, similarity):
        """Predict probability of success for a candidate"""
        try:
            features = self.extract_features(candidate, pattern_used, similarity)
            X = np.array([features])
            X_scaled = self.scaler.transform(X)
            prob = self.model.predict_proba(X_scaled)[0][1]
            return prob
        except Exception as e:
            logger.error(f"Error predicting success probability: {e}")
            return 0.5
    
    def get_best_patterns(self, n=5):
        """Get the most successful patterns"""
        if not self.successful_patterns:
            return []
        
        # Sort by similarity and recency
        sorted_patterns = sorted(
            self.successful_patterns,
            key=lambda x: (x["similarity"], x["timestamp"]),
            reverse=True
        )
        return sorted_patterns[:n]
    
    def analyze_pattern_effectiveness(self):
        """Analyze effectiveness of different patterns"""
        pattern_stats = {}
        
        for entry in self.pattern_history:
            pattern = entry["pattern"]
            if pattern not in pattern_stats:
                pattern_stats[pattern] = {
                    "count": 0,
                    "successes": 0,
                    "avg_similarity": 0,
                    "total_similarity": 0
                }
            
            stats = pattern_stats[pattern]
            stats["count"] += 1
            stats["total_similarity"] += entry["similarity"]
            stats["avg_similarity"] = stats["total_similarity"] / stats["count"]
            if entry["success"]:
                stats["successes"] += 1
        
        return pattern_stats

# Initialize learning system
learning_system = LearningSystem()

# Manual RIPEMD160 implementation
def ripemd160(data):
    """
    Pure Python implementation of RIPEMD160 hash function
    """
    try:
        digest = hashlib.new('ripemd160', data).digest()
        return digest
    except:
        # Use SHA256 as fallback if RIPEMD160 is not available
        return hashlib.sha256(data).digest()[:20]

def private_key_to_address(private_key):
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
        
        # Use our manual RIPEMD160 implementation
        ripemd_digest = ripemd160(sha_digest)
        
        # Add version byte and checksum
        versioned_payload = b'\x00' + ripemd_digest
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        
        # Encode result in Base58
        address = base58.b58encode(versioned_payload + checksum).decode()
        return address
    except Exception as e:
        logger.error(f"Error in private_key_to_address: {e}")
        logger.error(traceback.format_exc())
        return None

def address_similarity(addr1, addr2):
    """
    Calculate similarity between two Bitcoin addresses
    """
    if not addr1 or not addr2:
        return 0
    
    # Direct match score (exact characters matching)
    direct_match = sum(a == b for a, b in zip(addr1, addr2)) / max(len(addr1), len(addr2))
    
    # Position-weighted match (earlier positions are more important)
    weighted_match = sum((a == b) * (1.0 - i/100) for i, (a, b) in enumerate(zip(addr1, addr2))) / min(len(addr1), len(addr2))
    
    # Combined score (weighted)
    return 0.5 * direct_match + 0.5 * weighted_match

def is_valid_candidate(value):
    """
    Check if a candidate is valid (positive and fits in 68 bits)
    """
    if value is None or value <= 0:
        return False
    if value > (1 << 68) - 1:  # Larger than 68 bits
        return False
    return True

def test_candidate(candidate):
    """
    Test a candidate private key
    """
    global recent_candidates, unique_candidates_count, total_candidates_count
    
    if not is_valid_candidate(candidate):
        return False, None, 0
    
    # Track candidate testing stats
    total_candidates_count += 1
    
    # Check if candidate was recently tested (avoid duplication)
    if candidate in recent_candidates:
        return False, None, 0
    
    # Mark as tested and increment unique count
    recent_candidates.append(candidate)
    unique_candidates_count += 1
        
    # Generate address
    address = private_key_to_address(candidate)
    
    # Calculate similarity
    similarity = address_similarity(address, TARGET_ADDRESS)
    
    # Check for exact match
    if address == TARGET_ADDRESS:
        return True, address, 1.0
    
    return False, address, similarity

def save_result(value):
    """
    Save the successful result
    """
    try:
        address = private_key_to_address(value)
        result = {
            "private_key_int": value,
            "private_key_hex": hex(value),
            "bitcoin_address": address,
            "timestamp": time.time(),
            "human_time": datetime.now().isoformat(),
            "status": "Match found"
        }
        
        with open(RESULT_FILE, 'w') as f:
            json.dump(result, f, indent=2)
        
        with open("term68_solution.txt", 'w') as f:
            f.write(f"Term 68 Solution Found!\n")
            f.write(f"Private Key: {hex(value)}\n")
            f.write(f"Bitcoin Address: {address}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        
        logger.info(f"MATCH FOUND! Result saved to {RESULT_FILE} and term68_solution.txt")
        return result
    except Exception as e:
        logger.error(f"Error saving result: {e}")
        logger.error(traceback.format_exc())
        return None

def save_closest_addresses(candidates):
    """
    Save the closest addresses found so far
    """
    try:
        with open(CLOSEST_ADDRESSES, 'w') as f:
            json.dump(candidates, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving closest addresses: {e}")
        return False

def load_closest_addresses():
    """
    Load the closest addresses from file
    """
    if os.path.exists(CLOSEST_ADDRESSES):
        try:
            with open(CLOSEST_ADDRESSES, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading closest addresses: {e}")
            return []
    return []

def save_progress(iteration, best_candidate, best_similarity, params):
    """
    Save search progress to a file
    """
    progress = {
        "iteration": iteration,
        "best_candidate": best_candidate,
        "best_candidate_hex": hex(best_candidate) if best_candidate else None,
        "best_similarity": best_similarity,
        "timestamp": time.time(),
        "human_time": datetime.now().isoformat(),
        "parameters": params,
        "unique_candidates": unique_candidates_count,
        "total_candidates": total_candidates_count,
        "unique_ratio": unique_candidates_count / max(1, total_candidates_count)
    }
    
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2)
        logger.info(f"Progress saved at iteration {iteration}")
        logger.info(f"Stats: {unique_candidates_count} unique candidates out of {total_candidates_count} total")
        logger.info(f"Uniqueness ratio: {unique_candidates_count / max(1, total_candidates_count):.4f}")
        return True
    except Exception as e:
        logger.error(f"Error saving progress: {e}")
        return False

def load_progress():
    """
    Load search progress from file
    """
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading progress: {e}")
            return None
    return None

def adjust_parameters(base_params, iteration, best_similarity):
    """
    Enhanced parameter adjustment based on sequence patterns and known solutions
    """
    # Copy base parameters
    params = base_params.copy()
    
    # Adjust based on iteration count and sequence patterns
    if iteration > 50:
        # After many iterations, increase probability of flips
        params["FLIP_PROBABILITY"] = min(0.2, base_params["FLIP_PROBABILITY"] * (1 + (iteration / 500)))
        
        # Adjust hammer iterations based on sequence patterns
        pattern_index = iteration % len(SEQUENCE_PATTERNS)
        params["HAMMER_ITERATIONS"] = base_params["HAMMER_ITERATIONS"] + random.randint(-100, 100)
        
    # Adjust based on best similarity and sequence patterns
    if best_similarity > 0.3:
        # If we're getting close, focus more on adjacent bits
        params["ADJACENT_INFLUENCE"] = max(1, base_params["ADJACENT_INFLUENCE"] - 1)
        params["ACTIVATION_THRESHOLD"] = max(50, base_params["ACTIVATION_THRESHOLD"] - 10)
        
        # Increase hammer iterations for promising candidates
        params["HAMMER_ITERATIONS"] = min(2000, params["HAMMER_ITERATIONS"] + 100)
    elif best_similarity < 0.1:
        # If we're far off, explore more widely
        params["ADJACENT_INFLUENCE"] = min(6, base_params["ADJACENT_INFLUENCE"] + 1)
        params["MAX_FLIPS_PER_HAMMER"] = min(8, base_params["MAX_FLIPS_PER_HAMMER"] + 1)
        
        # Try different sequence patterns
        params["FLIP_PROBABILITY"] = min(0.3, params["FLIP_PROBABILITY"] * 1.5)
    
    # Check uniqueness ratio and adjust strategy if needed
    uniqueness_ratio = unique_candidates_count / max(1, total_candidates_count)
    if uniqueness_ratio < 0.3:  # If we're generating too many duplicates
        # Increase randomness to escape local patterns
        params["FLIP_PROBABILITY"] = min(0.3, params["FLIP_PROBABILITY"] * 1.5)
        params["HAMMER_ITERATIONS"] = params["HAMMER_ITERATIONS"] + random.randint(100, 300)
        logger.info(f"Low uniqueness ratio ({uniqueness_ratio:.4f}), increasing randomness")
    
    # Periodically change strategy completely to avoid local maxima
    if iteration % 25 == 0:
        # Try different sequence patterns
        pattern_name = random.choice(list(SEQUENCE_PATTERNS.keys()))
        logger.info(f"Switching to {pattern_name} pattern for next iteration")
        
        params["HAMMER_ITERATIONS"] = base_params["HAMMER_ITERATIONS"] + random.randint(-200, 200)
        params["FLIP_PROBABILITY"] = max(0.01, min(0.3, base_params["FLIP_PROBABILITY"] + random.uniform(-0.02, 0.02)))
        
        # Every 100 iterations, perform a more radical strategy change
        if iteration % 100 == 0:
            logger.info("Performing radical strategy change to escape local patterns")
            params["ADJACENT_INFLUENCE"] = random.randint(1, 8)  # More radical range
            params["ACTIVATION_THRESHOLD"] = random.randint(50, 150)
            params["MAX_FLIPS_PER_HAMMER"] = random.randint(1, 10)
    
    return params

def simulate_rowhammer(base_value, aggressor_bits, num_iterations=HAMMER_ITERATIONS):
    """
    Simulate RowHammer effects on a value based on Hammulator paper
    """
    candidates = []
    hammer_counts = np.zeros(68)  # 68 bits in our value
    
    # Convert to bit array for easier manipulation
    bits = [int(b) for b in bin(base_value)[2:].zfill(68)]
    
    # Simulate hammering
    for _ in range(num_iterations):
        # Increment hammer count for aggressor bits
        for bit in aggressor_bits:
            hammer_counts[bit] += 1
        
        # Check if any bits have reached the activation threshold
        for bit in range(68):
            # Only affect bits adjacent to the aggressors (based on Hammulator paper)
            if any(abs(bit - aggressor) <= ADJACENT_INFLUENCE for aggressor in aggressor_bits):
                if hammer_counts[bit] >= ACTIVATION_THRESHOLD:
                    # Probability-based bit flip
                    if random.random() < FLIP_PROBABILITY:
                        # Flip the bit
                        bits[bit] = 1 - bits[bit]
                        
                        # Convert flipped bit array back to integer
                        candidate = int(''.join(map(str, bits)), 2)
                        
                        if is_valid_candidate(candidate) and candidate not in candidates:
                            candidates.append(candidate)
                            
                        # Reset hammer count after successful flip
                        hammer_counts[bit] = 0
    
    return candidates

def systematic_rowhammer_search(base_candidates, max_candidates=1000):
    """
    Perform a systematic RowHammer-inspired search
    """
    logger.info(f"Starting RowHammer-inspired search with {len(base_candidates)} base candidates")
    
    tested = 0
    best_similarity = 0
    best_candidates = []
    
    # For each base candidate, try hammering different bit regions
    for base_value in base_candidates:
        if tested >= max_candidates:
            break
            
        logger.info(f"Simulating RowHammer on base value: {hex(base_value)}")
        
        # Try different aggressor bit patterns (based on Hammulator paper)
        for num_aggressors in range(1, 5):  # 1 to 4 aggressor bits
            if tested >= max_candidates:
                break
                
            # Select aggressor bits with more randomization
            # For low uniqueness ratio, use completely random bit positions
            if unique_candidates_count / max(1, total_candidates_count) < 0.5:
                for _ in range(min(5, max_candidates - tested)):  # Try more random patterns
                    aggressor_bits = sorted(random.sample(range(68), num_aggressors))
                    
                    # Simulate RowHammer with these aggressor bits
                    candidates = simulate_rowhammer(base_value, aggressor_bits)
                    
                    # Add some completely random candidates to escape patterns
                    for _ in range(3):
                        random_candidate = base_value ^ random.randint(1, 1 << 67)
                        if is_valid_candidate(random_candidate):
                            candidates.append(random_candidate)
                    
                    # Test candidates
                    for candidate in candidates:
                        if tested >= max_candidates:
                            break
                            
                        match, address, similarity = test_candidate(candidate)
                        tested += 1
                        
                        # Track best candidates
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_candidates = [{"value": candidate, "address": address, "similarity": similarity}]
                            logger.info(f"New best similarity: {similarity:.6f} for {hex(candidate)} -> {address}")
                        elif similarity == best_similarity:
                            best_candidates.append({"value": candidate, "address": address, "similarity": similarity})
                        
                        # If we found a match, we're done
                        if match:
                            logger.info(f"EXACT MATCH FOUND! Candidate: {hex(candidate)} -> {address}")
                            return candidate
            else:
                # Original systematic selection of aggressor bits
                for aggressor_bits in itertools.combinations(range(68), num_aggressors):
                    if tested >= max_candidates:
                        break
                    
                    # Simulate RowHammer with these aggressor bits
                    candidates = simulate_rowhammer(base_value, aggressor_bits)
                    
                    # Test all candidates generated
                    for candidate in candidates:
                        if tested >= max_candidates:
                            break
                            
                        match, address, similarity = test_candidate(candidate)
                        tested += 1
                        
                        # Track best candidates
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_candidates = [{"value": candidate, "address": address, "similarity": similarity}]
                            logger.info(f"New best similarity: {similarity:.6f} for {hex(candidate)} -> {address}")
                        elif similarity == best_similarity:
                            best_candidates.append({"value": candidate, "address": address, "similarity": similarity})
                        
                        # If we found a match, we're done
                        if match:
                            logger.info(f"EXACT MATCH FOUND! Candidate: {hex(candidate)} -> {address}")
                            return candidate
    
    # Save the best candidates we found
    save_closest_addresses(best_candidates)
    logger.info(f"Completed testing {tested} RowHammer-generated candidates")
    logger.info(f"Best similarity: {best_similarity:.6f}")
    
    if best_candidates and best_similarity > 0.3:  # Only return a candidate if it has decent similarity
        return best_candidates[0]["value"]
    return None

def apply_double_sided_hammering(center, num_patterns=10, max_candidates=500):
    """
    Apply a double-sided hammering approach as described in Hammulator
    """
    logger.info(f"Starting double-sided RowHammer on {hex(center)}")
    
    tested = 0
    best_similarity = 0
    best_candidate = None
    
    # We'll try various patterns of double-sided hammering
    for pattern_idx in range(num_patterns):
        if tested >= max_candidates:
            break
            
        # In double-sided hammering, we select two groups of aggressor bits
        # that sandwich our target bits
        
        # Randomly select bit sections (8-bit chunks) to hammer
        chunk_size = 8
        num_chunks = 68 // chunk_size
        
        # Select two chunks to act as aggressors
        aggressor1 = random.randint(0, num_chunks-1) * chunk_size
        aggressor2 = random.randint(0, num_chunks-1) * chunk_size
        while abs(aggressor1 - aggressor2) <= chunk_size:  # Ensure they're not adjacent
            aggressor2 = random.randint(0, num_chunks-1) * chunk_size
            
        # Create aggressor bit lists
        aggressor1_bits = list(range(aggressor1, aggressor1 + chunk_size))
        aggressor2_bits = list(range(aggressor2, aggressor2 + chunk_size))
        
        # The victim bits are between the two aggressors
        start_victim = min(aggressor1, aggressor2) + chunk_size
        end_victim = max(aggressor1, aggressor2)
        victim_bits = list(range(start_victim, end_victim))
        
        logger.info(f"Double-sided hammer pattern {pattern_idx+1}: " +
                  f"Aggressors at bits {aggressor1}-{aggressor1+chunk_size-1} and " +
                  f"{aggressor2}-{aggressor2+chunk_size-1}, victim bits {start_victim}-{end_victim-1}")
        
        # We'll hammer both aggressors multiple times
        candidates = set()
        for _ in range(HAMMER_ITERATIONS):
            if tested >= max_candidates:
                break
                
            # Create a modified version of center
            bits = [int(b) for b in bin(center)[2:].zfill(68)]
            
            # Each hammer iteration has a chance to flip bits in the victim region
            for bit in victim_bits:
                if random.random() < FLIP_PROBABILITY * 2:  # Double-sided gives higher probability
                    bits[bit] = 1 - bits[bit]
            
            # Convert back to integer
            candidate = int(''.join(map(str, bits)), 2)
            
            if is_valid_candidate(candidate) and candidate not in candidates:
                candidates.add(candidate)
                
                # Test the candidate
                match, address, similarity = test_candidate(candidate)
                tested += 1
                
                # Track best candidate
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_candidate = candidate
                    logger.info(f"New best similarity: {similarity:.6f} for {hex(candidate)} -> {address}")
                
                # If we found a match, we're done
                if match:
                    logger.info(f"EXACT MATCH FOUND! Candidate: {hex(candidate)} -> {address}")
                    return candidate
    
    logger.info(f"Completed double-sided hammering test with {tested} candidates")
    logger.info(f"Best similarity: {best_similarity:.6f}")
    
    if best_candidate and best_similarity > 0.3:  # Only return if decent similarity
        return best_candidate
    return None

def half_double_attack(center, max_candidates=500):
    """
    Implement a half-double RowHammer attack pattern from Hammulator paper
    """
    logger.info(f"Starting half-double RowHammer on {hex(center)}")
    
    tested = 0
    best_similarity = 0
    best_candidate = None
    
    # In half-double, we want to affect bits at distance 2
    bits = [int(b) for b in bin(center)[2:].zfill(68)]
    
    # We'll iterate through sections of bits
    for start_bit in range(0, 68, 4):
        if tested >= max_candidates:
            break
            
        # For each section, we'll hammer the first bit and check effects
        # at distance 2 (half-double effect)
        aggressor_bit = start_bit
        target_bits = [i for i in range(max(0, start_bit-4), min(68, start_bit+8)) 
                       if abs(i - aggressor_bit) == 2]
        
        logger.info(f"Half-double pattern: Aggressor bit {aggressor_bit}, target bits {target_bits}")
        
        candidates = set()
        for _ in range(HAMMER_ITERATIONS):
            if tested >= max_candidates:
                break
                
            # Create a modified version of center
            new_bits = bits.copy()
            
            # Each hammer iteration has a chance to flip bits at distance 2
            for bit in target_bits:
                if random.random() < FLIP_PROBABILITY:
                    new_bits[bit] = 1 - new_bits[bit]
            
            # Convert back to integer
            candidate = int(''.join(map(str, new_bits)), 2)
            
            if is_valid_candidate(candidate) and candidate not in candidates:
                candidates.add(candidate)
                
                # Test the candidate
                match, address, similarity = test_candidate(candidate)
                tested += 1
                
                # Track best candidate
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_candidate = candidate
                    logger.info(f"New best similarity: {similarity:.6f} for {hex(candidate)} -> {address}")
                
                # If we found a match, we're done
                if match:
                    logger.info(f"EXACT MATCH FOUND! Candidate: {hex(candidate)} -> {address}")
                    return candidate
    
    logger.info(f"Completed half-double attack test with {tested} candidates")
    logger.info(f"Best similarity: {best_similarity:.6f}")
    
    if best_candidate and best_similarity > 0.3:  # Only return if decent similarity
        return best_candidate
    return None

def sequence_based_hammering(center, pattern_name="consecutive", max_candidates=500):
    """
    Implement sequence-based hammering patterns inspired by known solutions
    """
    logger.info(f"Starting sequence-based hammering with {pattern_name} pattern on {hex(center)}")
    
    tested = 0
    best_similarity = 0
    best_candidate = None
    
    if pattern_name not in SEQUENCE_PATTERNS:
        logger.error(f"Unknown pattern: {pattern_name}")
        return None
        
    pattern = SEQUENCE_PATTERNS[pattern_name]
    bits = [int(b) for b in bin(center)[2:].zfill(68)]
    
    # Apply pattern-based hammering
    for i in range(len(pattern)):
        if tested >= max_candidates:
            break
            
        # Calculate bit positions based on pattern
        base_pos = pattern[i] % 68  # Ensure we stay within 68 bits
        target_bits = []
        
        # Generate target bits based on pattern type
        if pattern_name == "consecutive":
            target_bits = [base_pos + j for j in range(4) if base_pos + j < 68]
        elif pattern_name == "fibonacci":
            target_bits = [base_pos, (base_pos + pattern[i-1]) % 68 if i > 0 else base_pos]
        elif pattern_name == "prime":
            target_bits = [base_pos, (base_pos + pattern[i]) % 68]
        elif pattern_name == "hamming":
            target_bits = [base_pos, (base_pos + 1) % 68, (base_pos + 2) % 68]
        
        logger.info(f"Pattern {pattern_name} iteration {i}: Target bits {target_bits}")
        
        candidates = set()
        for _ in range(HAMMER_ITERATIONS):
            if tested >= max_candidates:
                break
                
            # Create a modified version of center
            new_bits = bits.copy()
            
            # Apply pattern-specific bit flips
            for bit in target_bits:
                if random.random() < FLIP_PROBABILITY:
                    new_bits[bit] = 1 - new_bits[bit]
            
            # Convert back to integer
            candidate = int(''.join(map(str, new_bits)), 2)
            
            if is_valid_candidate(candidate) and candidate not in candidates:
                candidates.add(candidate)
                
                # Test the candidate
                match, address, similarity = test_candidate(candidate)
                tested += 1
                
                # Track best candidate
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_candidate = candidate
                    logger.info(f"New best similarity: {similarity:.6f} for {hex(candidate)} -> {address}")
                
                # If we found a match, we're done
                if match:
                    logger.info(f"EXACT MATCH FOUND! Candidate: {hex(candidate)} -> {address}")
                    return candidate
    
    logger.info(f"Completed {pattern_name} pattern test with {tested} candidates")
    logger.info(f"Best similarity: {best_similarity:.6f}")
    
    if best_candidate and best_similarity > 0.3:  # Only return if decent similarity
        return best_candidate
    return None

def pattern_based_hammering(center, pattern_name="consecutive_zeros", max_candidates=500):
    """
    Implement pattern-based hammering based on analyzed bit patterns
    """
    logger.info(f"Starting pattern-based hammering with {pattern_name} pattern on {hex(center)}")
    
    tested = 0
    best_similarity = 0
    best_candidate = None
    
    if pattern_name not in BIT_PATTERNS:
        logger.error(f"Unknown pattern: {pattern_name}")
        return None
        
    pattern = BIT_PATTERNS[pattern_name]
    bits = [int(b) for b in bin(center)[2:].zfill(68)]
    
    # Apply pattern-based hammering
    for i in range(len(pattern)):
        if tested >= max_candidates:
            break
            
        # Calculate bit positions based on pattern
        run_length = pattern[i]
        start_pos = i * 4  # Start position for each run
        
        # Generate target bits based on pattern type
        if pattern_name == "consecutive_zeros":
            # Target bits after runs of zeros
            target_bits = [start_pos + run_length + j for j in range(2) if start_pos + run_length + j < 68]
        elif pattern_name == "consecutive_ones":
            # Target bits before and after runs of ones
            target_bits = []
            if start_pos > 0:
                target_bits.append(start_pos - 1)
            if start_pos + run_length < 68:
                target_bits.append(start_pos + run_length)
        else:  # xor_masks
            # Apply XOR mask at specific positions
            mask = BIT_PATTERNS["xor_masks"][pattern_name]
            target_bits = [i for i in range(68) if (mask & (1 << i)) != 0]
        
        logger.info(f"Pattern {pattern_name} iteration {i}: Target bits {target_bits}")
        
        candidates = set()
        for _ in range(HAMMER_ITERATIONS):
            if tested >= max_candidates:
                break
                
            # Create a modified version of center
            new_bits = bits.copy()
            
            # Apply pattern-specific bit flips
            for bit in target_bits:
                if random.random() < FLIP_PROBABILITY:
                    new_bits[bit] = 1 - new_bits[bit]
            
            # Convert back to integer
            candidate = int(''.join(map(str, new_bits)), 2)
            
            if is_valid_candidate(candidate) and candidate not in candidates:
                candidates.add(candidate)
                
                # Test the candidate
                match, address, similarity = test_candidate(candidate)
                tested += 1
                
                # Track best candidate
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_candidate = candidate
                    logger.info(f"New best similarity: {similarity:.6f} for {hex(candidate)} -> {address}")
                
                # If we found a match, we're done
                if match:
                    logger.info(f"EXACT MATCH FOUND! Candidate: {hex(candidate)} -> {address}")
                    return candidate
    
    logger.info(f"Completed {pattern_name} pattern test with {tested} candidates")
    logger.info(f"Best similarity: {best_similarity:.6f}")
    
    if best_candidate and best_similarity > 0.3:  # Only return if decent similarity
        return best_candidate
    return None

def main():
    """
    Main function to run the RowHammer search continuously
    """
    global HAMMER_ITERATIONS, ADJACENT_INFLUENCE, ACTIVATION_THRESHOLD, MAX_FLIPS_PER_HAMMER, FLIP_PROBABILITY
    global recent_candidates, unique_candidates_count, total_candidates_count
    
    start_time = time.time()
    
    # Initialize parameters
    base_params = {
        "HAMMER_ITERATIONS": HAMMER_ITERATIONS,
        "ADJACENT_INFLUENCE": ADJACENT_INFLUENCE,
        "ACTIVATION_THRESHOLD": ACTIVATION_THRESHOLD,
        "MAX_FLIPS_PER_HAMMER": MAX_FLIPS_PER_HAMMER,
        "FLIP_PROBABILITY": FLIP_PROBABILITY
    }
    
    # Load previous progress if available
    progress = load_progress()
    iteration = 1
    best_overall_candidate = None
    best_overall_similarity = 0
    
    if progress:
        iteration = progress.get("iteration", 1) + 1
        best_overall_candidate = progress.get("best_candidate")
        best_overall_similarity = progress.get("best_similarity", 0)
        # Restore candidate tracking stats if available
        unique_candidates_count = progress.get("unique_candidates", 0)
        total_candidates_count = progress.get("total_candidates", 0)
        logger.info(f"Resuming search from iteration {iteration}")
        logger.info(f"Previous best similarity: {best_overall_similarity:.6f}")
        if best_overall_candidate:
            logger.info(f"Previous best candidate: {hex(best_overall_candidate)}")
        logger.info(f"Uniqueness stats: {unique_candidates_count} unique out of {total_candidates_count} total candidates")
    
    try:
        logger.info("Starting continuous search - will run until interrupted")
        
        while True:  # Run indefinitely until interrupted
            logger.info(f"=== Starting iteration {iteration} ===")
            
            # Adjust parameters periodically
            if iteration % ADAPTATION_INTERVAL == 0:
                current_params = adjust_parameters(base_params, iteration, best_overall_similarity)
                logger.info(f"Adjusted parameters: {current_params}")
                
                # Update global parameters
                HAMMER_ITERATIONS = current_params["HAMMER_ITERATIONS"]
                ADJACENT_INFLUENCE = current_params["ADJACENT_INFLUENCE"]
                ACTIVATION_THRESHOLD = current_params["ACTIVATION_THRESHOLD"]
                MAX_FLIPS_PER_HAMMER = current_params["MAX_FLIPS_PER_HAMMER"]
                FLIP_PROBABILITY = current_params["FLIP_PROBABILITY"]
            
            # Run one iteration of search
            result = combined_rowhammer_search(best_overall_candidate)
            
            if result:
                # Verify the result
                match, address, similarity = test_candidate(result)
                
                # Update best candidate if better
                if similarity > best_overall_similarity:
                    best_overall_similarity = similarity
                    best_overall_candidate = result
                    logger.info(f"New best overall: {similarity:.6f} for {hex(result)} -> {address}")
                    
                    # Save best candidate
                    with open("term68_best_candidate.json", 'w') as f:
                        json.dump({
                            "private_key_int": result,
                            "private_key_hex": hex(result),
                            "bitcoin_address": address,
                            "similarity": similarity,
                            "timestamp": time.time(),
                            "human_time": datetime.now().isoformat(),
                            "iteration": iteration,
                            "status": "Best candidate (continuous search)"
                        }, f, indent=2)
                
                # If exact match, save and exit
                if match:
                    logger.info(f"EXACT MATCH FOUND! Candidate: {hex(result)} -> {address}")
                    save_result(result)
                    break
            
            # Save progress periodically
            if iteration % SAVE_INTERVAL == 0:
                save_progress(iteration, best_overall_candidate, best_overall_similarity, {
                    "HAMMER_ITERATIONS": HAMMER_ITERATIONS,
                    "ADJACENT_INFLUENCE": ADJACENT_INFLUENCE,
                    "ACTIVATION_THRESHOLD": ACTIVATION_THRESHOLD,
                    "MAX_FLIPS_PER_HAMMER": MAX_FLIPS_PER_HAMMER,
                    "FLIP_PROBABILITY": FLIP_PROBABILITY
                })
            
            iteration += 1
            
    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
        # Save progress on interrupt
        save_progress(iteration, best_overall_candidate, best_overall_similarity, {
            "HAMMER_ITERATIONS": HAMMER_ITERATIONS,
            "ADJACENT_INFLUENCE": ADJACENT_INFLUENCE,
            "ACTIVATION_THRESHOLD": ACTIVATION_THRESHOLD,
            "MAX_FLIPS_PER_HAMMER": MAX_FLIPS_PER_HAMMER,
            "FLIP_PROBABILITY": FLIP_PROBABILITY
        })
    except Exception as e:
        logger.error(f"Error during search: {e}")
        logger.error(traceback.format_exc())
    
    duration = time.time() - start_time
    logger.info(f"Total search time: {duration:.2f} seconds")
    logger.info(f"Completed {iteration-1} iterations")
    logger.info(f"Uniqueness stats: {unique_candidates_count} unique out of {total_candidates_count} total candidates ({unique_candidates_count/max(1,total_candidates_count):.4f})")
    if best_overall_candidate:
        logger.info(f"Best overall similarity: {best_overall_similarity:.6f} with candidate {hex(best_overall_candidate)}")

def combined_rowhammer_search(best_overall_candidate=None):
    """
    Enhanced combined RowHammer search with self-learning capabilities
    """
    logger.info(f"Target Address: {TARGET_ADDRESS}")
    logger.info(f"Previous Term (67): {PREV_TERM_67}")
    
    # Load previous best candidates if available
    best_candidates_list = load_closest_addresses()
    base_candidates = [entry["value"] for entry in best_candidates_list] if best_candidates_list else []
    
    # Get pattern effectiveness analysis
    pattern_stats = learning_system.analyze_pattern_effectiveness()
    best_patterns = learning_system.get_best_patterns()
    
    # Adjust search strategy based on learning
    if best_patterns:
        logger.info("Using learned patterns for search")
        for pattern_info in best_patterns:
            pattern = pattern_info["pattern"]
            similarity = pattern_info["similarity"]
            logger.info(f"Applying learned pattern with similarity {similarity:.6f}")
            
            for base in base_candidates[:2]:
                # Predict success probability
                prob = learning_system.predict_success_probability(base, pattern, similarity)
                if prob > 0.3:  # Only try if probability is decent
                    result = pattern_based_hammering(base, pattern, max_candidates=200)
                    if result:
                        match, address, similarity = test_candidate(result)
                        learning_system.update(result, pattern, similarity, match)
                        if match:
                            logger.info(f"EXACT MATCH confirmed with learned pattern: {hex(result)} -> {address}")
                            return result
    
    # Original strategies with learning integration
    strategies = [
        ("systematic", systematic_rowhammer_search),
        ("double_sided", apply_double_sided_hammering),
        ("half_double", half_double_attack)
    ]
    
    for strategy_name, strategy_func in strategies:
        # Check pattern effectiveness for this strategy
        strategy_patterns = [p for p in pattern_stats if p.startswith(strategy_name)]
        if strategy_patterns:
            avg_success = sum(pattern_stats[p]["successes"] / max(1, pattern_stats[p]["count"]) 
                            for p in strategy_patterns) / len(strategy_patterns)
            if avg_success < 0.1:  # Skip if strategy has been ineffective
                logger.info(f"Skipping {strategy_name} due to low effectiveness")
                continue
        
        for base in base_candidates[:2]:
            result = strategy_func(base, max_candidates=200)
            if result:
                match, address, similarity = test_candidate(result)
                learning_system.update(result, strategy_name, similarity, match)
                if match:
                    logger.info(f"EXACT MATCH confirmed with {strategy_name}: {hex(result)} -> {address}")
                    return result
    
    # Pattern-based hammering with learning
    for pattern_name in BIT_PATTERNS.keys():
        # Check pattern effectiveness
        if pattern_name in pattern_stats:
            stats = pattern_stats[pattern_name]
            success_rate = stats["successes"] / max(1, stats["count"])
            if success_rate < 0.05:  # Skip if pattern has been ineffective
                logger.info(f"Skipping {pattern_name} due to low effectiveness")
                continue
        
        for base in base_candidates[:2]:
            result = pattern_based_hammering(base, pattern_name, max_candidates=200)
            if result:
                match, address, similarity = test_candidate(result)
                learning_system.update(result, pattern_name, similarity, match)
                if match:
                    logger.info(f"EXACT MATCH confirmed with {pattern_name}: {hex(result)} -> {address}")
                    return result
    
    # XOR mask-based hammering with learning
    for mask_name, mask_value in BIT_PATTERNS["xor_masks"].items():
        # Check mask effectiveness
        mask_pattern = f"xor_{mask_name}"
        if mask_pattern in pattern_stats:
            stats = pattern_stats[mask_pattern]
            success_rate = stats["successes"] / max(1, stats["count"])
            if success_rate < 0.05:  # Skip if mask has been ineffective
                logger.info(f"Skipping {mask_name} mask due to low effectiveness")
                continue
        
        for base in base_candidates[:2]:
            for shift in range(0, 68, 4):
                shifted_mask = (mask_value << shift) & ((1 << 68) - 1)
                candidate = base ^ shifted_mask
                if is_valid_candidate(candidate):
                    match, address, similarity = test_candidate(candidate)
                    learning_system.update(candidate, mask_pattern, similarity, match)
                    if match:
                        logger.info(f"EXACT MATCH confirmed with {mask_name} mask: {hex(candidate)} -> {address}")
                        return candidate
    
    logger.info("All search strategies completed without finding an exact match")
    
    # Return best candidate found among all strategies
    if best_candidates_list:
        best_value = sorted(best_candidates_list, key=lambda x: x.get("similarity", 0), reverse=True)[0]["value"]
        best_similarity = sorted(best_candidates_list, key=lambda x: x.get("similarity", 0), reverse=True)[0]["similarity"]
        logger.info(f"Returning best candidate with similarity {best_similarity:.6f}: {hex(best_value)}")
        return best_value
    return None

if __name__ == "__main__":
    main() 