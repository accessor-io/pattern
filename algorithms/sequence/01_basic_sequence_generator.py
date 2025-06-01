#!/usr/bin/env python3
"""
01_basic_sequence_generator.py - Basic Sequence Generator

This generator implements a dual-mode approach to sequence generation:
- Simple mode: Uses XOR operations with sequential constants and grid navigation
- Crypto mode: Leverages the Puzzle66Solver for cryptographic sequences

Features:
- Grid-based navigation for sequence position tracking
- Simple transformations for basic sequences
- Complex transformations for cryptographic applications
- Sequence validation capabilities

Used in:
- Sequence integrity verification
- Bitcoin puzzle solving operations
- Grid-based sequence navigation
"""

from src.btc_puzzle_solver.core import Puzzle66Solver
from src.btc_puzzle_solver.patterns.grid_movement import GridNavigator


class SequenceGenerator:
    def __init__(self, initial_value: int):
        self.initial_value = initial_value
        self.position = 0
        if initial_value == 1:
            self.mode = "simple"
            self.current = initial_value
            self.grid_nav = GridNavigator()
            self.grid_position = (0, 0)  # Initial grid position
        else:
            self.mode = "crypto"
            self.solver = Puzzle66Solver(initial_value)
            self.current = initial_value
            self.position = self.solver.position
            self.grid_position = (0, 0)

    def _next_transformation(self):
        if self.mode == "simple":
            # Simple transformation: XOR with sequential constants [2, 4, 15]
            simple_constants = [2, 4, 15]
            if self.position < len(simple_constants):
                factor = simple_constants[self.position]
                new_val = self.current ^ factor
            else:
                # If beyond defined simple constants, no further change
                new_val = self.current
            self.grid_position = self.grid_nav.move(self.position)
            self.current = new_val
            self.position += 1
            return new_val
        else:
            new_val, grid = self.solver.generate_next()
            self.current = new_val
            self.position = self.solver.position
            self.grid_position = grid
            return new_val

    def validate(self, sequence):
        generated = []
        for _ in range(len(sequence)):
            generated.append(self._next_transformation())
        return generated == list(sequence) 