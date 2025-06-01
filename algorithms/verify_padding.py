#!/usr/bin/env python3
"""
Padding Verification and Standardization Script

This script checks all relevant Python files in the project to:
1. Verify they use proper 64-character padding for Bitcoin private keys
2. Check for any issues with padding implementations
3. Fix common padding problems it discovers
"""

import os
import re
import sys
import glob

def scan_file_for_padding_issues(file_path):
    """Scan a Python file for potential padding issues with private keys"""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        
    # Check for various indicators of correct/incorrect padding
    lines = content.split('\n')
    line_num = 0
    for line in lines:
        line_num += 1
        
        # Look for hex strings that aren't padded properly
        unpadded_hex = re.search(r'hex\(.*?\)[^\.2:]', line)
        if unpadded_hex and 'format' not in line and 'zfill' not in line and '064' not in line:
            issues.append({
                'line': line_num,
                'text': line.strip(),
                'issue': 'Possible unpadded hex conversion',
                'fix': 'Use format(value, \'064x\') instead of hex(value)[2:]'
            })
        
        # Look for byte conversion without proper padding
        if 'bytes.fromhex' in line and 'zfill' not in line and 'format' not in line and '064' not in line:
            issues.append({
                'line': line_num,
                'text': line.strip(),
                'issue': 'Byte conversion without padding',
                'fix': 'Ensure hex values are padded to 64 chars before converting to bytes'
            })
        
        # Check ECDSA key creation without proper padding
        if 'SigningKey.from_string' in line and ('format' not in line or '064' not in content[:line_num]):
            issues.append({
                'line': line_num,
                'text': line.strip(),
                'issue': 'ECDSA key creation without clear padding',
                'fix': 'Ensure private key is padded to 64 chars before creating ECDSA key'
            })
    
    # Check common functions
    # 1. Check if there's a address conversion function
    if 'def private_key_to_address' in content or 'def privkey_to_address' in content:
        # Check if it uses proper padding
        if 'format' in content and '064' in content and 'x' in content:
            # This is likely correct
            pass
        elif 'zfill(64)' in content:
            # This is also likely correct
            pass
        else:
            issues.append({
                'line': 0,
                'text': 'private_key_to_address function',
                'issue': 'Address conversion may not use proper padding',
                'fix': 'Update function to use format(private_key, \'064x\') for padding'
            })
    
    return issues

def fix_padding_issues(file_path, make_changes=False):
    """Fix common padding issues in the file"""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Common fixes
    
    # 1. Fix hex conversion without padding
    content = re.sub(
        r'hex\(([^)]+)\)\[2:\]',
        r'format(\1, \'064x\')',
        content
    )
    
    # 2. Fix bytes.fromhex without padding
    content = re.sub(
        r'bytes\.fromhex\(hex\(([^)]+)\)\[2:\]\)',
        r'bytes.fromhex(format(\1, \'064x\'))',
        content
    )
    
    # 3. Add a padding note for key creation
    content = re.sub(
        r'(SigningKey\.from_string\([^,)]+)',
        r'# Ensure proper 32-byte padding\n        \1',
        content
    )
    
    if make_changes:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return content

def scan_all_files(directory='.', pattern='*.py', fix=False):
    """Scan all files matching pattern in directory and subdirectories"""
    files = glob.glob(f"{directory}/**/{pattern}", recursive=True)
    
    results = []
    for file_path in files:
        # Skip this verification script itself
        if file_path.endswith('verify_padding.py'):
            continue
            
        try:
            issues = scan_file_for_padding_issues(file_path)
            if issues:
                results.append({
                    'file': file_path,
                    'issues': issues
                })
                if fix:
                    fix_padding_issues(file_path, make_changes=True)
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
    
    return results

def main():
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Verify and fix padding in Python scripts')
    parser.add_argument('--dir', '-d', default='.', help='Directory to scan')
    parser.add_argument('--pattern', '-p', default='*.py', help='File pattern to match')
    parser.add_argument('--fix', '-f', action='store_true', help='Automatically fix issues')
    parser.add_argument('--check', '-c', action='store_true', help='Only check files, don\'t print details')
    args = parser.parse_args()
    
    # Scan all files
    print(f"Scanning {args.pattern} files in {args.dir}...")
    results = scan_all_files(args.dir, args.pattern, fix=args.fix)
    
    if args.check:
        # Just print summary
        if results:
            print(f"Found padding issues in {len(results)} files:")
            for result in results:
                print(f"- {result['file']}: {len(result['issues'])} issues")
            sys.exit(1)
        else:
            print("No padding issues found!")
            sys.exit(0)
    else:
        # Print detailed report
        if results:
            print(f"\nDetailed Report ({len(results)} files with issues):")
            for result in results:
                print(f"\n{'-' * 80}\nFile: {result['file']}\n{'-' * 80}")
                for issue in result['issues']:
                    print(f"Line {issue['line']}: {issue['issue']}")
                    print(f"  {issue['text']}")
                    print(f"  Fix: {issue['fix']}")
                    print()
            
            if args.fix:
                print(f"Fixed padding issues in {len(results)} files.")
            else:
                print("Run with --fix to automatically fix these issues.")
        else:
            print("No padding issues found! All scripts appear to be using proper padding.")
    
    # Give specific advice for additional manual checks
    print("\nAdditional Manual Verification Recommendations:")
    print("1. Ensure all private key to address conversion functions use format(private_key, '064x')")
    print("2. Check that all ECDSA key creation uses properly padded private keys")
    print("3. Verify that any script that uses bytes.fromhex() properly pads the hex string first")

if __name__ == "__main__":
    main() 