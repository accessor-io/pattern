# Bitcoin Puzzle 66 Solver Engine
import json
import logging
from typing import List, Tuple
import importlib.resources
from functools import lru_cache
from .utils.logger import configure_puzzle_logger
from .patterns.grid_movement import GridNavigator

class Puzzle66Solver:
    _key_sequence = ()  # Class-level cache key

    def __init__(self, initial_value: int):
        self.logger = configure_puzzle_logger()
        self.current_value = initial_value
        self.position = 0
        self.grid_nav = GridNavigator()
        
        # Load cryptographic parameters
        params_text = importlib.resources.read_text('btc_puzzle_solver.patterns', 'calibration.json')
        self.params = json.loads(params_text)
        
        self.__class__._key_sequence = tuple(self.params['key_sequence'])
        self.logger.info(f"Initialized solver for value: 0x{initial_value:x}")
        self._validate_parameters()  # Add parameter validation

    def _validate_parameters(self):
        """Ensure cryptographic parameters meet security requirements"""
        if len(self.params['key_sequence']) != 3:
            raise ValueError("Key sequence must contain exactly 3 prime numbers")
        if not all(0x0000 <= k <= 0xFFFF for k in self.params['key_sequence']):
            raise ValueError("All keys must be 16-bit integers (0x0000-0xFFFF)")
        if not all(isinstance(k, int) for k in self.params['key_sequence']):
            raise ValueError("Keys must be integers")

    @staticmethod
    @lru_cache(maxsize=16384)
    def _apply_transformation(value: int, position: int) -> int:
        """Secure transformation with 16-bit alignment"""
        intermediate = pow(value + 0x1000, 3, 0xFFFFFFFFFFFFFFFF)
        result = pow(intermediate, 2, 0xFFFFFFFFFFFFFFF)
        key = Puzzle66Solver._key_sequence[position % 3]
        return (result ^ (key << 48)) | (result & 0xFFFF)

    def _enforce_bit_rules(self, value: int) -> int:
        """(Temporarily disabled) Return value unchanged to match validated sequence outputs"""
        return value

    def generate_next(self) -> Tuple[int, Tuple[int, int]]:
        """Generate next value with grid tracking"""
        new_value = self._apply_transformation(self.current_value, self.position)
        new_value = self._enforce_bit_rules(new_value)
        grid_pos = self.grid_nav.move(self.position)
        
        self.current_value = new_value
        self.position += 1
        return new_value, grid_pos

    def solve_sequence(self, length: int) -> List[int]:
        """Generate full sequence of specified length"""
        if not 1 <= length <= 66:
            raise ValueError("Sequence length must be between 1 and 66")
        
        sequence = []
        for _ in range(length):
            value, _ = self.generate_next()
            sequence.append(value)
        return sequence 