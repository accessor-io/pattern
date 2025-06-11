import requests
import time
from datetime import datetime
import json
import os
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from urllib.parse import urlparse
import logging
from tqdm import tqdm
import aiohttp
import asyncio
import re
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.prompt import Prompt
from rich.syntax import Syntax
import questionary
from rich.tree import Tree
from rich.text import Text
import sys
from rich.live import Live
from rich.console import Console
from rich.panel import Panel
from collections import defaultdict

class CryptoBucketScannerUI:
    def __init__(self):
        self.console = Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        )

    def display_banner(self):
        banner = """
        🔍 Crypto Bucket Scanner 🔍
        [bold green]Searching for cryptocurrency treasures in the cloud[/bold green]
        """
        self.console.print(Panel(banner, style="bold blue", expand=False))

    def display_menu(self) -> dict:
        self.console.clear()
        self.display_banner()
        
        # Replace questionary.form with individual prompts
        choices = {
            "scan_mode": questionary.select(
                "Select scan mode:",
                choices=[
                    "Quick Scan (100 results per keyword)",
                    "Deep Scan (1000 results per keyword)",
                    "Custom Scan"
                ]
            ).ask(),
            "download_files": questionary.confirm("Download suspicious files?", default=True).ask(),
            "analyze_content": questionary.confirm("Analyze file contents?", default=True).ask(),
            "keywords": questionary.checkbox(
                "Select additional keywords to scan:",
                choices=[
                    "NFT Collections",
                    "DeFi Protocols",
                    "Mining Operations",
                    "Exchange Data",
                    "Custom Keywords"
                ]
            ).ask()
        }
        
        return choices

    def display_live_stats(self, scanner):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")
        
        table.add_row("Files Found", str(scanner.stats['total_files_found']))
        table.add_row("High Priority", str(scanner.stats['high_priority_files']))
        table.add_row("Sensitive Content", str(scanner.stats['sensitive_content_found']))
        table.add_row("Errors", str(scanner.stats['errors']))
        
        return table

class CryptoBucketScanner:
    def __init__(self, api_key: str, verbose: bool = False):
        self.api_key = api_key
        self.base_url = "https://buckets.grayhatwarfare.com/api/v2"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.last_request_time = 0
        self.rate_limit_delay = 1
        
        # Setup logging
        self.setup_logging()
        
        # Add high-priority keywords for special attention
        self.high_priority_keywords = {
            "private-key", "wallet.dat", ".env", "secrets.json",
            "keystore", "mnemonic", "seed-phrase"
        }
        
        # Enhanced crypto-related keywords
        self.crypto_keywords = [
            # Major Cryptocurrencies and Tokens
            "bitcoin", "btc", "ethereum", "eth", "usdt", "bnb", "xrp", "ada", "sol",
            "doge", "dot", "shib", "matic", "polygon", "avalanche", "avax", "chainlink",
            "link", "uniswap", "uni", "aave", "compound", "maker", "mkr", "dai",
            
            # Wallet and Key Related
            "wallet", "private-key", "seed-phrase", "wallet.dat", "keystore",
            "utxo", "mnemonic", ".wlt", "wallet.json", "credentials.json",
            "encrypted_key", "backup_wallet", "recovery_phrase", "key.pem",
            "wallet_backup", "metamask_vault", "trezor", "ledger", "exodus",
            
            # Smart Contract Development
            ".sol", "truffle", "hardhat", "ganache", "geth", "web3js", "ethers.js",
            "infura", "alchemy", "etherscan", "remix", ".env", "constructor(",
            "function", "event", "modifier", "mapping", "struct", "interface",
            "abstract", "library", "using", "pragma solidity", "inheritance",
            
            # DeFi Protocol Files
            "liquidity_pool", "amm", "yield_farm", "staking_contract",
            "governance", "timelock", "vesting", "merkle_distributor",
            "oracle", "price_feed", "swap_router", "factory", "pair",
            "lending_pool", "collateral", "flash_loan", "liquidation",
            
            # NFT Development
            "ERC721", "ERC1155", "NFT", "tokenURI", "baseURI", "metadata.json",
            "assets", "collection", "mint", "whitelist", "presale", "airdrop",
            "royalty", "marketplace", "auction", "bid", "offer", "ipfs://",
            "pinata", "arweave", "opensea", "rarible", "foundation",
            
            # Configuration Files
            ".config.js", "secrets.json", ".secret", "config.json", ".env.local",
            ".env.production", "hardhat.config.js", "truffle-config.js",
            "deployment.json", "networks.json", "addresses.json", "abi/",
            
            # Security and Keys
            "apikey", "secret_key", "access_token", "jwt_secret", "rpc_url",
            "infura_key", "etherscan_api", "alchemy_key", "moralis_key",
            "pinata_secret", "aws_key", "firebase_config", "private_key",
            
            # Blockchain Data
            "chaindata", "nodekey", "blockchain", "blocks", "txpool",
            "network", "mainnet", "testnet", "rinkeby", "goerli", "sepolia",
            "mumbai", "bsc", "arbitrum", "optimism", "zkSync", "rollup",
            
            # Mining and Staking
            "mining_pool", "miner_config", "worker", "hashrate", "payout",
            "stake_pool", "validator", "node_operator", "consensus",
            "proof_of_stake", "delegation", "slashing", "rewards",
            
            # Protocol Specific
            "uniswap_v2", "uniswap_v3", "sushiswap", "pancakeswap",
            "curve_pool", "balancer", "yearn", "compound", "aave_v2",
            "aave_v3", "maker_dao", "synthetix", "chainlink_oracle",
            
            # Development Tools
            "brownie/", "foundry/", "forge/", "cast/", "anvil/",
            "tenderly/", "hardhat/", "waffle/", "slither/", "mythril/",
            "echidna/", "truffle/", "openzeppelin/", "defender/",
            
            # Smart Contract Patterns
            "proxy", "implementation", "upgradeable", "beacon", "factory",
            "registry", "multicall", "flashloan", "reentrancy", "pausable",
            "ownable", "access_control", "eip712", "permit", "signature",
            
            # Deployment and Testing
            "deploy.js", "deploy.py", "migration", "test.js", "test.sol",
            "fixture", "mock", "setup", "scenario", "fork_mainnet",
            "integration_test", "unit_test", "benchmark", "gas_report",
            
            # Cross-chain and Bridges
            "bridge", "cross_chain", "wrapped", "portal", "wormhole",
            "layerzero", "stargate", "hop_protocol", "across", "synapse",
            "multichain", "anyswap", "orbit", "zkbridge", "channel",
            
            # DAO and Governance
            "dao", "governance", "proposal", "vote", "quorum", "snapshot",
            "delegation", "timelock", "executor", "governor", "council",
            "committee", "multisig", "safe", "gnosis", "aragon"
        ]
        
        # Add file extensions commonly used in crypto projects
        self.file_extensions = [
            ".sol", ".js", ".ts", ".json", ".yaml", ".toml", ".md", ".env",
            ".txt", ".key", ".pem", ".abi", ".bin", ".dat", ".config", ".lock",
            ".py", ".rs", ".go", ".java", ".cpp", ".h", ".cairo", ".vy",
            ".yul", ".huff", ".move", ".clar", ".scilla", ".rkt", ".wasm"
        ]
        
        # Combine keywords with file extensions
        self.crypto_keywords.extend([
            f"*{ext}" for ext in self.file_extensions
        ])
        
        # Add content patterns to scan within files
        self.sensitive_patterns = {
            'ethereum_private_key': r'0x[a-fA-F0-9]{64}',
            'ethereum_address': r'0x[a-fA-F0-9]{40}',
            'infura_url': r'https://[a-zA-Z0-9-]+\.infura\.io/v3/[a-zA-Z0-9]+',
            'mnemonic_phrase': r'(?:\b\w+\b\s+){11,23}\b\w+\b',  # 12-24 word phrases
            'aws_key': r'AKIA[0-9A-Z]{16}',
        }
        
        # Initialize results storage
        self.results_dir = "crypto_bucket_results"
        self.download_dir = os.path.join(self.results_dir, "downloads")
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Initialize statistics
        self.stats = {
            'total_files_found': 0,
            'high_priority_files': 0,
            'sensitive_content_found': 0,
            'errors': 0
        }
        
        # Add API request tracking
        self.request_count = 0
        self.max_requests_per_minute = 30  # Adjust based on API limits
        self.request_timestamps = []
        
        # Add download management
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit for downloads
        self.download_count = 0
        self.max_downloads = 1000  # Limit total downloads
        
        # Add bucket blacklist/whitelist
        self.bucket_blacklist = set()  # Add known false-positive buckets
        self.processed_buckets = set()  # Track already processed buckets
        
        # Enhanced sensitive patterns
        self.sensitive_patterns.update({
            'jwt_token': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
            'ssh_key': r'-----BEGIN.*?PRIVATE KEY-----',
            'api_key': r'[a-zA-Z0-9]{32,45}',
            'grayhat_api': r'[0-9a-f]{32}',  # Pattern matching your API key format
            'ethereum_json': r'UTC--\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+Z--',
        })
        
        self.ui = CryptoBucketScannerUI()
        self.live_display = None
        self.verbose = verbose
        self._rate_limit = asyncio.Semaphore(5)  # Add rate limiting
        self._last_request = 0
        self._min_request_interval = 1.0  # Minimum seconds between requests
        self.skipped_words = set()
        self.results_log = []
        self._setup_results_logging()
        
        self.text_extensions = {
            '.txt', '.doc', '.docx', '.pdf', '.csv', 
            '.json', '.xml', '.yaml', '.yml', '.md',
            '.log', '.conf', '.cfg', '.ini', '.env',
            '.properties', '.sql', '.sh', '.bat',
            '.rtf', '.tex', '.rst'
        }
        self.skipped_extensions = set()  # Track skipped file types
        
    def setup_logging(self):
        """Configure logging for the scanner"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'scanner_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def _manage_rate_limit(self):
        """Enhanced rate limiting with sliding window"""
        current_time = time.time()
        self.request_timestamps = [ts for ts in self.request_timestamps 
                                 if current_time - ts < 60]
        
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - self.request_timestamps[0])
            self.logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
            await asyncio.sleep(wait_time)
        
        self.request_timestamps.append(current_time)

    async def download_file(self, url: str, filename: str) -> bool:
        """Download and save interesting files"""
        if self.download_count >= self.max_downloads:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as response:
                    size = int(response.headers.get('content-length', 0))
                    if size > self.max_file_size:
                        self.logger.warning(f"File too large: {filename} ({size/1024/1024:.2f}MB)")
                        return False
                
                async with session.get(url) as response:
                    if response.status == 200:
                        file_path = os.path.join(self.download_dir, 
                                               self._sanitize_filename(filename))
                        async with aiohttp.StreamReader(response.content) as reader:
                            with open(file_path, 'wb') as f:
                                while True:
                                    chunk = await reader.read(8192)
                                    if not chunk:
                                        break
                                    f.write(chunk)
                        
                        self.download_count += 1
                        return True
        except Exception as e:
            self.logger.error(f"Download error for {url}: {str(e)}")
        return False

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe saving"""
        return re.sub(r'[^\w\-_.]', '_', filename)

    async def analyze_file_content(self, url: str, filename: str) -> Dict:
        """Enhanced file content analysis"""
        if self.verbose:
            self.ui.console.print(f"[magenta]Analyzing content:[/magenta] {filename}")
        
        findings = {}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        for pattern_name, pattern in self.sensitive_patterns.items():
                            matches = re.findall(pattern, content)
                            if matches:
                                findings[pattern_name] = matches
        
            if findings and self.verbose:
                self.ui.console.print(f"[yellow]Found sensitive content in:[/yellow] {filename}")
                for pattern_name, matches in findings.items():
                    self.ui.console.print(f"[red]Pattern {pattern_name}:[/red] {len(matches)} matches")
        except Exception as e:
            if self.verbose:
                self.ui.console.print(f"[red]Analysis error:[/red] {str(e)}")
            self.stats['errors'] += 1
        
        return findings

    def _save_extended_metadata(self, metadata: Dict):
        """Save extended metadata for sensitive findings"""
        metadata_dir = os.path.join(self.results_dir, "metadata")
        os.makedirs(metadata_dir, exist_ok=True)
        
        filename = f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(metadata['url'])}.json"
        filepath = os.path.join(metadata_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=4)

    async def process_results(self, files: List[Dict]):
        """Process results with duplicate checking"""
        seen_urls = set()
        for file in files:
            if file['url'] in seen_urls:
                continue
                
            seen_urls.add(file['url'])
            try:
                if self.verbose:
                    self.ui.console.print(
                        f"[blue]Processing:[/blue] {file['filename']} "
                        f"[yellow](Keyword: {file.get('matched_keyword', 'unknown')})[/yellow]"
                    )
                
                # Log unique finds
                self.results_logger.info(
                    f"Processing file: {file['filename']} | "
                    f"Bucket: {file['bucket']} | "
                    f"Matched: {file.get('matched_keyword')} | "
                    f"URL: {file['url']}"
                )
                
                if hasattr(self, 'analyze_content') and self.analyze_content:
                    findings = await self.analyze_file_content(file['url'], file['filename'])
                    if findings:
                        self.results_logger.warning(
                            f"Sensitive content found in {file['filename']}: {findings}"
                        )
                
            except Exception as e:
                self.logger.error(f"Error processing file {file.get('url')}: {str(e)}")

    def _is_text_file(self, filename: str) -> bool:
        """Check if file is a text document"""
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.text_extensions

    async def search_files(self, keyword: str, start: int = 0) -> Dict:
        """Enhanced file search with better filtering and validation"""
        async with self._rate_limit:
            await self._wait_for_rate_limit()
            try:
                if self.verbose:
                    self.ui.console.print(f"[cyan]Searching for {keyword} (offset: {start})[/cyan]")
                
                base_url = "https://buckets.grayhatwarfare.com/api/v1"
                params = {
                    'keywords': keyword,
                    'start': start,
                    'limit': 100,  # Add limit parameter
                    'access_token': self.api_key
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{base_url}/files", params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Validate response structure
                            if not isinstance(data, dict) or 'files' not in data:
                                self.logger.error(f"Invalid API response format for {keyword}")
                                return {'files': []}
                            
                            # Filter for text files and validate each file
                            filtered_files = []
                            for file in data['files']:
                                # Validate file data
                                if not all(k in file for k in ['url', 'filename', 'bucket']):
                                    continue
                                
                                # Check if file matches keyword
                                if keyword.lower() not in file['filename'].lower() and \
                                   keyword.lower() not in file['url'].lower():
                                    continue
                                
                                if self._is_text_file(file['filename']):
                                    # Add metadata
                                    file['matched_keyword'] = keyword
                                    file['discovery_time'] = datetime.now().isoformat()
                                    filtered_files.append(file)
                                    
                                    if self.verbose:
                                        self.ui.console.print(
                                            f"[green]Found matching file:[/green] {file['filename']} "
                                            f"[yellow](Keyword: {keyword})[/yellow]"
                                        )
                                    
                                    # Log each unique find
                                    self.results_logger.info(
                                        f"Found file matching '{keyword}': "
                                        f"Bucket: {file['bucket']} | "
                                        f"File: {file['filename']} | "
                                        f"URL: {file['url']}"
                                    )
                                else:
                                    ext = os.path.splitext(file['filename'].lower())[1]
                                    self.skipped_extensions.add(ext)
                            
                            if self.verbose:
                                self.ui.console.print(
                                    f"[blue]Results for {keyword}:[/blue] "
                                    f"Found {len(filtered_files)} matching text documents"
                                )
                            
                            return {'files': filtered_files}
                        else:
                            error_msg = f"API returned status {response.status}"
                            self.logger.error(f"API Error for {keyword}: {error_msg}")
                            if self.verbose:
                                self.ui.console.print(f"[red]API Error:[/red] {error_msg}")
                            return {'files': []}
                            
            except Exception as e:
                self.logger.error(f"Search error for {keyword}: {str(e)}")
                if self.verbose:
                    self.ui.console.print(f"[red]Search error:[/red] {str(e)}")
                return {'files': []}

    async def scan_buckets(self, max_results: int = 1000):
        try:
            with self.ui.progress:
                for keyword in self.crypto_keywords:
                    if keyword in self.skipped_words:
                        if self.verbose:
                            self.ui.console.print(f"[yellow]Skipping keyword:[/yellow] {keyword}")
                        self.results_logger.info(f"Skipped keyword: {keyword}")
                        continue

                    if self.verbose:
                        self.ui.console.print(f"[yellow]Scanning keyword:[/yellow] {keyword}")
                    
                    start = 0
                    while start < max_results:
                        try:
                            if self.verbose:
                                self.ui.console.print(f"[cyan]Fetching results {start}-{start+100} for {keyword}[/cyan]")
                            
                            response_data = await self.search_files(keyword, start=start)
                            
                            if response_data and response_data.get('files'):
                                if self.verbose:
                                    for file in response_data['files']:
                                        self.ui.console.print(f"[green]Found:[/green] {file['url']}")
                                        self.results_logger.info(f"Found file for {keyword}: {file['url']}")
                                
                                self.stats['total_files_found'] += len(response_data['files'])
                                await self.process_results(response_data['files'])
                                
                                if len(response_data['files']) < 100:
                                    break
                            
                            start += 100
                            
                        except KeyboardInterrupt:
                            user_choice = questionary.select(
                                "What would you like to do?",
                                choices=[
                                    "Skip this keyword",
                                    "Continue scanning",
                                    "Exit scanner"
                                ]
                            ).ask()
                            
                            if user_choice == "Skip this keyword":
                                self.skipped_words.add(keyword)
                                self.results_logger.info(f"User skipped keyword: {keyword}")
                                if self.verbose:
                                    self.ui.console.print(f"[yellow]Skipping remaining results for:[/yellow] {keyword}")
                                break
                            elif user_choice == "Exit scanner":
                                raise KeyboardInterrupt
                            # Continue scanning will just continue the loop
                            
                        except Exception as e:
                            if self.verbose:
                                self.ui.console.print(f"[red]Error scanning {keyword}:[/red] {str(e)}")
                            self.logger.error(f"Error in scan loop: {str(e)}")
                            self.results_logger.error(f"Error scanning {keyword}: {str(e)}")
                            await asyncio.sleep(5)
                            continue
                        
                        await asyncio.sleep(1)
                    
                # Log summary after each keyword
                self.results_logger.info(f"Completed keyword: {keyword} - Found {self.stats['total_files_found']} files")
                
        except Exception as e:
            self.logger.error(f"Scan error: {str(e)}")
            self.results_logger.error(f"Fatal scan error: {str(e)}")
            raise
        finally:
            # Log final summary
            self.results_logger.info(f"Scan completed. Total files found: {self.stats['total_files_found']}")
            self.results_logger.info(f"Skipped keywords: {list(self.skipped_words)}")

    def display_final_report(self):
        """Enhanced final report with file type statistics"""
        self.ui.console.print("\n[bold blue]Scan Complete - Final Report[/bold blue]")
        self.ui.console.print(f"Total text documents found: {self.stats['total_files_found']}")
        
        if self.skipped_extensions:
            self.ui.console.print("\n[yellow]Skipped File Types:[/yellow]")
            for ext in sorted(self.skipped_extensions):
                self.ui.console.print(f"- {ext}")
        
        self.results_logger.info("=== Final Scan Report ===")
        self.results_logger.info(f"Total text documents found: {self.stats['total_files_found']}")
        self.results_logger.info(f"Skipped file types: {sorted(list(self.skipped_extensions))}")

    async def interactive_scan(self):
        """Interactive scanning with UI controls"""
        try:
            choices = self.ui.display_menu()
            
            max_results = {
                "Quick Scan (100 results per keyword)": 100,
                "Deep Scan (1000 results per keyword)": 1000,
                "Custom Scan": int(prompt("Enter maximum results per keyword", default="500"))
            }[choices["scan_mode"]]
            
            if "Custom Keywords" in choices["keywords"]:
                custom_keywords = prompt("Enter custom keywords (comma-separated)")
                self.crypto_keywords.extend([k.strip() for k in custom_keywords.split(",")])
            
            async with Live(self.ui.display_live_stats(self), refresh_per_second=4) as live:
                self.live_display = live
                await self.scan_buckets(max_results)
                
        except Exception as e:
            self.logger.error(f"Interactive scan error: {e}")
            raise

    def save_sensitive_findings(self, filename: str, findings: Dict):
        """Save sensitive findings to a separate file"""
        sensitive_dir = os.path.join(self.results_dir, "sensitive_findings")
        os.makedirs(sensitive_dir, exist_ok=True)
        
        output_file = os.path.join(sensitive_dir, f"sensitive_{filename}.json")
        with open(output_file, 'w') as f:
            json.dump(findings, f, indent=4)

    def generate_report(self):
        """Generate a summary report of the scan"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'scan_duration': time.time() - self.last_request_time,
        }
        
        report_file = os.path.join(self.results_dir, f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=4)
        
        self.logger.info(f"Scan report generated: {report_file}")

    def _save_scan_state(self):
        """Save scan state for potential resume"""
        state = {
            'processed_buckets': list(self.processed_buckets),
            'download_count': self.download_count,
            'stats': self.stats,
            'timestamp': datetime.now().isoformat()
        }
        
        state_file = os.path.join(self.results_dir, 'scan_state.json')
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=4)

    async def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        now = time.time()
        if now - self._last_request < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - (now - self._last_request))
        self._last_request = time.time()

    def _setup_results_logging(self):
        """Setup results logging"""
        results_logger = logging.getLogger('results_logger')
        results_logger.setLevel(logging.INFO)
        fh = logging.FileHandler('scan_results.log')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        results_logger.addHandler(fh)
        self.results_logger = results_logger

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Add verbose flag to scanner initialization
        scanner = CryptoBucketScanner("3701f2a6058ad30e9598f4e7202aef9b", verbose=True)
        scanner.ui.console.print("[bold blue]Starting scan in verbose mode...[/bold blue]")
        scanner.ui.display_banner()
        
        loop.run_until_complete(scanner.scan_buckets())
        
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        try:
            pending = asyncio.all_tasks(loop)
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        finally:
            loop.close()

if __name__ == "__main__":
    main()