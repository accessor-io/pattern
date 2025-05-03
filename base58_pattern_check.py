def analyze_base58_patterns():
    # Our target string with invalid Base58 char
    target_str = "KwgpK6VwravTrH6yCAuaRRLhs4P36CdlAttvryUZVMJZuGqjdFZSt3roegDP7mRct25cKypgSA"
    
    # Transaction ID
    tx_id = "fb231435137f7e9290d8b56dcfbe9dce5a618d62d11ab5c2e527c79b5d625b72"
    
    print("Base58 Pattern Analysis:")
    print(f"Target string length: {len(target_str)}")
    print(f"Transaction ID length: {len(tx_id)}")
    
    # Check character distribution
    BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
    # Count character types in target string
    upper_count = sum(1 for c in target_str if c.isupper())
    lower_count = sum(1 for c in target_str if c.islower())
    digit_count = sum(1 for c in target_str if c.isdigit())
    
    print("\nCharacter Distribution:")
    print(f"Uppercase: {upper_count}")
    print(f"Lowercase: {lower_count}")
    print(f"Digits: {digit_count}")
    
    # Check for invalid Base58 characters
    invalid_chars = [c for c in target_str if c not in BASE58_ALPHABET]
    print(f"\nInvalid Base58 characters: {invalid_chars}")
    
    # Check if replacing 'l' with '1' makes it valid Base58
    modified_str = target_str.replace('l', '1')
    print(f"\nModified string (l->1): {modified_str}")
    print(f"All valid Base58 now: {all(c in BASE58_ALPHABET for c in modified_str)}")

analyze_base58_patterns() 