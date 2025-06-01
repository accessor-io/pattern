import hashlib
import binascii
from crypto_data import CRYPTO_MAPPINGS

class IterativeProtocol:
    def __init__(self):
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        self.master_key = "73fc74d3cc995ae3f81703688d7409bb38d26f167bbc47aa82bc89592db41422"
        # Use the actual command sequence from CRYPTO_MAPPINGS
        self.initial_command = CRYPTO_MAPPINGS[0][1]  # BEGIN_GATEWAY_ZERO_TRANSFER_SECURE_ACCESS_METHOD
        self.max_iterations = 32
        
        # Command flow patterns from life.ini
        self.flow_patterns = {
            'BEGIN_GATEWAY_ZERO_TRANSFER': ['INIT_87_SECURE_FORWARD', 'BUFFER_VERIFY_SEQUENCE'],
            'CRYPTO_UNIFORM_NET_ENABLE': ['CIPHER_ZERO_WAIT_KEY', 'BUFFER_ZONE_PROTOCOL'],
            'BUFFER_VERIFY_SEQUENCE': ['KEY_UNIFORM_VERIFY_642'],
            'KEY_HASH_22_PROCESS': ['PROCESS_WAIT_BUFFER_ECHO'],
            'PROCESS_WAIT_BUFFER_ECHO': ['TRANSFER_NET_VERIFY_MEMORY'],
            'INIT_87_SECURE_FORWARD': ['MEMORY_VERIFY_QUEUE', 'PROCESS_INIT_FORWARD']
        }
        
    def execute_iteration(self, current_key, master_key, iteration):
        print(f"\nIteration {iteration}")
        print("=" * 50)
        
        # Step 1: Map commands to both keys
        chain_positions = []
        master_positions = []
        
        for cmd in self.command_path.split():
            hex_cmd = ''.join(hex(ord(c))[2:] for c in cmd)
            
            # Check chain code
            chain_pos = current_key.find(hex_cmd)
            if chain_pos >= 0:
                chain_positions.append(chain_pos//2)
                print(f"Chain: Command {cmd:4} at position {chain_pos//2:2}")
                
            # Check master key
            master_pos = master_key.find(hex_cmd)
            if master_pos >= 0:
                master_positions.append(master_pos//2)
                print(f"Master: Command {cmd:4} at position {master_pos//2:2}")
                
        # Step 2: Extract values from both keys
        chain_values = []
        master_values = []
        
        for pos in chain_positions:
            if pos * 2 < len(current_key):
                value = current_key[pos*2:pos*2+8]
                chain_values.append(value)
                print(f"Chain position {pos:2}: {value}")
                
        for pos in master_positions:
            if pos * 2 < len(master_key):
                value = master_key[pos*2:pos*2+8]
                master_values.append(value)
                print(f"Master position {pos:2}: {value}")
                
        # Step 3: Combine values
        all_values = chain_values + master_values
        if all_values:
            combined = ''.join(all_values)
            print(f"\nCombined values: {combined}")
            
            # Try to decode as ASCII
            try:
                bytes_val = bytes.fromhex(combined)
                ascii_str = bytes_val.decode('ascii', errors='ignore')
                if ascii_str:
                    print(f"ASCII: {ascii_str}")
            except:
                pass
                
        # Step 4: Generate next keys
        next_chain = ""
        next_master = ""
        
        if chain_values and master_values:
            # XOR chain values with master values
            chain_bytes = [bytes.fromhex(v) for v in chain_values]
            master_bytes = [bytes.fromhex(v) for v in master_values]
            
            # XOR corresponding values
            results = []
            for c, m in zip(chain_bytes, master_bytes):
                if len(c) == len(m):
                    result = bytes(a ^ b for a, b in zip(c, m))
                    results.append(result)
                    
            if results:
                # Combine results
                next_chain = b''.join(results).hex()
                # Rotate master key
                next_master = master_key[8:] + master_key[:8]
                
                print(f"\nNext chain key: {next_chain}")
                print(f"Next master key: {next_master}")
                
        return next_chain, next_master
        
    def follow_protocol(self):
        print("Following Protocol Sequence")
        print("=" * 50)
        
        current_chain = self.chain_code
        current_master = self.master_key
        seen_pairs = set([(current_chain, current_master)])
        messages = []
        
        for i in range(self.max_iterations):
            next_chain, next_master = self.execute_iteration(current_chain, current_master, i+1)
            
            if not next_chain or not next_master:
                print("\nNo next keys generated")
                break
                
            # Try to decode both keys
            try:
                chain_bytes = bytes.fromhex(next_chain)
                master_bytes = bytes.fromhex(next_master)
                
                # XOR the keys together
                xored = bytes(a ^ b for a, b in zip(chain_bytes, master_bytes))
                message = xored.decode('ascii', errors='ignore')
                
                if any(c.isalnum() for c in message):
                    messages.append(message)
                    print(f"\nPossible message found: {message}")
            except:
                pass
                
            # Check for cycles
            current_pair = (next_chain, next_master)
            if current_pair in seen_pairs:
                print(f"\nCycle detected after {i+1} iterations")
                break
                
            seen_pairs.add(current_pair)
            current_chain = next_chain
            current_master = next_master
            
        # Final analysis
        print("\nProtocol Execution Complete")
        print("=" * 50)
        print(f"Total iterations: {len(seen_pairs)}")
        if messages:
            print("\nPossible messages found:")
            for i, msg in enumerate(messages, 1):
                print(f"{i}. {msg}")
                
def main():
    protocol = IterativeProtocol()
    protocol.follow_protocol()

if __name__ == "__main__":
    main() 