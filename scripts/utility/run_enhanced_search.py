#!/usr/bin/env python3
"""
Enhanced Bitcoin Private Key Search

This script runs the continuous adaptive search algorithm with our
enhanced Bitcoin-specific candidate generation for better results.
"""

import os
import sys
import time
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='enhanced_search.log',
    filemode='a'
)
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

def main():
    """
    Main function to run the enhanced search
    """
    parser = argparse.ArgumentParser(description="Enhanced Bitcoin Private Key Search")
    parser.add_argument("--duration", type=int, default=24, help="Duration to run the search in hours")
    parser.add_argument("--candidates-per-batch", type=int, default=100, help="Number of candidates to test per batch")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Logging level")
    args = parser.parse_args()
    
    # Set log level
    log_level = getattr(logging, args.log_level)
    logger.setLevel(log_level)
    console.setLevel(log_level)
    
    logger.info("Starting Enhanced Bitcoin Key Search")
    logger.info(f"Duration: {args.duration} hours")
    logger.info(f"Candidates per batch: {args.candidates_per_batch}")
    
    # First, make sure we patch the search algorithm with our enhanced candidate generator
    try:
        from bitcoin_utils.integration import patch_search_algorithm
        success = patch_search_algorithm()
        if success:
            logger.info("Successfully patched search algorithm with enhanced candidate generator")
        else:
            logger.error("Failed to patch search algorithm. Falling back to original algorithm.")
    except Exception as e:
        logger.error(f"Error loading integration module: {e}")
        logger.error("Continuing with original algorithm")
    
    # Now import and run the main search algorithm
    try:
        # We need to use dynamic import since the module name starts with a number
        import importlib.util
        spec = importlib.util.spec_from_file_location("search", "68_continuous_adaptive_search.py")
        search = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(search)
        
        # Set up search parameters
        search.SEARCH_DURATION_HOURS = args.duration
        search.CANDIDATES_PER_BATCH = args.candidates_per_batch
        
        # Override logging level if needed
        if args.log_level:
            search.logger.setLevel(log_level)
            for handler in search.logger.handlers:
                handler.setLevel(log_level)
        
        # Calculate end time based on duration
        end_time = time.time() + (args.duration * 3600)
        
        # Update the global variable if it exists
        if hasattr(search, 'END_TIME'):
            search.END_TIME = end_time
            
        logger.info(f"Configured search to run for {args.duration} hours with {args.candidates_per_batch} candidates per batch")
        
        # Run the continuous adaptive search function
        logger.info("Starting continuous adaptive search with enhanced candidate generation")
        search.continuous_adaptive_search()
    except Exception as e:
        logger.error(f"Error running search algorithm: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 