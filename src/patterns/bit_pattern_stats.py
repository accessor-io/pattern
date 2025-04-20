#!/usr/bin/python3

def statistical_analysis(hex_string):
    """Analyze statistical properties"""
    binary = bin(int(hex_string, 16))[2:].zfill(256)
    chunks = [binary[i:i+8] for i in range(0, 256, 8)]
    
    return {
        'chi_square_test': calculate_chi_square(binary),
        'autocorrelation': calculate_autocorrelation(binary),
        'byte_frequency': calculate_byte_frequency(chunks),
        'distribution_metrics': {
            'mean': statistics.mean(int(chunk, 2) for chunk in chunks),
            'median': statistics.median(int(chunk, 2) for chunk in chunks),
            'stdev': statistics.stdev(int(chunk, 2) for chunk in chunks)
        }
    } 