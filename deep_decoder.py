#!/usr/bin/env python3
"""
DEEP DECODER - Advanced Pattern Analysis
Analyze the LXG(Saout# pattern and try multiple interpretation methods
"""

import base64
import hashlib
import re
from itertools import cycle

class DeepDecoder:
    def __init__(self):
        self.target_string = "LXG(Saout#k/@M1L,Nec;I{XoymLiF-GD5p-A^XSH"
        self.full_hex = "925f94cd6e13cb4fa50400050664458b371cc56a324b4d1e38e27305badbef1582c32d061820081b6f1172c9937f4eafd7cb7d2f2e4b2f95e23beafd2197e"
        
    def analyze_pattern_structure(self):
        """Analyze the structure of our target string"""
        print("🔍 PATTERN STRUCTURE ANALYSIS")
        print("=" * 50)
        
        s = self.target_string
        print(f"String: {s}")
        print(f"Length: {len(s)}")
        
        # Character frequency analysis
        char_freq = {}
        for char in s:
            char_freq[char] = char_freq.get(char, 0) + 1
        
        print(f"Character frequencies: {char_freq}")
        
        # Look for repeating patterns
        for pattern_len in [2, 3, 4, 5]:
            patterns = {}
            for i in range(len(s) - pattern_len + 1):
                pattern = s[i:i+pattern_len]
                patterns[pattern] = patterns.get(pattern, 0) + 1
            
            repeats = {p: c for p, c in patterns.items() if c > 1}
            if repeats:
                print(f"Repeating {pattern_len}-char patterns: {repeats}")
        
        # ASCII value analysis
        ascii_values = [ord(c) for c in s]
        print(f"ASCII range: {min(ascii_values)} - {max(ascii_values)}")
        print(f"ASCII values: {ascii_values[:10]}... (first 10)")
        
    def try_custom_base_decodings(self):
        """Try various custom base encodings"""
        print("\n🔢 CUSTOM BASE DECODING ATTEMPTS")
        print("=" * 50)
        
        s = self.target_string
        results = {}
        
        # Try Base64 variations
        try:
            # Add padding if needed
            for padding in ['', '=', '==', '===']:
                test_string = s + padding
                if re.match(r'^[A-Za-z0-9+/]*={0,3}$', test_string):
                    try:
                        decoded = base64.b64decode(test_string)
                        results[f'base64_pad_{len(padding)}'] = decoded
                    except:
                        pass
        except:
            pass
        
        # Try treating as hex with character substitution
        hex_mapping = {
            'L': '1', 'X': '0', 'G': '9', '(': 'A', 'S': '5', 'a': 'a', 'o': '0', 'u': 'b', 't': '7', '#': 'F'
        }
        
        possible_hex = ""
        for char in s:
            if char in hex_mapping:
                possible_hex += hex_mapping[char]
            elif char.lower() in '0123456789abcdef':
                possible_hex += char.lower()
        
        if len(possible_hex) % 2 == 0 and all(c in '0123456789abcdef' for c in possible_hex):
            try:
                hex_decoded = bytes.fromhex(possible_hex)
                results['hex_substitution'] = hex_decoded
            except:
                pass
        
        # Try Base58-like decoding
        base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        if all(c in base58_chars + "()/@{}-^," for c in s):
            # Remove non-base58 chars and try decoding
            clean_s = ''.join(c for c in s if c in base58_chars)
            if clean_s:
                results['cleaned_for_base58'] = clean_s
        
        for name, result in results.items():
            if isinstance(result, bytes):
                readable = result.decode('utf-8', errors='ignore')
                print(f"{name}: {readable[:50]}..." if len(readable) > 50 else f"{name}: {readable}")
            else:
                print(f"{name}: {result}")
        
        return results
    
    def try_arithmetic_operations(self):
        """Try arithmetic operations on ASCII values"""
        print("\n➕ ARITHMETIC OPERATIONS")
        print("=" * 50)
        
        s = self.target_string
        ascii_vals = [ord(c) for c in s]
        
        operations = {
            'subtract_32': [chr(max(0, val - 32)) for val in ascii_vals if val >= 32],
            'subtract_48': [chr(max(0, val - 48)) for val in ascii_vals if val >= 48],
            'xor_with_42': [chr(val ^ 42) for val in ascii_vals],
            'xor_with_key_cycle': []
        }
        
        # XOR with KONAMI repeating
        key = "KONAMI"
        for i, val in enumerate(ascii_vals):
            key_char = key[i % len(key)]
            operations['xor_with_key_cycle'].append(chr(val ^ ord(key_char)))
        
        for name, result in operations.items():
            result_str = ''.join(result)
            printable = ''.join(c if 32 <= ord(c) <= 126 else '.' for c in result_str)
            print(f"{name}: {printable}")
    
    def try_steganographic_methods(self):
        """Try steganographic extraction methods"""
        print("\n🕵️ STEGANOGRAPHIC METHODS")
        print("=" * 50)
        
        s = self.target_string
        
        # Extract based on character positions
        methods = {
            'uppercase_only': ''.join(c for c in s if c.isupper()),
            'lowercase_only': ''.join(c for c in s if c.islower()),
            'numbers_only': ''.join(c for c in s if c.isdigit()),
            'special_chars_only': ''.join(c for c in s if not c.isalnum()),
            'ascii_above_90': ''.join(c for c in s if ord(c) > 90),
            'ascii_below_90': ''.join(c for c in s if ord(c) <= 90)
        }
        
        # Extract every nth character
        for n in [2, 3, 4, 5, 6]:
            methods[f'every_{n}th'] = ''.join(s[i] for i in range(0, len(s), n))
        
        # Extract based on binary representation of ASCII
        binary_str = ''.join(format(ord(c), '08b') for c in s)
        
        # Look for patterns in binary
        if len(binary_str) >= 8:
            methods['binary_chunks'] = [binary_str[i:i+8] for i in range(0, min(len(binary_str), 64), 8)]
        
        for name, result in methods.items():
            if isinstance(result, str) and result:
                print(f"{name}: {result}")
            elif isinstance(result, list):
                print(f"{name}: {result[:5]}..." if len(result) > 5 else f"{name}: {result}")
    
    def analyze_as_coordinates_or_keys(self):
        """Analyze if the string could represent coordinates or cryptographic keys"""
        print("\n🗺️ COORDINATES & CRYPTO KEYS ANALYSIS")
        print("=" * 50)
        
        s = self.target_string
        
        # Look for numbers that could be coordinates
        numbers = re.findall(r'\d+', s)
        if numbers:
            print(f"Extracted numbers: {numbers}")
            
            # Try to interpret as lat/lon
            if len(numbers) >= 2:
                try:
                    lat = float(numbers[0])
                    lon = float(numbers[1])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        print(f"Possible coordinates: {lat}, {lon}")
                except:
                    pass
        
        # Check if it could be a Bitcoin private key or address
        # Bitcoin addresses start with 1, 3, or bc1
        if s.startswith(('1', '3')) and len(s) in range(25, 35):
            print("Possible Bitcoin address format")
        
        # Check for Ethereum-like patterns
        if s.startswith('0x') and len(s) == 42:
            print("Possible Ethereum address format")
        
        # Hash the string to see if it produces known patterns
        hash_results = {
            'md5': hashlib.md5(s.encode()).hexdigest(),
            'sha1': hashlib.sha1(s.encode()).hexdigest(),
            'sha256': hashlib.sha256(s.encode()).hexdigest()
        }
        
        print("Hash results:")
        for hash_type, hash_val in hash_results.items():
            print(f"  {hash_type}: {hash_val[:16]}...")
    
    def comprehensive_analysis(self):
        """Run all analysis methods"""
        print("🔬 COMPREHENSIVE PATTERN ANALYSIS")
        print("=" * 70)
        print(f"Target String: {self.target_string}")
        print("=" * 70)
        
        self.analyze_pattern_structure()
        self.try_custom_base_decodings()
        self.try_arithmetic_operations()
        self.try_steganographic_methods()
        self.analyze_as_coordinates_or_keys()
        
        # Final attempt: Try the original hex with different interpretations
        print("\n🎯 ORIGINAL HEX ALTERNATIVE INTERPRETATIONS")
        print("=" * 50)
        
        # Try interpreting the hex as different data types
        try:
            hex_bytes = bytes.fromhex(self.full_hex + '0')  # Adding 0 to fix odd length
            
            # Try as different encodings
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    decoded = hex_bytes.decode(encoding, errors='ignore')
                    printable = ''.join(c if 32 <= ord(c) <= 126 else '.' for c in decoded)
                    if len(printable.strip('.')) > 10:
                        print(f"{encoding}: {printable[:60]}...")
                except:
                    continue
                    
        except Exception as e:
            print(f"Error with hex interpretation: {e}")

def main():
    decoder = DeepDecoder()
    decoder.comprehensive_analysis()

if __name__ == "__main__":
    main() 