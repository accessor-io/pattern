#!/usr/bin/env python3
import re
from bitcoin import *
import hashlib
import sqlite3

CONTROL_CHAR_MAP = {
    0x00: 'NUL', 0x01: 'SOH', 0x02: 'STX', 0x03: 'ETX',
    0x04: 'EOT', 0x05: 'ENQ', 0x06: 'ACK', 0x07: 'BEL',
    0x08: 'BS', 0x09: 'HT', 0x0A: 'LF', 0x0B: 'VT',
    0x0C: 'FF', 0x0D: 'CR', 0x0E: 'SO', 0x0F: 'SI',
    0x10: 'DLE', 0x11: 'DC1', 0x12: 'DC2', 0x13: 'DC3',
    0x14: 'DC4', 0x15: 'NAK', 0x16: 'SYN', 0x17: 'ETB',
    0x18: 'CAN', 0x19: 'EM', 0x1A: 'SUB', 0x1B: 'ESC',
    0x1C: 'FS', 0x1D: 'GS', 0x1E: 'RS', 0x1F: 'US',
    0x7F: 'DEL'
}

WEBSOCKET_OPCODES = {
    0x00: 'CONTINUATION',
    0x01: 'TEXT',
    0x02: 'BINARY',
    0x08: 'CLOSE',
    0x09: 'PING',
    0x0A: 'PONG'
}

class WebSocketValidationError(Exception):
    """Custom exception for WebSocket validation errors"""
    pass

def validate_websocket_frame(byte_val, bit_length):
    """Validate byte value against WebSocket protocol rules"""
    try:
        if bit_length == 68:
            if byte_val not in WEBSOCKET_OPCODES:
                raise WebSocketValidationError(f"Invalid opcode: 0x{byte_val:02x}")
            return WEBSOCKET_OPCODES[byte_val]
        elif bit_length == 69:
            if byte_val not in (0x09, 0x0A):  # Only PING/PONG allowed
                raise WebSocketValidationError("69-bit sequences must be PING/PONG frames")
            return WEBSOCKET_OPCODES[byte_val]
        return None
    except Exception as e:
        return f"[VALIDATION_ERROR: {str(e)}]"

def decode_hex_key(hex_str, validate_ws=False):
    """Decode hexadecimal key with WebSocket validation option"""
    try:
        hex_clean = re.sub(r'^0x|\s', '', hex_str, flags=re.IGNORECASE)
        if not hex_clean:
            return '[EMPTY]'
            
        if len(hex_clean) % 2 != 0:
            hex_clean = '0' + hex_clean
            
        if not re.match(r'^[0-9a-fA-F]+$', hex_clean):
            return f'[INVALID_HEX: {hex_str}]'

        bytes_val = bytes.fromhex(hex_clean)
        decoded = []
        
        for i, byte in enumerate(bytes_val):
            if validate_ws and i == 0:
                ws_frame = validate_websocket_frame(byte, len(hex_clean) * 4)
                if ws_frame:
                    decoded.append(f'[WS:{ws_frame}]')
                    continue
                    
            if byte in CONTROL_CHAR_MAP:
                decoded.append(f'[{CONTROL_CHAR_MAP[byte]}]')
            elif 32 <= byte <= 126:
                decoded.append(chr(byte))
            else:
                decoded.append(f'\\x{byte:02x}')
                
        return ''.join(decoded)
    except Exception as e:
        return f'[ERROR: {str(e)}]'

def process_file(filename, validate_ws=False):
    """Process file with WebSocket validation option"""
    try:
        results = []
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    if match := re.search(r'Index:\s*(\d+).*?Key:\s*(0x[\da-fA-F]+)', line):
                        index = match.group(1)
                        hex_key = match.group(2)
                        enhanced = decode_hex_key(hex_key, validate_ws)
                        results.append({
                            'index': index,
                            'key': hex_key,
                            'decoded': enhanced,
                            'bit_length': len(hex_key[2:]) * 4
                        })
                except Exception as e:
                    print(f"Warning: Error processing line {line_num}: {str(e)}")
                    continue
                    
        # Sort and display results
        for result in sorted(results, key=lambda x: int(x['index'])):
            print(f"Index: {result['index']} | "
                  f"Key: {result['key']} => {result['decoded']} "
                  f"(Bits: {result['bit_length']})")
                  
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
    except Exception as e:
        print(f"Critical error: {str(e)}")
        raise

def verify_1b_solution():
    """Demonstrate 0x1B → Address transformation"""
    hex_byte = '1B'
    print(f"\nVerifying 0x{hex_byte} solution:")
    
    # Step 1: Pad to 32 bytes
    private_key = bytes.fromhex(hex_byte.zfill(64))
    print(f"1. Private Key: {private_key.hex()}")
    
    # Step 2: Generate public key
    public_key = privkey_to_pubkey(private_key)
    print(f"2. Public Key: {public_key.hex()}")
    
    # Step 3: Hash functions
    sha = sha256(public_key).digest()
    print(f"3. SHA-256: {sha.hex()}")
    
    ripemd = hashlib.new('ripemd160', sha).digest()
    print(f"4. RIPEMD-160: {ripemd.hex()}")
    
    # Step 4: Address encoding
    address = base58.b58encode_check(b'\x00' + ripemd).decode()
    print(f"5. Address: {address}")

def explain_1b_transformation():
    """Show step-by-step transformation of 0x1B to address"""
    from hashlib import sha256, new
    
    print("\n0x1B Transformation Pipeline:")
    print("1. Original byte: 0x1B (ESC control character)")
    
    # Step 1: Create valid private key
    private_key = bytes.fromhex('1B'.zfill(64))  # 32 bytes
    print(f"2. Padded private key: {private_key.hex()}")
    
    # Step 2: Generate public key
    sk = SigningKey.from_string(private_key, curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key = b'\x02' + vk.pubkey.point.x().to_bytes(32, 'big')
    print(f"3. Compressed public key: {public_key.hex()}")
    
    # Step 3: SHA-256 hash
    sha_hash = sha256(public_key).digest()
    print(f"4. SHA-256 result: {sha_hash.hex()}")
    
    # Step 4: RIPEMD-160 hash
    ripemd = new('ripemd160')
    ripemd.update(sha_hash)
    hash160 = ripemd.digest()
    print(f"5. RIPEMD-160 result: {hash160.hex()}")
    
    # Step 5: Base58Check encoding
    address = base58.b58encode_check(b'\x00' + hash160).decode()
    print(f"6. Final address: {address}")

class Puzzle67Solver:
    def __init__(self):
        self.db_conn = sqlite3.connect('puzzle67_progress.db')
        self._init_database()

    def _init_database(self):
        # Implementation of _init_database method
        pass

if __name__ == "__main__":
    process_file('ascii_keys.txt')
    verify_1b_solution()
    explain_1b_transformation() 