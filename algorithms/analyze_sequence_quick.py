#!/usr/bin/env python3
"""
Quick Bitcoin Puzzle Sequence Transformation Analysis
Analyzes the first 10 positions with a focused set of formulas to identify transformation patterns.
"""

import sys

# Bitcoin secp256k1 parameters
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Base58 alphabet
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# Address string
FULL_STRING = "6PnU5voARjBBykwSddQCdcn6EvUfBh2vejdqisJGANpEm4HXVmVcaJBGrP8Sn7N54q46fBdpL3Jy4hMGPwF1s5xJ4xTLvWi76aP"

def analyze_quick_transformations(max_positions=10, verbose=True):
    """
    Quick analysis of Bitcoin sequence transformations for the first few positions.
    """
    print("\n===== QUICK SEQUENCE TRANSFORMATION ANALYSIS =====")
    
    # Read the verified sequence from file
    verified_keys = {}
    try:
        with open('verified_bitcoin_sequence.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or not line[0].isdigit():
                    continue
                parts = line.split('.', 1)
                if len(parts) != 2:
                    continue
                pos = int(parts[0])
                hex_and_status = parts[1].strip()
                if ' - ' in hex_and_status:
                    hex_key = hex_and_status.split(' - ')[0].strip()
                else:
                    hex_key = hex_and_status.strip()
                verified_keys[pos] = int(hex_key, 16)
                
                # Only load first max_positions for quick analysis
                if len(verified_keys) >= max_positions:
                    break
                
        print(f"Successfully loaded {len(verified_keys)} verified keys for quick analysis")
        
    except FileNotFoundError:
        print("Error: verified_bitcoin_sequence.txt not found")
        return {}
    except Exception as e:
        print(f"Error reading verified sequence: {e}")
        return {}
    
    if len(verified_keys) < 2:
        print("Need at least 2 keys to analyze transformations")
        return {}
    
    # Define focused set of formulas for quick analysis
    def get_focused_formulas():
        formulas = []
        
        # 1. Basic arithmetic operations (comprehensive)
        ops = [
            (lambda k,p,co,ci,v: (k + v) % N, "+"),
            (lambda k,p,co,ci,v: (k - v) % N, "-"), 
            (lambda k,p,co,ci,v: (k * v) % N, "*"),
            (lambda k,p,co,ci,v: (k ^ v) % N, "XOR"),
            (lambda k,p,co,ci,v: (k | v) % N, "OR"),
            (lambda k,p,co,ci,v: (k & v) % N, "AND"),
        ]
        
        # Test with constants 1-20, position, ASCII, B58idx
        for val in range(1, 21):
            for op, op_name in ops:
                formulas.append((lambda k,p,co,ci,v=val,o=op: o(k,p,co,ci,v), f"k {op_name} {val}"))
        
        # With position
        for op, op_name in ops:
            formulas.append((lambda k,p,co,ci,o=op: o(k,p,co,ci,p), f"k {op_name} pos"))
        
        # With character values
        for op, op_name in ops:
            formulas.extend([
                (lambda k,p,co,ci,o=op: o(k,p,co,ci,co) if co else None, f"k {op_name} ASCII"),
                (lambda k,p,co,ci,o=op: o(k,p,co,ci,ci) if ci != -1 else None, f"k {op_name} B58idx")
            ])
        
        # 2. Powers and exponentials (comprehensive)
        bases = [2, 3, 5, 7, 11, 13]
        for base in bases:
            for exp in range(1, 11):
                power = pow(base, exp, N)
                for op, op_name in ops:
                    formulas.append((lambda k,p,co,ci,v=power,o=op: o(k,p,co,ci,v), f"k {op_name} {base}^{exp}"))
        
        # 3. Bit manipulation (comprehensive)
        for shift in range(1, 33):
            formulas.extend([
                (lambda k,p,co,ci,s=shift: (k << s) % N, f"k << {shift}"),
                (lambda k,p,co,ci,s=shift: (k >> s) % N, f"k >> {shift}"),
                (lambda k,p,co,ci,s=shift: ((k << s) | (k >> (32-s))) % N, f"ROL({shift})"),
                (lambda k,p,co,ci,s=shift: ((k >> s) | (k << (32-s))) % N, f"ROR({shift})"),
            ])
        
        # 4. Multi-parameter combinations 
        for a in range(1, 6):
            for b in range(1, 6):
                formulas.extend([
                    (lambda k,p,co,ci,A=a,B=b: (A*k + B*p) % N, str(a) + "k + " + str(b) + "p"),
                    (lambda k,p,co,ci,A=a,B=b: (A*k - B*p) % N, str(a) + "k - " + str(b) + "p"),
                    (lambda k,p,co,ci,A=a,B=b: (A*k * B*p) % N, str(a) + "k * " + str(b) + "p"),
                    (lambda k,p,co,ci,A=a,B=b: (A*k ^ B*p) % N, str(a) + "k XOR " + str(b) + "p"),
                ])
        
        # 5. Polynomial operations
        for a in range(1, 4):
            for b in range(1, 4):
                for c in range(0, 3):
                    formulas.extend([
                        (lambda k,p,co,ci,A=a,B=b,C=c: (A*k*k + B*k + C) % N, str(a) + "k² + " + str(b) + "k + " + str(c)),
                        (lambda k,p,co,ci,A=a,B=b,C=c: (A*k + B*p*p + C) % N, str(a) + "k + " + str(b) + "p² + " + str(c)),
                    ])
        
        # 6. Three-way combinations with characters
        for a in range(1, 4):
            for b in range(1, 4):
                for c in range(1, 4):
                    formulas.extend([
                        (lambda k,p,co,ci,A=a,B=b,C=c: (k*A + p*B + (co or 0)*C) % N if co else None, 
                         "k*" + str(a) + " + p*" + str(b) + " + ASCII*" + str(c)),
                        (lambda k,p,co,ci,A=a,B=b,C=c: (k*A + p*B + ci*C) % N if ci != -1 else None,
                         "k*" + str(a) + " + p*" + str(b) + " + B58*" + str(c)),
                    ])
        
        # 7. Cryptographic constants
        crypto_constants = [
            0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476,  # MD5
            0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6,  # SHA-1
            0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5,  # SHA-256
        ]
        for i, const in enumerate(crypto_constants):
            for op, op_name in ops:
                formulas.append((lambda k,p,co,ci,v=const,o=op: o(k,p,co,ci,v), "k " + op_name + " C" + str(i)))
        
        # 8. Prime operations
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        for prime in primes:
            for op, op_name in ops:
                formulas.extend([
                    (lambda k,p,co,ci,pr=prime,o=op: o(k,p,co,ci,pr), "k " + op_name + " P(" + str(prime) + ")"),
                    (lambda k,p,co,ci,pr=prime: (k + p*pr) % N, "k + pos*P(" + str(prime) + ")"),
                ])
        
        # 9. Fibonacci sequence
        fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
        for i, f in enumerate(fib):
            for op, op_name in ops:
                formulas.append((lambda k,p,co,ci,v=f,o=op: o(k,p,co,ci,v), "k " + op_name + " F(" + str(i) + ")"))
        
        # 10. Elliptic curve parameters
        ec_params = [Gx, Gy, N, P]
        param_names = ["Gx", "Gy", "N", "P"]
        for param, name in zip(ec_params, param_names):
            for op, op_name in ops:
                formulas.append((lambda k,p,co,ci,v=param,o=op: o(k,p,co,ci,v), "k " + op_name + " " + name))
        
        # 11. Multi-parameter combinations
        for op1, op1_name in ops[:4]:  # Limit to avoid explosion
            for op2, op2_name in ops[:4]:
                formulas.extend([
                    (lambda k,p,co,ci,o1=op1,o2=op2: o2(k,p,co,ci,o1(k,p,co,ci,2)), "(" + op1_name + "2) " + op2_name + " k"),
                    (lambda k,p,co,ci,o1=op1,o2=op2: o1(k,p,co,ci,o2(k,p,co,ci,p)), op1_name + " " + op2_name + " pos"),
                ])
        
        # 12. Mask operations
        masks = [0xFF, 0xFFFF, 0xFFFFFF, 0xFFFFFFFF, 0x55555555, 0xAAAAAAAA, 0x33333333, 0xCCCCCCCC]
        for mask in masks:
            formulas.extend([
                (lambda k,p,co,ci,m=mask: (k & m) % N, "k & 0x" + hex(mask)[2:].upper()),
                (lambda k,p,co,ci,m=mask: (k | m) % N, "k | 0x" + hex(mask)[2:].upper()),
                (lambda k,p,co,ci,m=mask: (k ^ m) % N, "k ^ 0x" + hex(mask)[2:].upper()),
            ])
        
        # 13. Sequential combinations (if we had previous keys)
        # Note: In quick analysis, we don't have full history, but we can simulate
        for offset in range(1, 4):
            formulas.extend([
                (lambda k,p,co,ci,off=offset: (k + off) % N, "k + simulated_key[pos-" + str(offset) + "]"),
                (lambda k,p,co,ci,off=offset: (k * off) % N, "k * simulated_key[pos-" + str(offset) + "]"),
                (lambda k,p,co,ci,off=offset: (k ^ off) % N, "k XOR simulated_key[pos-" + str(offset) + "]"),
            ])
        
        # 14. Advanced mathematical functions
        formulas.extend([
            # Modular inverse (when possible)
            (lambda k,p,co,ci: pow(k, N-2, N) if k != 0 else None, "k⁻¹"),
            # Square root mod N (when N ≡ 3 mod 4)
            (lambda k,p,co,ci: pow(k, (N+1)//4, N) if (N % 4) == 3 else None, "√k"),
            # Quadratic residue
            (lambda k,p,co,ci: (k*k) % N, "k²"),
            (lambda k,p,co,ci: (k*k*k) % N, "k³"),
            # Combined with position
            (lambda k,p,co,ci: (k*k + p) % N, "k² + pos"),
            (lambda k,p,co,ci: (k*k + p*p) % N, "k² + pos²"),
            (lambda k,p,co,ci: (k*k - p*p) % N, "k² - pos²"),
            (lambda k,p,co,ci: (k + p*p) % N, "k + pos²"),
        ])
        
        return formulas
    
    formulas = get_focused_formulas()
    print(f"Testing {len(formulas)} focused formulas against verified sequence...")
    
    # Store transformation results
    transformation_results = {}
    successful_transformations = {}
    
    # Analyze each transition
    sorted_positions = sorted(verified_keys.keys())
    
    for i in range(len(sorted_positions) - 1):
        pos_current = sorted_positions[i]
        pos_next = sorted_positions[i + 1]
        
        if pos_next != pos_current + 1:
            if verbose:
                print(f"Skipping non-consecutive transition: {pos_current} → {pos_next}")
            continue
            
        key_current = verified_keys[pos_current]
        key_next = verified_keys[pos_next]
        
        if verbose:
            print(f"\n--- Analyzing position {pos_current} → {pos_next} ---")
            print(f"Key[{pos_current}] = 0x{key_current:x}")
            print(f"Key[{pos_next}] = 0x{key_next:x}")
        
        # Get character information for this transition (0-based indexing)
        char_for_pos = FULL_STRING[pos_current-1] if (pos_current-1) >= 0 and (pos_current-1) < len(FULL_STRING) else None
        char_ord_for_pos = ord(char_for_pos) if char_for_pos else None
        char_idx_for_pos = BASE58_ALPHABET.index(char_for_pos) if char_for_pos and char_for_pos in BASE58_ALPHABET else -1
        
        if verbose and char_for_pos:
            print(f"Character: '{char_for_pos}' (ASCII: {char_ord_for_pos}, B58_idx: {char_idx_for_pos})")
        
        # Test all formulas for this transition
        matching_formulas = []
        
        for formula_lambda, formula_desc in formulas:
            try:
                predicted_key = formula_lambda(key_current, pos_next, char_ord_for_pos, char_idx_for_pos)
                if predicted_key is not None:
                    predicted_key %= N
                    if predicted_key == key_next:
                        matching_formulas.append(formula_desc)
                        if verbose:
                            print(f"  ✓ MATCH: {formula_desc}")
            except Exception as e:
                # Silently skip formulas that cause errors
                continue
        
        if matching_formulas:
            successful_transformations[pos_next] = matching_formulas
            if verbose:
                print(f"  Found {len(matching_formulas)} matching transformations")
        else:
            if verbose:
                print(f"  ❌ NO TRANSFORMATIONS FOUND")
        
        transformation_results[pos_next] = {
            'from_key': key_current,
            'to_key': key_next,
            'character': char_for_pos,
            'ascii': char_ord_for_pos,
            'b58_idx': char_idx_for_pos,
            'matching_formulas': matching_formulas
        }
        
        # Stop if we've reached max_positions
        if pos_next >= max_positions:
            break
    
    # Summary report
    print(f"\n===== TRANSFORMATION SUMMARY =====")
    print(f"Analyzed {len(transformation_results)} transitions")
    print(f"Found transformations for {len(successful_transformations)} positions")
    
    # Group by transformation type
    formula_usage = {}
    for pos, formulas_list in successful_transformations.items():
        for formula in formulas_list:
            if formula not in formula_usage:
                formula_usage[formula] = []
            formula_usage[formula].append(pos)
    
    if formula_usage:
        print(f"\n--- Most Common Transformations ---")
        sorted_formulas = sorted(formula_usage.items(), key=lambda x: len(x[1]), reverse=True)
        
        for formula, positions in sorted_formulas[:10]:  # Top 10
            print(f"  '{formula}': used {len(positions)} times at positions {positions}")
    
    # Check for position-specific patterns
    print(f"\n--- Position-Specific Analysis ---")
    for pos in range(2, max_positions + 1):
        if pos in successful_transformations:
            formula_count = len(successful_transformations[pos])
            formulas_str = ", ".join(successful_transformations[pos][:3])
            if formula_count > 3:
                formulas_str += f"... (and {formula_count-3} more)"
            print(f"  Position {pos}: {formula_count} formulas → {formulas_str}")
        else:
            print(f"  Position {pos}: NO TRANSFORMATIONS FOUND")
    
    return transformation_results

# Main execution
if __name__ == "__main__":
    analyze_quick_transformations(max_positions=10, verbose=True) 