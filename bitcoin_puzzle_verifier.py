def generate_private_key(hex_string):
    """Generate a private key from a hex string."""
    # Convert hex string to bytes
    private_key_bytes = bytes.fromhex(hex_string)
    # Convert to integer
    private_key = int.from_bytes(private_key_bytes, byteorder='big')
    return private_key 