"""
Test Runner with Detailed Output
"""

import unittest
import sys
from test_integrated import TestIntegratedAnalysis

def run_tests_with_details():
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegratedAnalysis)
    
    # Create test runner with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True
    )
    
    print("Running Integrated Analysis Tests")
    print("=" * 80)
    
    # Run tests
    result = runner.run(suite)
    
    # Print summary
    print("\nTest Summary")
    print("-" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed:")
        for failure in result.failures:
            print(f"\nTest: {failure[0]}")
            print(f"Error: {failure[1]}")
            
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests_with_details()
    sys.exit(0 if success else 1) 