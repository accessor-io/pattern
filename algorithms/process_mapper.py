from collections import defaultdict

class ProcessMapper:
    def __init__(self):
        self.command_sequences = []
        self.state_transitions = defaultdict(list)
        self.address_states = {}
        self.key_segments = {}
        
    def add_command_sequence(self, address, command, next_address=None, next_command=None):
        # Track command sequences
        if next_command:
            self.command_sequences.append((command, next_command))
            self.key_segments[next_command] = next_address[:8]
        else:
            self.command_sequences.append((command,))
            
        # Track state transitions
        if address[:8] not in self.address_states:
            self.address_states[address[:8]] = []
        self.address_states[address[:8]].append(command)
        
        # Store 8-char key segments
        self.key_segments[command] = address[:8]
        
    def analyze_flow(self):
        # Analyze command sequences
        paths = []
        current_path = []
        
        def build_paths(command):
            current_path.append(command)
            next_commands = [seq[1] for seq in self.command_sequences if seq[0] == command and len(seq) > 1]
            
            if not next_commands:
                paths.append(current_path[:])
            else:
                for next_cmd in next_commands:
                    build_paths(next_cmd)
                    
            current_path.pop()
        
        # Start from BEGIN command
        build_paths("BEGIN_GATEWAY_ZERO_TRANSFER_SECURE_ACCESS_METHOD")
        
        # Analyze state transitions
        transitions = defaultdict(int)
        for addr, commands in self.address_states.items():
            for i in range(len(commands)-1):
                transition = f"{commands[i]} -> {commands[i+1]}"
                transitions[transition] += 1
                
        return {
            'paths': paths,
            'transitions': dict(transitions),
            'key_segments': self.key_segments
        }

def main():
    mapper = ProcessMapper()
    
    # Add known command sequences
    mapper.add_command_sequence(
        "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH",
        "BEGIN_GATEWAY_ZERO_TRANSFER_SECURE_ACCESS_METHOD",
        "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb",
        "CRYPTO_UNIFORM_NET_ENABLE_BINARY_PROTOCOL"
    )
    
    mapper.add_command_sequence(
        "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb",
        "CRYPTO_UNIFORM_NET_ENABLE_BINARY_PROTOCOL",
        "19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA",
        "ZERO_ENCRYPT_WAIT_HASH_PROTOCOL_DATA"
    )
    
    mapper.add_command_sequence(
        "19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA",
        "ZERO_ENCRYPT_WAIT_HASH_PROTOCOL_DATA",
        "1EhqbyUMvvs7BfL8goY6qcPbD6YKfPqb7e",
        "ECHO_HASH_QUERY_BUFFER_VERIFY_SEQUENCE"
    )
    
    mapper.add_command_sequence(
        "1EhqbyUMvvs7BfL8goY6qcPbD6YKfPqb7e",
        "ECHO_HASH_QUERY_BUFFER_VERIFY_SEQUENCE",
        "1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k",
        "ENTRY_NODE_FUNCTION_CIPHER_WAIT_ROUTE_SYNC"
    )
    
    # Add final command without next sequence
    mapper.add_command_sequence(
        "1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k",
        "ENTRY_NODE_FUNCTION_CIPHER_WAIT_ROUTE_SYNC"
    )
    
    # Analyze flow
    results = mapper.analyze_flow()
    
    print("\nComplete Process Map:")
    print("-" * 50)
    print("\nCommand Paths:")
    for path in results['paths']:
        print("\nPath:")
        for i, command in enumerate(path, 1):
            key_segment = results['key_segments'][command]
            print(f"{i}. {command}")
            print(f"   Key Segment: {key_segment}")
            print(f"   Operations: {', '.join(command.split('_'))}")
    
    print("\nState Transitions:")
    print("-" * 50)
    for transition, count in results['transitions'].items():
        print(f"{transition}: {count} times")
    
    print("\nKey Segment Analysis:")
    print("-" * 50)
    for command, segment in results['key_segments'].items():
        operations = command.split('_')
        print(f"\nCommand: {command}")
        print(f"Key Segment: {segment}")
        print(f"Operations: {', '.join(operations)}")
        print(f"Segment Structure: {segment[0]} + {segment[1:4]} + {segment[4:8]}")

if __name__ == "__main__":
    main() 