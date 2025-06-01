#!/usr/bin/env python3
from key_sequence_generator import (
    analyze_transitions,
    analyze_sequence_transformations,
    analyze_special_operations,
    analyze_differences_between_known_keys,
    analyze_known_transitions,
    check_transition_formulas,
    pubkey_to_address
)

def verify_key(private_key_int, target_address):
    """Verify if a private key generates the target address"""
    try:
        # Convert private key to hex
        privkey_hex = format(private_key_int, '064x')
        # Generate address
        address = pubkey_to_address(bytes.fromhex(privkey_hex))
        print(f"Generated address: {address}")
        return address == target_address
    except Exception as e:
        print(f"Error verifying key: {e}")
        return False

def get_prime_factors(n):
    """Get prime factors of a number"""
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

def analyze_position_71():
    print("=== Direct Analysis of Position 71 ===")
    
    # Known sequence with hex values
    SEQUENCE = {
        64: 0x18e186a0b4c7594d,
        65: 0x13a52c20c7e93900,
        66: 0x1368d75b7a31a9b9,
        67: 0x1b728d02d6dfe00d,
        68: 0x1f685e68d87bb9fb,
        69: 0x17d7672819a1f82922,
        70: 0x349b84b6431a6c4ef1,  # This is 33,201,509 in decimal
        71: None,  # Target to find
        72: 0xd26e12d90c69b13bcb
    }
    
    TARGET_71 = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
    
    # Analyze hex power breakdown of key_70 (similar to image)
    key_70 = SEQUENCE[70]
    hex_str = format(key_70, 'x')
    print("\nAnalyzing hex power breakdown of position 70:")
    print(f"Hex: 0x{hex_str}")
    print(f"Decimal: {key_70}")
    
    # Break down into powers of 16 (similar to image pattern)
    powers = []
    remaining = key_70
    for i in range(8, -1, -1):  # From 16^8 down to 16^0
        power = 16 ** i
        coefficient = remaining // power
        if coefficient > 0:
            powers.append((coefficient, i))
            remaining %= power
    
    print("\nPower breakdown:")
    total = 0
    for coef, power in powers:
        value = coef * (16 ** power)
        total += value
        print(f"{coef} × 16^{power} = {coef} × {16 ** power} = {value}")
    print(f"Total: {total}")
    
    # Get prime factors of key_70 and its components
    factors_70 = get_prime_factors(key_70)
    print("\nPrime factorization of position 70:")
    print(f"Factors: {factors_70}")
    
    # Get prime factors of each coefficient
    coef_factors = []
    for coef, _ in powers:
        factors = get_prime_factors(coef)
        coef_factors.append(factors)
    print("\nPrime factors of coefficients:")
    for i, (coef, _) in enumerate(powers):
        print(f"Coefficient {coef}: {coef_factors[i]}")
    
    # Try patterns based on prime factorization
    candidates = []
    
    # Pattern 1: Based on prime factor relationships in image
    # The image shows numbers being factored as products of small primes
    new_coeffs = []
    for factors in coef_factors:
        # Take product of smallest prime factors
        small_primes = [p for p in factors if p < 16]
        if small_primes:
            product = 1
            for p in small_primes[:3]:  # Use up to 3 smallest primes
                product = (product * p) % 16
            new_coeffs.append(product)
        else:
            new_coeffs.append(1)
    value = sum(c * (16 ** p[1]) for c, p in zip(new_coeffs, powers))
    candidates.append((value, "small_primes_pattern"))
    
    # Pattern 2: Based on prime factor counts
    # The image shows numbers with specific counts of each prime factor
    new_coeffs = []
    for factors in coef_factors:
        # Count occurrences of each prime
        prime_counts = {}
        for p in factors:
            prime_counts[p] = prime_counts.get(p, 0) + 1
        # Use count of most frequent prime
        max_count = max(prime_counts.values()) if prime_counts else 1
        new_coeffs.append(max_count % 16)
    value = sum(c * (16 ** p[1]) for c, p in zip(new_coeffs, powers))
    candidates.append((value, "prime_count_pattern"))
    
    # Pattern 3: Based on prime gaps
    # Look at gaps between consecutive primes in factorization
    new_coeffs = []
    for factors in coef_factors:
        if len(factors) > 1:
            # Calculate gaps between consecutive primes
            gaps = [factors[i+1] - factors[i] for i in range(len(factors)-1)]
            gap_sum = sum(gaps) % 16
            new_coeffs.append(gap_sum)
        else:
            new_coeffs.append(factors[0] % 16 if factors else 0)
    value = sum(c * (16 ** p[1]) for c, p in zip(new_coeffs, powers))
    candidates.append((value, "prime_gap_pattern"))
    
    # Pattern 4: Based on position-relative prime factors
    # Use position 71 in relation to prime factors
    new_coeffs = []
    for factors in coef_factors:
        if factors:
            # Combine position with prime factors
            val = 1
            for p in factors[:2]:  # Use first two prime factors
                val = (val * ((p + 71) % 16)) % 16
            new_coeffs.append(val)
        else:
            new_coeffs.append(71 % 16)
    value = sum(c * (16 ** p[1]) for c, p in zip(new_coeffs, powers))
    candidates.append((value, "pos_prime_pattern"))
    
    # Pattern 5: Based on prime factor sums
    # The image shows relationships between sums of prime factors
    new_coeffs = []
    total_sum = sum(sum(f) for f in coef_factors) % 16
    for factors in coef_factors:
        factor_sum = sum(factors) % 16
        new_val = (factor_sum * total_sum) % 16
        new_coeffs.append(new_val)
    value = sum(c * (16 ** p[1]) for c, p in zip(new_coeffs, powers))
    candidates.append((value, "prime_sum_pattern"))
    
    # Pattern 6: Combine prime patterns from image examples
    new_coeffs = []
    for factors in coef_factors:
        if factors:
            val1 = sum(f % 16 for f in factors)  # Sum of factors mod 16
            val2 = len(factors)  # Count of factors
            val3 = factors[0] % 16  # First factor mod 16
            new_val = ((val1 + val2 + val3) * 71) % 16  # Combine with position
            new_coeffs.append(new_val)
        else:
            new_coeffs.append(0)
    value = sum(c * (16 ** p[1]) for c, p in zip(new_coeffs, powers))
    candidates.append((value, "combined_prime_pattern"))
    
    print("\nTrying prime factorization patterns:")
    for candidate, formula in candidates:
        print(f"\nTrying {formula}:")
        print(f"Result: 0x{candidate:x}")
        if verify_key(candidate, TARGET_71):
            print("✅ VALID KEY FOUND!")
            return candidate
        else:
            print("❌ Invalid key")
    
    return None

if __name__ == "__main__":
    result = analyze_position_71()
    if result:
        print(f"\nFound valid key for position 71: 0x{result:x}") 