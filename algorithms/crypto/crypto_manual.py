import os
import time
from typing import Dict, List, Tuple
from crypto_data import CRYPTO_MAPPINGS

class CryptoManualBrowser:
    def __init__(self):
        self.entries = CRYPTO_MAPPINGS
        self.current_page = 0
        self.entries_per_page = 10
        self.total_pages = (len(self.entries) + self.entries_per_page - 1) // self.entries_per_page

    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self):
        print("""
/*
 * ┌─[SYSTEM]───────────────────────────────────────────────────────┐
 * │ [!] Cryptographic Address Manual Browser v0x01                 │
 * └──────────────────────────────────────────────────────────────┘
 *
 * [BOOT] Loading cryptographic mappings...
 * ████████████████████████████████████████████████████  100%
 *
 * ┌─[ACTIVE SIGNATURES]──────────────┬─[STATUS]─────────────────┐
 * │ > 0xDEAD : MONITORING           │ [ACTIVE]                 │
 * │ > 0xBEEF : ANALYZING           │ [ACTIVE]                 │
 * │ > 0xCAFE : SCANNING            │ [ACTIVE]                 │
 * │ > 0xBABE : PROCESSING          │ [ACTIVE]                 │
 * └────────────────────────────────┴─────────────────────────┘
*/""")

    def print_content(self):
        start_idx = self.current_page * self.entries_per_page
        end_idx = min(start_idx + self.entries_per_page, len(self.entries))
        
        print(f"""
┌─[PAGE {self.current_page + 1}/{self.total_pages}]───────────────────────────────────┐""")
        
        for i in range(start_idx, end_idx):
            addr, cmd = self.entries[i]
            print(f"│ [{i+1:03d}] {addr}")
            print(f"│      → {cmd}")
            print("│")
        
        print("└─────────────────────────────────────────────────────────────┘")

    def print_help(self):
        print("""
┌─[COMMANDS]─────────────────────────────────────────────────┐
│ [n/SPACE] Next page      [p] Previous page                │
│ [g] Go to page          [s] Search                       │
│ [q] Quit                [h] Show this help               │
└─────────────────────────────────────────────────────────────┘
""")

    def search_entries(self, query: str) -> List[Tuple[int, str, str]]:
        results = []
        query = query.lower()
        for i, (addr, cmd) in enumerate(self.entries):
            if query in addr.lower() or query in cmd.lower():
                results.append((i + 1, addr, cmd))
        return results

    def print_search_results(self, results: List[Tuple[int, str, str]]):
        print(f"""
┌─[SEARCH RESULTS]───────────────────────────────────────────┐""")
        for num, addr, cmd in results:
            print(f"│ [{num:03d}] {addr}")
            print(f"│      → {cmd}")
            print("│")
        print("└─────────────────────────────────────────────────────────────┘")

    def run(self):
        while True:
            self.clear_screen()
            self.print_header()
            self.print_content()
            self.print_help()
            
            cmd = input("\n[INPUT] > ").lower().strip()
            
            if cmd in ['q', 'quit', 'exit']:
                print("\n[SYS] Closing manual browser...")
                break
            elif cmd in ['n', ' ', 'next']:
                self.current_page = (self.current_page + 1) % self.total_pages
            elif cmd in ['p', 'prev', 'previous']:
                self.current_page = (self.current_page - 1) % self.total_pages
            elif cmd.startswith('g'):
                try:
                    page = int(cmd[1:]) - 1
                    if 0 <= page < self.total_pages:
                        self.current_page = page
                except ValueError:
                    print("\n[ERROR] Invalid page number")
                    input("Press Enter to continue...")
            elif cmd.startswith('s'):
                search_query = input("\nEnter search term: ").strip()
                if search_query:
                    results = self.search_entries(search_query)
                    self.clear_screen()
                    self.print_header()
                    self.print_search_results(results)
                    input("\nPress Enter to continue...")
            elif cmd in ['h', 'help', '?']:
                continue
            else:
                print("\n[ERROR] Invalid command. Press 'h' for help.")
                input("Press Enter to continue...")

if __name__ == "__main__":
    browser = CryptoManualBrowser()
    browser.run() 