#!/usr/bin/env python3
import sys
import time
import json
import random
from .helpers.address_utils import private_key_to_address, private_key_to_wif
from .helpers.pattern_analyzer import PatternDiscoverer
import logging
import datetime

# [Keep all the core BitcoinPuzzleSolver class logic here]
# [Same as your original code but with updated imports]
# [Make sure to remove any duplicate helper functions] 

class BitcoinPuzzleSolver:
    def __init__(self):
        self.known_addresses = self.load_known_addresses()
        self.pattern_finder = PatternDiscoverer()
        self.patterns = self.load_calibration_patterns()
        self.progress = {
            'current_index': 0,
            'total_indices': 0,
            'start_time': None,
            'found_solutions': []
        }
        self.load_progress()
        self.last_update = time.time()
        self.status_messages = []

    def run_puzzle_for_all_indices(self, txid_hex: str, start: int, end: int) -> None:
        txid_int = int(txid_hex, 16)
        self.progress.update({
            'current_index': start,
            'start_index': start,
            'total_indices': end - start + 1,
            'start_time': time.time(),
            'found_solutions': []
        })
        
        for i in range(start, end + 1):
            self.progress['current_index'] = i
            self.status_messages.append(f"Starting index {i}")
            
            # Add periodic status message
            if i % 10 == 0:
                logging.info(f"{datetime.datetime.now().isoformat()} - Processing index {i} - Elapsed: {self.format_time(time.time() - self.progress['start_time'])}")
            
            combined = (txid_int * i) % (2**256)
            candidate = pow(combined, 3, ORDER)
            
            target_addr = self.known_addresses[i-1] if i-1 < len(self.known_addresses) else None
            
            if target_addr:
                self.status_messages.append(f"Analyzing index {i} - {target_addr}")
                offset, constant = self.calibrate_parameters(candidate, i, target_addr)
                extracted = self.extract_bits(candidate, i, offset, constant)
                
                pk_hex = hex(extracted)[2:].zfill(64)
                addr_comp = self.private_key_to_address(pk_hex, compressed=True)
                addr_uncomp = self.private_key_to_address(pk_hex, compressed=False)
                
                if addr_comp == target_addr or addr_uncomp == target_addr:
                    self.status_messages.append(f"FOUND SOLUTION FOR INDEX {i}")
                    self.progress['found_solutions'].append({
                        'index': i,
                        'offset': offset,
                        'constant': constant,
                        'private_key': pk_hex
                    })
                self.print_progress_update()
                self.save_progress()
            
            self.print_progress_update()

    def print_progress_update(self):
        """Display real-time progress with time estimation"""
        now = time.time()
        elapsed = now - self.progress['start_time']
        processed = self.progress['current_index'] - self.progress['start_index'] + 1
        remaining = self.progress['total_indices'] - processed
        avg_time = elapsed / processed if processed > 0 else 0
        eta = remaining * avg_time
        
        # Update every 2 seconds or when important events happen
        if now - self.last_update > 2 or any("FOUND" in msg for msg in self.status_messages):
            sys.stdout.write("\033[2J\033[H")  # Clear screen
            print(f"=== Bitcoin Puzzle Solver ===")
            print(f"Current Index: {self.progress['current_index']}")
            print(f"Processed: {processed}/{self.progress['total_indices']} ({processed/self.progress['total_indices']:.1%})")
            print(f"Elapsed: {self.format_time(elapsed)}")
            print(f"ETA: {self.format_time(eta)}")
            print(f"Found Solutions: {len(self.progress['found_solutions'])}")
            print("\nRecent Activity:")
            for msg in self.status_messages[-5:]:  # Show last 5 messages
                print(f" - {msg}")
            
            self.last_update = now
            self.status_messages = []

    def calibrate_parameters(self, candidate_key: int, num_bits: int, target_address: str) -> (int, int):
        logging.debug(f"Calibrating for {num_bits} bits")
        # Add debug logging in critical functions

    def load_known_addresses(self):
        """Load addresses from addresses.txt"""
        try:
            with open('bitcoin-puzzle-solver/addresses.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("Error: addresses.txt not found")
            return []

    def load_calibration_patterns(self):
        """Load patterns from JSON"""
        try:
            with open('data/calibration_patterns.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def load_progress(self):
        # Implementation of load_progress method
        pass

    def save_progress(self):
        """Save progress to JSON"""
        try:
            with open('bitcoin-puzzle-solver/data/progress.json', 'w') as f:
                json.dump({
                    'last_index': self.progress['current_index'],
                    'found_solutions': self.progress['found_solutions'],
                    'start_time': self.progress['start_time']
                }, f)
        except IOError as e:
            print(f"Error saving progress: {str(e)}")

    def format_time(self, seconds: float) -> str:
        # Implementation of format_time method
        pass

    def extract_bits(self, candidate: int, index: int, offset: int, constant: int) -> int:
        # Implementation of extract_bits method
        pass
