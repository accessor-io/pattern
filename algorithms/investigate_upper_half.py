#!/usr/bin/env python3
"""
Investigate the spending of upper half Bitcoin puzzle addresses.
The theory is that positions 161-256 (or similar) were intentionally spent by the creator,
exposing their private keys, and the funds were consolidated back into positions 1-160.
"""

import urllib.request
import urllib.error
import time
import json

def generate_puzzle_address_from_position(position):
    """
    Generate the expected Bitcoin address for a given puzzle position.
    This uses the known pattern: private_key = position (in binary range)
    """
    # For now, we'll use the known addresses from positions 1-160
    # but we need to extrapolate for positions 161-256
    
    # This is a placeholder - the actual generation requires the private key
    # But we can check if addresses exist and have been spent
    return None

def check_address_spent(address):
    """
    Check if a Bitcoin address has been spent (has outgoing transactions)
    """
    try:
        # Using blockstream.info API to check address activity
        url = f"https://blockstream.info/api/address/{address}/txs"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                txs = json.loads(data)
                
                # Check if any transaction spends from this address (has inputs from this address)
                for tx in txs:
                    for tx_in in tx.get('vin', []):
                        if tx_in.get('prevout', {}).get('scriptpubkey_address') == address:
                            return True, tx['txid']
        
        return False, None
        
    except Exception as e:
        print(f"Error checking address {address}: {e}")
        return None, None

def investigate_original_transaction():
    """
    Investigate the original Bitcoin puzzle creation transaction to find all funded addresses
    """
    creation_txid = "08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15"
    
    try:
        url = f"https://blockstream.info/api/tx/{creation_txid}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                tx_data = json.loads(data)
                
                print("=== ORIGINAL PUZZLE CREATION TRANSACTION ===")
                print(f"TX ID: {creation_txid}")
                print(f"Block Height: {tx_data.get('status', {}).get('block_height', 'Unknown')}")
                print(f"Confirmation Time: {tx_data.get('status', {}).get('block_time', 'Unknown')}")
                
                outputs = tx_data.get('vout', [])
                print(f"Total Outputs: {len(outputs)}")
                
                puzzle_addresses = []
                for i, output in enumerate(outputs):
                    address = output.get('scriptpubkey_address')
                    value_satoshis = output.get('value', 0)
                    value_btc = value_satoshis / 100000000  # Convert satoshis to BTC
                    
                    if address and value_btc > 0:
                        # Check if this looks like a puzzle address (value = position/1000)
                        expected_position = round(value_btc * 1000)
                        if abs(value_btc - expected_position/1000) < 0.0001:  # Allow small rounding
                            puzzle_addresses.append((expected_position, address, value_btc))
                
                print(f"Identified {len(puzzle_addresses)} puzzle addresses")
                
                # Sort by position
                puzzle_addresses.sort(key=lambda x: x[0])
                
                # Show first and last few
                print("\nFirst 10 puzzle addresses:")
                for pos, addr, btc in puzzle_addresses[:10]:
                    print(f"  Position {pos:3}: {addr} ({btc:.3f} BTC)")
                
                print("\nLast 10 puzzle addresses:")
                for pos, addr, btc in puzzle_addresses[-10:]:
                    print(f"  Position {pos:3}: {addr} ({btc:.3f} BTC)")
                
                return puzzle_addresses
            
    except Exception as e:
        print(f"Error investigating original transaction: {e}")
        return []

def check_upper_addresses_spent(puzzle_addresses, start_position=161):
    """
    Check if addresses from start_position onwards have been spent
    """
    print(f"\n=== CHECKING IF UPPER ADDRESSES (>= {start_position}) WERE SPENT ===")
    
    spent_addresses = []
    unspent_addresses = []
    
    upper_addresses = [addr for addr in puzzle_addresses if addr[0] >= start_position]
    print(f"Found {len(upper_addresses)} addresses with position >= {start_position}")
    
    for pos, address, btc in upper_addresses:
        print(f"Checking position {pos}: {address}")
        
        spent, spending_txid = check_address_spent(address)
        
        if spent:
            spent_addresses.append((pos, address, spending_txid))
            print(f"  ✓ SPENT in transaction: {spending_txid}")
        elif spent is False:
            unspent_addresses.append((pos, address))
            print(f"  ○ Unspent")
        else:
            print(f"  ? Error checking")
        
        # Rate limiting to be respectful to the API
        time.sleep(1)
    
    print(f"\n=== SUMMARY ===")
    print(f"Spent addresses (>= position {start_position}): {len(spent_addresses)}")
    print(f"Unspent addresses (>= position {start_position}): {len(unspent_addresses)}")
    
    if spent_addresses:
        print("\nSpent addresses:")
        for pos, addr, txid in spent_addresses:
            print(f"  Position {pos}: {addr} -> {txid}")
    
    return spent_addresses, unspent_addresses

def analyze_spending_transactions(spent_addresses):
    """
    Analyze the transactions that spent from the upper addresses
    to see if we can extract private key information
    """
    print(f"\n=== ANALYZING SPENDING TRANSACTIONS ===")
    
    for pos, address, spending_txid in spent_addresses:
        print(f"\nAnalyzing spending of position {pos} ({address}):")
        print(f"Spending TX: {spending_txid}")
        
        try:
            url = f"https://blockstream.info/api/tx/{spending_txid}"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    tx_data = json.loads(data)
                    
                    # Look at inputs to find the one spending from our address
                    for vin in tx_data.get('vin', []):
                        if vin.get('prevout', {}).get('scriptpubkey_address') == address:
                            print(f"  Input spending from {address}:")
                            print(f"    Witness: {vin.get('witness', [])}")
                            print(f"    Script Sig: {vin.get('scriptsig', {})}")
                            
                            # The signature in the witness/scriptsig was created with the private key
                            witness = vin.get('witness', [])
                            if len(witness) >= 2:
                                signature = witness[0]
                                pubkey = witness[1]
                                print(f"    Signature: {signature}")
                                print(f"    Public Key: {pubkey}")
                                
                                # Try to extract the private key from the signature if possible
                                # (This is complex and may not always be possible)
                                
        except Exception as e:
            print(f"  Error analyzing transaction: {e}")
        
        time.sleep(1)

def main():
    print("=== INVESTIGATING UPPER HALF BITCOIN PUZZLE ADDRESSES ===")
    print()
    print("Theory: The creator funded positions 1-256 but then spent positions 161-256,")
    print("exposing their private keys, and consolidated into the current 1-160 structure.")
    print()
    
    # Step 1: Get all addresses from the original transaction
    puzzle_addresses = investigate_original_transaction()
    
    if not puzzle_addresses:
        print("Could not retrieve original transaction data")
        return
    
    # Step 2: Check which upper addresses have been spent
    spent_addresses, unspent_addresses = check_upper_addresses_spent(puzzle_addresses, start_position=161)
    
    # Step 3: If any were spent, analyze those transactions
    if spent_addresses:
        analyze_spending_transactions(spent_addresses[:5])  # Limit to first 5 to avoid rate limits
    else:
        print("No spent addresses found in the upper range")
        
        # Maybe try a different threshold
        print("\nTrying a different threshold (>= 129)...")
        spent_addresses, unspent_addresses = check_upper_addresses_spent(puzzle_addresses, start_position=129)
        
        if spent_addresses:
            analyze_spending_transactions(spent_addresses[:3])

if __name__ == "__main__":
    main() 