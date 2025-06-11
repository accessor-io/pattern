from crypto_data import CRYPTO_MAPPINGS
from collections import defaultdict

def analyze_address_patterns(address):
    """Analyze patterns within a Bitcoin address"""
    patterns = {
        'segments': [],
        'repeating': [],
        'special': []
    }
    
    # Look for interesting segments (8-char windows)
    for i in range(len(address)-7):
        segment = address[i:i+8]
        if segment.isalnum():  # Only alphanumeric segments
            patterns['segments'].append(segment)
    
    # Look for repeating patterns
    for length in range(2, 5):  # Look for patterns of length 2-4
        for i in range(len(address)-length):
            pattern = address[i:i+length]
            if address.count(pattern) > 1:
                patterns['repeating'].append((pattern, address.count(pattern)))
    
    # Look for special patterns (numbers, letters only)
    numbers = ''.join(c for c in address if c.isdigit())
    letters = ''.join(c for c in address if c.isalpha())
    if numbers:
        patterns['special'].append(('numbers', numbers))
    if letters:
        patterns['special'].append(('letters', letters))
    
    return patterns

def find_hidden_messages(address, command):
    """Look for potential hidden messages in address transformations"""
    messages = []
    
    # Try different sliding windows
    for window in range(4, 9):
        for i in range(len(address)-window+1):
            segment = address[i:i+window]
            # Check if segment might be meaningful
            if segment.isalnum() and not segment.isdigit():
                messages.append(f"Window-{window}: {segment}")
    
    # Try command-based transformations
    ops = command.split('_')
    current = address
    for op in ops:
        if op == "ZERO":
            current = current[:8]
        elif op == "TRANSFER":
            mid = len(current) // 2
            current = current[mid-4:mid+4]
        elif op == "SECURE":
            current = current[-8:]
        messages.append(f"{op}: {current}")
    
    # Look for potential words or codes
    potential_words = []
    for i in range(len(address)-2):
        for j in range(i+3, min(i+9, len(address)+1)):
            word = address[i:j]
            if word.isalpha() and len(word) >= 3:
                potential_words.append(word)
    
    if potential_words:
        messages.append("Potential words found: " + ", ".join(potential_words))
    
    return messages

def analyze_command_patterns(command):
    """Analyze patterns in the command sequence"""
    patterns = []
    
    # Split into operation parts
    ops = command.split('_')
    
    # Look for key operations
    key_ops = ['ZERO', 'TRANSFER', 'SECURE', 'ENCRYPT', 'DECRYPT', 'METHOD']
    found_ops = [op for op in ops if op in key_ops]
    if found_ops:
        patterns.append(f"Key operations: {', '.join(found_ops)}")
    
    # Look for operation sequence
    patterns.append(f"Operation sequence: {' -> '.join(ops)}")
    
    return patterns

def deep_analyze_transformations():
    """Perform deep analysis of all addresses and their transformations"""
    results = []
    
    for addr, cmd in CRYPTO_MAPPINGS:
        analysis = {
            'address': addr,
            'command': cmd,
            'patterns': analyze_address_patterns(addr),
            'hidden_messages': find_hidden_messages(addr, cmd),
            'command_patterns': analyze_command_patterns(cmd)
        }
        results.append(analysis)
    
    return results

if __name__ == "__main__":
    print("Performing deep analysis of addresses and transformations...")
    
    # Analyze first few addresses in detail
    analyses = deep_analyze_transformations()
    
    for i, analysis in enumerate(analyses[:5]):  # Show first 5 for brevity
        print(f"\nAnalyzing address {i+1}:")
        print(f"Address: {analysis['address']}")
        print(f"Command: {analysis['command']}")
        
        print("\nInteresting segments found:")
        for segment in analysis['patterns']['segments'][:3]:
            print(f"- {segment}")
        
        print("\nRepeating patterns:")
        for pattern, count in sorted(analysis['patterns']['repeating'], key=lambda x: x[1], reverse=True)[:3]:
            print(f"- '{pattern}' appears {count} times")
        
        print("\nSpecial patterns:")
        for pattern_type, pattern in analysis['patterns']['special']:
            print(f"- {pattern_type}: {pattern}")
        
        print("\nCommand analysis:")
        for pattern in analysis['command_patterns']:
            print(f"- {pattern}")
        
        print("\nPotential hidden messages:")
        for msg in analysis['hidden_messages']:
            print(f"- {msg}")
        
        print("-" * 50)
    
    # Look for patterns across all addresses
    print("\nAnalyzing patterns across all addresses...")
    
    # Collect common segments
    segment_counts = defaultdict(int)
    for analysis in analyses:
        for segment in analysis['patterns']['segments']:
            segment_counts[segment] += 1
    
    print("\nMost common segments across addresses:")
    for segment, count in sorted(segment_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"- {segment}: found in {count} addresses") 