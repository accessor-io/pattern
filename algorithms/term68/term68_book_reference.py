def is_prime(n):
    """Check if a number is prime."""
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

def generate_sequence(n):
    """Generate n elements of the sequence."""
    sequence = [1]  # Start with 1
    
    for i in range(1, n):
        # Calculate next element based on previous
        # We need a value with binary length i+1
        
        # Get previous value
        prev = sequence[-1]
        
        # Apply a feedback function using primitive polynomial concepts
        # This combines shifting with polynomial feedback
        
        # For a value with binary length i+1
        target_bit_length = i + 1
        
        # Create new value using nonlinear feedback
        if i % 3 == 0:
            # Use XOR-based feedback for every third element
            new_val = (prev << 1) ^ ((prev >> (i//3)) | 1)
        elif i % 3 == 1:
            # Use addition-based feedback
            new_val = prev + (prev >> (i//4) + 1) + (1 << (target_bit_length-1))
        else:
            # Use multiplication-based feedback
            new_val = prev + ((prev & ((1 << (i//2)) - 1)) * 2) + 1
            
        # Ensure the result has the correct bit length
        while new_val.bit_length() < target_bit_length:
            new_val |= 1 << (target_bit_length - 1)
        while new_val.bit_length() > target_bit_length:
            new_val &= ~(1 << new_val.bit_length() - 1)
            
        sequence.append(new_val)
    
    return sequence

# Generate the first 65 elements
result = generate_sequence(65)

# Print the result with appropriate formatting
print("Index,Hex,Decimal,Octal,Binary Length,Is Prime")
for i, val in enumerate(result, 1):
    binary_length = val.bit_length()
    is_prime_result = "True" if is_prime(val) else "False"
    print(f"{i},{val:x},{val},{oct(val)[2:]},{binary_length},{is_prime_result}")