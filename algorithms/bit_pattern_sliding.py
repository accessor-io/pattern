#!/usr/bin/python3

def sliding_window_analysis(hex_string, window_size=8):
    """Analyze bit patterns using a sliding window"""
    hex_string = hex_string.zfill(64)
    num = int(hex_string, 16)
    binary = format(num, '0256b')
    
    patterns = {}
    for i in range(len(binary) - window_size + 1):
        pattern = binary[i:i+window_size]
        if pattern not in patterns:
            patterns[pattern] = []
        patterns[pattern].append(i)
    
    return {
        'window_size': window_size,
        'patterns': patterns,
        'most_common': sorted(patterns.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    } 