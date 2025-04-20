import os
import json
import math
import struct
from pathlib import Path

def calculate_dimensions(size_bytes):
    """Calculate optimal width/height for ImageJ."""
    if size_bytes < 1:
        return (1, 1)
    
    # Try to make it as square as possible
    width = int(math.sqrt(size_bytes))
    height = math.ceil(size_bytes / width)
    return (width, height)

def convert_file_to_raw(input_path, output_dir):
    """Convert a file to raw binary format and create metadata."""
    try:
        # Skip if file is already in our output directory
        if str(input_path).startswith(str(output_dir)):
            return False
            
        with open(input_path, 'rb') as f:
            data = f.read()
        
        # Create output filename with original path structure
        rel_path = os.path.relpath(input_path, start='.')
        output_base = rel_path.replace('/', '_').replace('\\', '_')
        name_without_ext = os.path.splitext(output_base)[0]
        raw_path = os.path.join(output_dir, f"{name_without_ext}.raw")
        meta_path = os.path.join(output_dir, f"{name_without_ext}.json")
        
        # Calculate dimensions
        width, height = calculate_dimensions(len(data))
        
        # Write raw data
        with open(raw_path, 'wb') as f:
            f.write(data)
        
        # Create detailed metadata for ImageJ
        metadata = {
            'original_file': str(input_path),
            'original_path': str(rel_path),
            'size_bytes': len(data),
            'suggested_width': width,
            'suggested_height': height,
            'file_stats': {
                'created': os.path.getctime(input_path),
                'modified': os.path.getmtime(input_path),
                'original_extension': os.path.splitext(input_path)[1],
                'is_binary': any(x < 9 for x in data[:1024]) if data else False
            },
            'import_notes': 'In ImageJ: File > Import > Raw... then use these dimensions'
        }
        
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        return False

def main():
    # Create output directory
    output_dir = Path('raw_binary_analysis')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Walk through all files in the pattern directory
    files_to_process = []
    for root, dirs, files in os.walk('.'):
        # Skip the output directory itself
        if str(output_dir) in root:
            continue
        # Skip git directory
        if '.git' in root:
            continue
        # Skip pycache
        if '__pycache__' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            files_to_process.append(Path(file_path))
    
    # Process each file
    success_count = 0
    total_files = len(files_to_process)
    
    print(f"Found {total_files} files to process")
    print("Converting files to raw format...")
    
    for i, file_path in enumerate(files_to_process, 1):
        if convert_file_to_raw(file_path, output_dir):
            success_count += 1
            print(f"[{i}/{total_files}] Converted: {file_path}")
        else:
            print(f"[{i}/{total_files}] Skipped: {file_path}")
    
    print(f"\nProcessed {success_count} of {total_files} files")
    print(f"Output directory: {output_dir}")
    print("\nTo import in ImageJ:")
    print("1. File > Import > Raw...")
    print("2. Select any .raw file")
    print("3. Check the corresponding .json file for dimensions")
    print("4. Try different import options:")
    print("   - 8-bit for basic visualization")
    print("   - 16-bit unsigned for more detail")
    print("   - 32-bit float for numerical data")
    print("\nThe .json files contain detailed metadata about each file")

if __name__ == '__main__':
    main()