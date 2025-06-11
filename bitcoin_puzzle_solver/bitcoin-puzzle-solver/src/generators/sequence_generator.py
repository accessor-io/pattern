def generate_term_candidate(n: int, prev: int, prime: int, prime_offset: int,
                            variant: dict, offset_shift: int) -> int:
    """Generate candidate with exact bit length handling"""
    # ... existing candidate generation logic ...
    
    # Enforce exact bit length
    candidate &= (1 << n) - 1
    
    # Pad with zeros if needed
    if candidate.bit_length() < n:
        candidate |= (1 << (n-1))  # Set highest bit to ensure minimum length
    
    return candidate

def generate_sequence():
    # ... existing code ...
    for idx in range(1, 161):
        # ... generation logic ...
        
        if idx > 66:
            # Final bit length validation
            if term.bit_length() != idx:
                l.e(f"Bit length mismatch: {term.bit_length()} vs {idx}")
                raise ValueError("Invalid bit length")
            
            # Address validation
            if idx in KNOWN_ADDRESSES:
                addr = private_key_to_address(term, idx)
                if addr != KNOWN_ADDRESSES[idx]:
                    l.e(f"Address mismatch for {idx}: {addr} vs {KNOWN_ADDRESSES[idx]}")
                    raise ValueError("Address validation failed")
        
        sequence.append(term) 