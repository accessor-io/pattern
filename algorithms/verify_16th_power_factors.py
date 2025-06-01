#!/usr/bin/env python3
"""Verify 16th power pattern and factorization of predicted keys"""

def factorize(n):
    """Simple prime factorization"""
    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
        if d * d > n:
            if n > 1:
                factors.append(n)
            break
    return factors

def analyze_16th_power(hex_key):
    """Analyze if number follows 16th power pattern"""
    # Convert hex to decimal
    decimal = int(hex_key, 16)
    
    # Count trailing zeros in hex (should be multiple of 4 for 16th powers)
    trailing_zeros = len(hex_key) - len(hex_key.rstrip('0'))
    
    # Check if number can be expressed as sum of 16th powers
    coefficients = []
    remaining = decimal
    power = len(hex_key) - 2  # Subtract '0x' prefix
    
    while remaining > 0 and power >= 0:
        coef = remaining // (16 ** power)
        if coef > 0:
            coefficients.append((coef, power))
            remaining -= coef * (16 ** power)
        power -= 1
    
    return {
        'decimal': decimal,
        'trailing_zeros': trailing_zeros,
        'coefficients': coefficients,
        'is_16th_power_sum': remaining == 0,
        'factors': factorize(decimal)
    }

def main():
    # Predicted keys for positions 71-75
    predictions = {
        71: '0x68f5c28f5c28f60000',
        72: '0xcccccccccccccc0000',
        73: '0x19eb851eb851eb80000',
        74: '0x347ae147ae147b00000',
        75: '0x4c5a1cac08312700000'
    }
    
    print("ANALYZING 16TH POWER PATTERNS AND FACTORIZATION")
    print("=" * 60)
    
    for pos, hex_key in predictions.items():
        print(f"\nPosition {pos}: {hex_key}")
        analysis = analyze_16th_power(hex_key)
        
        print("Decimal:", analysis['decimal'])
        print("Trailing zeros (hex):", analysis['trailing_zeros'])
        print("\n16th Power Decomposition:")
        for coef, power in analysis['coefficients']:
            print(f"  {coef} × 16^{power}")
        
        print("\nPrime Factorization:")
        factors = analysis['factors']
        factor_counts = {}
        for f in factors:
            factor_counts[f] = factor_counts.get(f, 0) + 1
            
        factor_str = ' × '.join([f"{f}^{c}" if c > 1 else str(f) 
                               for f, c in factor_counts.items()])
        print(f"  {factor_str}")
        
        # Verify pattern matches previous terms
        print("\nPattern Analysis:")
        print(f"Multiple of 16: {'Yes' if analysis['decimal'] % 16 == 0 else 'No'}")
        print(f"Follows 16th power sum: {'Yes' if analysis['is_16th_power_sum'] else 'No'}")
        print(f"Common factors with previous terms: 2, 3, 5, 7 present: " +
              f"{'Yes' if all(x in factors for x in [2,3,5,7]) else 'No'}")
        
        print("-" * 60)

if __name__ == "__main__":
    main() 