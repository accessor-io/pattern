import math

def generate_sequence(n=256):
    """
    Generate the custom mathematical sequence up to n elements.
    This algorithm combines multiple mathematical approaches to generate a sequence with
    specific bit length properties and mathematical relationships.
    
    Extended to handle up to 256 terms.
    """
    # Constants used in the sequence generation
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
             101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
             211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317]
    
    FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711,
          28657, 46368, 75025, 121393, 196418, 317811, 514229, 832040, 1346269, 2178309]
    
    PHI = (1 + math.sqrt(5)) / 2
    E = math.e
    PI = math.pi
    MODULUS = 1 << 512  # Increased to 2^512 to handle larger numbers
    
    # Start with 1 as the first element
    sequence = [1]
    
    # Generate each subsequent element
    for i in range(1, n):
        prev = sequence[-1]
        target_bit_length = i + 1
        
        # Choose generation method based on iteration
        method_selector = i % 4
        
        if method_selector == 0:
            # Bit manipulation method
            rotation = i % min(target_bit_length, 100)  # Cap rotation to avoid excessive shifting
            if rotation == 0:
                rotation = 1
            candidate = ((prev << rotation) | (prev >> (target_bit_length - rotation))) & ((1 << target_bit_length) - 1)
        
        elif method_selector == 1:
            # Fibonacci-based method
            fib_index = i % len(FIB)
            multiplier = FIB[fib_index]
            candidate = (prev * multiplier + FIB[(fib_index + 1) % len(FIB)]) % MODULUS
        
        elif method_selector == 2:
            # Golden ratio-based method
            phi_scaled = int(PHI * (1 << 40))  # Increased scale for larger numbers
            candidate = (prev * phi_scaled + int(E * 1e12)) % MODULUS
        
        else:  # method_selector == 3
            # Prime-based method
            prime_index = i % len(PRIMES)
            prime = PRIMES[prime_index]
            shift = (i // len(PRIMES)) % min(target_bit_length, 64)  # Cap shift to avoid excessive shifting
            candidate = (prev * prime + (prime << shift)) % MODULUS
        
        # Ensure the result has exactly the target bit length
        if candidate.bit_length() > target_bit_length:
            candidate &= ((1 << target_bit_length) - 1)
        if candidate.bit_length() < target_bit_length:
            candidate |= (1 << (target_bit_length - 1))
        
        sequence.append(candidate)
    
    return sequence

def is_prime(n):
    """
    Check if a number is prime using an efficient algorithm.
    For very large numbers, we use a probabilistic primality test.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    # For smaller numbers, use trial division
    if n < 1000000:
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True
    
    # For larger numbers, use Miller-Rabin primality test (simplified version)
    # This is a probabilistic test, but very reliable for our purposes
    def miller_rabin_pass(a, s, d, n):
        a_to_power = pow(a, d, n)
        if a_to_power == 1:
            return True
        for i in range(s - 1):
            if a_to_power == n - 1:
                return True
            a_to_power = (a_to_power * a_to_power) % n
        return a_to_power == n - 1
    
    # Write n-1 as 2^s * d
    s = 0
    d = n - 1
    while d % 2 == 0:
        d >>= 1
        s += 1
    
    # Witness loop - test with first few prime numbers
    for a in [2, 3, 5, 7, 11, 13, 17]:
        if n == a:
            return True
        if not miller_rabin_pass(a, s, d, n):
            return False
    return True

def format_sequence_output(sequence, output_file=None):
    """Format the sequence with detailed information for each element."""
    result = "Index,Hex,Decimal,Octal,Binary Length,Is Prime\n"
    
    # For terminal output, limit to first 100 and last 10 elements if more than 100 elements
    display_limit = 100
    
    for i, val in enumerate(sequence, 1):
        binary_length = val.bit_length()
        
        # Only compute primality for smaller numbers to avoid excessive computation
        if binary_length <= 64:
            prime_status = "True" if is_prime(val) else "False"
        else:
            prime_status = "Unknown"  # Mark as unknown for very large numbers
            
        line = f"{i},{val:x},{val},{oct(val)[2:]},{binary_length},{prime_status}\n"
        
        # Add to full result for file output
        result += line
        
        # Print to console with limits if there are many elements
        # Print all elements regardless of sequence length
        print(line.strip())
    # Save to file if specified
    if output_file:
        with open(output_file, "w") as f:
            f.write(result)
        print(f"\nFull sequence written to {output_file}")
    
    return result

def main():
    """Generate and display the sequence."""
    print("Generating sequence of 256 terms...")
    sequence = generate_sequence(256)
    
    print("\nSequence generated. Formatting output...")
    format_sequence_output(sequence, "generated_sequence_256.csv")
    
    print(f"\nSequence of {len(sequence)} elements generated successfully.")

if __name__ == "__main__":
    main()