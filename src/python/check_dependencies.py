import ast
import sys
from pathlib import Path
from typing import Dict, Set, List

class DependencyChecker:
    def __init__(self):
        self.root = Path('.')
        self.imports = {}
        self.source_files = set()
        self.missing_imports = {}
        self.duplicate_modules = {}

    def scan_python_files(self):
        """Scan all Python files and their imports"""
        print("Scanning Python files...")
        
        # Known source directories
        src_dirs = [
            'src',
            'blockchain_scanners',
            'wallet_tools',
            'utils',
            'server',
            'ethereum-node-scanner/src',
            'electrum wallet checker/wallet_tools'
        ]

        for src_dir in src_dirs:
            path = self.root / src_dir
            if path.exists():
                for py_file in path.glob('**/*.py'):
                    self.analyze_file(py_file)

    def analyze_file(self, file_path: Path):
        """Analyze imports in a Python file"""
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
                
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

            rel_path = file_path.relative_to(self.root)
            self.imports[str(rel_path)] = imports
            self.source_files.add(str(rel_path))
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def check_dependencies(self):
        """Check for missing or duplicate dependencies"""
        print("\nChecking dependencies...")
        
        # Standard library modules
        stdlib_modules = set(sys.stdlib_module_names)
        
        # Common third-party modules
        third_party = {
            'requests', 'bs4', 'web3', 'eth_utils', 'yaml', 
            'json', 'datetime', 'logging', 'pathlib'
        }

        for file_path, imports in self.imports.items():
            missing = set()
            for imp in imports:
                if imp not in stdlib_modules and imp not in third_party:
                    # Check if module exists in our source files
                    found = False
                    for src in self.source_files:
                        if imp in str(src):
                            found = True
                            break
                    if not found:
                        missing.add(imp)
            
            if missing:
                self.missing_imports[file_path] = missing

    def find_duplicates(self):
        """Find duplicate module implementations"""
        print("\nChecking for duplicate modules...")
        
        module_locations = {}
        for src in self.source_files:
            module_name = Path(src).stem
            if module_name in module_locations:
                module_locations[module_name].append(src)
            else:
                module_locations[module_name] = [src]

        self.duplicate_modules = {
            name: locs for name, locs in module_locations.items()
            if len(locs) > 1 and name != '__init__'
        }

    def suggest_fixes(self):
        """Suggest fixes for dependency issues"""
        print("\n=== Dependency Analysis Results ===")
        
        if self.missing_imports:
            print("\nMissing Imports:")
            for file, missing in self.missing_imports.items():
                print(f"\n{file}:")
                for imp in missing:
                    print(f"  - {imp}")
                    self._suggest_import_fix(imp)

        if self.duplicate_modules:
            print("\nDuplicate Modules:")
            for module, locations in self.duplicate_modules.items():
                print(f"\n{module}:")
                for loc in locations:
                    print(f"  - {loc}")
                self._suggest_module_fix(module, locations)

    def _suggest_import_fix(self, missing_import: str):
        """Suggest fix for missing import"""
        similar_modules = []
        for src in self.source_files:
            if missing_import.lower() in src.lower():
                similar_modules.append(src)
        
        if similar_modules:
            print("  Possible fixes:")
            for mod in similar_modules:
                print(f"    - Import from {mod}")

    def _suggest_module_fix(self, module: str, locations: List[str]):
        """Suggest fix for duplicate modules"""
        print("  Suggested fix:")
        print(f"    - Consolidate implementations into single module")
        print(f"    - Update imports to use consolidated module")
        print(f"    - Consider creating a common interface")

def main():
    checker = DependencyChecker()
    checker.scan_python_files()
    checker.check_dependencies()
    checker.find_duplicates()
    checker.suggest_fixes()

if __name__ == "__main__":
    main() 