from crypto_data import CRYPTO_MAPPINGS
from collections import defaultdict

def analyze_address_patterns(address):
    """1. Detailed analysis of address patterns"""
    patterns = {
        'segments': [],
        'numerical': [],
        'alphabetical': [],
        'position_patterns': [],
        'checksums': []
    }
    
    # Analyze segments
    for i in range(len(address)-3):
        for j in range(i+4, min(i+9, len(address)+1)):
            segment = address[i:j]
            if segment.isalnum():
                patterns['segments'].append((segment, i))
    
    # Analyze numerical patterns
    numbers = [c for c in address if c.isdigit()]
    patterns['numerical'] = {
        'count': len(numbers),
        'positions': [i for i, c in enumerate(address) if c.isdigit()],
        'sequences': ''.join(numbers)
    }
    
    # Analyze alphabetical patterns
    letters = [c for c in address if c.isalpha()]
    patterns['alphabetical'] = {
        'count': len(letters),
        'positions': [i for i, c in enumerate(address) if c.isalpha()],
        'sequences': ''.join(letters)
    }
    
    # Look for position-based patterns
    for i in range(len(address)-1):
        if address[i].isdigit() and address[i+1].isalpha():
            patterns['position_patterns'].append(f"Number->Letter at {i}")
        elif address[i].isalpha() and address[i+1].isdigit():
            patterns['position_patterns'].append(f"Letter->Number at {i}")
    
    # Calculate simple checksums
    patterns['checksums'] = {
        'sum_numbers': sum(int(n) for n in numbers),
        'letter_positions': sum(patterns['alphabetical']['positions'])
    }
    
    return patterns

def analyze_command_sequences(cmd):
    """2. Deep analysis of command sequences"""
    analysis = {
        'operations': [],
        'flow': [],
        'security_level': 0
    }
    
    # Split into operations
    ops = cmd.split('_')
    analysis['operations'] = ops
    
    # Analyze operation flow
    security_words = {'SECURE', 'ENCRYPT', 'DECRYPT', 'HASH', 'VERIFY'}
    transfer_words = {'TRANSFER', 'SEND', 'ROUTE', 'FORWARD'}
    init_words = {'BEGIN', 'ZERO', 'INIT', 'START'}
    
    for op in ops:
        if op in security_words:
            analysis['security_level'] += 1
        if op in transfer_words:
            analysis['flow'].append('TRANSFER')
        if op in init_words:
            analysis['flow'].append('INIT')
            
    return analysis

def find_hidden_messages(addr, cmd):
    """3. Search for hidden messages"""
    messages = {
        'words': [],
        'codes': [],
        'sequences': []
    }
    
    # Look for English-like words (3+ letters)
    for i in range(len(addr)-2):
        for j in range(i+3, min(i+8, len(addr)+1)):
            word = addr[i:j]
            if word.isalpha() and len(word) >= 3:
                messages['words'].append(word)
    
    # Look for code patterns (letter-number combinations)
    for i in range(len(addr)-3):
        segment = addr[i:i+4]
        if any(c.isalpha() for c in segment) and any(c.isdigit() for c in segment):
            messages['codes'].append(segment)
    
    # Look for meaningful sequences in commands
    ops = cmd.split('_')
    for i in range(len(ops)-1):
        pair = f"{ops[i]}->{ops[i+1]}"
        messages['sequences'].append(pair)
    
    return messages

def map_transformation_chain(addr, cmd):
    """4. Map the complete transformation chain"""
    chain = {
        'steps': [],
        'transformations': [],
        'state_changes': []
    }
    
    # Track the state changes
    current_state = addr
    ops = cmd.split('_')
    
    for i, op in enumerate(ops):
        if op == 'ZERO':
            current_state = current_state[:8]
        elif op == 'TRANSFER':
            mid = len(current_state) // 2
            current_state = current_state[mid-4:mid+4]
        elif op == 'SECURE':
            current_state = current_state[-8:]
        
        chain['steps'].append(op)
        chain['transformations'].append(current_state)
        chain['state_changes'].append(f"{op}: {current_state}")
    
    return chain

def analyze_all():
    """Run all analyses"""
    results = []
    
    for addr, cmd in CRYPTO_MAPPINGS:
        analysis = {
            'address': addr,
            'command': cmd,
            'patterns': analyze_address_patterns(addr),
            'command_analysis': analyze_command_sequences(cmd),
            'hidden_messages': find_hidden_messages(addr, cmd),
            'transformation_chain': map_transformation_chain(addr, cmd)
        }
        results.append(analysis)
    
    return results

if __name__ == "__main__":
    print("Running comprehensive crypto analysis...")
    analyses = analyze_all()
    
    # Show detailed analysis for first few entries
    for i, analysis in enumerate(analyses[:3]):
        print(f"\n{'='*50}")
        print(f"Analysis {i+1}: {analysis['address']}")
        print(f"Command: {analysis['command']}")
        
        print("\n1. Address Patterns:")
        print("Numerical patterns:", analysis['patterns']['numerical'])
        print("Alphabetical patterns:", analysis['patterns']['alphabetical'])
        print("Position patterns:", analysis['patterns']['position_patterns'])
        print("Checksums:", analysis['patterns']['checksums'])
        
        print("\n2. Command Analysis:")
        print("Operations:", analysis['command_analysis']['operations'])
        print("Flow:", analysis['command_analysis']['flow'])
        print("Security Level:", analysis['command_analysis']['security_level'])
        
        print("\n3. Hidden Messages:")
        print("Potential words:", analysis['hidden_messages']['words'])
        print("Code patterns:", analysis['hidden_messages']['codes'])
        print("Command sequences:", analysis['hidden_messages']['sequences'])
        
        print("\n4. Transformation Chain:")
        print("Steps:", analysis['transformation_chain']['steps'])
        print("State changes:", analysis['transformation_chain']['state_changes'])
        
        print("\n" + "="*50) 