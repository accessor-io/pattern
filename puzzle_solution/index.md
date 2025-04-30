# Bitcoin Key Pattern Puzzle - Solution Index

This folder contains all the essential files for understanding and solving the Bitcoin key pattern puzzle.

## Core Files

- [5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3k.vb](5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3k.vb) - The original puzzle file containing Bitcoin private/public key pairs
- [README.md](README.md) - Overview of the puzzle and solution approach
- [workflow_solution.md](workflow_solution.md) - Step-by-step workflow explaining how to solve the puzzle
- [python_solution.py](python_solution.py) - Complete Python implementation of the solution

## Analysis Files

- [analysis_results.txt](analysis_results.txt) - Detailed analysis of the key patterns and mathematical relationships
- [derived_private_keys.txt](derived_private_keys.txt) - Analysis of the derived private keys and their patterns

## Utility Scripts

- [solve_bitcoin_pattern.py](solve_bitcoin_pattern.py) - Script for solving the Bitcoin pattern puzzle
- [base58_decode_attempt.py](base58_decode_attempt.py) - Utility for decoding Base58 strings

## Additional Resources

- [addresses/addresses.txt](addresses/addresses.txt) - List of Bitcoin addresses involved in the puzzle
- [tools/puzzle_deep_dive.py](tools/puzzle_deep_dive.py) - In-depth analysis tools for the puzzle

## Solution Steps

1. Extract and analyze keys from `5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3k.vb`
2. Discover the mathematical pattern in early keys (Fibonacci-influenced sequence)
3. Generate the complete key sequence of all 160 keys
4. Convert keys to ASCII to extract the hidden steganographic message
5. Find Bitcoin address patterns in the message
6. Apply character substitution ('l' to '1') to fix the address
7. Verify the final solution: `1CZqucvN1wZ4Gwq95dsNgj1xVjUcK3pcMQ`

For a detailed explanation of the solution process, see [workflow_solution.md](workflow_solution.md).

To run the Python solution script:
```bash
python python_solution.py
``` 