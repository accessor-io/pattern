#!/usr/bin/python3

def hamming_analysis(hex_string):
    """Analyze Hamming weight (population count) patterns"""
    hex_string = hex_string.zfill(64)
    num = int(hex_string, 16)
    binary = format(num, '0256b')
    
    # Analyze in different chunk sizes
    analysis = {}
    for chunk_size in [8, 16, 32, 64]:
        weights = []
        for i in range(0, 256, chunk_size):
            chunk = binary[i:i+chunk_size]
            weight = chunk.count('1')
            weights.append({
                'position': i//chunk_size,
                'weight': weight,
                'percentage': (weight/chunk_size) * 100
            })
        analysis[chunk_size] = weights
    
    return analysis 