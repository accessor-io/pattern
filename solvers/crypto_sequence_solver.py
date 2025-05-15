import hmac
import hashlib
import argparse

def hex_key_to_ascii(hex_key: str) -> str:
    """Convert hex key to ASCII using same logic as JavaScript version"""
    # Remove '0x' prefix if present
    hex_str = hex_key[2:] if hex_key.startswith('0x') else hex_key
    # Add sanitization
    clean_hex_str = "".join(filter(str.isxdigit, hex_str.lower()))
    if not clean_hex_str: # Handle case where string becomes empty after cleaning
        # Depending on desired behavior, either return an error or a default value.
        # For now, returning '.' for each byte of an assumed default length (e.g., 32 if it were a key)
        # or simply an error message. Let's return an error indicator.
        return "Error: Empty hex after cleaning"
    if len(clean_hex_str) % 2 != 0:
        # Handle odd length. bytes.fromhex needs even length.
        # Prepending '0' is a common way if appropriate for the number's magnitude.
        # Or return error.
        # Given the original error was "non-hexadecimal", not "odd length",
        # this might be less likely the primary issue, but good to be robust.
        # For now, let's assume the original logic implies keys that would have even length if clean.
        # If cleaning results in odd, it's a problem.
        return f"Error: Odd length hex after cleaning ({len(clean_hex_str)})"

    try:
        key_bytes = bytes.fromhex(clean_hex_str)
    except ValueError as e:
        return f"Error during fromhex: {e}" # More specific error

    result = []
    # Reverse bytes to process from MSB to LSB (Original logic)
    # If key_bytes can be of variable length (e.g. 88 chars from log vs 64 from this function's apparent design)
    # this reversal might need context. Assuming it's byte-wise.
    for byte_val in reversed(key_bytes): # Renamed 'byte' to 'byte_val' to avoid conflict if 'bytes' module is used
        # Printable ASCII range: 0x20 (space) to 0x7E (~)
        char = chr(byte_val) if 0x20 <= byte_val <= 0x7E else '.'
        result.append(char)
    return ''.join(result)

def generate_next_key(prev_key_hex: str, index: int) -> str:
    """Generate next key with index in MSB and zeroed LSB"""
    # Remove '0x' prefix if present
    hex_str_input = prev_key_hex[2:] if prev_key_hex.startswith('0x') else prev_key_hex
    
    # Sanitize the input hex string before zfill and fromhex
    clean_hex_str_input = "".join(filter(str.isxdigit, hex_str_input.lower()))

    if not clean_hex_str_input:
        # Handle empty string after cleaning. What should prev_key_bytes be?
        # This might indicate a severe issue with prev_key_hex.
        # Let's return an error or a known "safe" key to prevent crash.
        # Returning '0x00...00' (32 bytes) as a fallback.
        return "0x" + "00" * 32 

    # The zfill(64) indicates an expectation that the key material is 64 hex characters (32 bytes).
    # This contradicts the 88-character key from the error logs.
    # If the input `clean_hex_str_input` is longer than 64, zfill(64) does nothing.
    # If it's shorter, it's padded with leading zeros.
    # If cleaning results in an odd-length string, zfill will make it even if padding occurs,
    # but the value might be wrong. e.g. "abc" cleaned, zfill(64) -> "0...0abc"
    # bytes.fromhex requires an even number of digits.
    
    # Ensure even length before fromhex, especially if zfill isn't hit or doesn't guarantee it
    # for all cases (e.g., if clean_hex_str_input is already > 64 but odd length - though filter+lower implies it would be hex)
    # Actually, if clean_hex_str_input contains only hex digits, its length will be even if it represents whole bytes.
    # If cleaning made it odd, it means partial byte representation, which is an issue.
    if len(clean_hex_str_input) % 2 != 0:
        # This is problematic. How to best handle?
        # Prepending '0' is one option but might alter the value incorrectly.
        # For now, indicate error by returning a known non-progressing key.
         return "0x" + "bad1" * 16 # Error indicator

    try:
        # Apply zfill to the cleaned string
        processed_hex_str = clean_hex_str_input.zfill(64)
        prev_key_bytes = bytes.fromhex(processed_hex_str)
    except ValueError as e:
        # If fromhex still fails, the cleaning wasn't enough or zfill created an issue.
        return f"0x{'error'.ljust(64, '0')}" # Error key

    # Original logic for key generation:
    salt = f"salt-{index}".encode()
    hmac_digest = hmac.new(salt, prev_key_bytes, hashlib.sha256).digest()
    index_header = index.to_bytes(8, 'big')
    masked_key = (
        index_header +
        hmac_digest[:16] +
        bytes(8)
    )
    # This output (masked_key.hex()) should be clean (even length, pure hex).
    return f"0x{masked_key.hex()}"

def validate_67():
    # Validate against known index 67 key
    key_66 = "2832ed74f2b5e35ee"  # Previous key
    result = generate_next_key(key_66, 66)
    assert result == "0x00000000000000000000000000000000000000000000000730fc235c1942c1ae"

def main():
    parser = argparse.ArgumentParser(description="Crypto sequence solver.")
    parser.add_argument("--start-key", type=str, required=True, help="Starting key in hex format.")
    parser.add_argument("--start-index", type=int, required=True, help="Starting index.")
    parser.add_argument("--count", type=int, default=10, help="Number of keys to generate.")
    
    args = parser.parse_args()

    current_key_hex = args.start_key.lstrip('0x').lower() # Ensure start_key is raw hex

    for i in range(args.count):
        current_index = args.start_index + i
        
        # Ensure current_key_hex remains a string without '0x' for internal processing
        # Defensively clean current_key_hex at the start of each loop iteration
        # as it's an output from generate_next_key which could be problematic
        current_key_hex = "".join(filter(str.isxdigit, current_key_hex.lstrip('0x').lower()))
        if not current_key_hex: # If cleaning results in empty, default to "0" to avoid downstream errors
            current_key_hex = "0"
        if len(current_key_hex) % 2 != 0: # Pad if odd length after cleaning
             current_key_hex = '0' + current_key_hex


        print(f"Index: {current_index}")
        # Display with '0x' prefix, ensure it's padded if it's short (e.g. "0x1" -> "0x01")
        display_key = current_key_hex
        if len(display_key) % 2 != 0:
            display_key = '0' + display_key
        if not display_key: # handle case where current_key_hex might become empty
            display_key = "00"

        print(f"Key:   0x{display_key}")
        
        # hex_key_to_ascii expects a string that might have '0x'.
        # Our current_key_hex is raw, so we can pass it directly, or pass the display version.
        # Let's pass the raw version as hex_key_to_ascii handles lstrip('0x').
        ascii_str = hex_key_to_ascii(current_key_hex) # Pass the raw hex string
        print(f"ASCII: {ascii_str}")
        print("--------------------------------------------------")
        
        if i < args.count - 1: # Don't generate next key for the last item
            current_key_hex = generate_next_key(current_key_hex, current_index)
            # Ensure output of generate_next_key is also cleaned for the next iteration
            current_key_hex = "".join(filter(str.isxdigit, current_key_hex.lstrip('0x').lower()))
            if not current_key_hex: # Default if empty
                current_key_hex = "0" # Default to "0" to allow int conversion and continuation
            # No odd length padding here, as generate_next_key should return valid hex string
            # which format(val, 'x') does.
            # The next iteration's defensive cleaning will handle it if generate_next_key is still faulty.

if __name__ == "__main__":
    main()