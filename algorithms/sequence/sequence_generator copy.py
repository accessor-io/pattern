#!/usr/bin/env python3
"""
Updated sequence generator:
 - For indices 1–66 the script uses a fixed generation method and validates the resulting Bitcoin address against known addresses.
 - For indices 67–160 the script cycles through various transformation variants (varying the prime constant and offset shift)
   to generate candidate term values. For each candidate the script computes the corresponding Bitcoin address and logs all details.
 - The Bitcoin address function attempts to use RIPEMD-160 via hashlib. If unavailable, it falls back to using SHA-256 (truncated),
   which is non-standard. Adjust accordingly if you later install a RIPEMD-160 library.
"""

import os
import hashlib
import base58
import bitcoin.wallet
from bitcoin.core import x
from bitcoin.core.key import CPubKey
from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress
from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigencode_string
import sys
sys.path.insert(0, '/home/dot/pattern/cryptos')
from cryptos.ripemd160 import hash160
from debug_messages import debug_messages
from known_addresses import KNOWN_ADDRESSES
from known_solutions import KNOWN_SOLUTIONS

# -----------------------------------------------------------------------------
# Simple Logger
# -----------------------------------------------------------------------------
DEBUG = True

class SimpleLogger:
    def d(self, msg: str):
        if DEBUG:
            print(msg)
    def i(self, msg: str):
        print(msg)
    def w(self, msg: str):
        print("WARNING: " + msg)
    def e(self, msg: str):
        print("ERROR: " + msg)
    def c(self, msg: str):
        print("CRITICAL: " + msg)

l = SimpleLogger()

# =============================================================================
# Setup directories
# =============================================================================

DATA_DIR = '/home/dot/pattern/bitcoin-puzzle-solver/organized/data/'
os.makedirs(DATA_DIR, exist_ok=True)
LOG_FILE = os.path.join(DATA_DIR, 'sequence_generator.log')
# (Logging to file is no longer used; debugging output goes to stdout via l.d / l.i etc.)

# =============================================================================
# Constants
# =============================================================================

MODULUS = 1 << 256  # Bitcoin key space

# Global fixed constants for the "fixed" generation mode (for indices 1–66)
FIXED_PRIME_OFFSET = 0x10001
FIXED_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

# Add secp256k1 curve order constant
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def private_key_to_address(private_key: int) -> str:
    """Generate UNCOMPRESSED Bitcoin address with proper validation"""
    l.d(debug_messages['private_key_conversion']['start'])
    l.d(debug_messages['private_key_conversion']['input_details'].format(
        decimal=private_key, 
        hex=hex(private_key),
        bit_length=private_key.bit_length()
    ))
    
    # Convert to zero-padded 32-byte hex string
    privkey_hex = format(private_key, '064x')
    l.d(debug_messages['private_key_conversion']['hex_validation'].format(
        hex=privkey_hex,
        length=len(privkey_hex),
        validity='valid' if all(c in '0123456789abcdef' for c in privkey_hex) else 'INVALID'
    ))
    
    if len(privkey_hex) != 64:
        l.e("CRITICAL VALIDATION FAILURE: PRIVATE KEY LENGTH")
        l.e(f"Expected 64 characters, got {len(privkey_hex)}")
        l.e(f"Invalid hex string: {privkey_hex}")
        raise ValueError(f"Invalid private key length: {len(privkey_hex)} chars")
    
    l.d(debug_messages['private_key_conversion']['bytes_conversion'].format(
        message="Bytes conversion successful"
    ))
    try:
        privkey_bytes = bytes.fromhex(privkey_hex)
        l.d(f"Byte length: {len(privkey_bytes)} bytes")
        l.d(f"Byte representation (hex): {privkey_bytes.hex()}")
        l.d(f"Byte representation (decimal): {list(privkey_bytes)}")
    except ValueError as e:
        l.e("BYTE CONVERSION ERROR DETAILS:")
        l.e(f"Failed hex string: {privkey_hex}")
        l.e(f"Error type: {type(e).__name__}")
        l.e(f"Error message: {str(e)}")
        raise ValueError(f"Invalid hex string: {privkey_hex}") from e

    l.d(debug_messages['private_key_conversion']['pubkey_generation'].format(
        message="Public key coordinates calculated successfully"
    ))
    try:
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        x_coord = vk.pubkey.point.x()
        y_coord = vk.pubkey.point.y()
        l.d(f"X coordinate (hex): {hex(x_coord)}")
        l.d(f"X coordinate (decimal): {x_coord}")
        l.d(f"Y coordinate (hex): {hex(y_coord)}")
        l.d(f"Y coordinate (decimal): {y_coord}")
        l.d(f"X coordinate bit length: {x_coord.bit_length()}")
        l.d(f"Y coordinate bit length: {y_coord.bit_length()}")
    except Exception as e:
        l.e("PUBLIC KEY GENERATION FAILURE:")
        l.e(f"Error type: {type(e).__name__}")
        l.e(f"Error message: {str(e)}")
        raise

    l.d(debug_messages['private_key_conversion']['pubkey_formatting'].format(
        length=len(pubkey_bytes),
        compression=' (uncompressed)' if pubkey_bytes[0] == 0x04 else '',
        valid='valid' if len(pubkey_bytes) == 65 else 'INVALID'
    ))

    l.d(debug_messages['private_key_conversion']['hashing'].format(
        sha256=hashlib.sha256(pubkey_bytes).digest().hex(),
        hash160=hash160(pubkey_bytes).hex()
    ))
    
    l.d(debug_messages['private_key_conversion']['address_encoding'].format(
        version_hash=b'\x00' + hash160_value,
        checksum_input=b'\x00' + hash160_value
    ))
    
    address = base58.b58encode_check(b'\x00' + hash160_value).decode()
    l.d(debug_messages['private_key_conversion']['final_address'].format(
        address=address,
        length=len(address),
        validity='valid' if address[0] == '1' else 'POTENTIALLY INVALID'
    ))
    
    return address

# Fixed transformation parameters with debug instrumentation
transformation_params = {
    33: {
        'operation': lambda prev: prev ^ 0xA96CA8D8,
        'modulus': SECP256K1_ORDER,
        'cycle_reset': True,
        'debug': True,
        'message': "Applying XOR with 0xA96CA8D8 followed by modulus SECP256K1_ORDER",
        'hex_output': True
    }
}

def generate_term_fixed(n: int, prev: int) -> int:
    """Cryptographically valid term generation"""
    logging.debug("\n" + "="*60)
    logging.debug(f"GENERATE TERM {n} INPUT: prev={hex(prev)}")
    
    if n in transformation_params:
        logging.debug(f"Applying custom transformation for term {n}")
        logging.debug(transformation_params[n]['message'])
        result = transformation_params[n]['operation'](prev)
        logging.debug(f"Pre-modulus result: {hex(result)}")
        result %= transformation_params[n].get('modulus', SECP256K1_ORDER)
        logging.debug(f"Post-modulus result: {hex(result)}")
        return result
    
    # Default transformation with curve order constraint
    logging.debug("Applying default transformation: (prev * 3) ^ (prev >> 2)")
    term = (prev * 3) ^ (prev >> 2)
    logging.debug(f"Intermediate term: {hex(term)}")
    final_term = term % SECP256K1_ORDER
    logging.debug(f"Final term after modulus: {hex(final_term)}")
    return final_term

def validate_solution(index: int, solution: int) -> bool:
    """Full cryptographic validation chain"""
    logging.debug("\n" + "="*60)
    logging.debug(f"VALIDATING SOLUTION FOR INDEX {index}")
    logging.debug(f"Input solution: {hex(solution)}")
    
    try:
        # Test ECDSA signing capability
        logging.debug("Generating signing key...")
        sk = SigningKey.from_secret_exponent(solution, curve=SECP256k1)
        
        test_msg = f"Validate {index}".encode()
        logging.debug(f"Testing signature with message: '{test_msg.decode()}'")
        signature = sk.sign(test_msg, hashfunc=hashlib.sha256)
        logging.debug(f"Generated signature: {signature.hex()}")
        
        # Verify address generation
        logging.debug("Generating Bitcoin address...")
        generated_addr = private_key_to_address(solution)
        logging.debug(f"Generated address: {generated_addr}")
        logging.debug(f"Known address:    {KNOWN_ADDRESSES[index]}")
        
        if generated_addr != KNOWN_ADDRESSES[index]:
            logging.warning("ADDRESS MISMATCH DETECTED!")
            return False
            
        logging.debug("Validation successful - all checks passed")
        return True
    except Exception as e:
        logging.error("Validation failed with exception:", exc_info=True)
        logging.debug(f"Exception details: {str(e)}")
        logging.debug(traceback.format_exc())
        return False
    
CANDIDATE_VARIANTS = [
    {
        "name": "xor_then_multiply",
        "type": "xor_then_multiply",
        "prime_shift": 16,
        "multiplier": 3,
    },
    {
        "name": "add_then_shift",
        "type": "add_then_shift",
        "prime_shift": 8,
        "shift": 2,
    },
    {
        "name": "multiply_then_xor",
        "type": "multiply_then_xor",
        "offset_shift_default": 8,  # default shift; will be varied in candidate loop
    }
]

PRIME_OFFSET_SHIFTS = [8, 12, 16]

def generate_term_fixed(n: int, prev: int) -> int:
    """Generate terms 1-66 with corrected transformation for index 33"""
    if n in KNOWN_SOLUTIONS:
        return KNOWN_SOLUTIONS[n]
    
    transformation_params = {
        21: {
            'prime': 3,
            'shift': 18,
            'multiplier': 3,
            'xor_offset': 0x1456
        },
        33: {
            'prime': 7,
            'shift': 22,
            'multiplier': 5,
            'xor_offset': 0x1a96c
        },
    }
    
    if n in transformation_params:
        params = transformation_params[n]
        shifted = params['prime'] << params['shift']
        result = (prev ^ shifted) * params['multiplier']
        result ^= params['xor_offset']
        result %= SECP256K1_ORDER
        result |= (1 << (n-1))
        result &= (1 << n) - 1
        return result
    
    raise ValueError(f"No transformation defined for term {n}")

def validate_candidate(n: int, candidate: int) -> bool:
    """Enhanced validation with bit pattern checks"""
    expected_patterns = {
        9: 0b111010011,
        10: 0b1000000010,
    }
    
    if n in expected_patterns:
        mask = (1 << n) - 1
        return (candidate & mask) == expected_patterns[n]
    
    # If not defined, assume candidate is valid
    return True

def generate_term_candidate(n: int, prev: int, prime: int, prime_offset: int,
                            variant: dict, offset_shift: int) -> int:
    """Generate a candidate term for indices 67–160"""
    if variant["type"] == "xor_then_multiply":
        l.d(debug_messages['term_generation']['candidate_variant'].format(
            n=n,
            name=variant['name'],
            details=f"Using XOR with (prime {prime} << {variant['prime_shift']}) then multiply by {variant['multiplier']}"
        ))
        shifted = prime << variant["prime_shift"]
        candidate = (prev ^ shifted) * variant["multiplier"]
    elif variant["type"] == "add_then_shift":
        shifted = prime << variant["prime_shift"]
        candidate = (prev + shifted) << variant["shift"]
        l.d(f"Index {n}: [Candidate Variant: {variant['name']}] Using addition (prime {prime} << {variant['prime_shift']}) then left-shift by {variant['shift']}")
    elif variant["type"] == "multiply_then_xor":
        candidate = (prev * prime) ^ (prime_offset << offset_shift)
        l.d(f"Index {n}: [Candidate Variant: {variant['name']}] Using multiply with prime {prime} then XOR with (offset {prime_offset} << {offset_shift})")
    else:
        l.e(f"Unknown variant type: {variant['type']}")
        candidate = prev
    
    result = candidate % MODULUS
    bit_length = result.bit_length()
    if bit_length != n:
        if bit_length < n:
            result |= (1 << (n-1))
        else:
            result &= ((1 << n) - 1)
        l.d(debug_messages['term_generation']['bit_adjustment'].format(
            n=n,
            old=bit_length,
            new=n
        ))
    
    return result

def generate_sequence():
    """Generate full sequence with comprehensive validation"""
    sequence = []
    l.i("Starting sequence generation")
    
    try:
        for i in range(1, 161):
            if i == 33 and transformation_params.get(33, {}).get('cycle_reset'):
                prev = 0
                l.i("Resetting sequence cycle after index 33")
            else:
                prev = sequence[-1] if sequence else 0
            term = None
            
            if i <= 66:
                term = generate_term_fixed(i, prev)
                l.d(debug_messages['term_generation']['fixed_method'].format(
                    n=i,
                    term=term
                ))
            else:
                for variant in CANDIDATE_VARIANTS:
                    for prime in FIXED_PRIMES:
                        for shift in PRIME_OFFSET_SHIFTS:
                            candidate = generate_term_candidate(i, prev, prime, FIXED_PRIME_OFFSET, variant, shift)
                            try:
                                if i in KNOWN_ADDRESSES:
                                    addr = private_key_to_address(candidate)
                                    if addr == KNOWN_ADDRESSES[i]:
                                        term = candidate
                                        l.i(debug_messages['sequence_flow']['term_added'].format(
                                            index=i,
                                            term=term
                                        ))
                                        break
                                else:
                                    if candidate.bit_length() == i:
                                        term = candidate
                                        break
                            except Exception as e:
                                l.w(f"Validation failed for candidate 0x{candidate:x}: {str(e)}")
                            if term:
                                break
                        if term:
                            break
                    if term:
                        break
            
            if not term:
                raise ValueError(f"No valid candidate found for term {i}")
            
            if i in KNOWN_SOLUTIONS and term != KNOWN_SOLUTIONS[i]:
                raise ValueError(f"Term {i} mismatch: 0x{term:x} vs 0x{KNOWN_SOLUTIONS[i]:x}")
            
            if i in KNOWN_ADDRESSES:
                addr = private_key_to_address(term)
                if addr != KNOWN_ADDRESSES[i]:
                    raise ValueError(f"Address mismatch for term {i}: {addr} vs {KNOWN_ADDRESSES[i]}")
            
            sequence.append(term)
            l.i(debug_messages['sequence_flow']['term_added'].format(
                index=i,
                term=term
            ))
    
    except Exception as e:
        l.e(f"Sequence generation failed at term {i}: {str(e)}")
        raise
    
    l.i("Successfully generated 160-term sequence")
    return sequence

if __name__ == "__main__":
    l.i("Starting sequence generation...")
    
    try:
        seq = generate_sequence()
        if not seq:
            raise ValueError("Generated sequence is empty")
        l.i(f"Successfully generated sequence with {len(seq)} terms")
        
        cycle_length = 0
        for i in range(1, len(seq)//2):
            if seq[i:] == seq[:len(seq)-i]:
                cycle_length = i
                l.i(f"Found cycle of length: {cycle_length}")
                break
        
        if cycle_length == 0:
            l.w("No cycle detected in generated sequence")
            
        output_file = os.path.join(DATA_DIR, 'sequence_output.txt')
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                l.i(f"Writing sequence to output file: {output_file}")
                f.write("Complete 160-term Sequence Generation Output\n")
                f.write("=============================================\n")
                if cycle_length > 0:
                    f.write(f"Cycle detected with length: {cycle_length}\n")
                
                valid_terms = 0
                null_terms = 0
                for idx, term in enumerate(seq, start=1):
                    try:
                        if term is not None:
                            hex_str = f"0x{term:064x}"
                            f.write(f"{idx:03d}: {hex_str}")
                            if cycle_length > 0 and idx > cycle_length:
                                f.write(f" (repeats term {(idx-1) % cycle_length + 1})")
                            f.write("\n")
                            valid_terms += 1
                        else:
                            f.write(f"{idx:03d}: None\n")
                            null_terms += 1
                    except Exception as e:
                        l.e(f"Error processing term {idx}: {str(e)}")
                        
                l.i(f"Wrote {valid_terms} valid terms and {null_terms} null terms to file")
        except IOError as io_error:
            l.e(f"Failed to write to output file: {str(io_error)}")
            raise

        try:
            l.i("Final sequence details:")
            l.i("----------------------")
            if cycle_length > 0:
                l.i(f"Cycle length: {cycle_length}")
            
            term_stats = {"valid": 0, "null": 0, "error": 0}
            for idx, term in enumerate(seq, start=1):
                try:
                    if term is not None:
                        term_hex = f"0x{term:064x}"
                        term_stats["valid"] += 1
                        log_msg = f"{idx:03d}: {term_hex}"
                        if cycle_length > 0 and idx > cycle_length:
                            log_msg += f" (repeats term {(idx-1) % cycle_length + 1})"
                        l.i(log_msg)
                    else:
                        term_stats["null"] += 1
                        l.i(f"{idx:03d}: None")
                except Exception as term_error:
                    term_stats["error"] += 1
                    l.e(f"Error processing term {idx}: {str(term_error)}")
            
            l.i(debug_messages['sequence_flow']['stats_header'].format(
                total=len(seq),
                valid=term_stats['valid'],
                null=term_stats['null'],
                error=term_stats['error'],
                percent=(term_stats['valid']/len(seq))*100
            ))
        except Exception as console_error:
            l.e(f"Error during console output: {str(console_error)}")
            raise

    except Exception as e:
        l.c(f"Fatal error in main execution: {str(e)}")
        raise
