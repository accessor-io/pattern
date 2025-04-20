#!/usr/bin/python3

def repetition_analysis(hex_string):
    """Analyze repeating patterns"""
    binary = bin(int(hex_string, 16))[2:].zfill(256)
    
    patterns = {}
    for length in range(2, 33):  # Look for patterns up to 32 bits
        found_patterns = {}
        for i in range(len(binary) - length + 1):
            pattern = binary[i:i+length]
            if pattern in found_patterns:
                found_patterns[pattern].append(i)
            else:
                found_patterns[pattern] = [i]
        
        # Keep only patterns that repeat
        repeating = {k: v for k, v in found_patterns.items() if len(v) > 1}
        if repeating:
            patterns[length] = repeating
    
    return patterns 