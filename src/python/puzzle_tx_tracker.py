import requests
import json
import time
import os
from datetime import datetime
from collections import defaultdict, Counter
import concurrent.futures
import threading
import hashlib
import binascii
from concurrent.futures import ThreadPoolExecutor

class PuzzleTxTracker:
    def __init__(self):
        self.puzzle_addresses = {}  # Maps puzzle number to address
        self.tx_history = defaultdict(list)  # Maps txids to list of uses
        self.reused_txids = defaultdict(list)  # Maps txids to list of reused txid information
        self.output_patterns = defaultdict(list)  # Maps txids to list of output indices used
        self.consecutive_solves = []  # Track puzzles solved in sequence
        self.cache_dir = "tx_cache"
        self.apis = [
            "https://blockchain.info/rawaddr/{}",
            "https://api.blockcypher.com/v1/btc/main/addrs/{}/full",
            "https://blockstream.info/api/address/{}/txs"
        ]
        self.api_lock = threading.Lock()
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)

        self.tx_data = defaultdict(list)  # Maps TxIDs to list of puzzles
        self.script_types = defaultdict(int)
        self.sighash_flags = defaultdict(int)
        self.p2sh_patterns = defaultdict(list)
        self.reused_txids = defaultdict(list)
        self.tx_patterns = defaultdict(list)
        self.processed_addresses = set()  # Set of addresses that have been processed

    def get_cache_path(self, address):
        """Get cache file path for an address"""
        return os.path.join(self.cache_dir, f"{address}.json")

    def load_from_cache(self, address):
        """Load transaction data from cache if available"""
        cache_path = self.get_cache_path(address)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache for {address}: {e}")
        return None

    def save_to_cache(self, address, data):
        """Save transaction data to cache"""
        cache_path = self.get_cache_path(address)
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving cache for {address}: {e}")

    def load_puzzle_addresses(self, puzzle_data):
        """Load puzzle addresses from the provided data"""
        for line in puzzle_data.split('\n'):
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) >= 4:
                puzzle_num = parts[0].strip()
                address = parts[3].strip()
                if address.startswith('C '):
                    address = address[2:]
                self.puzzle_addresses[puzzle_num] = address

    def fetch_tx_history(self, address):
        """Fetch transaction history for an address"""
        cache_path = self.get_cache_path(address)
        
        # Try to load from cache first
        if os.path.exists(cache_path):
            print(f"Using cached data for {address}")
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                    return cached_data
            except json.JSONDecodeError:
                print(f"Error decoding cached data for {address}")
        
        # If not in cache, try each API
        for api in self.apis:
            try:
                with self.api_lock:
                    url = api.format(address)
                    print(f"Fetching from {url}")
                    response = requests.get(url)
                    
                if response.status_code == 200:
                    data = response.json()
                    print(f"Got response from {url}")
                    
                    # Save raw API response to cache
                    with open(cache_path, 'w') as f:
                        json.dump(data, f)
                    
                    return data
                    
                elif response.status_code == 429:  # Rate limited
                    print(f"Rate limited by {api}, waiting 30s...")
                    time.sleep(30)
                    continue
                else:
                    print(f"Error {response.status_code} from {api}")
                    
            except Exception as e:
                print(f"Error fetching data from {api}: {e}")
                continue
                
        return None

    def process_batch(self, batch):
        """Process a batch of addresses concurrently"""
        results = []
        for puzzle_num, address in batch:
            print(f"Analyzing puzzle #{puzzle_num} - {address}")
            tx_data = self.fetch_tx_history(address)
            if tx_data:
                self.process_transactions(puzzle_num, tx_data)
            results.append((puzzle_num, bool(tx_data)))
        return results

    def analyze_transactions(self):
        """Analyze transactions for all puzzle addresses"""
        self.load_progress()
        
        with open("puzzle_addresses.txt", "r") as f:
            # Format: puzzle_num    range   key    address
            puzzle_data = [line.strip().split("\t") for line in f if line.strip()]
        
        # Process addresses in batches of 3
        batch_size = 3
        for i in range(0, len(puzzle_data), batch_size):
            batch = puzzle_data[i:i + batch_size]
            print(f"\nSubmitting batch {i//batch_size + 1} for analysis")
            
            for puzzle in batch:
                puzzle_num = puzzle[0]
                address = puzzle[3]
                if address.startswith('C '):
                    address = address[2:]
                    
                print(f"\nAnalyzing puzzle #{puzzle_num} - {address}")
                txs = self.fetch_tx_history(address)
                if txs:
                    self.process_transactions(address, txs)
                    self.processed_addresses.add(address)
                    self.save_progress()
            
            # Wait between batches to avoid rate limits
            if i + batch_size < len(puzzle_data):
                print("\nWaiting between batches...")
                time.sleep(10)
        
        self.print_analysis()

    def save_progress(self):
        """Save current analysis progress"""
        data = {
            "processed_addresses": list(self.processed_addresses),
            "script_types": dict(self.script_types),
            "sighash_flags": dict(self.sighash_flags),
            "p2sh_patterns": dict(self.p2sh_patterns),
            "reused_txids": dict(self.reused_txids)
        }
        try:
            with open('analysis_progress.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def load_progress(self):
        """Load previous analysis progress if available"""
        try:
            if os.path.exists('analysis_progress.json'):
                with open('analysis_progress.json', 'r') as f:
                    data = json.load(f)
                self.processed_addresses = set(data.get("processed_addresses", []))
                self.script_types = Counter(data.get("script_types", {}))
                self.sighash_flags = Counter(data.get("sighash_flags", {}))
                self.p2sh_patterns = defaultdict(list, data.get("p2sh_patterns", {}))
                self.reused_txids = defaultdict(list, data.get("reused_txids", {}))
                return True
        except Exception as e:
            print(f"Error loading progress: {e}")
        return False

    def process_transactions(self, address, txs_data):
        """Process transactions from API response"""
        if not txs_data:
            return

        # Handle blockchain.info format
        if 'txs' in txs_data:
            transactions = txs_data['txs']
            for tx in transactions:
                tx_id = tx.get('hash', '')
                if not tx_id:
                    continue

                # Process inputs
                for inp in tx.get('inputs', []):
                    prev_out = inp.get('prev_out', {})
                    script = inp.get('script', '')
                    if script:
                        script_type = self.analyze_script_type(script)
                        self.script_types[script_type] += 1
                        sighash = self.extract_sighash_flags(script)
                        self.sighash_flags[sighash] += 1

                    prev_tx = prev_out.get('tx_index', '')
                    if prev_tx:
                        self.reused_txids[str(prev_tx)].append({
                            'puzzle': address,
                            'tx_id': tx_id,
                            'script_type': script_type if script else 'UNKNOWN',
                            'sighash': sighash if script else 'UNKNOWN'
                        })

                # Process outputs
                for out in tx.get('out', []):
                    script = out.get('script', '')
                    if script:
                        script_type = self.analyze_script_type(script)
                        self.script_types[script_type] += 1
                        if script_type == 'P2SH':
                            p2sh_data = self.analyze_p2sh(script)
                            if p2sh_data:
                                self.p2sh_patterns[tx_id].append(p2sh_data)

        # Handle blockcypher format
        elif 'txrefs' in txs_data:
            transactions = txs_data['txrefs']
            for tx in transactions:
                tx_id = tx.get('tx_hash', '')
                if not tx_id:
                    continue

                script_type = tx.get('script_type', 'UNKNOWN')
                self.script_types[script_type] += 1

                if script_type == 'P2SH':
                    p2sh_data = "Blockcypher P2SH"  # Basic P2SH detection
                    self.p2sh_patterns[tx_id].append(p2sh_data)

        # Handle blockstream.info format
        elif isinstance(txs_data, list):
            for tx in txs_data:
                tx_id = tx.get('txid', '')
                if not tx_id:
                    continue

                # Process inputs (vins)
                for vin in tx.get('vin', []):
                    script = vin.get('scriptsig', '')
                    if script:
                        script_type = self.analyze_script_type(script)
                        self.script_types[script_type] += 1
                        sighash = self.extract_sighash_flags(script)
                        self.sighash_flags[sighash] += 1

                    prev_tx = vin.get('txid', '')
                    if prev_tx:
                        self.reused_txids[prev_tx].append({
                            'puzzle': address,
                            'tx_id': tx_id,
                            'script_type': script_type if script else 'UNKNOWN',
                            'sighash': sighash if script else 'UNKNOWN'
                        })

                # Process outputs (vouts)
                for vout in tx.get('vout', []):
                    script = vout.get('scriptpubkey', '')
                    if script:
                        script_type = self.analyze_script_type(script)
                        self.script_types[script_type] += 1
                        if script_type == 'P2SH':
                            p2sh_data = self.analyze_p2sh(script)
                            if p2sh_data:
                                self.p2sh_patterns[tx_id].append(p2sh_data)

    def analyze_script_type(self, script_hex):
        """Analyze the type of Bitcoin script"""
        try:
            if not script_hex:
                return "EMPTY"
                
            script_bytes = bytes.fromhex(script_hex)
            if len(script_bytes) == 0:
                return "EMPTY"
            
            # P2PKH pattern: OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
            if (len(script_bytes) >= 25 and
                script_bytes[0] == 0x76 and  # OP_DUP
                script_bytes[1] == 0xa9 and  # OP_HASH160
                script_bytes[2] == 0x14 and  # Push 20 bytes
                script_bytes[-2] == 0x88 and # OP_EQUALVERIFY
                script_bytes[-1] == 0xac):   # OP_CHECKSIG
                return "P2PKH"
                
            # P2SH pattern: OP_HASH160 <scriptHash> OP_EQUAL
            if (len(script_bytes) >= 23 and
                script_bytes[0] == 0xa9 and  # OP_HASH160
                script_bytes[1] == 0x14 and  # Push 20 bytes
                script_bytes[-1] == 0x87):   # OP_EQUAL
                return "P2SH"
                
            # P2PK pattern: <pubKey> OP_CHECKSIG
            if (len(script_bytes) >= 35 and
                script_bytes[-1] == 0xac):   # OP_CHECKSIG
                return "P2PK"
                
            # Multisig pattern: m <pubkey1> ... <pubkeyn> n OP_CHECKMULTISIG
            if script_bytes[-1] == 0xae:     # OP_CHECKMULTISIG
                return "MULTISIG"
                
            # P2WPKH pattern: OP_0 <20-byte-key-hash>
            if (len(script_bytes) == 22 and
                script_bytes[0] == 0x00 and  # OP_0
                script_bytes[1] == 0x14):    # Push 20 bytes
                return "P2WPKH"
                
            # P2WSH pattern: OP_0 <32-byte-script-hash>
            if (len(script_bytes) == 34 and
                script_bytes[0] == 0x00 and  # OP_0
                script_bytes[1] == 0x20):    # Push 32 bytes
                return "P2WSH"
                
            # Null data pattern: OP_RETURN
            if script_bytes[0] == 0x6a:      # OP_RETURN
                return "NULL_DATA"
                
            # Check for signature script
            if (len(script_bytes) >= 70 and   # DER signature is typically ~70-72 bytes
                script_bytes[0] >= 0x47 and   # Push bytes for signature
                script_bytes[1] == 0x30):     # DER sequence
                return "SIGNATURE"
                
            return "NONSTANDARD"
        except Exception as e:
            print(f"Error analyzing script type: {e}")
            return "INVALID"

    def extract_sighash_flags(self, script_hex):
        try:
            script_bytes = bytes.fromhex(script_hex)
            if len(script_bytes) < 70:  # Minimum size for DER signature
                return "INVALID"
            
            # Look for DER signature
            der_start = script_bytes.find(bytes([0x30]))
            if der_start == -1:
                return "UNKNOWN"
                
            # Get sighash flag (last byte)
            sighash = script_bytes[-1]
            flags = []
            
            if sighash & 0x1f == 0x01:
                flags.append("SIGHASH_ALL")
            elif sighash & 0x1f == 0x02:
                flags.append("SIGHASH_NONE")
            elif sighash & 0x1f == 0x03:
                flags.append("SIGHASH_SINGLE")
                
            if sighash & 0x80:
                flags.append("ANYONECANPAY")
                
            return "|".join(flags) if flags else "UNKNOWN"
        except Exception:
            return "INVALID"

    def analyze_p2sh(self, script_hex):
        try:
            script_bytes = bytes.fromhex(script_hex)
            if len(script_bytes) < 3:
                return None
                
            # Extract redeem script
            push_size = script_bytes[0]
            if push_size + 1 > len(script_bytes):
                return None
                
            redeem_script = script_bytes[1:push_size+1]
            if len(redeem_script) == 0:
                return None
                
            # Analyze redeem script
            if redeem_script[-1] == 0xae:  # OP_CHECKMULTISIG
                m = redeem_script[0] - 0x50 if redeem_script[0] >= 0x51 else 0
                n = redeem_script[-2] - 0x50 if redeem_script[-2] >= 0x51 else 0
                if 1 <= m <= n <= 15:
                    return f"{m}-of-{n} multisig"
                    
            if redeem_script[0] == 0xb1:  # OP_CHECKSEQUENCEVERIFY
                return "CSV timelock"
                
            if redeem_script[0] == 0xb2:  # OP_CHECKLOCKTIMEVERIFY
                return "CLTV timelock"
                
            return "Unknown redeem script"
        except Exception:
            return None

    def print_analysis(self):
        print("\n=== Analysis Summary ===")
        
        print("\nScript Types:")
        for script_type, count in sorted(self.script_types.items(), key=lambda x: x[1], reverse=True):
            print(f"{script_type}: {count}")
        
        print("\nSighash Flags:")
        for flag, count in sorted(self.sighash_flags.items(), key=lambda x: x[1], reverse=True):
            print(f"{flag}: {count}")
        
        print("\nP2SH Patterns:")
        for tx_id, patterns in list(self.p2sh_patterns.items())[:5]:
            print(f"TxID {tx_id}: {len(patterns)} patterns")
            for pattern in patterns[:2]:
                print(f"  - {pattern}")
        if len(self.p2sh_patterns) > 5:
            print(f"... and {len(self.p2sh_patterns) - 5} more transactions")
        
        print("\nReused TxID Patterns:")
        sorted_txids = sorted(self.reused_txids.items(), key=lambda x: len(x[1]), reverse=True)
        for txid, uses in sorted_txids[:5]:
            puzzles = sorted(set(use['puzzle'] for use in uses))
            print(f"\nTxID {txid}:")
            print(f"  Used in {len(puzzles)} puzzles: {', '.join(puzzles)}")
            print(f"  Script Types: {', '.join(set(use['script_type'] for use in uses))}")
            print(f"  Sighash Flags: {', '.join(set(use['sighash'] for use in uses))}")
        if len(sorted_txids) > 5:
            print(f"\n... and {len(sorted_txids) - 5} more reused TxIDs")

def main():
    tracker = PuzzleTxTracker()
    
    # Load puzzle data
    with open('puzzle_addresses.txt', 'r') as f:
        puzzle_data = f.read()
    
    tracker.load_puzzle_addresses(puzzle_data)
    
    # Try to load previous progress
    if tracker.load_progress():
        print("Resumed from previous progress")
    
    tracker.analyze_transactions()

if __name__ == "__main__":
    main() 