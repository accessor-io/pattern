#!/usr/bin/env python3
"""
Complete Decryption Analysis Script
Following the 4-step process: Hex->Bytes, XOR, Vigenère, ROT47
"""

import base64

def process_all_variants():
    """Process all possible corrections to the hex string through the complete decryption pipeline"""
    
    # Original hex string with the problematic chunk
    base_hex = "925f94cd6e13cb4fa50400050664458b371cc56a324b4d1e38e27305badbef1582c32d061820081b6f1172c9937f4eafd7cb7d2f2e4b2f95e23beafd2197e"
    
    # Test all possible appends to fix the incomplete hex
    hex_chars = "0123456789abcdefABCDEF"
    results = []
    
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
            
            results.append({
                'append_char': append_char,
                'corrected_hex': corrected_hex,
                'xor_result': xor_text,
                'vigenere_result': vigenere_decrypted,
                'final_result': final_output,
                'readable_chars': count_readable_chars(final_output)
            })
            
        except Exception as e:
            print(f"Error with append char '{append_char}': {e}")
            continue
    
    return results

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

def count_readable_chars(text):
    """Count readable ASCII characters"""
    return sum(1 for char in text if 32 <= ord(char) <= 126)

def analyze_results(results):
    """Analyze all results to find the most promising ones"""
    print("=== DECRYPTION ANALYSIS RESULTS ===\n")
    
    # Sort by readability score
    sorted_results = sorted(results, key=lambda x: x['readable_chars'], reverse=True)
    
    for i, result in enumerate(sorted_results[:5]):  # Show top 5
        print(f"Rank {i+1}: Append char '{result['append_char']}'")
        print(f"Readable chars: {result['readable_chars']}/{len(result['final_result'])}")
        print(f"Final result: {repr(result['final_result'][:100])}...")
        print("-" * 60)
    
    # Check for specific patterns
    print("\n=== PATTERN ANALYSIS ===")
    for result in results:
        final = result['final_result']
        
        # Check for URLs
        if 'http' in final.lower() or 'www.' in final.lower():
            print(f"URL pattern found with append '{result['append_char']}': {final}")
        
        # Check for Bitcoin addresses
        if any(final.startswith(prefix) for prefix in ['1', '3', 'bc1']):
            print(f"Potential Bitcoin address with append '{result['append_char']}': {final}")
        
        # Check for base64-like patterns
        if len([c for c in final if c.isalnum() or c in '+/=']) > len(final) * 0.8:
            print(f"Base64-like pattern with append '{result['append_char']}': {final}")

def main():
    """Main execution function"""
    print("Starting comprehensive decryption analysis...")
    print("Processing all possible hex string corrections...\n")
    
    results = process_all_variants()
    analyze_results(results)
    
    # Save detailed results
    with open('decryption_results.txt', 'w') as f:
        for result in results:
            f.write(f"Append: {result['append_char']}\n")
            f.write(f"Final: {result['final_result']}\n")
            f.write(f"Readable: {result['readable_chars']}\n")
            f.write("-" * 50 + "\n")
    
    print(f"\nProcessed {len(results)} variants.")
    print("Detailed results saved to 'decryption_results.txt'")

if __name__ == "__main__":
    main() 