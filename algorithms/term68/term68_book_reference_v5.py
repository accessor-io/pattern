import math

def generate_sequence(n=256):
    """
    Generate the sequence using the exact algorithm from the original code.
    This uses four different methods in rotation:
    1. Fibonacci-based generation
    2. Golden ratio-based generation
    3. Prime-based generation
    4. Bit manipulation
    """
    # Constants exactly as defined in the original code
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
    PHI = (1 + math.sqrt(5)) / 2
    E = math.e
    
    # Start with 1 as the first element
    sequence = [1]
    
    # Generate each subsequent element
    for i in range(1, n):
        prev = sequence[-1]
        bit_length = i + 1  # Target bit length equals position + 1
        
        # Choose generation method based on iteration (cycling through all 4 methods)
        method_selector = i % 4
        
        if method_selector == 0:
            # Bit manipulation method
            rotation = i % bit_length
            if rotation == 0:  # Avoid division by zero
                rotation = 1
            candidate = ((prev << rotation) | (prev >> (bit_length - rotation))) & ((1 << bit_length) - 1)
        
        elif method_selector == 1:
            # Fibonacci-based method
            fib_index = i % len(FIB)
            multiplier = FIB[fib_index]
            candidate = (prev * multiplier + FIB[(fib_index + 1) % len(FIB)]) % (1 << 256)
        
        elif method_selector == 2:
            # Golden ratio-based method
            phi_scaled = int(PHI * (1 << 32))
            candidate = (prev * phi_scaled + int(E * 1e9)) % (1 << 256)
        
        else:  # method_selector == 3
            # Prime-based method
            prime_index = i % len(PRIMES)
            prime = PRIMES[prime_index]
            shift = (i // len(PRIMES)) % bit_length
            candidate = (prev * prime + (prime << shift)) % (1 << 256)
        
        # Ensure the result has exactly the target bit length
        if candidate.bit_length() > bit_length:
            candidate &= ((1 << bit_length) - 1)
        if candidate.bit_length() < bit_length:
            candidate |= (1 << (bit_length - 1))
        
        sequence.append(candidate)
    
    return sequence

def is_prime(n):
    """Check if a number is prime using an efficient algorithm."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    
    return True

def format_sequence_output(sequence, output_file="matched_sequence_256.csv"):
    """Format the sequence with detailed information in exact CSV format."""
    # Prepare the CSV header
    result = "Index,Hex,Decimal,Octal,Binary Length,Is Prime\n"
    
    for i, val in enumerate(sequence, 1):
        binary_length = val.bit_length()
        prime_status = "True" if is_prime(val) else "False"
        
        # Format exactly like the original CSV
        hex_val = f"{val:x}"
        octal_val = oct(val)[2:]  # Remove '0o' prefix
        
        line = f"{i},{hex_val},{val},{octal_val},{binary_length},{prime_status}\n"
        result += line
    
    # Write to file
    with open(output_file, "w") as f:
        f.write(result)
    
    print(f"Sequence written to {output_file}")
    return result

def main():
    """Generate the sequence and save in exact CSV format."""
    print("Generating sequence of 256 terms using the original algorithm...")
    sequence = generate_sequence(256)
    
    print("Formatting and saving output...")
    format_sequence_output(sequence)
    
    print(f"Sequence of {len(sequence)} elements generated successfully.")

if __name__ == "__main__":
    main()