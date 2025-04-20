from pathlib import Path
import shutil
import os
import toml

class ProjectFixer:
    def __init__(self):
        self.root = Path('.')
        
        # Define consolidated structure
        self.new_structure = {
            'src': {
                'server': [
                    'src/server/*.py',
                    'src/server/api/*.py',
                    'src/server/models/*.py'
                ],
                'scanners': [
                    'src/scanners/*/*.py',
                    'src/scanners/*/*/*.py'
                ]
            },
            'config': {
                'scanners': [
                    'src/**/config/*.py'
                ]
            },
            'wallet_tools': {
                'electrum': [
                    'electrum wallet checker/wallet_tools/*.py'
                ],
                'data': [
                    'electrum wallet checker/wallet_tools/wallet_data/**/*.json',
                    'electrum wallet checker/wallet_tools/wallet_data/**/*.txt'
                ]
            }
        }

    def create_requirements(self):
        """Create requirements.txt with all dependencies"""
        requirements = {
            'web': [
                'aiohttp',
                'flask',
                'requests'
            ],
            'data_science': [
                'numpy',
                'pandas',
                'sklearn',
                'tensorflow',
                'textblob'
            ],
            'network': [
                'whois',
                'geoip2',
                'dnspython'
            ],
            'utils': [
                'rich',
                'psutil',
                'pyyaml'
            ]
        }

        # Write requirements.txt
        with open('requirements.txt', 'w') as f:
            for category, deps in requirements.items():
                f.write(f"# {category.title()} Dependencies\n")
                for dep in deps:
                    f.write(f"{dep}\n")
                f.write("\n")

        # Write pyproject.toml
        project_config = {
            'tool': {
                'poetry': {
                    'name': "blockchain-tools",
                    'version': "0.1.0",
                    'description': "Blockchain scanning and analysis tools",
                    'dependencies': {
                        dep: "*" for deps in requirements.values() for dep in deps
                    }
                }
            }
        }
        
        with open('pyproject.toml', 'w') as f:
            toml.dump(project_config, f)

    def fix_imports(self):
        """Update import statements in Python files"""
        for py_file in self.root.glob('src/**/*.py'):
            self._update_imports(py_file)

    def _update_imports(self, file_path: Path):
        """Update imports in a single file"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Update relative imports
        updates = {
            'from server': 'from src.server',
            'from utils': 'from src.utils',
            'from scanners': 'from src.scanners'
        }

        for old, new in updates.items():
            content = content.replace(old, new)

        with open(file_path, 'w') as f:
            f.write(content)

    def reorganize(self):
        """Reorganize project structure"""
        for category, contents in self.new_structure.items():
            category_path = self.root / category
            category_path.mkdir(exist_ok=True)
            
            if isinstance(contents, dict):
                for subcat, patterns in contents.items():
                    subcat_path = category_path / subcat
                    subcat_path.mkdir(exist_ok=True)
                    
                    if isinstance(patterns, list):
                        for pattern in patterns:
                            self._copy_files(pattern, subcat_path)
                    elif isinstance(patterns, dict):
                        for section, section_patterns in patterns.items():
                            section_path = subcat_path / section
                            section_path.mkdir(exist_ok=True)
                            for pattern in section_patterns:
                                self._copy_files(pattern, section_path)

    def _copy_files(self, pattern: str, dest_path: Path):
        """Copy files while maintaining structure"""
        for src in self.root.glob(pattern):
            if src.is_file():
                # Get the last two parts of the path (e.g., 'server/file.py')
                parts = src.parts[-2:]
                # Create destination path without repeating directories
                dest_file = dest_path.joinpath(*parts)
                
                # Skip if already exists
                if dest_file.exists():
                    continue
                
                # Create parent directory if needed
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(src, dest_file)
                    print(f"Copied {src} -> {dest_file}")
                except Exception as e:
                    print(f"Error copying {src}: {e}")

def main():
    fixer = ProjectFixer()
    print("Creating requirements files...")
    fixer.create_requirements()
    print("Fixing imports...")
    fixer.fix_imports()
    print("Reorganizing project structure...")
    fixer.reorganize()
    print("Project fixes complete!")

if __name__ == "__main__":
    main() 