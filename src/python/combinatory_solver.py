from ecdsa import SigningKey, SECP256k1
import hashlib
import base58

def verify_term_68_address():
    # Term 68 private key (hexadecimal)
    hex_private_key = '79e3a8f7a8f9b3f3b72'.zfill(64)

    # Convert to bytes
    private_key_bytes = bytes.fromhex(hex_private_key)

    # Generate public key
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key = b'\x04' + vk.to_string()

    # SHA-256 hash
    sha_hash = hashlib.sha256(public_key).digest()

    # Manual RIPEMD-160 implementation
    class RIPEMD160:
        def __init__(self):
            self.h = [
                0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0
            ]

        def _f(self, j, x, y, z):
            if j <= 15:
                return x ^ y ^ z
            elif j <= 31:
                return (x & y) | (~x & z)
            elif j <= 47:
                return (x | ~y) ^ z
            elif j <= 63:
                return (x & z) | (y & ~z)
            else:
                return x ^ (y | ~z)

        def _K(self, j):
            if j <= 15:
                return 0x00000000
            elif j <= 31:
                return 0x5A827999
            elif j <= 47:
                return 0x6ED9EBA1
            elif j <= 63:
                return 0x8F1BBCDC
            else:
                return 0xA953FD4E

        def _Kp(self, j):
            if j <= 15:
                return 0x50A28BE6
            elif j <= 31:
                return 0x5C4DD124
            elif j <= 47:
                return 0x6D703EF3
            elif j <= 63:
                return 0x7A6D76E9
            else:
                return 0x00000000

        def _rol(self, s, x):
            return ((x << s) & 0xFFFFFFFF) | (x >> (32 - s))

        def _process_block(self, block):
            r = [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
                3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
                1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
                4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13
            ]

            rp = [
                5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
                6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
                15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
                8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
                12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11
            ]

            s = [
                11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
                7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
                11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
                11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12,
                9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6
            ]

            sp = [
                8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
                9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
                9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
                15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8,
                8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11
            ]

            X = [int.from_bytes(block[i:i+4], 'little') for i in range(0, 64, 4)]

            A, B, C, D, E = self.h
            Ap, Bp, Cp, Dp, Ep = self.h

            for j in range(80):
                T = (self._rol(s[j], A + self._f(j, B, C, D) + X[r[j]] + self._K(j)) + E) & 0xFFFFFFFF
                A, E, D, C, B = E, D, self._rol(10, C), B, T

                Tp = (self._rol(sp[j], Ap + self._f(79-j, Bp, Cp, Dp) + X[rp[j]] + self._Kp(j)) + Ep) & 0xFFFFFFFF
                Ap, Ep, Dp, Cp, Bp = Ep, Dp, self._rol(10, Cp), Bp, Tp

            T = (self.h[1] + C + Dp) & 0xFFFFFFFF
            self.h[1] = (self.h[2] + D + Ep) & 0xFFFFFFFF
            self.h[2] = (self.h[3] + E + Ap) & 0xFFFFFFFF
            self.h[3] = (self.h[4] + A + Bp) & 0xFFFFFFFF
            self.h[4] = (self.h[0] + B + Cp) & 0xFFFFFFFF
            self.h[0] = T

        def update(self, message):
            message = bytearray(message)
            orig_len_in_bits = (8 * len(message)) & 0xFFFFFFFFFFFFFFFF
            message.append(0x80)
            while len(message) % 64 != 56:
                message.append(0)
            message += orig_len_in_bits.to_bytes(8, 'little')
            for i in range(0, len(message), 64):
                self._process_block(message[i:i+64])

        def digest(self):
            return b''.join(h.to_bytes(4, 'little') for h in self.h)

    # Replace RIPEMD-160 hash with manual implementation
    ripemd160 = RIPEMD160()
    ripemd160.update(sha_hash)
    hash160 = ripemd160.digest()

    # Prepend version byte (0x00 for mainnet)
    versioned_payload = b'\x00' + hash160

    # Double SHA-256 hash
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]

    # Append checksum
    full_payload = versioned_payload + checksum

    # Base58Check encoding
    address = base58.b58encode(full_payload).decode()

    # Expected address
    expected_address = '1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ'

    # Verification
    if address == expected_address:
        print(f"Verification successful: {address} matches expected address.")
    else:
        print(f"Verification failed: {address} does not match expected address.")


def hex_to_bitcoin_address(hex_key):
    private_key_bytes = bytes.fromhex(hex_key.zfill(64))
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key = b'\x04' + vk.to_string()

    # SHA-256 hash
    sha_hash = hashlib.sha256(public_key).digest()

    # Manual RIPEMD-160 implementation
    class RIPEMD160:
        def __init__(self):
            self.h = [
                0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0
            ]

        def _f(self, j, x, y, z):
            if j <= 15:
                return x ^ y ^ z
            elif j <= 31:
                return (x & y) | (~x & z)
            elif j <= 47:
                return (x | ~y) ^ z
            elif j <= 63:
                return (x & z) | (y & ~z)
            else:
                return x ^ (y | ~z)

        def _K(self, j):
            if j <= 15:
                return 0x00000000
            elif j <= 31:
                return 0x5A827999
            elif j <= 47:
                return 0x6ED9EBA1
            elif j <= 63:
                return 0x8F1BBCDC
            else:
                return 0xA953FD4E

        def _Kp(self, j):
            if j <= 15:
                return 0x50A28BE6
            elif j <= 31:
                return 0x5C4DD124
            elif j <= 47:
                return 0x6D703EF3
            elif j <= 63:
                return 0x7A6D76E9
            else:
                return 0x00000000

        def _rol(self, s, x):
            return ((x << s) & 0xFFFFFFFF) | (x >> (32 - s))

        def _process_block(self, block):
            r = [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
                3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
                1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
                4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13
            ]

            rp = [
                5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
                6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
                15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
                8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
                12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11
            ]

            s = [
                11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
                7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
                11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
                11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12,
                9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6
            ]

            sp = [
                8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
                9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
                9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
                15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8,
                8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11
            ]

            X = [int.from_bytes(block[i:i+4], 'little') for i in range(0, 64, 4)]

            A, B, C, D, E = self.h
            Ap, Bp, Cp, Dp, Ep = self.h

            for j in range(80):
                T = (self._rol(s[j], A + self._f(j, B, C, D) + X[r[j]] + self._K(j)) + E) & 0xFFFFFFFF
                A, E, D, C, B = E, D, self._rol(10, C), B, T

                Tp = (self._rol(sp[j], Ap + self._f(79-j, Bp, Cp, Dp) + X[rp[j]] + self._Kp(j)) + Ep) & 0xFFFFFFFF
                Ap, Ep, Dp, Cp, Bp = Ep, Dp, self._rol(10, Cp), Bp, Tp

            T = (self.h[1] + C + Dp) & 0xFFFFFFFF
            self.h[1] = (self.h[2] + D + Ep) & 0xFFFFFFFF
            self.h[2] = (self.h[3] + E + Ap) & 0xFFFFFFFF
            self.h[3] = (self.h[4] + A + Bp) & 0xFFFFFFFF
            self.h[4] = (self.h[0] + B + Cp) & 0xFFFFFFFF
            self.h[0] = T

        def update(self, message):
            message = bytearray(message)
            orig_len_in_bits = (8 * len(message)) & 0xFFFFFFFFFFFFFFFF
            message.append(0x80)
            while len(message) % 64 != 56:
                message.append(0)
            message += orig_len_in_bits.to_bytes(8, 'little')
            for i in range(0, len(message), 64):
                self._process_block(message[i:i+64])

        def digest(self):
            return b''.join(h.to_bytes(4, 'little') for h in self.h)

    # Replace RIPEMD-160 hash with manual implementation
    ripemd160 = RIPEMD160()
    ripemd160.update(sha_hash)
    hash160 = ripemd160.digest()

    # Prepend version byte (0x00 for mainnet)
    versioned_payload = b'\x00' + hash160

    # Double SHA-256 hash
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]

    # Append checksum
    full_payload = versioned_payload + checksum

    # Base58Check encoding
    address = base58.b58encode(full_payload).decode()
    return address


if __name__ == "__main__":
    # Existing code...
    verify_term_68_address() 