from known_keys import KNOWN_KEYS, convert_significant_bits_to_ascii


def write_ascii_keys(output_file: str = "ascii_keys.txt"):
    """Write the ASCII conversion of each key's significant bits to a file."""
    with open(output_file, "w") as f:
        for index in sorted(KNOWN_KEYS.keys()):
            key_val = KNOWN_KEYS[index]
            ascii_str = convert_significant_bits_to_ascii(key_val)
            f.write(f"Index: {index:2d}  Key: {hex(key_val):<34} => ASCII: {ascii_str}\n")


if __name__ == '__main__':
    write_ascii_keys()
    print("ASCII conversion output written to ascii_keys.txt") 