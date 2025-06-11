"""
Test Suite for Integrated Analysis Algorithm
"""

import unittest
import math
from integrated_analysis import IntegratedAnalyzer

class TestIntegratedAnalysis(unittest.TestCase):
    def setUp(self):
        self.analyzer = IntegratedAnalyzer()
        
        # Known sequence values for testing
        self.test_values = {
            66: 0x2832ed74f2b5e35ee,
            70: 0x349b84b6431a6c4ef1,
            75: 0x4c5ce114686a1336e07,
            80: 0xea1a5c66dcc11b5ad180,
            85: 0x11720c4f018d51b8cebba8
        }
        
    def test_transition_analysis(self):
        """Test transition analysis between values"""
        val1 = self.test_values[66]
        val2 = self.test_values[70]
        
        result = self.analyzer.analyze_transition(val1, val2)
        
        # Test structure
        self.assertIn('changes', result)
        self.assertIn('weights', result)
        self.assertIn('rounds', result)
        
        # Test changes
        self.assertGreater(result['changes']['count'], 0)
        self.assertLessEqual(result['changes']['ratio'], 1.0)
        
        # Test weights
        self.assertGreaterEqual(result['weights']['from'], 0)
        self.assertGreaterEqual(result['weights']['to'], 0)
        
        # Test rounds
        self.assertGreaterEqual(result['rounds']['count'], self.analyzer.min_permutations)
        
    def test_block_structure(self):
        """Test block structure analysis"""
        val1 = self.test_values[70]
        val2 = self.test_values[75]
        
        result = self.analyzer.analyze_block_structure(val1, val2)
        
        # Test structure
        self.assertIn('blocks', result)
        self.assertIn('statistics', result)
        
        # Test statistics
        stats = result['statistics']
        self.assertGreaterEqual(stats['avg_changes'], 0)
        self.assertGreaterEqual(stats['max_changes'], stats['min_changes'])
        self.assertLessEqual(stats['distribution'], 1.0)
        
    def test_security_properties(self):
        """Test security property calculations"""
        val1 = self.test_values[75]
        val2 = self.test_values[80]
        
        result = self.analyzer.calculate_security_properties(val1, val2)
        
        # Test structure
        self.assertIn('alpha', result)
        self.assertIn('n', result)
        self.assertIn('collision_resistance', result)
        
        # Test values
        self.assertLess(result['alpha'], 0.5)  # Paper requirement
        self.assertGreater(result['n'], 0)
        
        # Test collision resistance
        cr = result['collision_resistance']
        self.assertGreaterEqual(cr['bits'], self.analyzer.min_security_bits)
        
    def test_sequence_verification(self):
        """Test complete sequence verification"""
        val1 = self.test_values[80]
        val2 = self.test_values[85]
        
        result = self.analyzer.verify_sequence_properties(val1, val2)
        
        # Test structure
        self.assertIn('valid', result)
        self.assertIn('properties', result)
        self.assertIn('analysis', result)
        
        # Test properties
        props = result['properties']
        self.assertIn('changes_valid', props)
        self.assertIn('rounds_valid', props)
        self.assertIn('distribution_valid', props)
        self.assertIn('security_valid', props)
        
    def test_sequence_range(self):
        """Test analysis over a range of values"""
        values = [
            self.test_values[66],
            self.test_values[70],
            self.test_values[75]
        ]
        
        results = self.analyzer.analyze_sequence_range(values)
        
        # Test results
        self.assertEqual(len(results), len(values) - 1)
        for result in results:
            self.assertIn('valid', result)
            self.assertIn('properties', result)
            self.assertIn('analysis', result)
            
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test with same value
        result = self.analyzer.verify_sequence_properties(
            self.test_values[66],
            self.test_values[66]
        )
        self.assertFalse(result['valid'])  # Should fail on changes
        
        # Test with very different values
        result = self.analyzer.verify_sequence_properties(
            self.test_values[66],
            self.test_values[85]
        )
        self.assertIn('valid', result)
        
    def test_paper_requirements(self):
        """Test specific requirements from the paper"""
        val1 = self.test_values[66]
        val2 = self.test_values[70]
        
        result = self.analyzer.verify_sequence_properties(val1, val2)
        
        # Test minimum permutations
        self.assertGreaterEqual(
            result['analysis']['transition']['rounds']['count'],
            self.analyzer.min_permutations
        )
        
        # Test bit change requirement
        self.assertGreaterEqual(
            result['analysis']['transition']['changes']['ratio'],
            self.analyzer.min_bit_change
        )
        
        # Test security bits
        self.assertGreaterEqual(
            result['analysis']['security']['collision_resistance']['bits'],
            self.analyzer.min_security_bits
        )

if __name__ == '__main__':
    unittest.main() 