#!/usr/bin/env python3

from typing import List, Dict, Tuple
import hashlib
import hmac
import ecdsa
from binascii import hexlify, unhexlify

class BIP44Analyzer:
    def __init__(self):
        self.HARDENED_INDEX = 0x80000000
        self.BITCOIN_SEED = b'Bitcoin seed'
        self.CURVE = ecdsa.SECP256k1
        
    def _hmac_sha512(self, key: bytes, msg: bytes) -> bytes:
        """Generate HMAC-SHA512"""
        return hmac.new(key, msg, hashlib.sha512).digest()
    
    def _derive_master_key(self, seed: bytes) -> Tuple[bytes, bytes]:
        """Derive master private key and chain code from seed"""
        I = self._hmac_sha512(self.BITCOIN_SEED, seed)
        master_private_key = I[:32]
        chain_code = I[32:]
        return master_private_key, chain_code
    
    def _ckd_priv(self, parent_key: bytes, parent_chain: bytes, i: int) -> Tuple[bytes, bytes]:
        """Child Key Derivation for private keys"""
        if i & self.HARDENED_INDEX:
            # Hardened derivation
            data = b'\x00' + parent_key + i.to_bytes(4, 'big')
        else:
            # Normal derivation
            parent_pub = self._privkey_to_pubkey(parent_key)
            data = parent_pub + i.to_bytes(4, 'big')
            
        I = self._hmac_sha512(parent_chain, data)
        child_key = (int.from_bytes(I[:32], 'big') + 
                    int.from_bytes(parent_key, 'big')) % self.CURVE.order
        child_chain = I[32:]
        
        return child_key.to_bytes(32, 'big'), child_chain
    
    def _privkey_to_pubkey(self, private_key: bytes) -> bytes:
        """Convert private key to public key"""
        signing_key = ecdsa.SigningKey.from_string(private_key, curve=self.CURVE)
        verifying_key = signing_key.get_verifying_key()
        return b'\x04' + verifying_key.to_string()
    
    def analyze_path(self, path: str, xpub: str = None) -> Dict[str, any]:
        """
        Analyze a BIP44 derivation path
        path format: m/44'/0'/account'/change/index
        """
        analysis = {
            'path': path,
            'components': [],
            'type': 'unknown',
            'warnings': [],
            'suggestions': []
        }
        
        # Parse path components
        if not path.startswith('m/'):
            analysis['warnings'].append('Path should start with "m/"')
            return analysis
            
        components = path[2:].split('/')
        if len(components) != 5:
            analysis['warnings'].append('BIP44 requires exactly 5 levels')
            return analysis
            
        # Analyze each component
        try:
            purpose = int(components[0].rstrip("'"))
            coin_type = int(components[1].rstrip("'"))
            account = int(components[2].rstrip("'"))
            change = int(components[3])
            index = int(components[4])
            
            analysis['components'] = [
                {'level': 'purpose', 'value': purpose, 'hardened': "'" in components[0]},
                {'level': 'coin_type', 'value': coin_type, 'hardened': "'" in components[1]},
                {'level': 'account', 'value': account, 'hardened': "'" in components[2]},
                {'level': 'change', 'value': change, 'hardened': "'" in components[3]},
                {'level': 'index', 'value': index, 'hardened': "'" in components[4]}
            ]
            
            # Validate purpose
            if purpose != 44:
                analysis['warnings'].append('Non-standard purpose value (should be 44)')
                
            # Validate coin type (0 for Bitcoin)
            if coin_type != 0:
                analysis['warnings'].append('Non-Bitcoin coin type')
                
            # Validate hardened/non-hardened components
            if not all(c['hardened'] for c in analysis['components'][:3]):
                analysis['warnings'].append('First three levels should be hardened')
            if any(c['hardened'] for c in analysis['components'][3:]):
                analysis['warnings'].append('Last two levels should not be hardened')
                
            # Determine path type
            if change == 0:
                analysis['type'] = 'external (receiving)'
            elif change == 1:
                analysis['type'] = 'internal (change)'
            else:
                analysis['type'] = 'non-standard'
                analysis['warnings'].append('Non-standard change value')
                
            # Add suggestions
            if index > 20:
                analysis['suggestions'].append('High index value - consider scanning earlier addresses first')
            if account > 0:
                analysis['suggestions'].append('Non-zero account - ensure previous accounts are used')
                
        except ValueError:
            analysis['warnings'].append('Invalid number format in path')
            
        return analysis
    
    def suggest_scanning_strategy(self, xpub: str = None) -> Dict[str, any]:
        """
        Suggest a strategy for scanning possible addresses
        """
        strategy = {
            'paths_to_check': [],
            'priority_order': [],
            'estimated_addresses': 0
        }
        
        # Common patterns to check
        patterns = []
        
        # Standard receiving addresses
        for account in range(2):
            for index in range(20):
                patterns.append(f"m/44'/0'/{account}'/0/{index}")
                
        # Change addresses for account 0
        for index in range(10):
            patterns.append(f"m/44'/0'/0'/1/{index}")
            
        # Add to strategy with priority
        for path in patterns:
            analysis = self.analyze_path(path)
            priority = 1
            
            # Adjust priority based on path properties
            if analysis['type'] == 'internal (change)':
                priority += 1
            if any('high index' in s.lower() for s in analysis.get('suggestions', [])):
                priority += 1
            if any('non-zero account' in s.lower() for s in analysis.get('suggestions', [])):
                priority += 1
                
            strategy['paths_to_check'].append({
                'path': path,
                'priority': priority,
                'analysis': analysis
            })
            
        # Sort by priority
        strategy['paths_to_check'].sort(key=lambda x: x['priority'])
        strategy['priority_order'] = [p['path'] for p in strategy['paths_to_check']]
        strategy['estimated_addresses'] = len(patterns)
        
        return strategy

def main():
    analyzer = BIP44Analyzer()
    
    # Example paths to analyze
    test_paths = [
        "m/44'/0'/0'/0/0",    # First receiving address
        "m/44'/0'/0'/1/0",    # First change address
        "m/44'/0'/1'/0/0",    # First address of second account
        "m/44'/0'/0'/0/1000", # High index
        "m/44'/1'/0'/0/0",    # Non-Bitcoin coin type
    ]
    
    print("\nBIP44 Path Analysis:")
    print("-" * 50)
    
    for path in test_paths:
        print(f"\nAnalyzing path: {path}")
        analysis = analyzer.analyze_path(path)
        
        print(f"Type: {analysis['type']}")
        
        if analysis['warnings']:
            print("Warnings:")
            for warning in analysis['warnings']:
                print(f"- {warning}")
                
        if analysis['suggestions']:
            print("Suggestions:")
            for suggestion in analysis['suggestions']:
                print(f"- {suggestion}")
                
    print("\nScanning Strategy:")
    print("-" * 50)
    
    strategy = analyzer.suggest_scanning_strategy()
    print(f"Total addresses to check: {strategy['estimated_addresses']}")
    print("\nPriority order (first 5):")
    for i, path in enumerate(strategy['priority_order'][:5]):
        print(f"{i+1}. {path}")

if __name__ == "__main__":
    main() 