#!/usr/bin/python3

import hashlib
from typing import List, Tuple
import numpy as np
import os

# secp256k1 curve parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
A = 0
B = 7

def is_quadratic_residue(x: int, p: int) -> bool:
    """Check if x is a quadratic residue modulo p"""
    return pow(x, (p - 1) // 2, p) == 1

def analyze_curve_properties(hex_sequence: List[str]) -> dict:
    """
    Analyze sequence for properties relevant to secp256k1
    - Point candidates
    - Field element properties
    - Order relationships
    """
    results = []
    for hex_str in hex_sequence:
        num = int(hex_str, 16)
        
        # Check if number could be a valid x-coordinate
        x = num % P
        y_square = (pow(x, 3, P) + B) % P
        is_point = is_quadratic_residue(y_square, P)
        
        # Check relationship with curve order
        order_residue = num % N
        
        # Field analysis
        field_properties = {
            'is_field_element': num < P,
            'could_be_point': is_point,
            'order_residue': order_residue,
            'potential_private_key': num < N
        }
        results.append(field_properties)
    
    return {
        'curve_points': results,
        'field_properties': analyze_field_properties(hex_sequence)
    }

def analyze_field_properties(hex_sequence: List[str]) -> dict:
    """Analyze properties in the context of the finite field"""
    numbers = [int(h, 16) for h in hex_sequence]
    
    # Field arithmetic patterns
    field_elements = [n % P for n in numbers]
    
    # Look for multiplicative relationships in the field
    field_products = [(field_elements[i] * field_elements[i+1]) % P 
                     for i in range(len(field_elements)-1)]
    
    # Check for potential curve points
    curve_properties = {
        'potential_x_coords': sum(1 for x in field_elements 
                                if is_quadratic_residue((pow(x, 3, P) + B) % P, P)),
        'field_elements': sum(1 for n in numbers if n < P),
        'potential_scalars': sum(1 for n in numbers if n < N)
    }
    
    return {
        'field_patterns': field_products[:10],  # First 10 field products
        'curve_properties': curve_properties
    }

def main():
    """Main analysis function"""
    # Get the absolute path to the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    # Try multiple possible data locations
    possible_paths = [
        os.path.join(project_root, 'data', '32bHex.txt'),
        os.path.join(current_dir, '..', 'data', '32bHex.txt'),
        os.path.join(current_dir, 'data', '32bHex.txt'),
        './data/32bHex.txt',
        '../data/32bHex.txt'
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
    
    if not file_path:
        print("Error: Could not find 32bHex.txt in any of these locations:")
        for path in possible_paths:
            print(f"- {os.path.abspath(path)}")
        print("\nPlease ensure the file exists in one of these locations")
        return
    
    try:
        with open(file_path, 'r') as f:
            hex_strings = [line.strip() for line in f if line.strip()]
        
        analysis = analyze_curve_properties(hex_strings)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(file_path), '..', 'output', 'elliptic_curves')
        os.makedirs(output_dir, exist_ok=True)
        
        # Write results
        output_path = os.path.join(output_dir, 'secp256k1_analysis.txt')
        with open(output_path, 'w') as f:
            f.write("secp256k1 Curve Analysis\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("Potential Curve Points:\n")
            f.write("-" * 40 + "\n")
            for i, result in enumerate(analysis['curve_points']):
                f.write(f"\nString {i+1}:\n")
                f.write(f"Valid field element: {result['is_field_element']}\n")
                f.write(f"Could be x-coordinate: {result['could_be_point']}\n")
                f.write(f"Order residue: {result['order_residue']:#x}\n")
                f.write(f"Valid private key: {result['potential_private_key']}\n")
            
            f.write("\nField Properties:\n")
            f.write("-" * 40 + "\n")
            props = analysis['field_properties']['curve_properties']
            f.write(f"Potential x-coordinates: {props['potential_x_coords']}\n")
            f.write(f"Valid field elements: {props['field_elements']}\n")
            f.write(f"Potential scalar multipliers: {props['potential_scalars']}\n")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    main() 