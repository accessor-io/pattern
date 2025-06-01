#!/usr/bin/env python3
"""
03_optimized_sequence_generator.py - High-Performance Sequence Generator

A memory-optimized sequence generator that uses memoization and precomputed prime values
to efficiently generate complex numerical sequences. This implementation prioritizes
performance for large-scale sequence generation.

Features:
- Precomputed prime sieve for fast access to prime numbers
- LRU cache for memoization of previously calculated terms
- Recursive generation algorithm with performance optimizations
- Efficient memory usage for large sequence generation

Applications:
- High-speed cryptographic sequence generation
- Memory-constrained environments
- Large-scale pattern analysis
"""

from functools import lru_cache

# Precompute primes for efficient access
def sieve(n):
    """Generate an efficient sieve of primes up to n"""
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            sieve[i*i : n+1 : i] = [False]*len(sieve[i*i : n+1 : i])
    return [i for i, is_prime in enumerate(sieve) if is_prime]

PRIMES = sieve(1000)  # Precompute first 1000 primes

@lru_cache(maxsize=None)
def generate_term(n):
    """Recursive term generation with memoization"""
    if n == 0:
        return 1  # Initial term
    
    # Get previous term and current prime
    prev = generate_term(n-1)
    prime = PRIMES[n % len(PRIMES)]
    
    # Apply transformation
    return (prev * prime) % (1 << 256)  # Mod 2^256 to stay in range 