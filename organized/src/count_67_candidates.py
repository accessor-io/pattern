def count_candidates():
    # For a number to have exactly 67 significant bits:
    # 1. Must have a 1 in position 67 (counting from right, 1-based)
    # 2. All bits after position 67 must be 0
    # 3. Can have any combination of bits in positions 1-66
    
    # Total possibilities:
    # - Position 67 must be 1
    # - Positions 1-66 can be 0 or 1 (2^66 combinations)
    # - Positions 68-256 must be 0
    
    total_candidates = 2 ** 66  # combinations for positions 1-66
    
    print(f"Total possible 67-bit candidates: {total_candidates}")
    print(f"In hex: {hex(total_candidates)}")
    print(f"Number of digits in decimal: {len(str(total_candidates))}")

if __name__ == "__main__":
    count_candidates() 