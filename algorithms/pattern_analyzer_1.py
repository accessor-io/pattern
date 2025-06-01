import random
from collections import defaultdict

class PatternDiscoverer:
    def __init__(self):
        self.prime_factors = defaultdict(int)
        self.bit_activation = defaultdict(int)
        
    def analyze_solutions(self, solutions):
        """Analyze found private keys for common patterns"""
        # Reset counters
        self.prime_factors.clear()
        self.bit_activation.clear()
        
        # Analyze each solution
        for sol in solutions:
            num = int(sol['private_key'], 16)
            
            # Prime factor analysis
            for prime in self._prime_factors(num):
                self.prime_factors[prime] += 1
                
            # Bit activation analysis
            for bit in range(256):
                if num & (1 << bit):
                    self.bit_activation[bit] += 1

    def _prime_factors(self, n):
        """Prime factorization helper"""
        factors = set()
        while n % 2 == 0:
            factors.add(2)
            n //= 2
        i = 3
        while i*i <= n:
            while n % i == 0:
                factors.add(i)
                n //= i
            i += 2
        if n > 2:
            factors.add(n)
        return factors

    @property
    def common_primes(self):
        """Get top 10 most frequent prime factors"""
        return sorted(self.prime_factors.items(), 
                    key=lambda x: x[1], reverse=True)[:10] 