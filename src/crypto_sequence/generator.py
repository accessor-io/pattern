# Added grid pattern validation and enhanced bit adjustment
import json
import logging
from typing import List, Tuple

class SequenceGenerator:
    def __init__(self, initial_value: int, key_numbers: List[int] = [67, 12, 247]):
        self.logger = logging.getLogger('SequenceGenerator')
        self.logger.setLevel(logging.DEBUG)
        
        # Configure file handler
        fh = logging.FileHandler('sequence_transformations.log')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)
        
        self.logger.info(f"Initializing generator with value: 0x{initial_value:x}")
        self.logger.debug(f"Key numbers: {key_numbers}")
        self.current_value = initial_value
        self.key_numbers = key_numbers
        self.bit_target = 66
        self.grid_size = (5, 3)  # From 5x3 grid analysis
        self.movement_index = 0
        self.movement_pattern = [4,5,4,4,5,4,5,4]  # Documented directional pattern
        
        # Load calibration patterns
        with open('calibration_patterns.json') as f:
            self.calibration = json.load(f)

    def _transform_value(self, move_type: int) -> int:
        """Exact transformation from cryptographic analysis"""
        if move_type == 4:  # Right move
            # (value + 2)^4 XOR 67 pattern
            transformed = pow(self.current_value + 2, 4, 2**256)
            transformed ^= self.key_numbers[0]
        elif move_type == 5:  # Down move
            # (value XOR 12) * 247 pattern
            transformed = self.current_value ^ self.key_numbers[1]
            transformed = (transformed * self.key_numbers[2]) % 2**256
        return transformed

    def _adjust_bits(self, value: int) -> int:
        """Precision bit adjustment using calibration patterns"""
        def count_bits(v): return bin(v).count('1')
        
        current_bits = count_bits(value)
        strategy = self.calibration['bit_patterns']['66_bit_strategy']
        
        while current_bits != self.bit_target:
            if current_bits < self.bit_target:
                # Add bits following calibration pattern
                added = self._add_bits_strategically(value, strategy)
                value |= added
            else:
                # Remove bits from LSB regions
                value = self._remove_bits_strategically(value)
                
            current_bits = count_bits(value)
            
        return value

    def _add_bits_strategically(self, value: int, strategy: dict) -> int:
        """Strategic bit addition following calibration patterns"""
        added = 0
        # Try MSB region first
        msb_start, msb_end = map(int, strategy['msb_range'].split('-'))
        for pos in range(msb_end, msb_start-1, -1):
            if not (value & (1 << pos)):
                added |= (1 << pos)
                if count_bits(value | added) == self.bit_target:
                    break
                
        # If still need bits, use XOR zone
        if count_bits(value | added) < self.bit_target:
            xor_start, xor_end = map(int, strategy['xor_zone'].split('-'))
            for pos in range(xor_end, xor_start-1, -1):
                if not (value & (1 << pos)):
                    added |= (1 << pos)
                    if count_bits(value | added) == self.bit_target:
                        break
                    
        return added

    def _remove_bits_strategically(self, value: int) -> int:
        """Remove bits from LSB while preserving pattern"""
        lsb_positions = [i for i, bit in enumerate(bin(value)[2:]) if bit == '1']
        keep_positions = lsb_positions[:len(lsb_positions)-(self.bit_target)]
        for pos in keep_positions:
            value &= ~(1 << pos)
        return value

    def _update_grid_position(self, move_type: int):
        """5x3 grid navigation system from cryptographic analysis"""
        if move_type == 4:  # Right
            self.movement_index = (self.movement_index + 1) % len(self.movement_pattern)
        else:  # Down
            self.movement_index = (self.movement_index + 1) % len(self.movement_pattern)

    def next(self) -> Tuple[int, Tuple[int, int]]:
        """Generates next value with grid position tracking"""
        move_type = self.movement_pattern[self.movement_index]
        raw_value = self._transform_value(move_type)
        adjusted_value = self._adjust_bits(raw_value)
        
        self._update_grid_position(move_type)
        self.current_value = adjusted_value
        
        # Calculate grid position based on movement index
        grid_x = self.movement_index % self.grid_size[0]
        grid_y = self.movement_index // self.grid_size[0]
        return adjusted_value, (grid_x, grid_y)

    def validate(self, sequence: List[int]) -> bool:
        self.logger.info(f"Starting validation of {len(sequence)} terms")
        for i, expected in enumerate(sequence):
            actual = self._transform_value(i % 2 + 4)
            self.logger.debug(f"Term {i+1}: Expected 0x{expected:x} | Actual 0x{actual:x}")
            if actual != expected:
                self.logger.error(f"Validation failed at term {i+1}")
                self.logger.error(f"Expected: 0x{expected:x} | Actual: 0x{actual:x}")
                return False
        self.logger.info("Validation succeeded")
        return True    