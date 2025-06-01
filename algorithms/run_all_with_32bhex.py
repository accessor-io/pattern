#!/usr/bin/env python3

import os
import sys
import shutil
import importlib
import subprocess
from datetime import datetime

def update_changelog(message):
    """Log messages to CHANGELOG.md with timestamps"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('CHANGELOG.md', 'a') as f:
        f.write(f"\n## {timestamp}\n{message}\n")

def setup_data_paths():
    """Ensure data file is accessible from all required locations"""
    source_file = os.path.abspath('data/32bHex.txt')
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Source data file not found at {source_file}")
    
    # Create required data directories
    data_paths = [
        os.path.expanduser('~/data'),
        'src/data',
        '../data',
        '../../data'
    ]
    
    for path in data_paths:
        try:
            os.makedirs(path, exist_ok=True)
            target = os.path.join(path, '32bHex.txt')
            if os.path.exists(target):
                os.remove(target)
            shutil.copy2(source_file, target)
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not setup {path}: {str(e)}")

def run_module(script_path):
    """Run a Python module either by importing or as subprocess"""
    try:
        # Get the directory of the script
        script_dir = os.path.dirname(os.path.abspath(script_path))
        
        # Add script directory to Python path
        sys.path.insert(0, script_dir)
        
        # Convert file path to module path
        module_name = os.path.splitext(os.path.basename(script_path))[0]
        module = importlib.import_module(module_name)
        
        # Change to script directory
        original_dir = os.getcwd()
        os.chdir(script_dir)
        
        try:
            if hasattr(module, 'main'):
                module.main()
            elif hasattr(module, 'analyze'):
                module.analyze()
        finally:
            # Restore original directory
            os.chdir(original_dir)
            # Remove script directory from path
            sys.path.pop(0)
        
        update_changelog(f"Successfully completed: {script_path}")
        return True
    except Exception as e:
        update_changelog(f"Error running {script_path}: {str(e)}")
        return False

def main():
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Setup data paths first
    try:
        setup_data_paths()
        update_changelog("Data paths setup complete")
    except Exception as e:
        update_changelog(f"Error setting up data paths: {str(e)}")
        return

    # List of analysis scripts to run
    analysis_scripts = [
        'src/bit_pattern_2bit.py',
        'src/bit_pattern_4bit.py',
        'src/bitcoin_math/schnorr_analysis.py',
        'src/number_theory/modular_forms.py',
        'src/stark_analysis/witness_patterns.py',
        'src/stark_analysis/deep_analysis.py',
        'src/stark_analysis/enhanced_witness_patterns.py',
        'src/visualization_entropy.py',
        'src/visualization_sequence.py'
    ]

    # Run each analysis script
    for script in analysis_scripts:
        if os.path.exists(script):
            print(f"Running {script}...")
            update_changelog(f"Running analysis: {script}")
            
            try:
                # Try running as module first
                if not run_module(script):
                    # Fall back to subprocess if module import fails
                    result = subprocess.run([sys.executable, script], 
                                         capture_output=True, 
                                         text=True,
                                         cwd=os.path.dirname(os.path.abspath(script)))
                    if result.returncode == 0:
                        update_changelog(f"Successfully completed: {script}")
                    else:
                        update_changelog(f"Failed to run {script}: {result.stderr}")
            except Exception as e:
                update_changelog(f"Error processing {script}: {str(e)}")
        else:
            update_changelog(f"Script not found: {script}")

    update_changelog("Completed all analyses")

if __name__ == "__main__":
    main() 