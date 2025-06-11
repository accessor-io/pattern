import os
import shutil
from pathlib import Path

class ProjectReorganizer:
    def __init__(self):
        self.root = Path('.')
        self.new_structure = {
            'blockchain_scanners': {
                'ethereum': {
                    'node_scanner': [
                        'node_scanner.py',
                        'node.py',
                        'nodescraper.py',
                        'node_scan.log',
                        'node_scanner.log'
                    ],
                    'config': [
                        'src/ethereum/config/*'
                    ],
                    'data': [
                        'data/ethereum/node_scans/**/*'
                    ],
                    'logs': [
                        'scanner_20241031.log',
                        'scanner_20241101.log',
                        'eth_node_scan.log'
                    ]
                },
                'iotex': {
                    'scanner': [
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
                    'scanner': [
                        'src/token/**/*',
                        'token_scanner/*',
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
                    'scanners': [
                        'electrum wallet checker/wallet_tools/*.py'
                    ],
                    'data': [
                        'electrum wallet checker/wallet_tools/wallet_data/**/*'
                    ],
                    'logs': [
                        'electrum wallet checker/wallet_tools/*.log'
                    ]
                }
            },
            'server': {
                'core': [
                    'src/server/**/*'
                ],
                'logs': [
                    'logs/server/**/*',
                    'visitor_logs.log'
                ]
            },
            'utils': {
                'converters': [
                    'src/utils/converters/**/*'
                ],
                'logging': [
                    'src/utils/logging/**/*'
                ]
            },
            'tests': {
                'blockchain': [
                    'tests/test_ethereum/*',
                    'tests/test_iotex/*',
                    'tests/test_token_scanner/*'
                ],
                'wallet': [
                    'tests/test_wallet_tools/*'
                ]
            },
            'config': {
                'environment': [
                    'environment/config.yaml'
                ],
                'alchemy': [
                    'src/alchemy/config/**/*'
                ]
            }
        }

    def reorganize(self):
        """Reorganize project structure"""
        for category, subcats in self.new_structure.items():
            category_path = self.root / category
            category_path.mkdir(exist_ok=True)
            
            if isinstance(subcats, dict):
                for subcat, file_patterns in subcats.items():
                    subcat_path = category_path / subcat
                    subcat_path.mkdir(exist_ok=True)
                    self._move_files(file_patterns, subcat_path)
            else:
                self._move_files(subcats, category_path)

    def _move_files(self, patterns, dest_path):
        """Move files matching patterns to destination"""
        for pattern in patterns:
            for src in self.root.glob(pattern):
                if src.is_file():
                    dest_file = dest_path / src.name
                    shutil.copy2(src, dest_file)
                    print(f"Moved {src} -> {dest_file}")

    def create_readme(self):
        """Create README with new structure documentation"""
        readme = """# Project Structure

## Blockchain Scanners
- ethereum/
  - node_scanner/ (Ethereum node scanning tools)
  - config/ (Ethereum-specific configuration)
  - data/ (Node scan results)
  - logs/ (Scanner logs)
- iotex/
  - scanner/ (IoTeX network scanner)
  - data/ (Scan results and live data)
  - logs/ (IoTeX scanner logs)
- token/
  - scanner/ (Token scanning and analysis)
  - data/ (Token scan results)
  - logs/ (Token scanner logs)

## Wallet Tools
- electrum/
  - scanners/ (Electrum wallet analysis tools)
  - data/ (Wallet data and results)
  - logs/ (Scanner logs)

## Server
- core/ (Server implementation)
- logs/ (Server and visitor logs)

## Utils
- converters/ (Data conversion utilities)
- logging/ (Logging utilities)

## Tests
- blockchain/ (Blockchain scanner tests)
- wallet/ (Wallet tools tests)

## Config
- environment/ (Environment configuration)
- alchemy/ (Alchemy API configuration)
"""
        with open('README.md', 'w') as f:
            f.write(readme)

def main():
    reorganizer = ProjectReorganizer()
    reorganizer.reorganize()
    reorganizer.create_readme()
    print("\nProject reorganization complete!")

if __name__ == "__main__":
    main() 