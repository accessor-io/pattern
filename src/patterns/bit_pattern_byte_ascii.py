#!/usr/bin/python3

def hex_to_byte_patterns(hex_string):
    """Convert hex string to byte patterns with ASCII representation"""
    hex_string = hex_string.zfill(64)
    byte_array = bytes.fromhex(hex_string)
    
    patterns = []
    for byte in byte_array:
        ascii_char = chr(byte) if 32 <= byte <= 126 else '.'
        patterns.append({
            'byte': byte,
            'binary': format(byte, '08b'),
            'hex': format(byte, '02x'),
            'ascii': ascii_char
        })
    
    return patterns 