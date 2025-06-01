from known_addresses import KNOWN_ADDRESSES
from known_solutions import KNOWN_SOLUTIONS
from cryptos import Bitcoin

def validate_solutions():
    btc = Bitcoin()
    mismatches = []
    
    for index in KNOWN_SOLUTIONS:
        privkey = KNOWN_SOLUTIONS[index]
        expected_address = KNOWN_ADDRESSES[index]
        
        # Generate address from solution
        generated_address = btc.privkey_to_address(privkey)
        
        if generated_address != expected_address:
            mismatches.append({
                'index': index,
                'expected': expected_address,
                'actual': generated_address,
                'privkey_hex': hex(privkey)
            })
    
    if mismatches:
        print(f"Validation failed: {len(mismatches)} mismatches")
        for mismatch in mismatches:
            print(f"Index {mismatch['index']}:")
            print(f"  Expected: {mismatch['expected']}")
            print(f"  Actual:   {mismatch['actual']}")
            print(f"  Privkey:  {mismatch['privkey_hex']}")
        return False
    
    print("All known solutions match their addresses!")
    return True

# Run validation when script executes
if __name__ == "__main__":
    validate_solutions() 