from crypto_data import CRYPTO_MAPPINGS

def decode_final_message():
    # The key transitions
    transitions = [
        ("BgGZ9tc", "CUNEBjY"),  # BEGIN -> CRYPTO
        ("CUNEBjY", "9ZewH8K"),  # CRYPTO -> ZERO
        ("9ZewH8K", "EhqbyUM"),  # ZERO -> ECHO
        ("EhqbyUM", "E6NuFjC")   # ECHO -> ENTRY
    ]
    
    print("Final Message Decoder")
    print("=" * 40)
    
    # The key insight: The message is encoded in the transition patterns
    message_parts = []
    
    for i, (start, end) in enumerate(transitions):
        print(f"\nAnalyzing Transition {i+1}:")
        
        # Get the differences that form the message
        diffs = []
        for j in range(len(start)):
            if start[j] != end[j]:
                diff = ord(end[j]) - ord(start[j])
                diffs.append(diff)
        
        print(f"From: {start}")
        print(f"To:   {end}")
        print(f"Differences: {diffs}")
        
        # Apply the transformation:
        # 1. Take absolute value of differences
        # 2. Modulo with 26 (alphabet)
        # 3. Shift by 65 (ASCII 'A')
        chars = []
        for d in diffs:
            val = abs(d) % 26
            char = chr(val + 65)
            chars.append(char)
            
        message_part = ''.join(chars)
        message_parts.append(message_part)
        print(f"Decoded Part: {message_part}")
    
    # Combine the parts with the correct transformation
    final_message = ''
    for part in message_parts:
        # Take every second character
        final_message += ''.join(part[::2])
    
    print("\nFinal Decoded Message:")
    print("-" * 40)
    print(final_message)
    
    # The message is revealed by combining:
    # 1. First chars: BC9EE
    # 2. Last chars: cYKMC
    # 3. Transformed differences
    
    print("\nVerification:")
    print("First Sequence:", ''.join(t[0][0] for t in transitions))
    print("Last Sequence:", ''.join(t[0][-1] for t in transitions))
    print("Control Sequence:", ''.join(t[0][1:4] for t in transitions))
    print("Operation Sequence:", ''.join(t[0][4:7] for t in transitions))

if __name__ == "__main__":
    decode_final_message() 