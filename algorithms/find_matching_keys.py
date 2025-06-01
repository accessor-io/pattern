#!/usr/bin/env python3
"""
This script attempts to find private keys that generate Bitcoin addresses
matching a predefined list of target addresses (for indices 71-79).
It uses the address generation logic from complete_formula_reference.py.
"""

import hashlib
import base58
import ecdsa
from complete_formula_reference import privkey_to_address, EXPECTED_ADDRESSES

# Define the target addresses from the user's LaTeX formula
TARGET_ADDRESSES_TO_FIND = {
    71: "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",
    72: "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    73: "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
    74: "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
    # Index 75 is in EXPECTED_ADDRESSES but not in the user's explicit list for this search
    76: "1DJh2eHFYQfACPmrvpyWc8MSTYKh7w9eRF",
    77: "1Bxk4CQdqL9p22JEtDfdXMsng1XacifUtE",
    78: "15qF6X51huDjqTmF9BJgxXdt1xcj46Jmhb",
    79: "1ARk8HWJMn8js8tQmGUJeQHjSE7KRkn2t8",
}

# Invert the dictionary for quick lookup by address
TARGET_ADDRESS_TO_INDEX = {addr: index for index, addr in TARGET_ADDRESSES_TO_FIND.items()}

def N_i_to_bytes(N_i):
    """
    Serializes the integer N_i into bytes.
    The LaTeX formula implies N_i is derived from bit positions.
    For simplicity in this initial script, we'll assume N_i is the private key directly.
    The conversion N_i = sum(d_k * 16^k) = sum(2^j) is complex and context-dependent.
    This part might need refinement based on how N_i is actually constructed from puzzle inputs.
    """
    # Determine the number of bytes needed
    if N_i == 0:
        return b'\x00'
    length = (N_i.bit_length() + 7) // 8
    return N_i.to_bytes(length, 'big')

def generate_address_from_N_i(N_i):
    """
    Generates a Bitcoin address from an integer N_i based on the LaTeX formula.
    This function assumes N_i is the direct input for serialization,
    which might be a simplification of the d_k and b_m parts of the formula.
    """
    bytes_N_i = N_i_to_bytes(N_i)

    # h_i = HASH160(bytes_N_i)
    sha256_hash = hashlib.sha256(bytes_N_i).digest()
    h_i = hashlib.new('ripemd160', sha256_hash).digest()

    # p_i = 0x00 || h_i
    p_i = b'\x00' + h_i

    # checksum_i = first 4 bytes of SHA256(SHA256(p_i))
    checksum_i = hashlib.sha256(hashlib.sha256(p_i).digest()).digest()[:4]

    # payload_i = p_i || checksum_i
    payload_i = p_i + checksum_i

    # Address_i = Base58Encode(payload_i)
    address_i = base58.b58encode(payload_i).decode('utf-8')
    return address_i

def search_keys_for_targets(start_key_hex, end_key_hex):
    """
    Searches a range of private keys (N_i values) to find matches for target addresses.
    """
    print(f"Searching for private keys between {start_key_hex} and {end_key_hex}")
    start_key = int(start_key_hex, 16)
    end_key = int(end_key_hex, 16)

    found_keys = {}

    for N_i_candidate in range(start_key, end_key + 1):
        # This is the part where N_i would be constructed if it's not the key itself
        # For now, we assume N_i is the private key to be tested.
        # The formula N_i = sum(d_k * 16^k) etc. would need to be implemented here
        # if N_i is an intermediate value before the actual private key.

        # The privkey_to_address function expects an integer private key.
        # If N_i from the formula is directly the private key, we use it.
        # If the formula means N_i's *bytes* are hashed to become part of a *different*
        # key generation scheme (e.g. N_i is a seed for a KDF), that's more complex.
        # The LaTeX seems to imply N_i itself (serialized) is what's hashed.

        # Let's test two interpretations:
        # 1. N_i is the private key, and we use the imported privkey_to_address
        # 2. N_i is processed as per the HASH160 steps in the LaTeX formula directly

        # Interpretation 1: N_i is the private key for ECDSA
        # This is how privkey_to_address from complete_formula_reference works
        address_from_ecdsa_key = privkey_to_address(N_i_candidate)
        if address_from_ecdsa_key in TARGET_ADDRESS_TO_INDEX:
            idx = TARGET_ADDRESS_TO_INDEX[address_from_ecdsa_key]
            print(f"MATCH (ECDSA Key): Index {idx}, Key 0x{N_i_candidate:x} -> Address {address_from_ecdsa_key}")
            found_keys[idx] = (N_i_candidate, address_from_ecdsa_key)

        # Interpretation 2: N_i is processed as per the formula's HASH160 steps
        # This bypasses ECDSA and directly uses HASH160 on bytes_N_i
        address_from_N_i_hash = generate_address_from_N_i(N_i_candidate)
        if address_from_N_i_hash in TARGET_ADDRESS_TO_INDEX:
            idx = TARGET_ADDRESS_TO_INDEX[address_from_N_i_hash]
            # Avoid double printing if the address is the same and already found by method 1
            if not (address_from_N_i_hash == address_from_ecdsa_key and address_from_ecdsa_key in TARGET_ADDRESS_TO_INDEX):
                 print(f"MATCH (Direct N_i Hash): Index {idx}, N_i 0x{N_i_candidate:x} -> Address {address_from_N_i_hash}")
            if idx not in found_keys or found_keys[idx][1] != address_from_N_i_hash : # ensure we log this if different key or not found by method 1
                found_keys[idx] = (N_i_candidate, address_from_N_i_hash)


        if len(found_keys) == len(TARGET_ADDRESSES_TO_FIND):
            print("All target addresses found.")
            break
        
        if N_i_candidate % 100000 == 0: # Print progress
            print(f"Progress: Checked up to key 0x{N_i_candidate:x}...")

    if not found_keys:
        print("No matching private keys found in the specified range.")
    return found_keys

if __name__ == "__main__":
    # --- IMPORTANT ---
    # The search range for private keys needs to be defined.
    # Bitcoin private keys are typically 256-bit numbers.
    # A full scan is computationally infeasible.
    # This script requires a NARROW and TARGETED range to be effective.
    # For demonstration, let's try a very small range around a known key if available,
    # or a placeholder range.

    # Example: If we knew a key for index 70 was X, we might search X +/- some delta.
    # from complete_formula_reference import KNOWN_KEYS
    # key_70 = KNOWN_KEYS.get(70)
    # if key_70:
    #     demo_start_hex = hex(key_70 - 0x1000) # Example small range
    #     demo_end_hex = hex(key_70 + 0x1000)
    # else:
    #     # Placeholder range if key 70 is not in KNOWN_KEYS
    #     # WARNING: This is a tiny range, unlikely to find anything for real puzzles.
    #     demo_start_hex = "0x10000000000000000" # Example 68-bit start
    #     demo_end_hex =   "0x10000000000010000" # Example small range

    # For the puzzle addresses 71-79, the keys are likely very large.
    # Puzzle 71 is known to start with 0x4000... (16 zeros) for its 71-bit range.
    # Min key for 71-bit: 2^70 = 0x40000000000000000 (16 zeros)
    # Max key for 71-bit: 2^71 - 1 = 0x7FFFFFFFFFFFFFFFFFF (18 F's)

    # Let's define a small search space for demonstration.
    # ** This range MUST be adjusted for actual searching. **
    
    # Example for Puzzle 71's known range (tiny slice)
    # search_start_hex = "0x40000000000000000" # 2^70
    # search_end_hex   = "0x400000000000FFFFF" # A very small portion of the 71-bit space

    # It's better to test with actual known keys first if possible.
    # Let's try to find the key for Address 71 "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
    # if its private key is already in KNOWN_KEYS from complete_formula_reference.py
    
    # Let's use the known keys from complete_formula_reference to test the script
    print("Testing with known keys from complete_formula_reference.py:")
    found_any_known = False
    from complete_formula_reference import KNOWN_KEYS
    for index, p_key in KNOWN_KEYS.items():
        if index in TARGET_ADDRESSES_TO_FIND: # Only check if this index is one we are looking for
            addr_ecdsa = privkey_to_address(p_key)
            addr_direct_hash = generate_address_from_N_i(p_key)
            
            expected_addr = TARGET_ADDRESSES_TO_FIND[index]
            
            if addr_ecdsa == expected_addr:
                print(f"  FOUND (KNOWN KEY - ECDSA): Index {index}, Key 0x{p_key:x} -> Address {addr_ecdsa}")
                found_any_known = True
            elif addr_direct_hash == expected_addr: # Check direct hash method if ECDSA didn't match
                print(f"  FOUND (KNOWN KEY - Direct N_i Hash): Index {index}, N_i 0x{p_key:x} -> Address {addr_direct_hash}")
                found_any_known = True
            # else:
                # print(f"  MISMATCH (KNOWN KEY): Index {index}, Key 0x{p_key:x} -> ECDSA: {addr_ecdsa}, DirectHash: {addr_direct_hash}. Expected: {expected_addr}")


    if not found_any_known:
        print("  No matches found for target addresses using the keys in KNOWN_KEYS.")
    print("\n--- Starting Wider Search (Example Range) ---")
    print("NOTE: The default range is very small and for demonstration only.")
    print("You will likely need to adjust 'search_start_hex' and 'search_end_hex'.")

    # A small, illustrative search range.
    # For real searches, this needs to be carefully chosen based on puzzle parameters or clues.
    # Example: Small range within 71-bit space.
    # search_start_hex = "0x40000000000000000"  # 2^70
    # search_end_hex = "0x400000000000FFFFF"    # 2^70 + (2^20 -1) , covers about a million keys

    # Example: Range around the known key for puzzle 70, if we suspect proximity for 71
    key_70 = KNOWN_KEYS.get(70)
    if key_70:
        search_start_hex = hex(max(0, key_70 - 0x1FFFFF)) # Search 2 million below
        search_end_hex = hex(key_70 + 0x1FFFFF)      # Search 2 million above
    else: # Fallback if key 70 is not available
        search_start_hex = "0x40000000000000000"
        search_end_hex = "0x40000000000FFFFFE"


    found_keys_in_range = search_keys_for_targets(search_start_hex, search_end_hex)

    if found_keys_in_range:
        print("\n--- Summary of Found Keys in Search Range ---")
        for index, (key, addr) in sorted(found_keys_in_range.items()):
            print(f"Index {index}: Key 0x{key:x} -> Address {addr}")
    else:
        print("\nNo keys found for target addresses in the searched range.")

    print("\nScript finished.") 