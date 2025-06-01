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

# Attempt Base64 decoding
def try_base64(s):
    try:
        return base64.b64decode(s).decode('utf-8')
    except Exception:
        return None

# Attempt Hex decoding
def try_hex(s):
    try:
        return bytes.fromhex(s).decode('utf-8')
    except Exception:
        return None

# Correct ROT13 decoding
def try_rot13(s):
    return codecs.encode(s, 'rot_13')

# Morse code decoding
def try_morse(s):
    MORSE_CODE_DICT = {'.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G',
                       '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N',
                       '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U',
                       '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1',
                       '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
                       '---..': '8', '----.': '9'}
    return MORSE_CODE_DICT.get(s, None)

# XOR cipher decoding with a single-byte key
def try_xor(s, key=0x42):
    try:
        return ''.join(chr(ord(c) ^ key) for c in s)
    except Exception:
        return None

# Combined XOR followed by Morse decoding
def xor_then_morse(s, key=0x42):
    xor_decoded = try_xor(s, key)
    if xor_decoded:
        return try_morse(xor_decoded)
    return None

# Function to clearly display control characters
def display_control_chars(s):
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\x{ord(c):02x}' for c in s)

# Update decoding attempts
for ascii_str in ascii_outputs:
    print(f"Original: {ascii_str}")
    print(f"Base64: {try_base64(ascii_str)}")
    print(f"Hex: {try_hex(ascii_str)}")
    print(f"ROT13: {try_rot13(ascii_str)}")
    print(f"Morse: {try_morse(ascii_str)}")
    xor_result = try_xor(ascii_str)
    print(f"XOR (with control chars): {display_control_chars(xor_result)}")
    print(f"XOR then Morse: {xor_then_morse(ascii_str)}")
    print("-" * 40) 
    
    
    0456579536d150fbce94ee62b47db2ca43af0a730a0467ba55c79e2a7ec9ce4ad297e35cdbb8e42a4643a60eef7c9abee2f5822f86b1da242d9c2301c431facfd8