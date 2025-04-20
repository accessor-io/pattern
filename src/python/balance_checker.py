import requests
import time

class BalanceChecker:
    def __init__(self):
        self.addresses = [
            # Hardened children
            "1hSb3zasGqbGsF7BLfhNqwuBBZdwGFtbCM3k9zWuuLSPefRk9S",  # m/0'
            "12WkyaGRJ5psZKKJCfbFQNPTyvnDFqHdSUDwqVtaWtwezkATGpu",  # m/1'
            
            # Normal children
            "1AYLo9kVgNzCJq2SpPB86R5TW7YgFLQKrAimZBV6W3NZEzhyHA",  # m/0
            "1GdnzAeENWbc5KVWkX7zAwrscf4dMZCnaRDboHYGvhJJuocisg",  # m/0/1
            "12iBbuj9db9RkP46GpHxtpfXoDfvfm5KqiTepVZg55ZEAbxGz9G",  # m/0/2
            "12Ytu99fJHVPQCh7Q9J8yxi7JCuJaJe48YBJcpKAgyCGxsLDVQy"   # m/0/3
        ]
        
    def check_balance_blockchair(self, address):
        """Check balance using Blockchair API"""
        url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and address in data['data']:
                    addr_data = data['data'][address]
                    return {
                        'balance': addr_data['address']['balance'],
                        'total_received': addr_data['address']['received'],
                        'total_sent': addr_data['address']['spent'],
                        'tx_count': addr_data['address']['transaction_count']
                    }
            return None
        except:
            return None
            
    def check_balance_blockchain_info(self, address):
        """Check balance using Blockchain.info API"""
        url = f"https://blockchain.info/address/{address}?format=json"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    'balance': data['final_balance'],
                    'total_received': data['total_received'],
                    'total_sent': data['total_sent'],
                    'tx_count': data['n_tx']
                }
            return None
        except:
            return None
            
    def check_balance_blockcypher(self, address):
        """Check balance using BlockCypher API"""
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    'balance': data['final_balance'],
                    'total_received': data['total_received'],
                    'total_sent': data['total_sent'],
                    'tx_count': data['n_tx']
                }
            return None
        except:
            return None
            
    def check_all_balances(self):
        print("Checking Bitcoin Address Balances")
        print("=" * 50)
        
        for address in self.addresses:
            print(f"\nChecking address: {address}")
            
            # Try multiple APIs
            balance_data = None
            
            # Try Blockchair
            print("Checking Blockchair...")
            balance_data = self.check_balance_blockchair(address)
            
            # If failed, try Blockchain.info
            if not balance_data:
                print("Checking Blockchain.info...")
                balance_data = self.check_balance_blockchain_info(address)
                
            # If still failed, try BlockCypher
            if not balance_data:
                print("Checking BlockCypher...")
                balance_data = self.check_balance_blockcypher(address)
            
            if balance_data:
                print("\nBalance Information:")
                print(f"Current Balance: {balance_data['balance']/100000000:.8f} BTC")
                print(f"Total Received: {balance_data['total_received']/100000000:.8f} BTC")
                print(f"Total Sent: {balance_data['total_sent']/100000000:.8f} BTC")
                print(f"Transaction Count: {balance_data['tx_count']}")
            else:
                print("Could not fetch balance data")
                
            # Sleep to respect API rate limits
            time.sleep(1)
            
        print("\nBalance check complete!")

def main():
    checker = BalanceChecker()
    checker.check_all_balances()

if __name__ == "__main__":
    main() 