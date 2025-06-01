import csv
import time
from pathlib import Path
import sys

class AddressMatcherWithCleaning:
    def __init__(self):
        self.addresses_file = Path("/home/dot/New Folder/electrum wallet checker/wallet_tools/wallet_data/addresses/addresses_per_line_20241101_071641.txt")
        self.blockchair_tsv = Path("/home/dot/Downloads/blockchair_bitcoin_outputs_20241031.tsv")
        self.clean_recipients_file = Path("clean_recipients.txt")
        self.matches_file = f"matches_found_{time.strftime('%Y%m%d_%H%M%S')}.txt"

    def clean_tsv(self):
        """Extract and clean recipient addresses from TSV"""
        print("Step 1: Cleaning TSV file...")
        recipients = set()
        rows_processed = 0
        
        try:
            with open(self.blockchair_tsv, 'r') as tsv_file:
                reader = csv.DictReader(tsv_file, delimiter='\t')
                
                for row in reader:
                    rows_processed += 1
                    recipient = row['recipient'].strip()
                    if recipient:  # Only add non-empty addresses
                        recipients.add(recipient)
                    
                    if rows_processed % 1050000 == 0:
                        print(f"Cleaned {rows_processed:,} rows...")

            # Save clean recipients
            with open(self.clean_recipients_file, 'w') as out_file:
                for recipient in sorted(recipients):
                    out_file.write(f"{recipient}\n")

            print(f"TSV cleaning complete:")
            print(f"Processed {rows_processed:,} rows")
            print(f"Found {len(recipients):,} unique addresses")
            return recipients

        except Exception as e:
            print(f"Error cleaning TSV: {e}")
            return set()

    def load_electrum_addresses(self):
        """Load addresses from Electrum file"""
        print("\nStep 2: Loading Electrum addresses...")
        addresses = set()
        try:
            with open(self.addresses_file, 'r') as f:
                for line in f:
                    addr = line.strip()
                    if addr:
                        addresses.add(addr)
            print(f"Loaded {len(addresses)} Electrum addresses")
            return addresses
        except Exception as e:
            print(f"Error loading Electrum addresses: {e}")
            return set()

    def find_matches(self, clean_recipients, electrum_addresses):
        """Find matches between clean recipients and Electrum addresses"""
        print("\nStep 3: Finding matches...")
        matches = clean_recipients.intersection(electrum_addresses)
        
        # Save matches
        with open(self.matches_file, 'w') as f:
            f.write("MATCHING ADDRESSES\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total matches found: {len(matches)}\n\n")
            for addr in sorted(matches):
                f.write(f"{addr}\n")
                print(f"Match found: {addr}")

        return matches

    def run(self):
        print("Starting address matching process...")
        start_time = time.time()
        
        # Step 1: Clean TSV
        clean_recipients = self.clean_tsv()
        if not clean_recipients:
            print("Error: Failed to clean TSV file")
            return

        # Step 2: Load Electrum addresses
        electrum_addresses = self.load_electrum_addresses()
        if not electrum_addresses:
            print("Error: Failed to load Electrum addresses")
            return

        # Step 3: Find matches
        matches = self.find_matches(clean_recipients, electrum_addresses)

        # Print summary
        print("\nProcess Complete!")
        print(f"Clean recipients: {len(clean_recipients):,}")
        print(f"Electrum addresses: {len(electrum_addresses):,}")
        print(f"Matches found: {len(matches):,}")
        if matches:
            print("\nMatching addresses:")
            for addr in sorted(matches):
                print(addr)
        
        print(f"\nTotal processing time: {time.time() - start_time:.2f} seconds")
        print(f"Results saved to: {self.matches_file}")

if __name__ == "__main__":
    matcher = AddressMatcherWithCleaning()
    matcher.run()
