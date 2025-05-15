# Project Structure Documentation

## Overview
This document provides a detailed overview of the project's structure, organization, and key components.

## Directory Structure

### 1. Source Code (`src/`)
#### Core Components
- `bitcoin_math/`
  - Mathematical operations specific to Bitcoin
  - Schnorr signature analysis
  - Cryptographic primitives

- `crypto_sequence/`
  - Sequence generation and analysis
  - Cryptographic operations
  - Pattern detection

- `btc_puzzle_solver/`
  - Core puzzle solving functionality
  - Analysis tools
  - Pattern recognition
  - Utility functions

#### Implementation Languages
- `python/`
  - Main Python implementations
  - Analysis scripts
  - Solver implementations
  - Utility functions

- `javascript/`
  - Web-based implementations
  - Hex to ASCII conversion
  - Sequence generation
  - Browser-based tools

#### Analysis and Pattern Detection
- `analysis/`
  - Sequence analysis
  - Pattern detection
  - Statistical analysis

- `patterns/`
  - Bit pattern analysis
  - Pattern recognition
  - Pattern visualization

### 2. Data Organization (`data/`)
#### Data Types
- `binary/`
  - Binary data files
  - Database files
  - Compiled resources

- `config/`
  - Configuration files
  - Settings
  - Environment variables

- `text/`
  - Text-based data
  - Log files
  - Documentation

- `json/`
  - JSON data files
  - Configuration
  - Analysis results

- `sequences/`
  - Generated sequences
  - Pattern data
  - Analysis results

### 3. Documentation (`docs/`)
#### Documentation Types
- Analysis notes
- API references
- User guides
- Architecture documentation
- Reports
- Security documentation

### 4. Libraries (`libraries/`)
#### Library Components
- `sequence/`
  - Sequence generation
  - Sequence analysis
  - Pattern detection

- `crypto/`
  - Cryptographic operations
  - Security primitives
  - Hash functions

- `solvers/`
  - Puzzle solving algorithms
  - Optimization tools
  - Analysis utilities

### 5. Version Control
- Git repositories
- Commit history
- Version tracking
- Change logs

## Key Files

### Core Implementation Files
- `src/bitcoin_math/schnorr_analysis.py`
- `src/crypto_sequence/generator.py`
- `src/btc_puzzle_solver/core.py`
- `src/python/find_btc_address.py`
- `src/javascript/hexToAscii.js`

### Configuration Files
- `data/config/Cargo.toml`
- `data/config/pyproject.toml`
- `data/config/foundry.toml`

### Analysis Files
- `src/analysis/analyze_sequence.py`
- `src/patterns/bit_pattern_2bit.py`
- `src/btc_puzzle_solver/analysis/sequence_properties.py`

## Dependencies
- Python packages
- JavaScript libraries
- Rust crates
- System dependencies

## Build and Installation
- Python package setup
- Rust crate configuration
- Build scripts
- Installation instructions

## Development Guidelines
- Code organization
- Naming conventions
- Documentation standards
- Testing requirements

## Maintenance
- Version control
- Dependency management
- Build process
- Deployment procedures 