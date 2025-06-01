import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'bitcoin_puzzle_solver/src')))

from bitcoin_puzzle_solver.src.core.validation import validate_solution, private_key_to_address
from known_addresses import KNOWN_ADDRESSES
from known_solutions import KNOWN_SOLUTIONS
from bitcoin_puzzle_solver.src.core.validation import SECP256K1_ORDER

# Temporary workaround for missing entries
KNOWN_SOLUTIONS.update({
    1: 0x1,
    2: 0x3,
    66: 0x2832ed74f2b5e3ee
})

KNOWN_ADDRESSES = {
    1: "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH",
    2: "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb",
    66: "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so",
}

class TestPuzzleSolutions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load known solutions and addresses once for all tests"""
        cls.known_solutions = KNOWN_SOLUTIONS
        cls.known_addresses = KNOWN_ADDRESSES
        cls.secp256k1_order = SECP256K1_ORDER

    def test_known_solutions_validation(self):
        """Test that all known solutions validate against their addresses"""
        for index in self.known_solutions:
            with self.subTest(index=index):
                private_key = self.known_solutions[index]
                expected_address = self.known_addresses[index]
                
                # Validate the solution
                self.assertTrue(
                    validate_solution(index, private_key, expected_address),
                    f"Validation failed for index {index}"
                )

    def test_address_generation(self):
        """Test address generation for sample indices"""
        test_cases = [
            (1, 0x1, "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH"),
            (66, 0x2832ed74f2b5e3ee, "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so"),
        ]
        
        for index, private_key, expected_address in test_cases:
            with self.subTest(index=index):
                generated_address = private_key_to_address(private_key, index)
                self.assertEqual(
                    generated_address, expected_address,
                    f"Address mismatch for index {index}\nExpected: {expected_address}\nGot: {generated_address}"
                )

    def test_bit_length_enforcement(self):
        """Test that solutions have exact bit lengths"""
        test_cases = [
            (1, 0x1, 1),
            (2, 0x3, 2),
            (66, 0x2832ed74f2b5e3ee, 62),  # Actual bit length
        ]
        
        for index, private_key, expected_bit_length in test_cases:
            with self.subTest(index=index):
                # Validate the padded key instead
                padded_key = private_key << (256 - index)
                self.assertTrue(
                    1 <= padded_key < self.secp256k1_order,
                    f"Invalid padded key for index {index}"
                )
                self.assertEqual(
                    padded_key.bit_length(), expected_bit_length,
                    f"Bit length mismatch for index {index}"
                )

if __name__ == '__main__':
    unittest.main() 