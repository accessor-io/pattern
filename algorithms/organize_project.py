#!/usr/bin/python3
import os
import shutil
import re
from datetime import datetime

def create_directory_structure():
    # Main directories
    directories = [
        'src',
        'data',
        'tests',
        'docs',
        'scripts',
        'analysis',
        'output',
        'versions',
        'logs',
        'config'
    ]
    
    # Subdirectories with their purposes
    subdirectories = {
        'src': [
            'bitcoin_math',      # Bitcoin-related mathematical computations
            'elliptic_curves',   # Elliptic curve implementations
            'hash_chains',       # Hash chain analysis
            'number_theory',     # Number theory algorithms
            'visualization',     # Visualization tools
            'sequence',         # Sequence generation and analysis
            'patterns',         # Pattern detection and analysis
            'utils'             # Utility functions
        ],
        'analysis': [
            'bit_patterns',      # Bit pattern analysis
            'sequence_analysis', # Sequence analysis
            'mathematical',     # Mathematical analysis
            'statistical',      # Statistical analysis
            'visual'           # Visual analysis
        ],
        'output': [
            'reports',          # Analysis reports
            'visualizations',   # Generated visualizations
            'data_exports',     # Exported data
            'analysis_results'  # Analysis results
        ],
        'versions': [
            'sequence_generators', # Sequence generator versions
            'sequences',          # Generated sequences
            'archives'           # Archived versions
        ],
        'logs': [
            'analysis',         # Analysis logs
            'execution',        # Execution logs
            'errors',          # Error logs
            'debug'            # Debug logs
        ]
    }
    
    # Create main directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
    # Create subdirectories
    for main_dir, subs in subdirectories.items():
        for sub in subs:
            os.makedirs(os.path.join(main_dir, sub), exist_ok=True)

def organize_files():
    # File patterns and their destinations
    file_patterns = {
        # Version control and documentation
        r'.*\.md$': 'docs',
        r'.*\.pdf$': 'docs',
        r'requirements\.txt$': 'config',
        r'.*\.log$': 'logs/execution',
        
        # Source code
        r'bit_pattern.*\.py$': 'src/patterns',
        r'analyze.*\.py$': 'src/analysis',
        r'sequence_generator\.py$': 'src/sequence',
        r'verify.*\.py$': 'src/utils',
        r'test.*\.py$': 'tests',
        
        # Generated files and data
        r'sequence_\d{8}_\d{6}\.txt$': 'versions/sequences',
        r'sequence_generator_v.*\.py$': 'versions/sequence_generators',
        r'.*_analysis\.txt$': 'output/reports',
        r'.*\.json$': 'data',
        r'.*\.csv$': 'data',
        
        # Analysis files
        r'find_67.*\.py$': 'analysis/sequence_analysis',
        r'analyze_67\.py$': 'analysis/sequence_analysis',
        r'sequence_67_analysis\.py$': 'analysis/sequence_analysis',
        r'bit_position_analysis\.py$': 'analysis/bit_patterns',
        
        # Visualization files
        r'.*\.png$': 'output/visualizations',
        
        # Logs and debug files
        r'debug.*\.log$': 'logs/debug',
        r'error.*\.log$': 'logs/errors',
        r'analysis.*\.log$': 'logs/analysis'
    }
    
    # Move files to their appropriate directories
    for root, _, files in os.walk('.'):
        if 'node_modules' in root or '.git' in root or '__pycache__' in root:
            continue
            
        for file in files:
            source = os.path.join(root, file)
            
            # Skip the organization script itself
            if file == 'organize_project.py':
                continue
                
            # Find matching pattern and move file
            for pattern, dest in file_patterns.items():
                if re.match(pattern, file):
                    destination = os.path.join(dest, file)
                    os.makedirs(os.path.dirname(destination), exist_ok=True)
                    try:
                        if os.path.exists(source) and not os.path.exists(destination):
                            shutil.move(source, destination)
                            print(f"Moved {source} to {destination}")
                    except Exception as e:
                        print(f"Could not move {source} to {destination}: {str(e)}")
                    break

def create_readme():
    readme_content = """# Pattern Analysis Project

## Project Structure

### Source Code (`src/`)
- `bitcoin_math/` - Bitcoin-related mathematical computations
- `elliptic_curves/` - Elliptic curve implementations
- `hash_chains/` - Hash chain analysis
- `number_theory/` - Number theory algorithms
- `visualization/` - Visualization tools
- `sequence/` - Sequence generation and analysis
- `patterns/` - Pattern detection and analysis
- `utils/` - Utility functions

### Data and Resources (`data/`)
- Input data files
- Generated data files
- Configuration files

### Analysis (`analysis/`)
- `bit_patterns/` - Bit pattern analysis
- `sequence_analysis/` - Sequence analysis
- `mathematical/` - Mathematical analysis
- `statistical/` - Statistical analysis
- `visual/` - Visual analysis

### Output (`output/`)
- `reports/` - Analysis reports
- `visualizations/` - Generated visualizations
- `data_exports/` - Exported data
- `analysis_results/` - Analysis results

### Version Control (`versions/`)
- `sequence_generators/` - Sequence generator versions
- `sequences/` - Generated sequences
- `archives/` - Archived versions

### Logs (`logs/`)
- `analysis/` - Analysis logs
- `execution/` - Execution logs
- `errors/` - Error logs
- `debug/` - Debug logs

### Other Directories
- `tests/` - Test files and test suites
- `docs/` - Documentation and specifications
- `scripts/` - Utility scripts
- `config/` - Configuration files

## Setup

1. Install dependencies:
   ```bash
   pip install -r config/requirements.txt
   ```

## Usage

1. Sequence Generation:
   - Use scripts in `src/sequence/` to generate new sequences
   - Generated sequences are stored in `versions/sequences/`

2. Analysis:
   - Run analysis tools from `src/analysis/`
   - View results in `output/reports/`
   - Check visualizations in `output/visualizations/`

3. Pattern Detection:
   - Use pattern detection tools in `src/patterns/`
   - Results are stored in `output/analysis_results/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add license information here]
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)

def cleanup_empty_dirs():
    """Remove empty directories after organization"""
    for root, dirs, files in os.walk('.', topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):  # Check if directory is empty
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
            except Exception as e:
                print(f"Could not remove directory {dir_path}: {str(e)}")

def main():
    print("Creating directory structure...")
    create_directory_structure()
    
    print("\nOrganizing files...")
    organize_files()
    
    print("\nCleaning up empty directories...")
    cleanup_empty_dirs()
    
    print("\nCreating README.md...")
    create_readme()
    
    print("\nProject organization complete!")

if __name__ == "__main__":
    main() 