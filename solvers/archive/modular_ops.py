#!/usr/bin/env python3

import math
from typing import Tuple, List

class ModularArithmetic:
    """
    Implementation of efficient modular arithmetic operations.
    """
    
    @staticmethod
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """
        Extended Euclidean Algorithm to find GCD and Bézout's identity coefficients.
        Returns (gcd, x, y) where gcd = ax + by
        """
        if a == 0:
            return b, 0, 1
        
        gcd, x1, y1 = ModularArithmetic.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        
        return gcd, x, y

    @staticmethod
    def mod_inverse(a: int, m: int) -> int:
        """
        Calculate modular multiplicative inverse using extended Euclidean algorithm.
        Returns x where (a * x) % m = 1
        """
        gcd, x, _ = ModularArithmetic.extended_gcd(a, m)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        return (x % m + m) % m

    @staticmethod
    def montgomery_reduction(T: int, N: int, R: int) -> int:
        """
        Montgomery reduction algorithm.
        T is the number to reduce
        N is the modulus
        R is the Montgomery radix (power of 2 greater than N)
        """
        R_mask = R - 1
        N_prime = -ModularArithmetic.mod_inverse(N, R)  # N' = -N^(-1) mod R
        
        m = ((T & R_mask) * N_prime) & R_mask
        t = (T + m * N) >> int(math.log2(R))
        
        if t >= N:
            t -= N
        return t 