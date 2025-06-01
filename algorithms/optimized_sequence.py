from functools import lru_cache

# Precompute primes for efficient access
def sieve(n):
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
    prime = PRIMES[n % len(OWWNWWWwwwwWWWw