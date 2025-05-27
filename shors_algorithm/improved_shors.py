#!/usr/bin/env python3
"""
Improved implementation of Shor's algorithm using the quantum phase estimation module.
"""

import math
import random
import argparse
from typing import Tuple, Optional, List
import time
import sys

import numpy as np
import matplotlib.pyplot as plt

from quantum_phase_estimation import find_period_qpe


def gcd(a: int, b: int) -> int:
    """Calculate the greatest common divisor of a and b using Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a


def is_prime(n: int) -> bool:
    """Check if a number is prime using a simple trial division method."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def find_period_classical(a: int, N: int) -> int:
    """
    Find the period of f(x) = a^x mod N using classical computation.
    This is for testing and comparison purposes.
    """
    for r in range(1, N):
        if pow(a, r, N) == 1:
            return r
    return -1


def shor_factorize(N: int, use_quantum: bool = False, attempts: int = 10) -> Tuple[int, int]:
    """
    Implement Shor's algorithm to factorize the number N.
    
    Args:
        N: The number to factorize
        use_quantum: Whether to use quantum phase estimation (True) or classical period finding (False)
        attempts: Number of attempts to factorize N
    
    Returns:
        A pair of factors if successful, otherwise (1, N)
    """
    print(f"Attempting to factorize {N}")
    
    # Check if N is even
    if N % 2 == 0:
        return 2, N // 2
    
    # Check if N is a prime power
    for i in range(2, int(math.log2(N)) + 1):
        root = round(N**(1/i))
        if root**i == N:
            return root, N // root
    
    # If N is prime, we cannot factorize it
    if is_prime(N):
        print(f"{N} is prime and cannot be factorized further.")
        return 1, N
    
    for attempt in range(1, attempts + 1):
        print(f"\nAttempt {attempt}/{attempts}")
        
        # Step 1: Choose a random number a < N
        a = random.randint(2, N - 1)
        print(f"Randomly selected a = {a}")
        
        # Step 2: Compute gcd(a, N)
        factor = gcd(a, N)
        if factor > 1:
            print(f"Found factor directly using GCD: {factor}")
            return factor, N // factor
        
        # Step 3: Find the period r of f(x) = a^x mod N
        print(f"Finding period of f(x) = {a}^x mod {N}...")
        start_time = time.time()
        
        if use_quantum:
            try:
                # Use quantum period finding (slower in simulation but would be faster on quantum hardware)
                r = find_period_qpe(a, N)
                print(f"Using quantum period finding...")
                if r is None:
                    print("Quantum period finding failed, trying classical method")
                    r = find_period_classical(a, N)
            except Exception as e:
                print(f"Error in quantum period finding: {e}")
                r = find_period_classical(a, N)
        else:
            # Use classical period finding (faster for simulation purposes)
            r = find_period_classical(a, N)
        
        end_time = time.time()
        print(f"Period r = {r} (found in {end_time - start_time:.2f} seconds)")
        
        # Step 4: Check if r is usable
        if r % 2 != 0:
            print(f"Period {r} is odd, trying again")
            continue
        
        x = pow(a, r // 2, N)
        if x == N - 1:
            print(f"a^(r/2) mod N = -1, trying again")
            continue
        
        # Step 5: Compute potential factors
        factor1 = gcd(x - 1, N)
        factor2 = gcd(x + 1, N)
        
        print(f"Potential factors: gcd({x}-1, {N}) = {factor1}, gcd({x}+1, {N}) = {factor2}")
        
        if factor1 > 1 and factor1 < N:
            return factor1, N // factor1
        if factor2 > 1 and factor2 < N:
            return factor2, N // factor2
        
        print("Found trivial factors (1 and N), trying again")
    
    print(f"Failed to factorize {N} after {attempts} attempts")
    return 1, N


def factorize_completely(N: int, use_quantum: bool = False) -> List[int]:
    """
    Completely factorize a number into its prime factors.
    
    Args:
        N: The number to factorize
        use_quantum: Whether to use quantum methods for period finding
    
    Returns:
        A list of prime factors
    """
    factors = []
    
    # Handle special cases
    if N <= 1:
        return [N]
    
    if is_prime(N):
        return [N]
    
    # Start with N and factorize recursively
    to_factorize = [N]
    
    while to_factorize:
        num = to_factorize.pop()
        
        if is_prime(num):
            factors.append(num)
            continue
        
        # Try to factorize the number
        factor1, factor2 = shor_factorize(num, use_quantum)
        
        if factor1 == 1:  # Failed to factorize
            # As a fallback, try simple trial division
            for i in range(2, int(math.sqrt(num)) + 1):
                if num % i == 0:
                    factor1, factor2 = i, num // i
                    break
            else:
                # If all else fails, treat it as a prime (though it might not be)
                factors.append(num)
                continue
        
        # Add factors to the list of numbers to factorize
        to_factorize.append(factor1)
        to_factorize.append(factor2)
    
    return sorted(factors)


def visualize_factorization(N: int, factors: List[int]) -> None:
    """
    Create a visualization of the factorization.
    
    Args:
        N: The original number
        factors: The list of prime factors
    """
    # Count occurrences of each factor
    factor_counts = {}
    for factor in factors:
        if factor in factor_counts:
            factor_counts[factor] += 1
        else:
            factor_counts[factor] = 1
    
    # Create a string representation of the factorization
    factor_strings = []
    for factor, count in sorted(factor_counts.items()):
        if count > 1:
            factor_strings.append(f"{factor}^{count}")
        else:
            factor_strings.append(f"{factor}")
    
    factorization_str = " × ".join(factor_strings)
    
    # Create a simple bar chart of the factors
    factors_unique = sorted(factor_counts.keys())
    counts = [factor_counts[f] for f in factors_unique]
    
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(factors_unique)), counts)
    plt.xticks(range(len(factors_unique)), [str(f) for f in factors_unique])
    plt.xlabel('Prime Factors')
    plt.ylabel('Exponent')
    plt.title(f'Factorization of {N} = {factorization_str}')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save the visualization
    plt.savefig(f'factorization_{N}.png')
    plt.close()
    
    print(f"\nFactorization of {N} = {factorization_str}")
    print(f"Visualization saved as factorization_{N}.png")


def main():
    """Main function to run the algorithm from command line."""
    parser = argparse.ArgumentParser(description='Factorize a number using Shor\'s algorithm')
    parser.add_argument('number', type=int, help='The number to factorize')
    parser.add_argument('--quantum', action='store_true', help='Use quantum period finding (slower in simulation)')
    parser.add_argument('--visualize', action='store_true', help='Create a visualization of the factorization')
    parser.add_argument('--attempts', type=int, default=5, help='Number of attempts for each factorization')
    args = parser.parse_args()
    
    N = args.number
    
    if N <= 1:
        print("Please enter a number greater than 1")
        return
    
    print(f"Factorizing {N} using {'quantum' if args.quantum else 'classical'} period finding")
    
    start_time = time.time()
    factors = factorize_completely(N, args.quantum)
    end_time = time.time()
    
    print(f"\nFactorization completed in {end_time - start_time:.2f} seconds")
    
    if len(factors) == 1:
        print(f"{N} is a prime number")
    else:
        print(f"Prime factorization of {N}: {' × '.join(map(str, factors))}")
        
        # Verify the factorization
        product = 1
        for factor in factors:
            product *= factor
        
        if product == N:
            print("Verification: Correct! The product of factors equals the original number.")
        else:
            print(f"Verification failed! Product of factors is {product}, not {N}.")
    
    if args.visualize and len(factors) > 1:
        visualize_factorization(N, factors)


if __name__ == "__main__":
    main() 