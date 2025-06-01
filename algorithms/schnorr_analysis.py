#!/usr/bin/python3

import hashlib
import hmac
from typing import List, Tuple
import numpy as np
import os

def analyze_schnorr_properties(hex_sequence: List[str]) -> dict:
    """
    Analyze sequence for properties relevant to Schnorr signatures
    - Point generation patterns
    - Nonce candidates
    - Challenge-response patterns
    """
    results = []
    for hex_str in hex_sequence:
        num = int(hex_str, 16)
        binary = bin(num)[2:].zfill(256)
        
        # Check for potential nonce patterns
        nonce_entropy = sum(int(b) for b in binary) / len(binary)
        
        # Look for potential public key patterns
        potential_pubkey = bool(num % 2)  # Check if could be x-coordinate
        
        # Analyze for potential signature components
        sig_component_analysis = {
            'potential_r': num < 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
            'entropy_bits': nonce_entropy,
            'potential_pubkey': potential_pubkey
        }
        results.append(sig_component_analysis)
    
    return {
        'signature_components': results,
        'sequence_properties': analyze_sequence_properties(hex_sequence)
    }

def analyze_sequence_properties(hex_sequence: List[str]) -> dict:
    """Analyze mathematical properties relevant to signature schemes"""
    numbers = [int(h, 16) for h in hex_sequence]
    
    # Look for multiplicative relationships
    products = [numbers[i] * numbers[i+1] for i in range(len(numbers)-1)]
    
    # Check for potential ECDSA/Schnorr patterns
    potential_patterns = {
        'possible_nonces': sum(1 for n in numbers if n < 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141),
        'low_entropy_values': sum(1 for n in numbers if bin(n).count('1') < 128),
        'potential_pubkeys': sum(1 for n in numbers if n % 2 == 1)  # Odd numbers could be x-coordinates
    }
    
    return {
        'multiplicative_patterns': products[:10],  # First 10 products
        'signature_patterns': potential_patterns
    }

def main():
    """Main analysis function"""
    try:
        # First try original path
        file_path = '../data/32bHex.txt'
        if not os.path.exists(file_path):
            # Create directory if it doesn't exist
            os.makedirs('../data', exist_ok=True)
            # Move/copy your hex file to the correct location
            # You'll need to do this manually
            print(f"Please place your hex file at: {os.path.abspath(file_path)}")
            return
        
        with open(file_path, 'r') as f:
            hex_strings = [line.strip() for line in f if line.strip()]
        
        analysis = analyze_schnorr_properties(hex_strings)
        
        # Write results
        with open('../output/bitcoin_math/schnorr_analysis.txt', 'w') as f:
            f.write("Schnorr Signature Component Analysis\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("Potential Signature Components:\n")
            f.write("-" * 40 + "\n")
            for i, result in enumerate(analysis['signature_components']):
                f.write(f"\nString {i+1}:\n")
                f.write(f"Potential r value: {result['potential_r']}\n")
                f.write(f"Entropy bits: {result['entropy_bits']:.4f}\n")
                f.write(f"Could be pubkey: {result['potential_pubkey']}\n")
            
            f.write("\nSequence Properties:\n")
            f.write("-" * 40 + "\n")
            props = analysis['sequence_properties']
            f.write(f"Possible nonces: {props['signature_patterns']['possible_nonces']}\n")
            f.write(f"Low entropy values: {props['signature_patterns']['low_entropy_values']}\n")
            f.write(f"Potential pubkeys: {props['signature_patterns']['potential_pubkeys']}\n")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 