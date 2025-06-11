def total_hex_possibilities(length):
    return 16 ** length  # 16 possibilities for each position

def print_possibilities():
    # Total possibilities without constraints
    total_17 = total_hex_possibilities(17)
    total_18 = total_hex_possibilities(18)
    
    print(f"17 character possibilities (unconstrained): {total_17}")
    print(f"18 character possibilities (unconstrained): {total_18}")
    
    # With 67-bit constraint:
    # For 17 chars (68 bits):
    # C(68,67) possible arrangements of 67 '1' bits
    # For 18 chars (72 bits):
    # C(72,67) possible arrangements of 67 '1' bits
    
    from math import comb
    constrained_17 = comb(68, 67)  # number of ways to place 67 '1's in 68 bits
    constrained_18 = comb(72, 67)  # number of ways to place 67 '1's in 72 bits
    
    print(f"\n67-bit constrained possibilities:")
    print(f"17 character strings: {constrained_17}")
    print(f"18 character strings: {constrained_18}")
    
    print(f"\nReduction ratios:")
    print(f"17 chars: 1:{total_17//constrained_17}")
    print(f"18 chars: 1:{total_18//constrained_18}")

if __name__ == "__main__":
    print_possibilities() 