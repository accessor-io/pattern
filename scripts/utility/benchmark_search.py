#!/usr/bin/env python3
"""
Benchmarking script for the RowHammer-inspired search
This script measures the performance of different search approaches
"""

import time
import logging
import sys
from rowhammer_search import (
    systematic_rowhammer_search,
    apply_double_sided_hammering,
    half_double_attack,
    test_candidate,
    private_key_to_address,
    PREV_TERM_67_INT,
    ESTIMATE_VALUE
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def benchmark_function(func, *args, **kwargs):
    """
    Benchmark a function's execution time
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    duration = end_time - start_time
    return result, duration

def main():
    """
    Main benchmarking function
    """
    print("==== RowHammer Search Benchmarking ====\n")
    
    # Base candidates for testing
    base_candidates = [
        PREV_TERM_67_INT,
        ESTIMATE_VALUE,
        0x734fc235c1940c1af,  # From previous tests
        PREV_TERM_67_INT ^ (1 << 16)  # Bit flip at position 16
    ]
    
    # Small sample sizes for quick benchmarking
    systematic_sample_size = 100
    double_sided_sample_size = 50
    half_double_sample_size = 50
    
    print(f"Benchmarking with {len(base_candidates)} base candidates\n")
    
    # Benchmark systematic RowHammer search
    print(f"1. Systematic RowHammer Search (max_candidates={systematic_sample_size}):")
    result, duration = benchmark_function(
        systematic_rowhammer_search, 
        base_candidates,
        max_candidates=systematic_sample_size
    )
    print(f"   Duration: {duration:.2f} seconds")
    print(f"   Performance: {systematic_sample_size/duration:.2f} candidates/second")
    print()
    
    # Benchmark double-sided hammering
    print(f"2. Double-sided Hammering (max_candidates={double_sided_sample_size}):")
    for i, candidate in enumerate(base_candidates[:2]):  # Test first 2 candidates
        print(f"   Base candidate {i+1}: {hex(candidate)}")
        result, duration = benchmark_function(
            apply_double_sided_hammering,
            candidate,
            num_patterns=5,
            max_candidates=double_sided_sample_size
        )
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Performance: {double_sided_sample_size/duration:.2f} candidates/second")
    print()
    
    # Benchmark half-double attack
    print(f"3. Half-double Attack (max_candidates={half_double_sample_size}):")
    for i, candidate in enumerate(base_candidates[:2]):  # Test first 2 candidates
        print(f"   Base candidate {i+1}: {hex(candidate)}")
        result, duration = benchmark_function(
            half_double_attack,
            candidate,
            max_candidates=half_double_sample_size
        )
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Performance: {half_double_sample_size/duration:.2f} candidates/second")
    print()
    
    # Benchmark candidate testing
    print("4. Individual Candidate Testing:")
    test_iterations = 100
    start_time = time.time()
    for _ in range(test_iterations):
        test_candidate(PREV_TERM_67_INT)
    end_time = time.time()
    duration = end_time - start_time
    print(f"   Tested {test_iterations} candidates in {duration:.2f} seconds")
    print(f"   Performance: {test_iterations/duration:.2f} candidates/second")
    print()
    
    # Benchmark address generation
    print("5. Bitcoin Address Generation:")
    addr_iterations = 100
    start_time = time.time()
    for _ in range(addr_iterations):
        private_key_to_address(PREV_TERM_67_INT)
    end_time = time.time()
    duration = end_time - start_time
    print(f"   Generated {addr_iterations} addresses in {duration:.2f} seconds")
    print(f"   Performance: {addr_iterations/duration:.2f} addresses/second")
    
    print("\n==== Benchmarking Complete ====")
    
    # Generate search time estimates
    print("\n==== Search Time Estimates ====")
    candidates_per_second = systematic_sample_size/duration
    print(f"Based on benchmark results:")
    print(f"- Testing 1 million candidates would take approximately: {1000000/candidates_per_second/3600:.2f} hours")
    print(f"- Testing 1 billion candidates would take approximately: {1000000000/candidates_per_second/3600/24:.2f} days")
    print()
    print("Note: Actual performance may vary based on system load and search randomization.")

if __name__ == "__main__":
    main() 