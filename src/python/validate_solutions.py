import hashlib
from typing import Dict, Optional
from puzzle_solver_160 import PuzzleSolver

def validate_solution_chain(solutions: Dict[int, int]) -> bool:
    """Validate the entire chain of solutions."""
    for index in sorted(solutions.keys())[1:]:  # Skip first index
        curr_val = solutions[index]
        prev_val = solutions[index - 1]
        
        # Basic validation
        if curr_val <= prev_val:
            print(f"Error: Value at index {index} is not greater than previous value")
            return False
        
        # Validate bit growth
        curr_bits = curr_val.bit_length()
        prev_bits = prev_val.bit_length()
        bit_growth = curr_bits - prev_bits
        if bit_growth < 0 or bit_growth > 8:  # Reasonable bit growth limits
            print(f"Error: Unreasonable bit growth at index {index}: {bit_growth}")
            return False
        
        # Validate value range
        if curr_val >= (1 << 256):
            print(f"Error: Value at index {index} exceeds 256 bits")
            return False
    
    return True

def compute_hash_chain(value: int, num_steps: int) -> List[int]:
    """Compute a chain of hash values starting from a given value."""
    chain = [value]
    for i in range(num_steps):
        value_bytes = value.to_bytes(32, byteorder='big')
        hash_value = int.from_bytes(hashlib.sha256(value_bytes).digest(), byteorder='big')
        chain.append(hash_value)
        value = hash_value
    return chain

def validate_hash_relationships(solutions: Dict[int, int]) -> bool:
    """Validate hash relationships between solutions."""
    for index in sorted(solutions.keys())[1:]:
        curr_val = solutions[index]
        prev_val = solutions[index - 1]
        
        # Compute hash chains
        curr_chain = compute_hash_chain(curr_val, 3)
        prev_chain = compute_hash_chain(prev_val, 3)
        
        # Check for relationships
        for i in range(len(curr_chain)):
            for j in range(len(prev_chain)):
                if curr_chain[i] == prev_chain[j]:
                    print(f"Found hash relationship between indices {index-1} and {index}")
                    print(f"Steps: prev+{j} = curr+{i}")
    
    return True

def main():
    # Create solver and get solutions
    solver = PuzzleSolver()
    solutions = solver.solve_all()
    
    print("\nValidating solutions...")
    
    # Validate solution chain
    if validate_solution_chain(solutions):
        print("Solution chain validation passed")
    else:
        print("Solution chain validation failed")
    
    # Validate hash relationships
    print("\nChecking hash relationships...")
    validate_hash_relationships(solutions)
    
    # Print statistics
    print("\nSolution Statistics:")
    indices = sorted(solutions.keys())
    for i in range(len(indices)-1):
        curr_idx = indices[i]
        next_idx = indices[i+1]
        curr_val = solutions[curr_idx]
        next_val = solutions[next_idx]
        
        growth_ratio = next_val / curr_val
        bit_growth = next_val.bit_length() - curr_val.bit_length()
        
        print(f"\nIndices {curr_idx}-{next_idx}:")
        print(f"Growth ratio: {growth_ratio:.2f}")
        print(f"Bit growth: {bit_growth}")
        print(f"Value size: {next_val.bit_length()} bits")

if __name__ == "__main__":
    main() 