import os
import shutil
import datetime
import csv

# Configuration
INPUT_FILE = 'files_by_creation_date.txt'
LOG_FILE = 'organize_log.csv'
ERROR_LOG_FILE = 'organize_errors.log'

# Folders to skip (already organized or system)
SKIP_PREFIXES = [
    './.git/', './venv/', './src/', './scripts/', './data/', './output/', './docs/', './tests/', './archive/', './config/', './external/'
]

# Categorization rules
CATEGORY_MAP = {
    'src': ['.py', '.c', '.h', '.rs'],
    'scripts': ['.sh'],
    'data/raw': ['.txt', '.csv', '.json', '.db', '.bak', '.zip'],
    'output/logs': ['.log'],
    'output/reports': ['.md', '.pdf', '.rst'],
    'docs': ['.md', '.pdf', '.rst'],
    'tests': [],  # Handled by name
    'config': ['.toml', '.yml', '.ini', '.bat'],
}

# Helper functions
def get_date_str(path):
    t = os.path.getctime(path)
    return datetime.datetime.fromtimestamp(t).strftime('%Y%m%d')

def categorize(file, base, ext):
    # Test files by name
    if base.startswith('test_') or base.startswith('validate_') or '/tests/' in file:
        return 'tests', base
    # Scripts by name or extension
    if ext in CATEGORY_MAP['scripts'] or 'fix' in base or 'trim' in base:
        return 'scripts', base
    # Config files
    if ext in CATEGORY_MAP['config']:
        return 'config', base
    # Data files
    if ext in CATEGORY_MAP['data/raw']:
        # Add date to name if not present
        date_str = get_date_str(file)
        if date_str not in base:
            base = f"{os.path.splitext(base)[0]}_{date_str}{ext}"
        return 'data/raw', base
    # Output logs
    if ext in CATEGORY_MAP['output/logs']:
        date_str = get_date_str(file)
        if date_str not in base:
            base = f"{os.path.splitext(base)[0]}_{date_str}{ext}"
        return 'output/logs', base
    # Output reports
    if ext in CATEGORY_MAP['output/reports']:
        return 'output/reports', base
    # Docs
    if ext in CATEGORY_MAP['docs'] and ('doc' in file or 'README' in base or 'COMPLETE' in base):
        return 'docs', base
    # Source code
    if ext in CATEGORY_MAP['src']:
        return 'src', base
    # Archive fallback
    return 'archive', base

def should_skip(file):
    for prefix in SKIP_PREFIXES:
        if file.startswith(prefix):
            return True
    return False

def main():
    actions = []
    errors = []
    with open(INPUT_FILE) as f:
        for line in f:
            file = line.strip()
            if not os.path.isfile(file) or should_skip(file):
                continue
            base = os.path.basename(file)
            ext = os.path.splitext(base)[1].lower()
            category, new_base = categorize(file, base, ext)
            dest_dir = os.path.join('.', category)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, os.path.basename(new_base))
            # Avoid overwriting
            if os.path.abspath(file) == os.path.abspath(dest_path):
                continue
            counter = 1
            orig_dest_path = dest_path
            while os.path.exists(dest_path):
                dest_path = orig_dest_path.replace(ext, f'_{counter}{ext}')
                counter += 1
            try:
                shutil.move(file, dest_path)
                actions.append([file, dest_path, category])
                print(f"Moved {file} -> {dest_path}")
            except Exception as e:
                error_msg = f"Failed to move {file} -> {dest_path}: {e}"
                print(error_msg)
                errors.append([file, dest_path, str(e)])
    # Log actions
    with open(LOG_FILE, 'w', newline='') as logf:
        writer = csv.writer(logf)
        writer.writerow(['original_path', 'new_path', 'category'])
        writer.writerows(actions)
    # Log errors
    if errors:
        with open(ERROR_LOG_FILE, 'w', newline='') as errf:
            writer = csv.writer(errf)
            writer.writerow(['original_path', 'intended_path', 'error'])
            writer.writerows(errors)
        print(f"Some errors occurred. See {ERROR_LOG_FILE} for details.")
    print(f"Organization complete. Log saved to {LOG_FILE}.")

if __name__ == '__main__':
    main() 