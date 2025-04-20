#!/usr/bin/python3

import base64

def base_conversions(hex_string):
    """Convert hex string to various bases"""
    num = int(hex_string, 16)
    return {
        'hex': hex_string,
        'decimal': str(num),
        'binary': bin(num)[2:].zfill(256),
        'octal': oct(num)[2:],
        'base32': base64.b32encode(bytes.fromhex(hex_string)).decode(),
        'base64': base64.b64encode(bytes.fromhex(hex_string)).decode()
    } 