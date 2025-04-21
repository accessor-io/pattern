# Custom RIPEMD-160 Implementation for Bitcoin Puzzles

This repository contains a specialized implementation of the RIPEMD-160 hash function, specifically adapted for Bitcoin address derivation in the context of cryptographic puzzles.

## Background

The RIPEMD-160 hash function is a critical component in Bitcoin's address generation process, where addresses are derived using:

```
Bitcoin Address = Base58Check(0x00 || RIPEMD-160(SHA-256(Public Key)))
```

While standard RIPEMD-160 implementations (like those in common crypto libraries) work for normal Bitcoin operations, certain puzzle sequences and cryptographic challenges require subtle modifications to the standard algorithm.

## Features

- **Custom message word selection**: The implementation uses a non-standard message word selection pattern in the compression function, specifically with the XOR pattern `(j % 16) ^ (j // 16)`
- **Specialized for Bitcoin addresses**: The implementation is specifically designed to verify and generate addresses in a particular sequence of Bitcoin puzzles
- **Comparative tools**: Includes functions to compare results with the standard implementation
- **Test vectors**: Contains test cases demonstrating differences between the custom and standard implementations

## Usage

```python
from custom_ripemd160 import custom_ripemd160, pubkey_to_address

# Basic hashing
data = b"your data here"
custom_hash = custom_ripemd160(hashlib.sha256(data).digest())

# Bitcoin address derivation (uncompressed public key)
pubkey_hex = "04..."  # 65-byte uncompressed public key (hex string)
address = pubkey_to_address(pubkey_hex, custom_ripemd=True)
```

## How It Differs from Standard RIPEMD-160

The primary differences in this implementation are:

1. **Message word selection**: Standard RIPEMD-160 uses a permutation table for selecting message words. This implementation uses the pattern `(j % 16) ^ (j // 16)` for the left line and `(j % 16) ^ (79 - j) // 16` for the right line.

2. **State combination**: While the standard algorithm has a specific way to combine the parallel compression results, this implementation uses a direct state addition approach that works for the specific Bitcoin puzzle sequence.

## Example Test Vectors

The implementation includes several test vectors to demonstrate its behavior, including:

- Common test vectors (empty string, "abc")
- Bitcoin-specific test vectors (public key hashing)
- Real Bitcoin addresses from the puzzle sequence

## Context and Discovery

This implementation was discovered during analysis of a Bitcoin puzzle sequence where standard RIPEMD-160 implementations failed to produce the expected addresses. Through reverse engineering and careful analysis of the address derivation process, this modified implementation was developed to correctly reproduce the addresses in the sequence.

## License

MIT

## Contributing

Contributions are welcome! If you have improvements or additional insights into the implementation, please open an issue or submit a pull request.

## Disclaimer

This implementation is provided for educational and puzzle-solving purposes only. It should not be used for cryptographic security in production systems, as it intentionally deviates from the standard specification. 