# Debug message map for sequence generator
debug_messages = {
    'private_key_conversion': {
        'start': "=" * 80 + "\nSTARTING PRIVATE KEY TO ADDRESS CONVERSION\n" + "=" * 80,
        'input_details': "Input private key (decimal): {decimal}\nInput private key (hex): {hex}\nInput private key bit length: {bit_length}",
        'hex_validation': "=" * 60 + "\nHEX CONVERSION AND VALIDATION:\nFormatted private key hex: {hex}\nHex length: {length} characters\nHex validity: {validity}",
        'bytes_conversion': "=" * 60 + "\nBYTES CONVERSION PROCESS:\n{message}",
        'pubkey_generation': "=" * 60 + "\nPUBLIC KEY GENERATION:\n{message}",
        'pubkey_formatting': "=" * 60 + "\nPUBLIC KEY PADDING AND FORMATTING:\nFull public key length: {length} bytes\nPublic key prefix: 0x04{compression}\nPublic key structure verification: {valid}",
        'hashing': "=" * 60 + "\nHASHING PROCESS:\nPerforming SHA-256 hash...\nSHA-256 result (hex): {sha256}\nPerforming RIPEMD-160 hash...\nHash160 result (hex): {hash160}",
        'address_encoding': "=" * 60 + "\nBASE58CHECK ENCODING:\nVersion byte + Hash160 (hex): {version_hash}\nChecksum calculation input: {checksum_input}",
        'final_address': "=" * 60 + "\nFINAL ADDRESS VERIFICATION:\nFinal address: {address}\nAddress length: {length} characters\nAddress validity: {validity}"
    },
    'term_generation': {
        'fixed_method': "Term {n} generated using fixed method: 0x{term:x}",
        'candidate_variant': "Index {n}: [Candidate Variant: {name}] {details}",
        'bit_adjustment': "Index {n}: Adjusted bit length from {old} to {new}"
    },
    'validation': {
        'start': "=" * 60 + "\nVALIDATING SOLUTION FOR INDEX {index}",
        'signing_test': "Testing signature with message: '{message}'\nGenerated signature: {signature}",
        'address_match': "Generated address: {generated}\nKnown address:    {known}",
        'mismatch_warning': "ADDRESS MISMATCH DETECTED!"
    },
    'sequence_flow': {
        'cycle_reset': "Resetting sequence cycle after index 33",
        'term_added': "Successfully added term {index:03d}: 0x{term:064x}",
        'stats_header': "Sequence Statistics:\nTotal terms: {total}\nValid terms: {valid}\nNull terms: {null}\nError terms: {error}\nValid term percentage: {percent:.2f}%"
    }
} 