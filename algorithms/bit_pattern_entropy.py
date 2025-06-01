#!/usr/bin/python3

import math
from zlib import compress

def entropy_analysis(hex_string):
    """Analyze entropy and randomness metrics"""
    binary = bin(int(hex_string, 16))[2:].zfill(256)
    
    # Calculate Shannon entropy
    prob_1 = binary.count('1') / len(binary)
    prob_0 = 1 - prob_1
    shannon_entropy = 0
    if prob_0 > 0: shannon_entropy -= prob_0 * math.log2(prob_0)
    if prob_1 > 0: shannon_entropy -= prob_1 * math.log2(prob_1)
    
    return {
        'shannon_entropy': shannon_entropy,
        'bit_distribution': {
            '0': binary.count('0'),
            '1': binary.count('1')
        },
        'randomness_score': calculate_randomness_score(binary),
        'compression_ratio': len(compress(binary)) / len(binary)
    } 