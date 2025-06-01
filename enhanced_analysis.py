#!/usr/bin/env python3
"""
Enhanced Decryption Analysis - Bitcoin/Crypto Focus
"""

import binascii
import re

def analyze_bitcoin_patterns():
    """Analyze for Bitcoin-specific patterns"""
    
    base_hex = "925f94cd6e13cb4fa50400050664458b371cc56a324b4d1e38e27305badbef1582c32d061820081b6f1172c9937f4eafd7cb7d2f2e4b2f95e23beafd2197e"
    hex_chars = "0123456789abcdefABCDEF"
    
    print("=== BITCOIN/CRYPTO PATTERN ANALYSIS ===\n")
    
    for append_char in hex_chars:
        corrected_hex = base_hex + append_char
        
        try:
            # Step 1: Convert hex to bytes
            bytes_data = bytes.fromhex(corrected_hex)
            
            # Step 2: XOR with key "KONAMI"
            key = "KONAMI".encode('utf-8')
            xor_decrypted = bytearray()
            for i in range(len(bytes_data)):
                xor_decrypted.append(bytes_data[i] ^ key[i % len(key)])
            
            # Step 3: Vigenère cipher decryption
            xor_text = xor_decrypted.decode('latin-1', errors='ignore')
            vigenere_decrypted = vigenere_decrypt(xor_text, "KONAMI")
            
            # Step 4: ROT47 transformation
            final_output = rot47(vigenere_decrypted)
            
            # Analysis
            print(f"--- Append char: {append_char} ---")
            
            # Check raw bytes for patterns
            print(f"Raw bytes (first 32): {bytes_data[:32].hex()}")
            
            # Check for ASCII in final output
            ascii_chars = ''.join(c for c in final_output if 32 <= ord(c) <= 126)
            if len(ascii_chars) > 10:
                print(f"ASCII content: {ascii_chars}")
            
            # Look for specific patterns
            check_patterns(final_output, append_char)
            
            # Check XOR result for patterns
            check_patterns(xor_text, append_char, stage="XOR")
            
            # Check Vigenère result for patterns
            check_patterns(vigenere_decrypted, append_char, stage="Vigenère")
            
            print()
            
        except Exception as e:
            print(f"Error with append char '{append_char}': {e}")
            continue

def check_patterns(text, append_char, stage="Final"):
    """Check for various patterns in the decrypted text"""
    
    # Bitcoin address patterns
    if re.search(r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}', text):
        print(f"  {stage}: Potential Bitcoin address found!")
    
    # Private key patterns (64 hex chars)
    if re.search(r'[0-9a-fA-F]{64}', text):
        print(f"  {stage}: Potential private key pattern!")
    
    # URL patterns
    if re.search(r'https?://|www\.', text, re.IGNORECASE):
        print(f"  {stage}: URL pattern found!")
    
    # Base64 patterns
    if re.search(r'[A-Za-z0-9+/]{20,}={0,2}', text):
        print(f"  {stage}: Base64 pattern found!")
    
    # Ethereum address patterns
    if re.search(r'0x[a-fA-F0-9]{40}', text):
        print(f"  {stage}: Ethereum address pattern!")
    
    # Common crypto terms
    crypto_terms = ['bitcoin', 'btc', 'ethereum', 'eth', 'wallet', 'private', 'key', 'address', 'seed']
    for term in crypto_terms:
        if term.lower() in text.lower():
            print(f"  {stage}: Found crypto term: {term}")

def vigenere_decrypt(text, key):
    """Decrypt using Vigenère cipher"""
    decrypted = []
    key_length = len(key)
    key_int = [ord(i) for i in key]
    
    for i, char in enumerate(text):
        value = (ord(char) - key_int[i % key_length]) % 256
        decrypted.append(chr(value))
    
    return ''.join(decrypted)

def rot47(s):
    """Apply ROT47 transformation"""
    result = []
    for char in s:
        ascii_val = ord(char)
        if 33 <= ascii_val <= 126:
            result.append(chr(33 + ((ascii_val + 14) % 94)))
        else:
            result.append(char)
    return ''.join(result)

def analyze_raw_hex():
    """Analyze the raw hex string for direct patterns"""
    print("=== RAW HEX ANALYSIS ===\n")
    
    base_hex = "925f94cd6e13cb4fa50400050664458b371cc56a324b4d1e38e27305badbef1582c32d061820081b6f1172c9937f4eafd7cb7d2f2e4b2f95e23beafd2197e"
    
    # Look for embedded patterns in the hex itself
    print(f"Hex length: {len(base_hex)} characters")
    print(f"Byte length: {len(base_hex)//2} bytes (incomplete)")
    
    # Check for repeated patterns
    for i in range(2, 8, 2):  # Check for 1-4 byte patterns
        pattern_len = i
        patterns = {}
        for j in range(0, len(base_hex) - pattern_len + 1, 2):
            pattern = base_hex[j:j+pattern_len]
            if pattern in patterns:
                patterns[pattern] += 1
            else:
                patterns[pattern] = 1
        
        repeated = {k: v for k, v in patterns.items() if v > 1}
        if repeated:
            print(f"Repeated {pattern_len//2}-byte patterns: {repeated}")
    
    # Check for known magic bytes
    magic_bytes = {
        '504b': 'ZIP file',
        '89504e47': 'PNG image',
        'ffd8ff': 'JPEG image',
        '25504446': 'PDF file',
        '7f454c46': 'ELF executable'
    }
    
    for magic, desc in magic_bytes.items():
        if magic.lower() in base_hex.lower():
            print(f"Found magic bytes: {magic} ({desc})")

if __name__ == "__main__":
    analyze_raw_hex()
    print()
    analyze_bitcoin_patterns() 