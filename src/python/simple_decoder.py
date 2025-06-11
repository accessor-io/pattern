def decode_simple():
    key = "BHJKKXGOMMXCYTV"
    
    print("Simple Bitcoin Format Decoder")
    print("=" * 40)
    
    # Split into parts
    identifier = key[0]
    prefix = key[1:6]
    core = key[6:10]
    checksum = key[10:]
    
    print(f"\nParts:")
    print(f"Identifier: {identifier}")
    print(f"Prefix: {prefix}")
    print(f"Core: {core}")
    print(f"Checksum: {checksum}")
    
    # Convert to numbers (A=0, B=1, etc)
    prefix_nums = [ord(c) - ord('A') for c in prefix]
    core_nums = [ord(c) - ord('A') for c in core]
    checksum_nums = [ord(c) - ord('A') for c in checksum]
    
    print(f"\nNumeric Values:")
    print(f"Prefix: {prefix_nums}")
    print(f"Core: {core_nums}")
    print(f"Checksum: {checksum_nums}")
    
    # Try simple decoding
    try:
        # Convert numbers to bytes
        bytes_data = bytes(prefix_nums + core_nums)
        # Try to decode as ASCII
        ascii_text = ''.join(chr(n + 32) for n in prefix_nums + core_nums)
        print(f"\nPossible ASCII: {ascii_text}")
    except:
        print("\nCould not decode as ASCII")
        
    # Look for simple patterns
    print("\nPattern Analysis:")
    
    # Check if checksum is a function of prefix and core
    checksum_calc = [(a + b) % 26 for a, b in zip(prefix_nums[:len(checksum_nums)], core_nums[:len(checksum_nums)])]
    print(f"Expected checksum: {checksum_calc}")
    print(f"Actual checksum: {checksum_nums}")
    
    # Check if it's a simple substitution
    print("\nSubstitution Check:")
    substitutions = {}
    for i, c in enumerate(key):
        if c not in substitutions:
            substitutions[c] = 1
        else:
            substitutions[c] += 1
    
    print("Character frequencies:")
    for char, count in substitutions.items():
        print(f"{char}: {count} times")

if __name__ == "__main__":
    decode_simple() 