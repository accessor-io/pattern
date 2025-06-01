# Crypto Libraries

This directory contains organized libraries for cryptocurrency-related operations, specifically focused on Bitcoin analysis and hex string manipulation.

## Structure

- `crypto/` - Main package for cryptocurrency-related code
  - `bitcoin/` - Bitcoin-specific analysis tools
    - `bitcoin_tx_analyzer.py` - Tools for analyzing Bitcoin transactions
    - `enhanced_tx_analysis.py` - Advanced transaction analysis utilities
    - `private_key_decoder.py` - Tools for working with Bitcoin private keys
  - `utils/` - General cryptocurrency utilities
    - `hex_string_fix.py` - Utilities for fixing and manipulating hex strings

- `solvers/` - Collection of specialized solvers
  - `bitcoin/` - Bitcoin puzzle solving algorithms
    - `bitcoin_puzzle67_pro_solver.py` - Solver for Bitcoin puzzle #67
    - `puzzle_solver_160.py` - Comprehensive solver for puzzles up to #160
    - `puzzle-solver.py` - Generic Bitcoin puzzle solver
  - `sequence/` - Sequence analysis and solving tools
    - `websocket_sequence_solver.py` - WebSocket-based sequence solver
    - `x2_solver.py` - X2 pattern sequence solver
  - `utils/` - Helper utilities for solvers
    - `combinatory_solver.py` - Combinatorial approach to solving puzzles
    - `test_solver.py` - Testing framework for solvers

- `sequence/` - Sequence generation and analysis tools
  - `generators/` - Various sequence generation tools
    - `sequence_generator.py` - Basic sequence generation
    - `crypto_sequence_generator.py` - Cryptographic sequence generation

## Usage

These libraries can be imported in your Python scripts as follows:

```python
# Import hex string utilities
from crypto.utils.hex_string_fix import test_all_positions, check_bitcoin_patterns

# Import Bitcoin analysis tools
from crypto.bitcoin.bitcoin_tx_analyzer import analyze_transaction
from crypto.bitcoin.private_key_decoder import decode_private_key

# Import solvers
from solvers.bitcoin.puzzle_solver_160 import solve_puzzle
from solvers.sequence.websocket_sequence_solver import WebSocketSequenceSolver
from solvers.utils.combinatory_solver import combinatory_solver

# Import sequence generators
from sequence.generators.sequence_generator import generate_sequence
from sequence.generators.crypto_sequence_generator import generate_crypto_sequence
```

## Development

When adding new functionality:
1. Place Bitcoin-specific code in the `crypto/bitcoin/` directory
2. Place general cryptocurrency utilities in the `crypto/utils/` directory
3. Place solver algorithms in the appropriate `solvers/` subdirectory
4. Place sequence generation tools in the `sequence/generators/` directory
5. Make sure to commit changes to Git with descriptive commit messages 

# Bitcoin Private Key Search for Term 68

This project contains specialized scripts designed to search for the Bitcoin private key corresponding to the address `1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ`.

## Target Information

- **Target Address**: `1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ`
- **Previous Term (67)**: `0x730fc235c1942c1ae`
- **Target Index**: 68 (key must be exactly 68 bits)
- **Predicted Min Value**: `0x8747dd8c268dd31c4`
- **Predicted Max Value**: `0xd7db28ca2b3a33c0c`

## Search Strategy

The search is divided into multiple specialized approaches:

### 1. Focused Search (`68_focused_search.py`)
- Explores values around specific predicted ranges
- Implements systematic bit searches
- Targets values near previous term and estimated ranges

### 2. Mathematical Patterns (`68_mathematical_patterns.py`)
- Applies various mathematical transformations
- Tests polynomial relationships
- Explores number theory transformations
- Applies fibonacci-like sequences and golden ratio transformations

### 3. Bitwise Operations (`68_bitwise_search.py`)
- Focuses exclusively on bit-level operations and patterns
- Implements targeted bit searches
- Explores hamming distance variations
- Tests bit rotations and operations

### 4. Exact Candidate Testing (`exact_candidate_test.py`)
- Tests specific candidate values identified from analysis
- Examines values around promising candidates

### 5. Range Analysis (`extract_min_max.py`)
- Analyzes prediction files to establish search boundaries
- Extracts minimum and maximum values from predictions

## Search Constraints

Candidate values must:
1. Be greater than the previous term (`0x730fc235c1942c1ae`)
2. Have exactly 68 bits set
3. Not have more than 3 consecutive identical hex characters
4. Generate the target Bitcoin address when used as a private key

## Usage

Each script can be run independently to explore different search strategies:

```
python 68_focused_search.py
python 68_mathematical_patterns.py
python 68_bitwise_search.py
python exact_candidate_test.py
python extract_min_max.py
```

## Results

If a matching private key is found, it will be saved to:
- `term68_solution.json` (JSON format)
- `term68_solution.txt` (plain text)

Additionally, detailed logs for each search approach are saved to their respective log files.

## Current Status

As of the current execution, the search has generated 321,270 unique candidates but has not yet found a match for the target Bitcoin address. 

# RowHammer-Inspired Search for Term 68

This project implements a search approach inspired by the RowHammer memory vulnerability to find the Bitcoin private key for Term 68 of the pattern sequence.

## Target Information
- **Target Bitcoin Address**: `1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ`
- **Previous Term (67)**: `0x730fc235c1942c1ae`

## What is RowHammer?

RowHammer is a hardware vulnerability in DRAM where repeatedly accessing certain memory rows causes bit flips in adjacent rows due to electrical interference. This project adapts insights from the RowHammer vulnerability to search for the private key that generates the target Bitcoin address.

Key concepts from RowHammer applied in this search:

1. **Targeted bit flips** - Certain bit positions are more susceptible to flips
2. **Pattern-based disturbances** - Specific access patterns cause predictable flips
3. **Adjacency effects** - Bits next to frequently accessed bits are more vulnerable
4. **Multiple attack patterns** - Various hammering techniques (single-sided, double-sided, half-double)

This search implementation is heavily inspired by research from the [Hammulator paper](https://dramsec.ethz.ch/papers/hammulator.pdf), which provides a framework for understanding and simulating RowHammer effects.

## Scripts

The repository contains three main scripts:

1. **rowhammer_search.py**: The main search script that runs continuously to find the private key.
2. **rowhammer_search_debug.py**: A simplified debug script to test and validate individual components.
3. **run_search.sh**: A launcher script that runs the continuous search with proper output redirection.

## Requirements

- Python 3.6+
- Required Python packages:
  - `hashlib` (standard library)
  - `base58`
  - `ecdsa`
  - `numpy`

Install the required packages with:
```
pip install base58 ecdsa numpy
```

## Usage

### Running the Continuous Search

To start the continuous search, run:
```
./run_search.sh
```

This will run the search until interrupted or a match is found. Output will be logged to:
- `rowhammer_search.log` (main log file)
- `logs/rowhammer_search_TIMESTAMP.log` (timestamped log file)

The search saves progress periodically and can be resumed after interruption.

### Running the Debug Script

For debugging or testing specific components:
```
./rowhammer_search_debug.py
```

This runs a simplified version of the search with more detailed output for each tested candidate.

## How It Works

The search uses several RowHammer-inspired techniques to systematically explore the search space:

1. **Systematic RowHammer**: Tests different bit patterns, simulating how RowHammer affects memory.
2. **Double-sided hammering**: Focuses on "sandwiching" target bits between two aggressor regions.
3. **Half-double attacks**: Tests bit flips at a distance of 2 bits from the aggressor bits.

The search adapts its parameters over time to improve efficiency, based on:
- Current best similarity achieved
- Number of iterations completed
- Random exploration to avoid local optima

## Files Generated

- `term68_rowhammer_result.json`: Contains the final result if a match is found
- `term68_solution.txt`: Human-readable solution information
- `rowhammer_closest_addresses.json`: Tracks candidates with the highest similarity
- `rowhammer_progress.json`: Saves search progress for resumption
- `term68_best_candidate.json`: Stores the best candidate found so far

## Self-Adaptive Search

The search automatically adjusts its parameters over time to optimize the search:

- After 50 iterations, the flip probability increases gradually
- If similarity exceeds 0.3, search focuses more on adjacent bits
- If similarity is below 0.1, search explores more widely
- Every 25 iterations, parameters are randomly adjusted to escape local optima

## Contributing

Feel free to experiment with parameter adjustments or additional RowHammer-inspired attack patterns. The Hammulator paper provides excellent insights into how RowHammer effects can be simulated and exploited. 