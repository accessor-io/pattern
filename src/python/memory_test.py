#!/usr/bin/env python3
"""
Simple test script to verify MemoryManager functionality in 68_continuous_adaptive_search.py
"""

import json
import os
import time
import logging

# Constants - same as in 68_continuous_adaptive_search.py
CLOSEST_ADDRESSES_FILE = "closest_addresses_memory.json"
MEMORY_SIZE = 1000
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

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
            try:
                self.memory_index.add(int(entry["private_key_int"]))
            except (ValueError, KeyError):
                pass
        
        logger.info(f"Memory manager initialized with {len(self.memory)} entries")
    
    def load_memory(self):
        """Load memory from file if exists"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.memory = json.load(f)
                    logger.info(f"Loaded {len(self.memory)} previous results from memory")
                    
                    # Clean memory - sometimes there can be corrupt entries
                    valid_entries = []
                    for entry in self.memory:
                        if "private_key_int" in entry and "similarity" in entry and "address" in entry:
                            # Make sure similarity is a float
                            try:
                                entry["similarity"] = float(entry["similarity"])
                                valid_entries.append(entry)
                            except:
                                continue
                    
                    # Replace memory with valid entries
                    self.memory = valid_entries
                    logger.info(f"Validated {len(valid_entries)} entries in memory")
                    
                    # Sort memory by similarity (highest first)
                    self.memory.sort(key=lambda x: x["similarity"], reverse=True)
                    
                    # Set absolute best from memory if available
                    if self.memory:
                        self.absolute_best = self.memory[0]
                        logger.info(f"Loaded absolute best similarity: {self.absolute_best['similarity']:.6f}")
                        if 'private_key_int' in self.absolute_best:
                            logger.info(f"Absolute best candidate: {hex(int(self.absolute_best['private_key_int']))}")
                        if 'address' in self.absolute_best:
                            logger.info(f"Absolute best address: {self.absolute_best['address']}")
            except Exception as e:
                logger.error(f"Error loading memory: {e}")
                logger.error(f"Creating new memory file")
                self.memory = []
        else:
            logger.info(f"No memory file found at {self.filename}, starting fresh")
            self.memory = []
    
    def save_memory(self):
        """Save memory to file with error handling and atomic write"""
        # Create temp file
        tmp_filename = f"{self.filename}.tmp"
        try:
            with open(tmp_filename, 'w') as f:
                json.dump(self.memory, f, indent=2)
            
            # Rename to actual file (atomic operation)
            os.replace(tmp_filename, self.filename)
            logger.info(f"Saved {len(self.memory)} results to memory file")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            # Try to remove temp file if it exists
            try:
                if os.path.exists(tmp_filename):
                    os.remove(tmp_filename)
            except:
                pass
    
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
        
        # Save memory right away for this test
        self.save_memory()
    
    def get_best_candidates(self, n=10):
        """
        Get the n best candidates from memory
        
        Args:
            n: Number of candidates to return
            
        Returns:
            list: List of best candidate entries from memory (sorted by similarity)
        """
        # Refresh sort to ensure we have the best candidates first
        self.memory.sort(key=lambda x: float(x["similarity"]), reverse=True)
        
        # Return the top n candidates or all if we have fewer
        return self.memory[:min(n, len(self.memory))]
    
    def get_promising_values(self, n=5):
        """
        Get the n most promising values (private keys) from memory
        
        Args:
            n: Number of values to return
            
        Returns:
            list: List of promising private key integers
        """
        best_candidates = self.get_best_candidates(n)
        values = []
        
        for candidate in best_candidates:
            try:
                value = int(candidate["private_key_int"])
                values.append(value)
            except (ValueError, KeyError):
                # Skip invalid entries
                continue
                
        return values
    
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


def run_memory_test():
    """Run a test of the MemoryManager functionality"""
    # Create memory manager
    logger.info("Creating memory manager")
    memory_manager = MemoryManager()
    
    # Check current memory state
    logger.info("Current memory state:")
    best_similarity = memory_manager.get_absolute_best_similarity()
    logger.info(f"Best similarity: {best_similarity:.6f}")
    
    # Get best candidates
    best_candidates = memory_manager.get_best_candidates(5)
    logger.info(f"Best candidates: {len(best_candidates)}")
    for i, candidate in enumerate(best_candidates):
        logger.info(f"Candidate {i+1}: {candidate.get('address', 'N/A')} (similarity: {candidate.get('similarity', 0):.6f})")
    
    # Add some test data
    logger.info("Adding test data")
    test_data = [
        (12345, "1testAddress1", 0.1),
        (67890, "1testAddress2", 0.2),
        (54321, "1testAddress3", 0.3),
        (98765, "1testAddress4", 0.4),
        (13579, "1testAddress5", 0.5),
    ]
    
    for candidate, address, similarity in test_data:
        logger.info(f"Adding: {candidate} -> {address} (similarity: {similarity:.6f})")
        memory_manager.add_result(candidate, address, similarity)
    
    # Check memory again
    logger.info("Memory after adding test data:")
    best_similarity = memory_manager.get_absolute_best_similarity()
    logger.info(f"Best similarity: {best_similarity:.6f}")
    
    # Get best candidates again
    best_candidates = memory_manager.get_best_candidates(5)
    logger.info(f"Best candidates: {len(best_candidates)}")
    for i, candidate in enumerate(best_candidates):
        logger.info(f"Candidate {i+1}: {candidate.get('address', 'N/A')} (similarity: {candidate.get('similarity', 0):.6f})")
    
    # Get promising values
    promising_values = memory_manager.get_promising_values(3)
    logger.info(f"Promising values: {promising_values}")
    
    # Test updating an existing value
    logger.info("Testing update of existing value")
    memory_manager.add_result(67890, "1testAddress2Updated", 0.25)
    
    # Create a new memory manager to test loading
    logger.info("Creating new memory manager to test loading")
    new_memory_manager = MemoryManager()
    
    # Check memory loaded in new manager
    logger.info("Memory in new manager:")
    best_similarity = new_memory_manager.get_absolute_best_similarity()
    logger.info(f"Best similarity: {best_similarity:.6f}")
    
    best_candidates = new_memory_manager.get_best_candidates(5)
    logger.info(f"Best candidates: {len(best_candidates)}")
    for i, candidate in enumerate(best_candidates):
        logger.info(f"Candidate {i+1}: {candidate.get('address', 'N/A')} (similarity: {candidate.get('similarity', 0):.6f})")

if __name__ == "__main__":
    run_memory_test() 