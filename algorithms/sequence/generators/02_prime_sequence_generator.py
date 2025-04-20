#!/usr/bin/env python3
"""
02_prime_sequence_generator.py - Prime-Based Sequence Generator

A specialized sequence generator that constructs numerical sequences based on prime numbers.
This implementation uses a combination of prime generation and transformation 
functions to produce cryptographically useful sequences.

Features:
- Optimized prime number detection algorithm
- Sequential prime generation capabilities
- Transformation formula: current = current * 2 + prime
- 64-bit (16 hex character) formatted output

Applications:
- Cryptographic seed generation
- Deterministic sequence derivation
- Bitcoin address puzzle solutions
"""

def is_prime(n: int) -> bool:
    """Optimized prime check for sequence generation"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w
    return True

class PrimeSequenceGenerator:
    def __init__(self):
        self.current = 1
        self.primes = [2]
        self.next_candidate = 3
        
    def _get_next_prime(self) -> int:
        """Generate primes in order"""
        while True:
            if is_prime(self.next_candidate):
                self.primes.append(self.next_candidate)
                self.next_candidate += 2
                return self.primes[-2]  # Return previous prime
            self.next_candidate += 2
            
    def next(self) -> int:
        """Get next sequence term"""
        prime = self._get_next_prime()
        self.current = self.current * 2 + prime
        return self.current
    
    def generate(self, count: int) -> list:
        """Generate sequence starting from 1"""
        sequence = [1]
        for _ in range(count-1):
            sequence.append(self.next())
        return sequence

# Generate first 160 terms with proper formatting
if __name__ == "__main__":
    gen = PrimeSequenceGenerator()
    sequence = gen.generate(160)
    
    for i, val in enumerate(sequence):
        print(f"{i+1:03d}: 0x{val:016x}")  # 64-bit (16 hex char) format 