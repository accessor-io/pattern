#!/usr/bin/env python3

import unittest
from quantum_solver import QuantumMaskSolver

class TestQuantumSolver(unittest.TestCase):
    def setUp(self):
        self.start_key = 0x0000000000000000000000000000000000000000000000000000000000000001
        self.solver = QuantumMaskSolver(self.start_key)

    def test_mask_evolution(self):
        """Test that masks are correctly generated for each puzzle"""
        masks = self.solver.mask_evolution
        self.assertEqual(len(masks), 6)  # 6 masks for puzzles 65-70
        
        # Verify each mask has correct number of bits set
        for i, mask in enumerate(masks):
            puzzle_num = i + 65
            binary = format(mask, '0256b')
            ones_count = binary.count('1')
            self.assertEqual(ones_count, puzzle_num, 
                           f"Mask for puzzle {puzzle_num} should have {puzzle_num} bits set")

    def test_bit_pattern_validation(self):
        """Test position-based bit pattern validation"""
        # Test case for puzzle 66 (should have 66 bits set)
        test_key = 0x3  # Has bits set at positions 0 and 1
        self.assertTrue(self.solver._validate_bit_pattern(test_key, 2))
        
        # Test case with wrong number of bits
        test_key = 0x7  # Has bits set at positions 0, 1, and 2
        self.assertFalse(self.solver._validate_bit_pattern(test_key, 2))

    def test_candidate_generation(self):
        """Test candidate generation with position-based matching"""
        puzzle_num = 66
        candidates = list(self.solver.generate_candidates(puzzle_num))
        
        # Verify each candidate has correct bit pattern
        for candidate in candidates[:10]:  # Check first 10 candidates
            binary = format(candidate, '0256b')
            # Count bits in first puzzle_num positions
            significant_bits = sum(1 for i in range(puzzle_num) if binary[255-i] == '1')
            self.assertEqual(significant_bits, puzzle_num,
                           f"Candidate should have {puzzle_num} bits in significant positions")

if __name__ == '__main__':
    unittest.main() 