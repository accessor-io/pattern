import hashlib
from typing import List, Tuple
import re

def analyze_tx_patterns():
    # Transaction details
    txid = "fb231435137f7e9290d8b56dcfbe9dce5a618d62d11ab5c2e527c79b5d625b72"
    block_height = 723715
    target_string = "KwgpK6VwravTrH6yCAuaRRLhs4P36CdlAttvryUZVMJZuGqjdFZSt3roegDP7mRct25cKypgSA"
    
    # Output values (in satoshis)
    outputs = [
        1234567890,  # Example output 1
        987654321    # Example output 2
    ]
    
    print("Transaction Pattern Analysis:")
    print(f"TXID: {txid}")
    print(f"Block Height: {block_height}\n")

    # Character type analysis
    print("Character Type Distribution in Target String:")
    uppercase = sum(1 for c in target_string if c.isupper())
    lowercase = sum(1 for c in target_string if c.islower())
    digits = sum(1 for c in target_string if c.isdigit())
    print(f"Uppercase: {uppercase} ({(uppercase/len(target_string))*100:.2f}%)")
    print(f"Lowercase: {lowercase} ({(lowercase/len(target_string))*100:.2f}%)")
    print(f"Digits: {digits} ({(digits/len(target_string))*100:.2f}%)\n")

    # Sequential pattern analysis
    print("Sequential Pattern Analysis:")
    for i in range(len(target_string)-1):
        if ord(target_string[i+1]) - ord(target_string[i]) == 1:
            print(f"Sequential chars found: {target_string[i]}{target_string[i+1]} at position {i}")
    print()

    # Output Position Analysis
    print("Output Position Analysis:")
    for i, output in enumerate(outputs, 1):
        pos = output % len(target_string)
        print(f"Output{i} % len: {pos} -> '{target_string[pos]}'")
    print()

    # Block Height Analysis
    block_pos = block_height % len(target_string)
    print(f"Block Height % len: {block_pos} -> '{target_string[block_pos]}'\n")

    # TXID Pattern Analysis
    print("TXID Pattern Analysis:")
    for i in range(0, len(txid), 8):
        chunk = txid[i:i+8]
        pos = sum(int(x, 16) for x in chunk) % len(target_string)
        print(f"TXID bytes {i//2}-{(i+7)//2}: {chunk} -> pos {pos} -> '{target_string[pos]}'")
    print()

    # Base58 Analysis
    output_sum = sum(outputs) % 58
    print("Base58 Analysis:")
    print(f"Output sum % 58: {output_sum} -> '{target_string[output_sum % len(target_string)]}'\n")

    # Enhanced Pattern Analysis
    print("Enhanced Pattern Analysis:")
    
    # Analyze byte patterns
    txid_bytes = bytes.fromhex(txid)
    hash_result = hashlib.sha256(txid_bytes).hexdigest()
    pattern_pos = int(hash_result[:4], 16) % len(target_string)
    print(f"SHA256(TXID) first 2 bytes -> pos {pattern_pos} -> '{target_string[pattern_pos]}'")
    
    # Block height pattern
    block_pattern = (block_height * outputs[0]) % len(target_string)
    print(f"Block height * Output1 pattern -> pos {block_pattern} -> '{target_string[block_pattern]}'")
    
    # Output XOR pattern
    output_xor = outputs[0] ^ outputs[1]
    xor_pos = output_xor % len(target_string)
    print(f"Output XOR pattern -> pos {xor_pos} -> '{target_string[xor_pos]}'")

    # Distance analysis between mapped positions
    print("\nDistance Analysis:")
    positions = [
        output_sum % len(target_string),
        block_pos,
        pattern_pos,
        xor_pos
    ]
    for i in range(len(positions)):
        for j in range(i+1, len(positions)):
            dist = abs(positions[i] - positions[j])
            print(f"Distance between pos {positions[i]} and {positions[j]}: {dist}")

    # Potential shift values
    print("\nPotential Shift Values:")
    print(f"Letter shift (output1 % 26): {outputs[0] % 26}")
    print(f"Number shift (output2 % 10): {outputs[1] % 10}")

if __name__ == "__main__":
    analyze_tx_patterns() 