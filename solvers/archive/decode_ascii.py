import base64
import binascii
import codecs

# ASCII outputs extracted from ascii_keys.txt
ascii_outputs = [
    ".", ".", ".", ".", ".", "1", "L", ".", "..", "..", "..", ".{", ".`", ")0", "h.", ".6", ".vO",
    "...", ".t.", ".,U", "..4", "-..", "UnR", ".*.", "..^.", ".@2n", "..8u", "..l.", "..U.", "=..d", "}O.G", ".b..",
    "..l..", ".Je..", "....p", "....|", ".Wuj.", "\"8/..", "K_...", "..I3.", ".S...[", "..!...", "..;'..", "...Z5.",
    "./..<.", ".....D", "l...<.", "....;.", ".t.k._M", ".+.<..T", ".Pp....", "...d..<", "....~2l", "#o....C", "j...g..",
    "...:...", "..%.....", "..u.R..!", ".Il....O", "..z.%6{.", "..j7B.I.", "6=T.....", "|.^...h.", "...'....", "..8.5..hg",
    "....O+^5."
]

def try_base64(s):
    """Attempt Base64 decoding, return decoded string or None."""
    try:
        # Add padding if necessary
        missing_padding = len(s) % 4
        if missing_padding:
            s += '=' * (4 - missing_padding)
        return base64.b64decode(s).decode('utf-8')
    except Exception:
        return None

def try_hex(s):
    """Attempt Hex decoding, return decoded string or None."""
    try:
        return bytes.fromhex(s).decode('utf-8')
    except Exception:
        return None

def try_rot13(s):
    """Apply ROT13 transformation."""
    return codecs.encode(s, 'rot_13')

def try_morse(s):
    """Decode a Morse code string if it matches a single character."""
    MORSE_CODE_DICT = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G',
        '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N',
        '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U',
        '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1',
        '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
        '---..': '8', '----.': '9'
    }
    # Only decode if the string is a valid Morse code sequence
    return MORSE_CODE_DICT.get(s, None)

def try_xor(s, key=0x42):
    """XOR each character in the string with the given key."""
    try:
        return ''.join(chr(ord(c) ^ key) for c in s)
    except Exception:
        return None

def xor_then_morse(s, key=0x42):
    """Apply XOR, then try to decode as Morse code."""
    xor_decoded = try_xor(s, key)
    if xor_decoded:
        return try_morse(xor_decoded)
    return None

def display_control_chars(s):
    """Display string, escaping non-printable characters."""
    if s is None:
        return None
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\x{ord(c):02x}' for c in s)

def print_decoding_attempts(ascii_str):
    """Print all decoding attempts for a given ASCII string."""
    print(f"Original: {ascii_str!r}")
    print(f"  Base64: {try_base64(ascii_str)}")
    print(f"  Hex: {try_hex(ascii_str)}")
    print(f"  ROT13: {try_rot13(ascii_str)}")
    print(f"  Morse: {try_morse(ascii_str)}")
    xor_result = try_xor(ascii_str)
    print(f"  XOR (with control chars): {display_control_chars(xor_result)}")
    print(f"  XOR then Morse: {xor_then_morse(ascii_str)}")
    print("-" * 40)

def main():
    for ascii_str in ascii_outputs:
        print_decoding_attempts(ascii_str)

if __name__ == "__main__":
    main()