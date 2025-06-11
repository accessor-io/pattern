import sqlite3
import json
from typing import Dict, Any

def load_tx_cache() -> Dict[int, Any]:
    """Load transaction cache with strict index alignment to btcdb.py's address list"""
    conn = sqlite3.connect('bitcoin_analysis.db')
    cursor = conn.cursor()
    cache = {}
    
    # 1. Get the original address order from btcdb.py's addresses list
    with open('btcdb.py', 'r') as f:
        content = f.read()
        start = content.find('addresses = [')
        end = content.find(']', start)
        original_addresses = [line.strip('", \n') for line in content[start:end].split('\n')[1:-1]]
    
    # 2. Create direct index mapping from original list
    address_to_index = {addr: idx+1 for idx, addr in enumerate(original_addresses)}
    
    # Ensure we have addresses to query
    if not original_addresses:
        return {}
    
    # Build parameter list with correct number of placeholders
    params = original_addresses.copy() * 2  # WHERE clause + CASE statement
    
    cursor.execute(f'''
        SELECT address, inputs, outputs, received_time 
        FROM transactions
        WHERE address IN ({','.join(['?']*len(original_addresses))})
        ORDER BY CASE address {' '.join([f'WHEN ? THEN {i}' for i in range(len(original_addresses))])}
    ''', params)
    
    for idx, row in enumerate(cursor.fetchall(), start=1):
        address, inputs_json, outputs_json, timestamp = row
        cache[idx] = {
            'address': address,
            'index': idx,
            'timestamp': timestamp,
            'inputs': json.loads(inputs_json),
            'outputs': json.loads(outputs_json),
            'bit_pattern': (1 << idx) - 1,
            'original_order': original_addresses.index(address) + 1
        }
    
    conn.close()
    return cache

def create_difference_table(cache: Dict[int, Any]) -> Dict[int, int]:
    """Generate difference table from cached patterns"""
    diffs = {}
    prev = 0
    for index in sorted(cache.keys()):
        current = cache[index]['bit_pattern']
        diffs[index] = current - prev
        prev = current
    return diffs 