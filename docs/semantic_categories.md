# Semantic Categories of Files

## 1. Core Sequence Generation

### Base Sequence Generators
- `sequence_generator.py` — Abstract base/interface for sequence generators.
- `01_basic_sequence_generator.py` — Basic sequential number generator.
- `02_prime_sequence_generator.py` — Prime number sequence generator.
- `03_optimized_sequence_generator.py` — Performance-optimized sequence generator.
- `04_advanced_sequence_generator.py` — Advanced sequence generation algorithms/features.
- `algorithms/sequence/sequence_generator.py`
- `algorithms/sequence/generators/` (folder: all generator implementations)
- `algorithms/sequence/combined_sequence_generator.py`
- `algorithms/sequence/optimized_sequence.py`
- `algorithms/sequence/prime_sequence.py`
- `combined_sequence_generator.py`
- `optimized_sequence.py`
- `prime_sequence.py`

### Specialized Sequence Generators
- `presleys_non_linear_bit_permutation_sequence.py` — Non-linear bit permutation sequence generator.

### Sequence Analysis Tools
- `01_sequence_analyzer.py` — Base sequence analyzer.
- `02_pattern_sequence_analyzer.py` — Pattern-based sequence analyzer.
- `03_hex_sequence_analyzer.py` — Hexadecimal sequence analyzer.
- `04_sequence_predictor.py` — Sequence prediction tool.
- `algorithms/sequence/analyzers/01_sequence_analyzer.py`
- `algorithms/sequence/analyzers/02_pattern_sequence_analyzer.py`
- `algorithms/sequence/analyzers/03_hex_sequence_analyzer.py`
- `algorithms/sequence/analyzers/04_sequence_predictor.py`
- `pattern_analyzer.py`
- `solvers/helpers/pattern_analyzer.py`
- `sequence_proof.py`
- `validate_sequence.py`
- `solvers/validate_sequence.py`
- `priority_analysis.py`
- `input_string_analysis.py`

### Sequence Position Finders
- `find_67.py` — Finder for position 67 in sequences.
- `find_67_optimized.py` — Optimized finder for position 67.
- `find_67_complete.py` — Complete finder for position 67.
- `find_68_complete.py` — Complete finder for position 68.
- `find_67_with_hex.py` — Hex-based finder for position 67.
- `generate_full_sequence.py`
- `solvers/generate_full_sequence.py`

### General Sequence Finders and Utilities
- `sequence_finder.py` — General-purpose sequence finder.
- `constant_offset_finder.py` — Analyzer for constant offsets in sequences.
- `solvers/archive/constant_offset_finder.py`
- `p2sh_analyzer.py` — P2SH sequence analyzer.
- `solvers/archive/p2sh_analyzer.py`
- `convert_hex.py`
- `hex_possibilities.py`
- `hex_partition_analyzer.c`
- `permutation_proof.py`

### Bitcoin-Specific Sequence Generators and Utilities
- `bitcoin_sequence_generator.py` — Bitcoin-specific sequence generator (e.g., for private keys).
- `key_sequence_generator.py` — General key sequence generator (private/public).
- `key32WIF.py` — Wallet Import Format (WIF) private key generator.
- `key32addr.py` — Bitcoin address generator from public keys.
- `private_key_generator.py` — Bitcoin private key generator (random/range).
- `public_key_derivation.py` — Public key derivation (compressed/uncompressed).
- `address_derivation_p2pkh.py` — P2PKH address generator.
- `address_derivation_p2sh.py` — P2SH address generator.
- `address_derivation_bech32.py` — Bech32 (SegWit) address generator.
- `bip39_mnemonic_generator.py` — BIP39 mnemonic phrase generator.
- `bip39_seed_from_mnemonic.py` — Seed generator from BIP39 mnemonic.
- `bip32_master_key_generator.py` — BIP32 master key generator (xprv/xpub).
- `bip32_child_key_derivation.py` — BIP32 child key derivation.
- `vanity_address_generator.py` — Vanity address generator (custom prefix).
- `multisig_address_generator.py` — Multi-signature address/redeem script generator.
- `bitcoin_utils/address_derivation_bech32.py`
- `bitcoin_utils/address_derivation_p2pkh.py`
- `bitcoin_utils/address_derivation_p2sh.py`
- `bitcoin_utils/candidate_generator.py`
- `bitcoin_utils/integration.py`
- `bitcoin_utils/private_key_generator.py`
- `bitcoin_utils/public_key_derivation.py`
- `hex_sequence_analysis/bitcoin_sequence_generator.py`
- `hex_sequence_analysis/key_sequence_generator.py`
- `bitcoin_hd_wallet/bip32_child_key_derivation.py`
- `bitcoin_hd_wallet/bip32_master_key_generator.py`
- `bitcoin_hd_wallet/bip39_mnemonic_generator.py`
- `bitcoin_hd_wallet/bip39_seed_from_mnemonic.py`
- `multisig/multisig_address_generator.py`

### Candidate Generators
- `high_quality_generator.py` — High-quality candidate generator.
- `candidate_generator.py` — Bitcoin-focused candidate generator.
- `integration.py` — Enhanced candidate generator integration.
- `candidate_generation/high_quality_generator.py`
- `bitcoin_utils/candidate_generator.py`

### Crypto Analysis and Visualization
- `algorithms/crypto/crypto_advanced_analysis.py`
- `algorithms/crypto/crypto_chain_analyzer.py`
- `algorithms/crypto/crypto_visualizer.py`
- `base58_deep_analysis.py`
- `base58_pattern_check.py`

### Puzzle and Pattern Solvers
- `puzzle_solution/analyze_pubkey_pattern.py`
- `puzzle_solution/solve_bitcoin_pattern.py`
- `puzzle_solution/tools/puzzle_deep_dive.py`
- `solve_bitcoin_pattern.py`
- `puzzle-solver.py`
- `solvers/puzzle-solver.py`
- `crypto_sequence_solver.py`
- `solvers/crypto_sequence_solver.py`

### Transaction and Address Analysis
- `tx_pattern_analysis.py`

### Versioned and Experimental Code
- `versions/seq_deepseek_01.py`
- `versions/seq_deepseek_01 copy.py`
- `versions/seq_deepseek_01 copy 2.py`
- `versions/seq_deepseek_01 copy 3.py`
- `versions/seq_deepseek_01 copy 4.py`
- `versions/seq_deepseek_01 copy 5.py`
- `versions/seq_deepseek_01 copy 6.py`
- `versions/seq_deepseek_01 copy 7.py`
- `versions/sequence_generators/`

### Organized and Analysis Folders
- `organized/src/`
- `organized/analysis/sequence_analysis/`

### Miscellaneous Utilities and Scripts
- `priority_analysis.py`
- `sequence_proof.py`
- `input_string_analysis.py`

### Archive and Legacy Code
- `solvers/archive/constant_offset_finder.py`
- `solvers/archive/p2sh_analyzer.py`

### Folders (by semantic purpose)
- `algorithms/sequence/`
- `algorithms/sequence/generators/`
- `algorithms/sequence/analyzers/`
- `algorithms/crypto/`
- `hex_sequence_analysis/`
- `bitcoin_utils/`
- `bitcoin_hd_wallet/`
- `bitcoin_vanity/`
- `multisig/`
- `candidate_generation/`
- `organized/src/`
- `organized/analysis/sequence_analysis/`
- `solvers/archive/`
- `solvers/helpers/`
- `puzzle_solution/`
- `versions/`

---

## All Tracked Files (Complete List)

- 01_basic_sequence_generator.py
- 01_sequence_analyzer.py
- 02_pattern_sequence_analyzer.py
- 02_prime_sequence_generator.py
- 03_hex_sequence_analyzer.py
- 03_optimized_sequence_generator.py
- 04_advanced_sequence_generator.py
- 04_sequence_predictor.py
- address_derivation_bech32.py
- address_derivation_p2pkh.py
- address_derivation_p2sh.py
- algorithms/crypto/crypto_advanced_analysis.py
- algorithms/crypto/crypto_chain_analyzer.py
- algorithms/crypto/crypto_visualizer.py
- algorithms/sequence/analyzers/01_sequence_analyzer.py
- algorithms/sequence/analyzers/02_pattern_sequence_analyzer.py
- algorithms/sequence/analyzers/03_hex_sequence_analyzer.py
- algorithms/sequence/analyzers/04_sequence_predictor.py
- algorithms/sequence/combined_sequence_generator.py
- algorithms/sequence/generators/
- algorithms/sequence/optimized_sequence.py
- algorithms/sequence/prime_sequence.py
- algorithms/sequence/sequence_generator.py
- base58_deep_analysis.py
- base58_pattern_check.py
- bitcoin_hd_wallet/bip32_child_key_derivation.py
- bitcoin_hd_wallet/bip32_master_key_generator.py
- bitcoin_hd_wallet/bip39_mnemonic_generator.py
- bitcoin_hd_wallet/bip39_seed_from_mnemonic.py
- bitcoin_utils/address_derivation_bech32.py
- bitcoin_utils/address_derivation_p2pkh.py
- bitcoin_utils/address_derivation_p2sh.py
- bitcoin_utils/candidate_generator.py
- bitcoin_utils/integration.py
- bitcoin_utils/private_key_generator.py
- bitcoin_utils/public_key_derivation.py
- candidate_generation/high_quality_generator.py
- candidate_generator.py
- combined_sequence_generator.py
- constant_offset_finder.py
- convert_hex.py
- crypto_sequence_solver.py
- find_67.py
- find_67_complete.py
- find_67_optimized.py
- find_67_with_hex.py
- find_68_complete.py
- generate_full_sequence.py
- hex_partition_analyzer.c
- hex_possibilities.py
- hex_sequence_analysis/bitcoin_sequence_generator.py
- hex_sequence_analysis/key_sequence_generator.py
- input_string_analysis.py
- integration.py
- key32WIF.py
- key32addr.py
- multisig/multisig_address_generator.py
- optimized_sequence.py
- pattern_analyzer.py
- permutation_proof.py
- presleys_non_linear_bit_permutation_sequence.py
- prime_sequence.py
- priority_analysis.py
- private_key_generator.py
- public_key_derivation.py
- puzzle_solution/analyze_pubkey_pattern.py
- puzzle_solution/solve_bitcoin_pattern.py
- puzzle_solution/tools/puzzle_deep_dive.py
- puzzle-solver.py
- sequence_finder.py
- sequence_generator.py
- sequence_proof.py
- solve_bitcoin_pattern.py
- solvers/archive/constant_offset_finder.py
- solvers/archive/p2sh_analyzer.py
- solvers/crypto_sequence_solver.py
- solvers/generate_full_sequence.py
- solvers/helpers/pattern_analyzer.py
- solvers/puzzle-solver.py
- solvers/validate_sequence.py
- tx_pattern_analysis.py
- vanity_address_generator.py
- validate_sequence.py
- versions/seq_deepseek_01 copy 2.py
- versions/seq_deepseek_01 copy 3.py
- versions/seq_deepseek_01 copy 4.py
- versions/seq_deepseek_01 copy 5.py
- versions/seq_deepseek_01 copy 6.py
- versions/seq_deepseek_01 copy 7.py
- versions/seq_deepseek_01 copy.py
- versions/seq_deepseek_01.py
- versions/sequence_generators/
- organized/src/
- organized/analysis/sequence_analysis/
- bitcoin_vanity/
- candidate_generation/
- multisig/
- solvers/archive/
- solvers/helpers/
- puzzle_solution/
- algorithms/sequence/
- algorithms/sequence/generators/
- algorithms/sequence/analyzers/
- algorithms/crypto/
- hex_sequence_analysis/
- bitcoin_utils/
- bitcoin_hd_wallet/
- ... (and all other files in the project, including all files in all subfolders)

_Last updated: [Current Date]_