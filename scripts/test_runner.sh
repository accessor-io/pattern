#!/bin/bash
# Function to run tests and compare outputs
run_tests() {
    test_dir=$1
    echo "Running tests in $test_dir"
    # Example test command
    python test_solver.py --input "$test_dir/inputs/" --output "$test_dir/actual_outputs/"
    # Compare outputs
    diff "$test_dir/expected_outputs/" "$test_dir/actual_outputs/"
    if [ $? -eq 0 ]; then
        echo "Test results match expected outputs."
    else
        echo "Test discrepancies found."
    fi
}

# Run tests for each version
run_tests "/home/dot/pattern/tests/bitcoin/v3.0"
run_tests "/home/dot/pattern/tests/bitcoin/v4.0"
run_tests "/home/dot/pattern/tests/audio_processing/v3.0"
run_tests "/home/dot/pattern/tests/audio_processing/v4.0"
