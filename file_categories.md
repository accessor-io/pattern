# File Categories

## 1. Bitcoin Core Components
### Mathematical Operations
- `src/bitcoin_math/schnorr_analysis.py` - Schnorr signature analysis
- `src/bitcoin_math/__init__.py` - Bitcoin math package initialization
- `src/bitcoin_math/seq.py` - Sequence operations
- `src/bitcoin_math/analyze_sequence.py` - Sequence analysis

### Cryptographic Operations
- `src/crypto_sequence/generator.py` - Sequence generation
- `src/crypto_sequence/sequence_generator.py` - Advanced sequence generation
- `src/crypto_sequence/__init__.py` - Crypto sequence package initialization

### Key Generation and Management
- `hex_sequence_analysis/bitcoin_sequence_generator.py` - Bitcoin-specific sequence generator
- `hex_sequence_analysis/key_sequence_generator.py` - Key sequence generator
- `organized/src/key32WIF.py` - WIF key generator
- `organized/src/key32addr.py` - Address generator
- `src/python/key_generator.py` - Key generation
- `src/python/bitcoin_generator.py` - Bitcoin-specific generator

## 2. Puzzle Solving
### Core Solvers
- `src/btc_puzzle_solver/core.py` - Core puzzle solving functionality
- `src/btc_puzzle_solver/cli.py` - Command-line interface
- `src/btc_puzzle_solver/__init__.py` - Package initialization
- `src/python/puzzle_solver.py` - Python implementation
- `src/python/puzzle_solver_backup.py` - Backup solver implementation

### Analysis Tools
- `src/btc_puzzle_solver/analysis/sequence_properties.py` - Sequence property analysis
- `src/python/puzzle_analyzer.py` - Puzzle analysis
- `src/python/pattern_analyzer.py` - Pattern analysis
- `src/python/number_pattern_analyzer.py` - Number pattern analysis
- `src/python/chain_analyzer.py` - Chain analysis
- `src/python/bitcoin_key_analyzer.py` - Key analysis

## 3. Sequence Generation and Analysis
### Generators
- `src/sequence/sequence_generator.py` - Main sequence generator
- `src/javascript/sequenceGenerator.js` - JavaScript sequence generator
- `libraries/sequence/generators/base_sequence_generator.py` - Base sequence generation
- `libraries/sequence/generators/sequence_generator.py` - Sequence generation
- `libraries/sequence/generators/crypto_sequence_generator.py` - Crypto sequence generation

### Analyzers
- `src/analysis/analyze_sequence.py` - Sequence analysis
- `src/analysis/analyze_67.py` - Specific sequence analysis
- `src/python/chain_analyzer.py` - Chain analysis
- `src/python/bitcoin_key_analyzer.py` - Key analysis

## 4. Pattern Detection and Analysis
### Pattern Recognition
- `src/patterns/bit_pattern_2bit.py` - 2-bit pattern analysis
- `src/patterns/bit_pattern_sequence.py` - Sequence pattern analysis
- `src/patterns/bit_pattern_views.py` - Pattern visualization
- `src/patterns/bit_pattern_base_convert.py` - Base conversion patterns
- `src/patterns/bit_pattern_crypto.py` - Cryptographic patterns
- `src/patterns/bit_pattern_entropy.py` - Entropy analysis
- `src/patterns/bit_pattern_math.py` - Mathematical patterns
- `src/patterns/bit_pattern_repetition.py` - Repetition patterns
- `src/patterns/bit_pattern_stats.py` - Statistical patterns
- `src/patterns/bit_pattern_transitions.py` - Transition patterns
- `src/patterns/bit_pattern_visual.py` - Visual pattern analysis
- `src/patterns/bit_pattern_runs.py` - Run pattern analysis
- `src/patterns/bit_pattern_hamming.py` - Hamming distance analysis
- `src/patterns/bit_pattern_sliding.py` - Sliding window analysis
- `src/patterns/bit_pattern_byte_ascii.py` - Byte/ASCII patterns
- `src/patterns/bit_pattern_4bit.py` - 4-bit pattern analysis

## 5. Data Processing
### Data Files
- `data/binary/bitcoin_analysis.db` - Analysis database
- `data/text/keww.txt` - Text data
- `data/text/bitcoin_addresses_fixed_order.txt` - Address data
- `data/text/puzzle_solutions_summary.txt` - Solution summaries
- `data/json/search_checkpoint.json` - Search checkpoints
- `data/json/calibration_patterns.json` - Calibration data
- `data/sequences/generated_sequence.txt` - Generated sequences
- `data/sequences/sequence.txt` - Sequence data

### Configuration
- `data/config/Cargo.toml` - Rust configuration
- `data/config/pyproject.toml` - Python configuration
- `data/config/foundry.toml` - Foundry configuration
- `data/config/con.bat` - Batch configuration

## 6. Utility Functions
### Python Utilities
- `src/utils/verify_candidates.py` - Candidate verification
- `src/utils/verify.py` - General verification
- `src/utils/verify_bitcoin.py` - Bitcoin verification
- `src/utils/verify_address.py` - Address verification
- `src/python/clean_addresses.py` - Address cleaning
- `src/python/check_dependencies.py` - Dependency checking

### JavaScript Utilities
- `src/javascript/hexToAscii.js` - Hex to ASCII conversion
- `src/javascript/hexToAsciiProcessor.js` - Hex processing
- `src/javascript/bookmarklet.js` - Browser tools

## 7. Documentation
### Analysis Documentation
- `docs/analysis_notes.md` - Analysis notes
- `docs/security_incident_report.md` - Security reports
- `docs/network_analysis_report.md` - Network analysis
- `docs/README.md` - Main documentation

## 8. Libraries
### Core Libraries
- `libraries/sequence/generators/base_sequence_generator.py` - Base sequence generation
- `libraries/sequence/generators/sequence_generator.py` - Sequence generation
- `libraries/sequence/generators/crypto_sequence_generator.py` - Crypto sequence generation

### Solver Libraries
- `libraries/solvers/sequence/x2_solver.py` - X2 solver
- `libraries/solvers/sequence/websocket_sequence_solver.py` - WebSocket solver

## 9. Version Control
### Git Information
- `.git/` - Git repository
- `commits.txt` - Commit history
- `tree.txt` - File tree

## 10. Build and Package
### Package Information
- `src/btc_puzzle_solver.egg-info/` - Python package info
- `src/crypto_sequence.egg-info/` - Crypto sequence package info
- `src/bitcoin_puzzle_solver.egg-info/` - Bitcoin puzzle solver package info

### Build Configuration
- `src/setup.py` - Python setup
- `src/logging_config.py` - Logging configuration 