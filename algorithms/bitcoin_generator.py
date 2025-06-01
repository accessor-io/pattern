import itertools
import hashlib
import base58
import ecdsa
from tqdm import tqdm
import multiprocessing
import time

class BitcoinGenerator:
    def __init__(self):
        # Core word groups
        self.fixed_words = [
            "pumpkin", "light", "bench", "phone", 
            "sign", "beach", "leaf", "device", 
            "laptop", "key"
        ]
        self.art_words = ["art", "artwork"]
        self.end_words = ["water", "smart"]
        
        # Calculate total combinations
        self.total = len(list(itertools.permutations(self.fixed_words + ["x", "y"]))) * 2 * 2
        
    def generate_address(self, words):
        try:
            seed = ' '.join(words).encode()
            private_key = ecdsa.SigningKey.from_string(
                hashlib.sha256(seed).digest(), 
                curve=ecdsa.SECP256k1
            )
            public_key = private_key.get_verifying_key().to_string()
            key_hash = hashlib.sha256(public_key).digest()[:20]
            addr = base58.b58encode(b'\x00' + key_hash +   
                   hashlib.sha256(hashlib.sha256(b'\x00' + key_hash).digest()).digest()[:4])
            return addr.decode()
        except:
            return None

    def process_batch(self, base_perm):
        results = []
        for art in self.art_words:
            for end in self.end_words:
                # Create word list with placeholders
                word_list = list(base_perm)
                
                # Find placeholder positions
                art_pos = word_list.index('x')
                end_pos = word_list.index('y')
                
                # Replace placeholders
                word_list[art_pos] = art
                word_list[end_pos] = end
                
                addr = self.generate_address(word_list)
                if addr:
                    results.append((word_list, addr))
        return results

    def generate(self):
        print(f"Generating all combinations...")
        print(f"Total possible combinations: {self.total:,}")
        
        # Create base permutations with placeholders
        base_words = self.fixed_words + ['x', 'y']  # x for art/artwork, y for water/smart
        
        with multiprocessing.Pool() as pool:
            with open('all_combinations.txt', 'w') as f:
                with tqdm(total=self.total) as pbar:
                    # Process permutations in batches
                    for base_perm in itertools.permutations(base_words):
                        results = pool.apply(self.process_batch, (base_perm,))
                        
                        # Write results
                        for words, addr in results:
                            f.write(f"{' '.join(words)}|{addr}\n")
                            pbar.update(1)
                        
                        # Optional: flush every N combinations
                        if pbar.n % 1000 == 0:
                            f.flush()

def main():
    print("Bitcoin Address Generator - All Combinations")
    print("=" * 50)
    print("\nGenerating combinations with:")
    print("- art/artwork variations")
    print("- water/smart variations")
    print("- all possible positions")
    
    generator = BitcoinGenerator()
    
    try:
        generator.generate()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    finally:
        duration = time.time() - start_time
        print(f"\nTotal execution time: {duration:.2f} seconds")
        print("Results saved to all_combinations.txt")

if __name__ == "__main__":
    main()