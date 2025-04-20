from pathlib import Path
import shutil
import os

class ProjectReorganizer:
    def __init__(self):
        self.root = Path('.')
        self.structure = {
            'blockchain_scanners': {
                'ethereum': {
                    'src': [
                        'src/ethereum/**/*',
                        'ethereum-node-scanner/src/**/*',
                        'node.py',
                        'node_scanner.py',
                        'nodescraper.py'
                    ],
                    'data': [
                        'data/ethereum/**/*'
                    ],
                    'logs': [
                        'logs/ethereum/*',
                        'eth_node_scan.log',
                        'node_scan.log',
                        'node_scanner.log'
                    ]
                },
                'iotex': {
                    'src': [
                        'src/iotex/**/*'
                    ],
                    'data': [
                        'data/iotex/**/*',
                        'iotex_scan_results.json'
                    ],
                    'logs': [
                        'logs/iotex/*'
                    ]
                },
                'token': {
                    'src': [
                        'src/token/**/*',
                        'src/alchemy/token_scanner/**/*',
                        'crypto_bucket_scanner.py'
                    ],
                    'data': [
                        'data/token_scans/**/*',
                        'crypto_bucket_results/**/*'
                    ],
                    'logs': [
                        'logs/token_scanner/*'
                    ]
                }
            },
            'wallet_tools': {
                'electrum': {
                    'src': [
                        'electrum wallet checker/wallet_tools/*.py'
                    ],
                    'data': [
                        'electrum wallet checker/wallet_tools/wallet_data/**/*'
                    ],
                    'logs': [
                        'electrum wallet checker/wallet_tools/*.log'
                    ],
                    'text': [
                        'electrum wallet checker/text/**/*'
                    ]
                }
            },
            'server': {
                'src': [
                    'src/server/**/*',
                    'server/core/**/*'
                ],
                'logs': [
                    'logs/server/**/*',
                    'server/logs/**/*',
                    'visitor_logs.log'
                ]
            },
            'config': {
                'environment': [
                    'environment/config.yaml'
                ],
                'alchemy': [
                    'src/alchemy/config/**/*',
                    'config/alchemy/**/*'
                ]
            },
            'utils': {
                'converters': [
                    'src/utils/converters/**/*',
                    'utils/converters/**/*'
                ],
                'logging': [
                    'src/utils/logging/**/*',
                    'utils/logging/**/*'
                ]
            },
            'tests': {
                'blockchain': [
                    'tests/test_ethereum/**/*',
                    'tests/test_iotex/**/*',
                    'tests/test_token_scanner/**/*',
                    'tests/test_alchemy/**/*'
                ],
                'wallet': [
                    'tests/wallet/**/*'
                ]
            }
        }

    def clean_directory(self, path: Path):
        """Remove empty directories"""
        for item in path.glob('**/*'):
            if item.is_dir() and not any(item.iterdir()):
                item.rmdir()

    def copy_files(self, patterns: list, dest_path: Path):
        """Copy files while maintaining structure"""
        for pattern in patterns:
            for src in self.root.glob(pattern):
                if src.is_file():
                    # Maintain relative path structure
                    rel_path = src.relative_to(src.parts[0])
                    dest_file = dest_path / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest_file)
                    print(f"Copied: {src} -> {dest_file}")

    def reorganize(self):
        """Reorganize project structure"""
        print("Starting project reorganization...")
        
        # Create new structure
        for category, contents in self.structure.items():
            category_path = self.root / category
            category_path.mkdir(exist_ok=True)
            
            if isinstance(contents, dict):
                for subcategory, patterns in contents.items():
                    if isinstance(patterns, dict):
                        # Handle nested structure
                        subcat_path = category_path / subcategory
                        subcat_path.mkdir(exist_ok=True)
                        for section, section_patterns in patterns.items():
                            section_path = subcat_path / section
                            section_path.mkdir(exist_ok=True)
                            self.copy_files(section_patterns, section_path)
                    else:
                        # Handle flat structure
                        subcat_path = category_path / subcategory
                        subcat_path.mkdir(exist_ok=True)
                        self.copy_files(patterns, subcat_path)

        # Clean up empty directories
        self.clean_directory(self.root)
        print("\nReorganization complete!")

    def create_readme(self):
        """Create README with new structure documentation"""
        readme = """# Project Structure

## Blockchain Scanners
- ethereum/
  - src/ (Ethereum node scanning implementation)
  - data/ (Scan results and node data)
  - logs/ (Scanner logs)
- iotex/
  - src/ (IoTeX network scanner)
  - data/ (Live data and results)
  - logs/ (Operation logs)
- token/
  - src/ (Token scanning implementation)
  - data/ (Scan results)
  - logs/ (Scanner logs)

## Wallet Tools
- electrum/
  - src/ (Address extraction and analysis)
  - data/ (Wallet data and results)
  - logs/ (Operation logs)
  - text/ (Text outputs)

## Server
- src/ (Server implementation)
- logs/ (Server and visitor logs)

## Config
- environment/ (Global configuration)
- alchemy/ (Alchemy API configuration)

## Utils
- converters/ (Data conversion utilities)
- logging/ (Logging utilities)

## Tests
- blockchain/ (Blockchain scanner tests)
- wallet/ (Wallet tools tests)
"""
        with open('README.md', 'w') as f:
            f.write(readme)
        print("Created new README.md")

def main():
    reorganizer = ProjectReorganizer()
    reorganizer.reorganize()
    reorganizer.create_readme()

if __name__ == "__main__":
    main() 