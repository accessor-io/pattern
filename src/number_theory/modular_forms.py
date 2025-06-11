#!/usr/bin/python3

import numpy as np
from typing import List, Dict
from sympy import isprime, factorint, mod_inverse, legendre_symbol
import math
import os

def analyze_modular_properties(hex_sequence: List[str]) -> dict:
    """
    Analyze sequence for properties relevant to modular forms
    - Weight and level analysis
    - Fourier coefficients
    - Hecke eigenvalues
    - Atkin-Lehner eigenvalues
    """
    numbers = [int(h, 16) for h in hex_sequence]
    
    # Analyze modular properties
    results = []
    for num in numbers:
        # Analyze potential weights
        weights = analyze_weights(num)
        
        # Analyze potential levels
        levels = analyze_levels(num)
        
        # Check Fourier coefficient properties
        fourier_props = analyze_fourier_properties(num)
        
        # Analyze Hecke operator eigenvalues
        hecke_props = analyze_hecke_eigenvalues(num)
        
        result = {
            'weight_analysis': weights,
            'level_candidates': levels,
            'fourier_properties': fourier_props,
            'hecke_properties': hecke_props
        }
        results.append(result)
    
    return {
        'modular_properties': results,
        'sequence_properties': analyze_sequence_modular_properties(numbers)
    }

def analyze_weights(n: int) -> dict:
    """Analyze potential weights for the modular form"""
    # Check for holomorphic weight patterns
    holomorphic = n % 2 == 0 and n >= 0
    
    # Check for half-integral weight patterns
    half_integral = bool(n & 1)
    
    # Estimate weight bounds based on growth
    max_weight = math.floor(math.log2(abs(n) + 1))
    
    return {
        'holomorphic': holomorphic,
        'half_integral': half_integral,
        'estimated_max_weight': max_weight,
        'weight_parity': 'even' if n % 2 == 0 else 'odd'
    }

def analyze_levels(n: int) -> dict:
    """Analyze potential levels for the modular form"""
    # Find prime factors for level candidates
    try:
        factors = factorint(n, limit=1000)
    except:
        factors = {}
    
    # Check for square-free level candidates
    square_free_candidates = [p for p in factors if factors[p] == 1]
    
    # Check for conductor-like properties
    conductor_like = len(square_free_candidates) > 0
    
    return {
        'prime_factors': factors,
        'square_free_candidates': square_free_candidates,
        'conductor_like': conductor_like,
        'min_possible_level': min(square_free_candidates) if square_free_candidates else None
    }

def analyze_fourier_properties(n: int) -> dict:
    """Analyze Fourier coefficient properties"""
    # Check for Ramanujan bounds
    ramanujan_bound = abs(n) <= 2 * math.sqrt(n) if n > 0 else False
    
    # Check for multiplicative properties
    multiplicative = True
    for p in range(2, min(20, int(math.sqrt(abs(n))) + 1)):
        if isprime(p):
            if n % p == 0 and n % (p*p) != 0:
                multiplicative = False
                break
    
    # Check for potential CM properties (using only odd primes)
    potential_cm = all(legendre_symbol(n, p) in [-1, 0, 1] 
                      for p in [3, 5, 7, 11, 13] if n % p != 0)
    
    return {
        'satisfies_ramanujan': ramanujan_bound,
        'multiplicative': multiplicative,
        'potential_cm': potential_cm
    }

def analyze_hecke_eigenvalues(n: int) -> dict:
    """Analyze potential Hecke eigenvalue properties"""
    # Check basic Hecke operator properties
    small_primes = [p for p in range(2, 20) if isprime(p)]
    hecke_compatible = True
    
    for p in small_primes:
        if n % p == 0:
            # Check p-adic valuation
            val_p = 0
            temp_n = n
            while temp_n % p == 0:
                val_p += 1
                temp_n //= p
            if val_p > 2:  # Hecke eigenvalues typically have valuation ≤ 2
                hecke_compatible = False
                break
    
    # Check for potential newform properties
    potential_newform = hecke_compatible and n != 0
    
    # Estimate petersson norm
    petersson_estimate = math.sqrt(abs(n)) if n != 0 else 0
    
    return {
        'hecke_compatible': hecke_compatible,
        'potential_newform': potential_newform,
        'petersson_estimate': petersson_estimate
    }

def analyze_sequence_modular_properties(numbers: List[int]) -> dict:
    """Analyze modular properties of the sequence as a whole"""
    # Analyze level compatibility
    common_level_factors = set()
    for n in numbers:
        try:
            factors = set(factorint(n, limit=1000).keys())
            if not common_level_factors:
                common_level_factors = factors
            else:
                common_level_factors &= factors
        except:
            continue
    
    # Look for weight consistency
    weight_parities = [n % 2 for n in numbers]
    consistent_parity = len(set(weight_parities)) == 1
    
    # Check for Hecke relations
    hecke_relations = []
    for i in range(len(numbers)-2):
        # Check T_p relations for small p
        for p in [2, 3, 5]:
            if numbers[i] != 0 and numbers[i+1] != 0:
                expected = numbers[i] * numbers[i+1]
                actual = numbers[i+2] * p
                if expected == actual:
                    hecke_relations.append((i, i+1, i+2, p))
    
    return {
        'common_level_factors': list(common_level_factors),
        'consistent_weight_parity': consistent_parity,
        'hecke_relations': hecke_relations[:5],  # First 5 relations
        'potential_basis': len(set(numbers)) == len(numbers)  # Check for linear independence
    }

def main():
    """Main analysis function"""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, 'data', '32bHex.txt')
    
    try:
        with open(file_path, 'r') as f:
            hex_strings = [line.strip() for line in f if line.strip()]
        
        analysis = analyze_modular_properties(hex_strings)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(project_root, 'output', 'number_theory')
        os.makedirs(output_dir, exist_ok=True)
        
        # Write results
        output_file = os.path.join(output_dir, 'modular_analysis.txt')
        with open(output_file, 'w') as f:
            f.write("Modular Forms Analysis\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("Individual Form Properties:\n")
            f.write("-" * 40 + "\n")
            for i, result in enumerate(analysis['modular_properties']):
                f.write(f"\nForm {i+1}:\n")
                f.write("Weight Analysis:\n")
                for k, v in result['weight_analysis'].items():
                    f.write(f"  {k}: {v}\n")
                    
                f.write("\nLevel Analysis:\n")
                for k, v in result['level_candidates'].items():
                    f.write(f"  {k}: {v}\n")
                    
                f.write("\nFourier Properties:\n")
                for k, v in result['fourier_properties'].items():
                    f.write(f"  {k}: {v}\n")
                    
                f.write("\nHecke Properties:\n")
                for k, v in result['hecke_properties'].items():
                    f.write(f"  {k}: {v}\n")
            
            f.write("\nSequence Properties:\n")
            f.write("-" * 40 + "\n")
            seq_props = analysis['sequence_properties']
            
            f.write("\nCommon Structure:\n")
            f.write(f"Common level factors: {seq_props['common_level_factors']}\n")
            f.write(f"Consistent weight parity: {seq_props['consistent_weight_parity']}\n")
            f.write(f"Potential basis: {seq_props['potential_basis']}\n")
            
            f.write("\nHecke Relations:\n")
            for rel in seq_props['hecke_relations']:
                f.write(f"T_{rel[3]} relation between forms {rel[0]+1}, {rel[1]+1}, {rel[2]+1}\n")
    
    except FileNotFoundError:
        print(f"Error: Could not find file at {file_path}")
        print("Please ensure your file exists at this location")

if __name__ == "__main__":
    main() 