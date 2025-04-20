import os
import shutil
from datetime import datetime

def create_directory_structure():
    """Create the new directory structure"""
    directories = [
        'src/alchemy/config',
        'src/alchemy/endpoints',
        'src/alchemy/token_scanner',
        'src/ethereum/node_scanner',
        'src/ethereum/config',
        'src/iotex/config',
        'src/token/scanner',
        'src/token/config',
        'src/utils/converters',
        'src/utils/logging',
        'src/server/config',
        'data/ethereum/node_scans',
        'data/iotex/live_data',
        'data/token_scans',
        'logs/ethereum',
        'logs/iotex',
        'logs/token_scanner',
        'logs/server',
        'tests/test_alchemy',
        'tests/test_ethereum',
        'tests/test_iotex',
        'tests/test_token_scanner'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def move_files():
    """Move files to their new locations"""
    file_moves = {
        # Alchemy files
        'alchemy/config.yaml': 'src/alchemy/config/',
        'alchemy/endpoint_checker.py': 'src/alchemy/endpoints/',
        'alchemy/endpoints.json': 'src/alchemy/endpoints/',
        'alchemy/token_scanner/scanner.py': 'src/alchemy/token_scanner/',
        'alchemy/token_scanner/config.yaml': 'src/alchemy/token_scanner/',
        
        # Ethereum files
        'ethereum-node-scanner/src/scanner.py': 'src/ethereum/node_scanner/',
        'ethereum-node-scanner/src/utils.py': 'src/ethereum/node_scanner/',
        
        # IoTeX files
        'iotex_data_retriever.py': 'src/iotex/',
        'iotex_live_data.json': 'data/iotex/live_data/',
        
        # Token scanner files
        'token_scanner/enhanced_scanner.py': 'src/token/scanner/',
        'token_scanner/config.yaml': 'src/token/config/',
        
        # Server files
        'server.py': 'src/server/',
        
        # Utils
        'environment/json_to_yaml_converter.py': 'src/utils/converters/',
        
        # Logs
        'logs/connections.db': 'logs/',
        'logs/visitor_logs.log': 'logs/server/',
    }
    
    for source, dest in file_moves.items():
        if os.path.exists(source):
            shutil.move(source, os.path.join(dest, os.path.basename(source)))

def organize_scan_data():
    """Organize scan data by date"""
    scan_files = [f for f in os.listdir() if f.startswith('eth_node_scan')]
    
    for file in scan_files:
        try:
            date_str = file.split('_')[3].split('.')[0]
            date = datetime.strptime(date_str, '%Y%m%d')
            date_folder = date.strftime('%Y-%m-%d')
            
            dest_dir = f'data/ethereum/node_scans/{date_folder}'
            os.makedirs(dest_dir, exist_ok=True)
            
            if os.path.exists(file):
                shutil.move(file, os.path.join(dest_dir, file))
        except (IndexError, ValueError):
            continue

def create_init_files():
    """Create __init__.py files in Python packages"""
    for root, dirs, files in os.walk('src'):
        for dir in dirs:
            init_file = os.path.join(root, dir, '__init__.py')
            if not os.path.exists(init_file):
                open(init_file, 'a').close()

def create_readme():
    """Create a basic README.md file"""
    readme_content = """# Blockchain Network Scanner

A comprehensive suite of tools for scanning and analyzing various blockchain networks.

## Components

- Alchemy Integration
- Ethereum Node Scanner
- IoTeX Data Retriever
- Token Scanner
- Network Server

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the components in their respective config files

3. Run the desired scanner:
   ```bash
   python -m src.ethereum.node_scanner.scanner
   ```

## Project Structure

[Directory structure here]

## License

[Your chosen license]
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)

def main():
    """Main reorganization function"""
    # Create new directory structure
    create_directory_structure()
    
    # Move files to new locations
    move_files()
    
    # Organize scan data
    organize_scan_data()
    
    # Create __init__.py files
    create_init_files()
    
    # Create README
    create_readme()
    
    print("Project reorganization complete!")

if __name__ == "__main__":
    main() 