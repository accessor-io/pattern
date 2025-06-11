from crypto_data import CRYPTO_MAPPINGS
from collections import defaultdict

class CryptoDecoder:
    def __init__(self):
        self.mappings = CRYPTO_MAPPINGS
        self.current_state = None
        self.path_history = []
        
    def initialize_from_master(self):
        """Start from master key"""
        self.current_state = {
            'address': self.mappings[0][0],
            'command': self.mappings[0][1],
            'mode': 'INIT'
        }
        self.path_history.append(self.current_state)
        return self.current_state
    
    def follow_helix_pattern(self, address, window_size=4):
        """Generate helix pattern from address"""
        patterns = []
        for i in range(len(address) - window_size + 1):
            window = address[i:i+window_size]
            # Add spacing for visual effect
            spaced = ' ' * i + window
            # Count numbers and letters
            nums = sum(1 for c in window if c.isdigit())
            letters = sum(1 for c in window if c.isalpha())
            patterns.append({
                'window': window,
                'position': i,
                'composition': f"{nums}n{letters}l",
                'visual': spaced
            })
        return patterns
    
    def find_command_path(self, start_command):
        """Find possible next commands in sequence"""
        paths = []
        cmd_parts = set(start_command.split('_'))
        
        for addr, cmd in self.mappings:
            if cmd != start_command:
                next_parts = set(cmd.split('_'))
                shared = cmd_parts & next_parts
                if shared:
                    paths.append({
                        'address': addr,
                        'command': cmd,
                        'shared_ops': shared,
                        'new_ops': next_parts - cmd_parts,
                        'similarity': len(shared) / len(cmd_parts)
                    })
        
        return sorted(paths, key=lambda x: x['similarity'], reverse=True)
    
    def transform_address(self, address, command):
        """Apply command transformations to address"""
        result = address
        ops = command.split('_')
        
        for op in ops:
            if op == 'ZERO':
                result = result[:8]  # Take first 8 chars
            elif op == 'TRANSFER':
                mid = len(result) // 2
                result = result[mid-4:mid+4]  # Take middle 8 chars
            elif op == 'SECURE':
                result = result[-8:]  # Take last 8 chars
            elif op == 'ENCRYPT':
                result = result[::-1]  # Reverse
            elif op == 'DECRYPT':
                result = result[::-1]  # Reverse back
        
        return result
    
    def analyze_state(self):
        """Analyze current state and possible next steps"""
        if not self.current_state:
            return None
            
        analysis = {
            'current': self.current_state,
            'helix': self.follow_helix_pattern(self.current_state['address']),
            'possible_paths': self.find_command_path(self.current_state['command']),
            'transformations': []
        }
        
        # Try each possible next path
        for path in analysis['possible_paths'][:3]:  # Look at top 3 paths
            transformed = self.transform_address(self.current_state['address'], path['command'])
            analysis['transformations'].append({
                'command': path['command'],
                'result': transformed,
                'shared_ops': path['shared_ops']
            })
        
        return analysis
    
    def execute_next_step(self, path_choice=0):
        """Execute next step in the sequence"""
        analysis = self.analyze_state()
        if not analysis or not analysis['possible_paths']:
            return None
            
        # Take the specified path
        next_path = analysis['possible_paths'][path_choice]
        self.current_state = {
            'address': next_path['address'],
            'command': next_path['command'],
            'mode': 'EXECUTE'
        }
        self.path_history.append(self.current_state)
        
        return self.current_state

def main():
    # Initialize decoder
    decoder = CryptoDecoder()
    print("Initializing crypto decoder...")
    
    # Start from master key
    initial_state = decoder.initialize_from_master()
    print(f"\nStarting from master key:")
    print(f"Address: {initial_state['address']}")
    print(f"Command: {initial_state['command']}")
    
    # Follow each possible path
    print("\nFollowing possible paths...")
    
    for path_choice in range(3):  # Try top 3 paths
        print(f"\n{'='*50}")
        print(f"PATH {path_choice + 1}")
        print(f"{'='*50}")
        
        # Reset decoder
        decoder = CryptoDecoder()
        decoder.initialize_from_master()
        
        # Follow path for 3 steps
        for step in range(3):
            analysis = decoder.analyze_state()
            if not analysis:
                break
                
            print(f"\nStep {step + 1}:")
            print(f"Current address: {analysis['current']['address']}")
            print(f"Current command: {analysis['current']['command']}")
            
            print("\nHelix pattern:")
            for pattern in analysis['helix'][:3]:
                print(f"{pattern['visual']} [{pattern['composition']}]")
            
            if step < 2:  # Don't show next steps on last iteration
                print("\nTransforming to next state...")
                next_state = decoder.execute_next_step(path_choice)
                if next_state:
                    transformed = decoder.transform_address(analysis['current']['address'], next_state['command'])
                    print(f"Transform result: {transformed}")
                    print(f"Next address: {next_state['address']}")
                    print(f"Next command: {next_state['command']}")
                else:
                    print("No more valid steps in this path")
                    break
    
    # Show final analysis
    print(f"\n{'='*50}")
    print("FINAL ANALYSIS")
    print(f"{'='*50}")
    
    # Analyze command patterns
    all_commands = [state['command'] for state in decoder.path_history]
    command_pairs = list(zip(all_commands[:-1], all_commands[1:]))
    
    print("\nCommand sequence patterns:")
    for cmd1, cmd2 in command_pairs:
        shared = set(cmd1.split('_')) & set(cmd2.split('_'))
        print(f"\n{cmd1}\n↓ Shared: {shared}\n{cmd2}")
    
    # Analyze address transformations
    print("\nAddress transformation patterns:")
    addr_pairs = list(zip([state['address'] for state in decoder.path_history][:-1],
                         [state['address'] for state in decoder.path_history][1:]))
    
    for addr1, addr2 in addr_pairs:
        # Find matching segments
        matches = []
        for i in range(len(addr1)-3):
            for j in range(len(addr2)-3):
                if addr1[i:i+4] == addr2[j:j+4]:
                    matches.append((i, j, addr1[i:i+4]))
        
        print(f"\n{addr1}\n↓ Matching segments: {matches}\n{addr2}")
    
    print("\nDecoding complete!")

if __name__ == "__main__":
    main() 