def main():
    analyzer = BitcoinTransactionAnalyzer()
    txid_hex = "08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15"
    analyzer.load_progress()
    analyzer.run_puzzle_for_all_indices(txid_hex, 
                                      analyzer.progress['last_index'] + 1, 
                                      160)

if __name__ == "__main__":
    main() 