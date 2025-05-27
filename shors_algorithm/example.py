#!/usr/bin/env python3
"""
Example usage of Shor's algorithm for factoring small numbers.
"""

import time
from improved_shors import shor_factorize, factorize_completely, visualize_factorization

# List of numbers to factorize
test_numbers = [15, 21, 33, 35, 39, 55, 91, 119, 133, 155, 187, 221]

def run_examples():
    """Run examples of factorizing small numbers using Shor's algorithm."""
    print("Shor's Algorithm Examples")
    print("========================\n")
    
    results = []
    
    for N in test_numbers:
        print(f"\n==== Factorizing {N} ====")
        
        # Using classical period finding (faster for these small numbers)
        start_time = time.time()
        factors = factorize_completely(N, use_quantum=False)
        end_time = time.time()
        
        # Format factors nicely
        factor_str = " × ".join(map(str, factors))
        time_taken = end_time - start_time
        
        print(f"Prime factorization: {N} = {factor_str}")
        print(f"Time taken: {time_taken:.4f} seconds")
        
        # Store results for summary
        results.append({
            "number": N,
            "factors": factors,
            "time": time_taken
        })
    
    # Print summary
    print("\n\nSummary of Results")
    print("=================")
    print(f"{'Number':<10} {'Factorization':<30} {'Time (s)':<10}")
    print("-" * 50)
    
    for result in results:
        factorization = " × ".join(map(str, result["factors"]))
        print(f"{result['number']:<10} {factorization:<30} {result['time']:.4f}")


def demo_rsa_number():
    """Demonstrate Shor's algorithm on a small RSA-like number."""
    # This is a very small number for demonstration purposes
    # Real RSA numbers would be much larger (e.g., 1024 or 2048 bits)
    p, q = 17, 19
    N = p * q  # 323
    
    print("\n\nDemonstrating Shor's Algorithm on a Small RSA-like Number")
    print("==========================================================")
    print(f"p = {p}, q = {q}, N = p×q = {N}")
    
    print("\nAttempting to factorize without knowing p and q...")
    start_time = time.time()
    factor1, factor2 = shor_factorize(N, use_quantum=False, attempts=5)
    end_time = time.time()
    
    if factor1 * factor2 == N and factor1 > 1 and factor2 > 1:
        print(f"Success! Found factors: {factor1} and {factor2}")
    else:
        print(f"Failed to find non-trivial factors")
    
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    
    # Create a visualization
    if factor1 * factor2 == N and factor1 > 1 and factor2 > 1:
        visualize_factorization(N, [factor1, factor2])


if __name__ == "__main__":
    run_examples()
    demo_rsa_number() 