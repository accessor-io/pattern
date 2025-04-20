#!/usr/bin/python3

def hex_to_4bit_patterns(hex_string):
    """Convert hex string to 4-bit patterns (nibbles)"""
    hex_string = hex_string.zfill(64)
    num = int(hex_string, 16)
    binary = format(num, '0256b')
    
    patterns = []
    positions = {format(i, '04b'): [] for i in range(16)}  # 0000 to 1111
    
    for i in range(0, 256, 4):
        pattern = binary[i:i+4]
        patterns.append(pattern)
        positions[pattern].append(i//4)
    
    return {
        'binary': binary,
        'patterns': patterns,
        'positions': positions,
        'hex': hex_string
    } 