import base64
from itertools import cycle
class MessageDecoder:
    def __init__(self):
        # The sequences list was created to store dictionaries of command names and their associated keys.
        # Each dictionary contains a command name, a key, and the next key in the sequence.
        # This structure allows for easy iteration and manipulation of command sequences.
        # The full set of commands and addresses is included for comprehensive analysis.
        # These particular addresses are used as they represent a predefined sequence of operations
        # that are significant for the analysis of command flows and transitions in the system.
        self.sequences = [
            {"name": "BEGIN", "key": "1BgGZ9tc", "next_key": "1CUNEBjY"},
            {"name": "CRYPTO", "key": "1CUNEBjY", "next_key": "19ZewH8K"},
            {"name": "ZERO", "key": "19ZewH8K", "next_key": "1EhqbyUM"},
            {"name": "ECHO", "key": "1EhqbyUM", "next_key": "1E6NuFjC"},
            {"name": "ENTRY", "key": "1E6NuFjC", "next_key": "1GrwDkr3"},
            {"name": "SECURE", "key": "1GrwDkr3", "next_key": "1CUNEBjY"},
            {"name": "VERIFY", "key": "1CUNEBjY", "next_key": "19ZewH8K"},
            {"name": "GUARD", "key": "19ZewH8K", "next_key": "1EhqbyUM"},
            {"name": "INIT", "key": "1EhqbyUM", "next_key": "1E6NuFjC"},
            {"name": "PROCESS", "key": "1E6NuFjC", "next_key": "1GrwDkr3"},
            {"name": "MEMORY", "key": "1GrwDkr3", "next_key": "1CUNEBjY"},
            {"name": "LOAD", "key": "1CUNEBjY", "next_key": "19ZewH8K"},
            {"name": "EXECUTE", "key": "19ZewH8K", "next_key": "1EhqbyUM"},
            {"name": "BUFFER", "key": "1EhqbyUM", "next_key": "1E6NuFjC"},
            {"name": "SYNC", "key": "1E6NuFjC", "next_key": None}
        ]
    def decode_base64_segments(self):
        print("\nAttempting Base64 Decoding:")
        print("-" * 50)
        
        # Try different segment combinations
        for name, key, next_key in self.sequences:
            control = key[1:4]
            operation = key[4:8]
            
            # Pad and try to decode
            padded = control + operation + "=="
            try:
                decoded = base64.b64decode(padded)
                print(f"\n{name} Key: {key}")
                print(f"Segment: {control + operation}")
                print(f"Decoded: {decoded}")
            except:
                pass
                
    def analyze_ascii_shifts(self):
        print("\nAnalyzing ASCII Patterns:")
        print("-" * 50)
        
        message_parts = []
        for i, (name, current, next_key) in enumerate(self.sequences):
            if next_key:
                shifts = []
                for j in range(1, 8):  # Skip the '1' prefix
                    if current[j] != next_key[j]:
                        shift = ord(next_key[j]) - ord(current[j])
                        shifts.append(shift)
                
                # Look for patterns in shifts that might encode a message
                try:
                    # Convert shifts to ASCII
                    chars = [chr(abs(s) % 128) for s in shifts]
                    message_parts.append(''.join(chars))
                except:
                    pass
                    
        print("\nPotential Message Parts:")
        for part in message_parts:
            print(f"- {part}")
            
    def analyze_key_segments(self):
        print("\nAnalyzing Key Segments:")
        print("-" * 50)
        
        # Extract all segments
        controls = []
        operations = []
        for _, key, _ in self.sequences:
            controls.append(key[1:4])
            operations.append(key[4:8])
            
        # Try to decode control sequence
        print("\nControl Sequence:")
        print(' -> '.join(controls))
        
        # Try to decode operation sequence
        print("\nOperation Sequence:")
        print(' -> '.join(operations))
        
        # Look for patterns in the transitions
        print("\nTransition Analysis:")
        for i in range(len(controls)-1):
            c1, c2 = controls[i], controls[i+1]
            o1, o2 = operations[i], operations[i+1]
            
            print(f"\nTransition {i+1}:")
            print(f"Control: {c1} -> {c2}")
            print(f"Operation: {o1} -> {o2}")
            
            # Try to extract message from transition
            try:
                # XOR the segments
                xored_control = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(c1, c2))
                xored_operation = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(o1, o2))
                
                print(f"XOR Control: {xored_control}")
                print(f"XOR Operation: {xored_operation}")
            except:
                pass
                
    def find_hidden_message(self):
        print("\nAttempting to Extract Hidden Message:")
        print("-" * 50)
        
        # Combine all segments
        all_segments = []
        for _, key, _ in self.sequences:
            all_segments.append(key[1:])  # Skip the '1' prefix
            
        # Try different decoding methods
        print("\nMethod 1: Direct ASCII")
        print(''.join(all_segments))
        
        print("\nMethod 2: Every Nth character")
        for n in range(2, 5):
            chars = []
            for segment in all_segments:
                chars.extend(segment[i] for i in range(0, len(segment), n))
            print(f"Every {n}th: {''.join(chars)}")
            
        print("\nMethod 3: First/Last characters")
        firsts = ''.join(seg[0] for seg in all_segments)
        lasts = ''.join(seg[-1] for seg in all_segments)
        print(f"First chars: {firsts}")
        print(f"Last chars: {lasts}")
        
        # Look for ASCII art patterns
        print("\nASCII Art Pattern:")
        for segment in all_segments:
            print(' '.join(segment))

def main():
    decoder = MessageDecoder()
    
    print("Hidden Message Analysis")
    print("=" * 50)
    
    decoder.decode_base64_segments()
    decoder.analyze_ascii_shifts()
    decoder.analyze_key_segments()
    decoder.find_hidden_message()

if __name__ == "__main__":
    main() 