#!/usr/bin/env python3

with open('key_sequence_generator.py', 'r') as f:
    lines = f.readlines()

# Find the main block
main_block_start = None
for i, line in enumerate(lines):
    if 'if __name__ == "__main__":' in line:
        main_block_start = i
        break

# Find the function definition after main block
func_start = None
func_end = None
for i in range(main_block_start, len(lines)):
    if 'def get_prioritized_test_formulas(' in lines[i]:
        func_start = i
        break

if func_start:
    # Find the end of the function (look for next def or end of file)
    func_end = len(lines)
    for i in range(func_start + 1, len(lines)):
        if lines[i].startswith('def ') or i == len(lines) - 1:
            func_end = i if lines[i].startswith('def ') else i + 1
            break
    
    # Extract the function
    func_lines = lines[func_start:func_end]
    
    # Remove the function from its current location
    del lines[func_start:func_end]
    
    # Insert the function before main block
    for i, line in enumerate(func_lines):
        lines.insert(main_block_start + i, line)

# Write back to file
with open('key_sequence_generator.py', 'w') as f:
    f.writelines(lines)

print('Function moved successfully!') 