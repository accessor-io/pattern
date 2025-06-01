#!/usr/bin/env python3

from typing import List, Dict, Tuple
import hashlib
import binascii

class P2SHAnalyzer:
    def __init__(self):
        # Common script patterns
        self.OP_0 = 0x00
        self.OP_1 = 0x51
        self.OP_16 = 0x60
        self.OP_CHECKSIG = 0xac
        self.OP_CHECKMULTISIG = 0xae
        self.OP_HASH160 = 0xa9
        self.OP_EQUAL = 0x87
        self.OP_VERIFY = 0x69
        self.OP_EQUALVERIFY = 0x88
        self.OP_DUP = 0x76
        
    def parse_script(self, script_hex: str) -> List[Dict[str, any]]:
        """
        Parse a script into its components
        """
        script = bytes.fromhex(script_hex)
        components = []
        i = 0
        
        while i < len(script):
            op = script[i]
            
            # Data push operations
            if 0x01 <= op <= 0x4b:
                data = script[i+1:i+1+op]
                components.append({
                    'type': 'data',
                    'length': op,
                    'value': data.hex()
                })
                i += op + 1
            # OP_PUSHDATA1
            elif op == 0x4c:
                length = script[i+1]
                data = script[i+2:i+2+length]
                components.append({
                    'type': 'pushdata1',
                    'length': length,
                    'value': data.hex()
                })
                i += length + 2
            # OP_0 to OP_16
            elif self.OP_0 <= op <= self.OP_16:
                components.append({
                    'type': 'number',
                    'value': op - self.OP_0
                })
                i += 1
            # Other opcodes
            else:
                components.append({
                    'type': 'opcode',
                    'value': op
                })
                i += 1
                
        return components
    
    def analyze_redeem_script(self, script_hex: str) -> Dict[str, any]:
        """
        Analyze a redeem script to determine its type and requirements
        """
        components = self.parse_script(script_hex)
        analysis = {
            'type': 'unknown',
            'requirements': [],
            'possible_solutions': []
        }
        
        # Check for P2PKH pattern
        if (len(components) == 5 and
            components[0]['type'] == 'opcode' and components[0]['value'] == self.OP_DUP and
            components[1]['type'] == 'opcode' and components[1]['value'] == self.OP_HASH160 and
            components[2]['type'] == 'data' and len(components[2]['value']) == 40 and
            components[3]['type'] == 'opcode' and components[3]['value'] == self.OP_EQUALVERIFY and
            components[4]['type'] == 'opcode' and components[4]['value'] == self.OP_CHECKSIG):
            
            analysis['type'] = 'p2pkh'
            analysis['requirements'].append('Signature matching public key hash')
            analysis['pubkeyhash'] = components[2]['value']
            
        # Check for multisig pattern
        elif (len(components) >= 4 and
              components[0]['type'] == 'number' and
              components[-2]['type'] == 'number' and
              components[-1]['type'] == 'opcode' and
              components[-1]['value'] == self.OP_CHECKMULTISIG):
            
            m = components[0]['value']
            n = components[-2]['value']
            pubkeys = []
            
            for i in range(1, len(components)-2):
                if components[i]['type'] == 'data':
                    pubkeys.append(components[i]['value'])
                    
            if len(pubkeys) == n:
                analysis['type'] = 'multisig'
                analysis['required_signatures'] = m
                analysis['total_keys'] = n
                analysis['pubkeys'] = pubkeys
                analysis['requirements'].append(f'Need {m} of {n} signatures')
                
        # Check for time-locked pattern
        elif any(c['type'] == 'opcode' and c['value'] in [0xb1, 0xb2] for c in components):  # CHECKLOCKTIMEVERIFY or CHECKSEQUENCEVERIFY
            analysis['type'] = 'timelock'
            analysis['requirements'].append('Time/block conditions must be met')
            
        return analysis
    
    def suggest_spending_path(self, redeem_script_hex: str) -> Dict[str, any]:
        """
        Analyze redeem script and suggest possible spending paths
        """
        analysis = self.analyze_redeem_script(redeem_script_hex)
        suggestions = {
            'type': analysis['type'],
            'requirements': analysis['requirements'],
            'steps': [],
            'tools': []
        }
        
        if analysis['type'] == 'p2pkh':
            suggestions['steps'] = [
                'Generate signature for the spending transaction',
                'Provide the public key matching the hash',
                'Create transaction with proper scriptSig'
            ]
            suggestions['tools'] = ['bitcoin-cli', 'custom_signer']
            
        elif analysis['type'] == 'multisig':
            m = analysis['required_signatures']
            suggestions['steps'] = [
                f'Collect {m} valid signatures from available keys',
                'Order signatures properly',
                'Create transaction with proper scriptSig including OP_0 for bug compatibility'
            ]
            suggestions['tools'] = ['bitcoin-cli', 'multisig_tool']
            
        elif analysis['type'] == 'timelock':
            suggestions['steps'] = [
                'Wait for time/block conditions to be met',
                'Generate appropriate signature',
                'Create transaction with nLockTime/nSequence set properly'
            ]
            suggestions['tools'] = ['bitcoin-cli', 'timelock_checker']
            
        return suggestions

def main():
    analyzer = P2SHAnalyzer()
    
    # Example redeem script (2-of-3 multisig)
    redeem_script = "522102a5613bd857b7048924264d1e70e08fb2a7e6527d32b7ab1bb993ac59964ff397210397dae58c4f31e7120f5e5bfda9471c3a356a767a35b58f5d4b5c8a068291aff221024d4b6cd1361032ca9bd2aeb9d900aa4d45d9ead80ac9423374c451a7254d0766753ae"
    
    print("\nP2SH Script Analysis:")
    print("-" * 50)
    
    # Parse script components
    print("\nScript Components:")
    components = analyzer.parse_script(redeem_script)
    for i, comp in enumerate(components):
        print(f"{i+1}. Type: {comp['type']}")
        if comp['type'] == 'data':
            print(f"   Value: {comp['value'][:8]}...")
        else:
            print(f"   Value: {comp['value']}")
            
    # Analyze redeem script
    analysis = analyzer.analyze_redeem_script(redeem_script)
    print(f"\nScript Type: {analysis['type']}")
    print("Requirements:")
    for req in analysis['requirements']:
        print(f"- {req}")
        
    # Get spending suggestions
    suggestions = analyzer.suggest_spending_path(redeem_script)
    print("\nSuggested Spending Path:")
    print("Steps:")
    for i, step in enumerate(suggestions['steps']):
        print(f"{i+1}. {step}")
    print("\nRecommended Tools:")
    for tool in suggestions['tools']:
        print(f"- {tool}")

if __name__ == "__main__":
    main()  