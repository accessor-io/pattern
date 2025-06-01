#!/usr/bin/env python3
"""
FOCUSED DATA EXTRACTION
Target the highest readability results and extract the actual payload
"""

import re
import base64
import hashlib

class FocusedExtractor:
    def __init__(self):
        self.base_hex = "925f94cd6e13cb4fa50400050664458b371cc56a324b4d1e38e27305badbef1582c32d061820081b6f1172c9937f4eafd7cb7d2f2e4b2f95e23beafd2197e"
        self.lost_numbers = [4, 8, 15, 16, 23, 42]
        
    def get_best_decryption_path(self, append_char='0'):
        """Execute the highest-scoring decryption path"""
        corrected_hex = self.base_hex + append_char
        bytes_data = bytes.fromhex(corrected_hex)
        
        # Step 1: XOR with KONAMI + lost numbers
        key = "KONAMI" + "".join(map(str, self.lost_numbers))
        xor_result = self.xor_decrypt(bytes_data, key.encode())
        
        # Step 2: Vigenère with KONAMI
        xor_text = xor_result.decode('latin-1', errors='ignore')
        vigenere_result = self.vigenere_decrypt(xor_text, "KONAMI")
        
        # Step 3: ROT13
        final_result = self.rot13(vigenere_result)
        
        return final_result
    
    def xor_decrypt(self, data, key):
        """XOR decryption"""
        result = bytearray()
        for i in range(len(data)):
            result.append(data[i] ^ key[i % len(key)])
        return result
    
    def vigenere_decrypt(self, text, key):
        """Vigenère decryption"""
        decrypted = []
        key_length = len(key)
        key_int = [ord(i) for i in key]
        
        for i, char in enumerate(text):
            value = (ord(char) - key_int[i % key_length]) % 256
            decrypted.append(chr(value))
        
        return ''.join(decrypted)
    
    def rot13(self, s):
        """ROT13 transformation"""
        result = []
        for char in s:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                result.append(chr((ord(char) - ascii_offset + 13) % 26 + ascii_offset))
            else:
                result.append(char)
        return ''.join(result)
    
    def extract_meaningful_data(self, text):
        """Extract meaningful patterns from the decrypted text"""
        findings = {}
        
        # Clean printable text
        clean_text = ''.join(c for c in text if 32 <= ord(c) <= 126)
        findings['clean_text'] = clean_text
        
        # Look for URLs
        urls = re.findall(r'https?://[^\s]+|www\.[^\s]+', clean_text, re.IGNORECASE)
        if urls:
            findings['urls'] = urls
        
        # Look for Bitcoin addresses
        btc_addresses = re.findall(r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}', clean_text)
        if btc_addresses:
            findings['bitcoin_addresses'] = btc_addresses
        
        # Look for private keys (64 hex chars)
        private_keys = re.findall(r'[a-fA-F0-9]{64}', clean_text)
        if private_keys:
            findings['private_keys'] = private_keys
        
        # Look for Ethereum addresses
        eth_addresses = re.findall(r'0x[a-fA-F0-9]{40}', clean_text)
        if eth_addresses:
            findings['ethereum_addresses'] = eth_addresses
        
        # Look for Base58 patterns (wallet formats)
        base58_patterns = re.findall(r'[1-9A-HJ-NP-Za-km-z]{30,}', clean_text)
        if base58_patterns:
            findings['base58_patterns'] = base58_patterns
        
        # Look for mnemonic seed words
        potential_words = re.findall(r'\b[a-z]{3,8}\b', clean_text.lower())
        # Common BIP39 words
        bip39_sample = ['abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 
                       'abstract', 'absurd', 'abuse', 'access', 'accident', 'account', 
                       'accuse', 'achieve', 'acid', 'acoustic', 'acquire', 'across', 'act']
        found_bip39 = [word for word in potential_words if word in bip39_sample]
        if found_bip39:
            findings['potential_mnemonic_words'] = found_bip39
        
        # Look for coordinates
        coordinates = re.findall(r'(\d+°\d+\'\d+\.\d+"[NS])\s+(\d+°\d+\'\d+\.\d+"[EW])', clean_text)
        if coordinates:
            findings['coordinates'] = coordinates
        
        # Look for hidden messages in specific positions
        if len(clean_text) > 20:
            # Check first/last characters
            findings['first_10_chars'] = clean_text[:10]
            findings['last_10_chars'] = clean_text[-10:]
            
            # Check middle section
            mid = len(clean_text) // 2
            findings['middle_section'] = clean_text[mid-10:mid+10]
        
        return findings
    
    def try_alternative_interpretations(self, text):
        """Try alternative ways to interpret the text"""
        alternatives = {}
        
        # Try as Base64
        try:
            if len(text) % 4 == 0 and re.match(r'^[A-Za-z0-9+/]*={0,2}$', text):
                decoded = base64.b64decode(text)
                alternatives['base64_decode'] = decoded.decode('utf-8', errors='ignore')
        except:
            pass
        
        # Try reversing the string
        alternatives['reversed'] = text[::-1]
        
        # Try extracting every nth character
        for n in [2, 3, 4, 5]:
            nth_chars = ''.join(text[i] for i in range(0, len(text), n))
            if len(nth_chars) > 10:
                alternatives[f'every_{n}th_char'] = nth_chars
        
        # Try Caesar shifts on readable parts
        alpha_only = ''.join(c for c in text if c.isalpha())
        if len(alpha_only) > 10:
            for shift in [1, 7, 13, 25]:
                shifted = self.caesar_shift(alpha_only, shift)
                alternatives[f'caesar_shift_{shift}'] = shifted
        
        return alternatives
    
    def caesar_shift(self, text, shift):
        """Apply Caesar shift"""
        result = []
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                result.append(chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset))
            else:
                result.append(char)
        return ''.join(result)
    
    def comprehensive_extraction(self):
        """Run comprehensive extraction on all append variants"""
        print("🔍 FOCUSED DATA EXTRACTION - TARGETING HIGHEST READABILITY")
        print("=" * 70)
        
        all_findings = {}
        
        # Test all hex corrections with the best decryption path
        for append_char in "0123456789abcdefABCDEF":
            try:
                decrypted_text = self.get_best_decryption_path(append_char)
                findings = self.extract_meaningful_data(decrypted_text)
                alternatives = self.try_alternative_interpretations(findings['clean_text'])
                
                all_findings[append_char] = {
                    'decrypted_text': decrypted_text,
                    'findings': findings,
                    'alternatives': alternatives,
                    'readability': self.calculate_readability(decrypted_text)
                }
                
            except Exception as e:
                continue
        
        return all_findings
    
    def calculate_readability(self, text):
        """Calculate readability score"""
        if not text:
            return 0
        printable_chars = sum(1 for c in text if 32 <= ord(c) <= 126)
        return printable_chars / len(text)
    
    def display_best_results(self, all_findings):
        """Display the most promising results"""
        # Sort by readability
        sorted_findings = sorted(all_findings.items(), 
                               key=lambda x: x[1]['readability'], reverse=True)
        
        print(f"\n🎯 TOP EXTRACTION RESULTS")
        print("=" * 70)
        
        for i, (append_char, data) in enumerate(sorted_findings[:5]):
            print(f"\n🔍 RESULT #{i+1} (Append: {append_char}, Readability: {data['readability']:.1%})")
            
            findings = data['findings']
            
            # Show clean text
            clean_text = findings.get('clean_text', '')
            if clean_text:
                print(f"📝 Clean Text ({len(clean_text)} chars): {clean_text[:80]}...")
            
            # Show specific findings
            for key, value in findings.items():
                if key != 'clean_text' and value:
                    print(f"🔑 {key}: {value}")
            
            # Show promising alternatives
            alternatives = data['alternatives']
            for alt_name, alt_value in alternatives.items():
                if alt_value and len(str(alt_value)) > 5:
                    print(f"🔄 {alt_name}: {str(alt_value)[:60]}...")
            
            print("-" * 60)

def main():
    extractor = FocusedExtractor()
    findings = extractor.comprehensive_extraction()
    extractor.display_best_results(findings)

if __name__ == "__main__":
    main() 