#!/usr/bin/env python3

import numpy as np
from datetime import datetime

def read_hex_sequence(filename):
    with open(filename, 'r') as f:
        # Read lines and convert to integers
        numbers = [int(line.strip(), 16) for line in f.readlines()]
    return numbers

def analyze_sequence(numbers):
    # Convert to numpy array for easier analysis
    arr = np.array(numbers)
    
    # Basic statistics
    differences = np.diff(arr)
    
    analysis = {
        'count': len(numbers),
        'min': min(numbers),
        'max': max(numbers),
        'average_diff': np.mean(differences),
        'median_diff': np.median(differences),
        'is_strictly_increasing': np.all(differences > 0),
    }
    
    # Check for common mathematical patterns
    ratios = arr[1:] / arr[:-1]
    
    # Look for potential geometric sequences
    avg_ratio = np.mean(ratios)
    ratio_std = np.std(ratios)
    
    analysis['average_ratio'] = avg_ratio
    analysis['ratio_std'] = ratio_std
    
    return analysis

def update_changelog(analysis):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    changelog_entry = f"""
## Analysis Results - {timestamp}
- Sequence Length: {analysis['count']}
- Range: [{analysis['min']}, {analysis['max']}]
- Average Difference: {analysis['average_diff']:.2f}
- Median Difference: {analysis['median_diff']:.2f}
- Strictly Increasing: {analysis['is_strictly_increasing']}
- Average Ratio between consecutive numbers: {analysis['average_ratio']:.4f}
- Standard Deviation of Ratios: {analysis['ratio_std']:.4f}
"""
    
    with open('CHANGELOG.md', 'a') as f:
        f.write(changelog_entry)

def main():
    numbers = read_hex_sequence('data/32bHex.txt')
    analysis = analyze_sequence(numbers)
    update_changelog(analysis)
    
    # Print results to console as well
    print("Analysis complete. Results added to CHANGELOG.md")

if __name__ == "__main__":
    main() 