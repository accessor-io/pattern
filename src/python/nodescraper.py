import requests
from bs4 import BeautifulSoup
import concurrent.futures
import socket
import json
from datetime import datetime
import threading
import re
import time
import logging

class EthNodeScanner:
    def __init__(self):
        self.base_url = "https://etherscan.io/nodetracker"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.nodes = []
        self.lock = threading.Lock()
        self.setup_logging()
        
        # Expanded port list
        self.target_ports = {
            30303: 'ETH Discovery UDP',
            30304: 'ETH Alternative',
            30305: 'ETH Backup',
            8545: 'ETH RPC-HTTP',
            8546: 'ETH RPC-WebSocket',
            8551: 'ETH Engine API',
            443: 'HTTPS',
            80: 'HTTP',
            8080: 'Alternative HTTP',
            6060: 'ETH Metrics',
            9090: 'ETH Prometheus'
        }

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler('node_scanner.log'),
                logging.StreamHandler()
            ]
        )

    def extract_ips(self, html_content):
        ip_addresses = set()
        
        # Multiple IP extraction methods
        methods = [
            self.extract_from_table,
            self.extract_from_text,
            self.extract_from_scripts
        ]
        
        for method in methods:
            try:
                found_ips = method(html_content)
                logging.info(f"Found {len(found_ips)} IPs using {method.__name__}")
                ip_addresses.update(found_ips)
            except Exception as e:
                logging.error(f"Error in {method.__name__}: {str(e)}")
        
        return ip_addresses

    def extract_from_table(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        ip_addresses = set()
        
        # Look for tables
        tables = soup.find_all('table')
        logging.info(f"Found {len(tables)} tables to analyze")
        
        for table in tables:
            rows = table.find_all('tr')
            logging.debug(f"Processing table with {len(rows)} rows")
            
            for row in rows:
                cols = row.find_all('td')
                for col in cols:
                    text = col.get_text().strip()
                    ips = self.find_ips_in_text(text)
                    if ips:
                        ip_addresses.update(ips)
                        logging.debug(f"Found IP in table: {ips}")
        
        return ip_addresses

    def extract_from_text(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        return set(self.find_ips_in_text(text))

    def extract_from_scripts(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        ip_addresses = set()
        
        # Look in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                ips = self.find_ips_in_text(script.string)
                ip_addresses.update(ips)
        
        return ip_addresses

    def find_ips_in_text(self, text):
        # Enhanced IP regex pattern
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        return re.findall(ip_pattern, text)

    def fetch_and_scan(self):
        try:
            logging.info("Starting node discovery...")
            
            # Try multiple pages
            pages_to_try = [
                self.base_url,
                f"{self.base_url}/nodes",
                f"{self.base_url}?ps=100",  # Try to get more results
                "https://etherscan.io/nodes"
            ]
            
            all_ips = set()
            for url in pages_to_try:
                try:
                    logging.info(f"Fetching from {url}")
                    response = requests.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    ips = self.extract_ips(response.text)
                    logging.info(f"Found {len(ips)} IPs from {url}")
                    all_ips.update(ips)
                    
                    # Respect rate limits
                    time.sleep(2)
                    
                except Exception as e:
                    logging.error(f"Error fetching {url}: {str(e)}")
            
            logging.info(f"Total unique IPs found: {len(all_ips)}")
            
            # Start port scanning
            if all_ips:
                logging.info("Beginning port scan...")
                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                    executor.map(self.scan_ports, all_ips)
            
            return True
            
        except Exception as e:
            logging.error(f"Critical error in fetch_and_scan: {str(e)}")
            return False

    # ... (rest of the methods remain the same)

if __name__ == "__main__":
    scanner = EthNodeScanner()
    
    print("=== Enhanced Ethereum Node Scanner ===")
    print(f"Time: {datetime.now()}")
    print(f"Scanning ports: {', '.join(map(str, scanner.target_ports.keys()))}")
    print("=" * 50 + "\n")
    
    try:
        if scanner.fetch_and_scan():
            scanner.print_summary()
            print("\nFull results saved to eth_nodes_scan.json")
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        scanner.print_summary()
    except Exception as e:
        logging.critical(f"Unhandled error: {str(e)}")