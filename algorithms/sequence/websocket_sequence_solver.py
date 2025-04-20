#!/usr/bin/env python3
import asyncio
import os
from aiohttp import WSMsgType, WSCloseCode, WebSocketError
from ecdsa import SigningKey, SECP256k1
import base58
import hashlib
from functools import wraps
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import with error handling
try:
    from decode_ascii_keys import CONTROL_CHAR_MAP, decode_hex_key
except ImportError as e:
    logger.error(f"Failed to import from decode_ascii_keys: {e}")
    logger.info("Ensure decode_ascii_keys.py is in the same directory")
    raise SystemExit(1)

# Known correct sequence values
KNOWN_SEQUENCE = {
    1: 0x1,
    2: 0x3,
    3: 0x7,
    4: 0x8,
    5: 0x15,
    6: 0x31,
    7: 0x4c,
    8: 0xe0,
    9: 0x1d3,
    10: 0x202,
    67: 0x730fc235c1942c1ae,  # Term 67
    68: None,  # To be found (68-bit)
    69: None,  # To be found (69-bit)
}

# Constants
BIT_68_MAX = (1 << 68) - 1
BIT_69_MAX = (1 << 69) - 1
T6_FINAL = 0x349b84b6431a6c4ef1

class WebSocketSequenceError(Exception):
    """Custom exception for sequence validation errors"""
    pass

class WebSocketSequenceSolver:
    def __init__(self):
        self.current_state = None
        self.errors = []
        self.solutions = {
            'T4': None,  # 68-bit solutions
            'T5': None,  # 69-bit solutions
            'T6': T6_FINAL
        }
        self.sequence_history = KNOWN_SEQUENCE.copy()
        logger.info("WebSocketSequenceSolver initialized with known sequence")

    def verify_sequence_pattern(self, index: int, value: int) -> bool:
        """Verify if value matches known sequence pattern"""
        if index in KNOWN_SEQUENCE and KNOWN_SEQUENCE[index] is not None:
            expected = KNOWN_SEQUENCE[index]
            if value != expected:
                logger.warning(f"Sequence mismatch at index {index}: "
                             f"got {hex(value)}, expected {hex(expected)}")
                return False
        return True

    async def validate_continuation_frame(self, key_bytes):
        """Validate 68-bit CONTINUATION frame sequence"""
        if len(key_bytes) * 8 != 68:
            raise WebSocketSequenceError("Invalid bit length for T4")
            
        if key_bytes[0] != 0x00:  # Must start with CONTINUATION opcode
            raise WebSocketSequenceError("T4 must start with CONTINUATION frame")
            
        value = int.from_bytes(key_bytes, 'big')
        if not self.verify_sequence_pattern(68, value):
            raise WebSocketSequenceError("Value doesn't match sequence pattern")
            
        return True

    async def validate_ping_pong_sequence(self, key_bytes):
        """Validate 69-bit PING/PONG sequence"""
        if len(key_bytes) * 8 != 69:
            raise WebSocketSequenceError("Invalid bit length for T5")
            
        if key_bytes[0] not in (0x09, 0x0A):  # PING/PONG frames
            raise WebSocketSequenceError("T5 must use PING/PONG frames")
            
        value = int.from_bytes(key_bytes, 'big')
        if not self.verify_sequence_pattern(69, value):
            raise WebSocketSequenceError("Value doesn't match sequence pattern")
            
        if self.solutions['T4'] and value <= self.solutions['T4']:
            raise WebSocketSequenceError("T5 must be greater than T4")
            
        return True

    def calculate_next_term(self, prev_terms):
        """Calculate next term based on sequence pattern"""
        # This is where we'd implement the actual sequence pattern
        # For now, returning None to indicate manual validation
        return None

    async def run_solver(self, candidate_generator):
        """Main solver loop"""
        try:
            self.current_state = WSMsgType.TEXT
            logger.info("Starting solver with known sequence validation")
            
            async for candidate in candidate_generator:
                try:
                    value = int.from_bytes(candidate, 'big')
                    bit_length = len(candidate) * 8
                    
                    if bit_length == 68:
                        if await self.validate_continuation_frame(candidate):
                            self.solutions['T4'] = value
                            logger.info(f"Found potential T4: {hex(value)}")
                            
                    elif bit_length == 69:
                        if await self.validate_ping_pong_sequence(candidate):
                            self.solutions['T5'] = value
                            logger.info(f"Found potential T5: {hex(value)}")
                    
                    if self.solutions['T4'] and self.solutions['T5']:
                        logger.info("Found valid sequence:")
                        print(f"T4 (68-bit): {hex(self.solutions['T4'])}")
                        print(f"T5 (69-bit): {hex(self.solutions['T5'])}")
                        break
                        
                except WebSocketSequenceError as e:
                    logger.debug(f"Sequence error: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Critical error in solver: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage with sequence validation
    async def sample_generator():
        """Generate test candidates matching known sequence pattern"""
        test_values = [
            # 68-bit test values (8.5 bytes)
            bytes.fromhex('0001000000000008'),  # CONTINUATION frame with correct pattern
            bytes.fromhex('0001000000000015'),  # Another test matching sequence
            
            # 69-bit test values (8.625 bytes)
            bytes.fromhex('0915151515151515FF'),  # PING frame
            bytes.fromhex('0A15151515151515FF'),  # PONG frame
        ]
        
        for value in test_values:
            bit_length = len(value) * 8
            decoded = decode_hex_key(value.hex(), validate_ws=True)
            logger.info(f"Testing {bit_length}-bit candidate: {decoded}")
            yield value

    async def main():
        try:
            solver = WebSocketSequenceSolver()
            await solver.run_solver(sample_generator())
        except Exception as e:
            logger.error(f"Error in main: {str(e)}")
            raise SystemExit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Solver stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise SystemExit(1) 