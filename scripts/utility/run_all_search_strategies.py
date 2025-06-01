#!/usr/bin/env python3
"""
Combined search script that runs all strategies in parallel
"""

import subprocess
import threading
import time
import logging
import os
import json
import signal
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='combined_search.log',
    filemode='a'
)
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

# Target information
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"
TARGET_INDEX = 68
PREV_TERM_67 = "0x730fc235c1942c1ae"

# Script information
SCRIPTS = [
    {
        "name": "Focused Search",
        "file": "68_focused_search.py",
        "description": "Targeted range-based search"
    },
    {
        "name": "Mathematical Patterns",
        "file": "68_mathematical_patterns.py",
        "description": "Mathematical transformations and pattern search"
    },
    {
        "name": "Bitwise Operations",
        "file": "68_bitwise_search.py",
        "description": "Bit-level operations and patterns"
    },
    {
        "name": "Exact Candidate Testing",
        "file": "exact_candidate_test.py",
        "description": "Testing specific candidate values"
    }
]

# Global state
running_processes = []
solution_found = False
solution_lock = threading.Lock()
found_solution = {}

def run_script(script_info):
    """
    Run a search script in a subprocess and monitor its output
    """
    global solution_found, found_solution
    
    script_name = script_info["name"]
    script_file = script_info["file"]
    
    logger.info(f"Starting {script_name} ({script_file})")
    
    try:
        # Start the process
        process = subprocess.Popen(
            ["python3", script_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Add to global list of processes
        running_processes.append(process)
        
        # Monitor output
        for line in process.stdout:
            # Print the output
            logger.info(f"[{script_name}] {line.strip()}")
            
            # Check if solution found
            if "MATCH FOUND" in line or "Solution saved" in line:
                with solution_lock:
                    solution_found = True
                    # Try to get solution data from output
                    if "Candidate:" in line:
                        # Extract candidate from log
                        parts = line.split("Candidate:")
                        if len(parts) > 1:
                            candidate = parts[1].strip()
                            found_solution = {
                                "term_index": TARGET_INDEX,
                                "private_key_hex": candidate,
                                "bitcoin_address": TARGET_ADDRESS,
                                "found_timestamp": time.time(),
                                "previous_term_67": PREV_TERM_67,
                                "discovery_method": script_name
                            }
                # Terminate all other processes
                terminate_processes()
                break
        
        # Wait for process to complete
        process.wait()
        logger.info(f"{script_name} completed with code {process.returncode}")
        
    except Exception as e:
        logger.error(f"Error running {script_name}: {e}")

def terminate_processes():
    """
    Terminate all running processes
    """
    for process in running_processes:
        try:
            if process.poll() is None:  # Process is still running
                process.terminate()
                logger.info(f"Terminated process {process.pid}")
        except Exception as e:
            logger.error(f"Error terminating process: {e}")

def check_solution_file():
    """
    Check if a solution file exists
    """
    if os.path.exists("term68_solution.json"):
        try:
            with open("term68_solution.json", "r") as f:
                solution = json.load(f)
                return solution
        except Exception as e:
            logger.error(f"Error reading solution file: {e}")
    return None

def signal_handler(sig, frame):
    """
    Handle termination signals
    """
    logger.info("Received termination signal")
    terminate_processes()
    sys.exit(0)

def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=== Starting Combined Search ===")
    logger.info(f"Target Address: {TARGET_ADDRESS}")
    logger.info(f"Previous Term (67): {PREV_TERM_67}")
    
    # Check if solution already exists
    existing_solution = check_solution_file()
    if existing_solution:
        logger.info(f"Solution already found: {existing_solution.get('private_key_hex')}")
        return
    
    # Create threads for each script
    threads = []
    for script_info in SCRIPTS:
        thread = threading.Thread(target=run_script, args=(script_info,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # If a solution was found, save it
    if solution_found and found_solution:
        logger.info("=== SOLUTION FOUND ===")
        logger.info(f"Private Key: {found_solution.get('private_key_hex')}")
        
        # Save solution if not already saved
        if not os.path.exists("term68_solution.json"):
            with open("term68_solution.json", "w") as f:
                json.dump(found_solution, f, indent=2)
            
            with open("term68_solution.txt", "w") as f:
                f.write(f"Term 68 Solution\n")
                f.write(f"Private Key: {found_solution.get('private_key_hex')}\n")
                f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
                f.write(f"Previous Term (67): {PREV_TERM_67}\n")
                f.write(f"Discovery Method: {found_solution.get('discovery_method')}\n")
            
            logger.info("Solution saved to term68_solution.json and term68_solution.txt")
    else:
        # Check if solution was saved by one of the scripts
        final_solution = check_solution_file()
        if final_solution:
            logger.info("=== SOLUTION FOUND ===")
            logger.info(f"Private Key: {final_solution.get('private_key_hex')}")
        else:
            logger.info("No solution found by any strategy")

if __name__ == "__main__":
    start_time = time.time()
    main()
    duration = time.time() - start_time
    logger.info(f"Total search duration: {duration:.2f} seconds") 