#!/usr/bin/python3

def crypto_analysis(hex_string):
    """Analyze potential cryptographic properties"""
    binary = bin(int(hex_string, 16))[2:].zfill(256)
    
    return {
        'avalanche_effect': calculate_avalanche(binary),
        'hamming_distance_to_complement': calculate_hamming_distance(binary, ''.join('1' if b == '0' else '0' for b in binary)),
        'linear_complexity': calculate_linear_complexity(binary),
        'hash_values': {
            'md5': hashlib.md5(bytes.fromhex(hex_string)).hexdigest(),
            'sha1': hashlib.sha1(bytes.fromhex(hex_string)).hexdigest(),
            'sha256': hashlib.sha256(bytes.fromhex(hex_string)).hexdigest()
        }
    } 