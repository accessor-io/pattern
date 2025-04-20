import hashlib
from typing import List, Dict, Optional
from secp256k1 import PublicKey, ECDSA, constants
from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.script import Script
from bip44 import Wallet

class BitcoinTransactionAnalyzer:
    def __init__(self):
        setup('mainnet')
        self.ecdsa = ECDSA()

    # --------------------------------
    # 1. Transaction Parsing Utilities
    # --------------------------------
    def parse_raw_transaction(self, raw_tx_hex: str) -> Dict:
        """Parse raw transaction hex into structured data."""
        try:
            tx = Transaction.from_raw(raw_tx_hex)
            return {
                "txid": tx.get_txid(),
                "version": tx.version,
                "inputs": [self._parse_input(inp) for inp in tx.inputs],
                "outputs": [self._parse_output(out) for out in tx.outputs],
                "locktime": tx.locktime
            }
        except Exception as e:
            raise ValueError(f"Invalid transaction: {str(e)}")

    def _parse_input(self, tx_input: TxInput) -> Dict:
        """Parse transaction input details."""
        return {
            "txid": tx_input.txid,
            "vout": tx_input.vout,
            "script_sig": tx_input.script_sig.to_hex(),
            "sequence": tx_input.sequence,
            "witness": tx_input.witness.serialize() if tx_input.witness else None
        }

    def _parse_output(self, tx_output: TxOutput) -> Dict:
        """Parse transaction output details."""
        return {
            "address": tx_output.script_pubkey.to_address().to_string(),
            "value": tx_output.value,
            "script_pubkey": tx_output.script_pubkey.to_hex()
        }

    # --------------------------------
    # 2. Cryptographic Vulnerability Checks
    # --------------------------------
    def detect_nonce_reuse(self, signatures: List[str]) -> Dict:
        """
        Detect ECDSA nonce reuse across multiple signatures.
        Returns: { "reused_nonces": List, "vulnerable_keys": List }
        """
        r_values = {}
        for i, sig in enumerate(signatures):
            der_sig = bytes.fromhex(sig[:-2])  # Exclude sighash byte
            r = der_sig[4:36].hex()  # Extract r-value from DER encoding
            if r in r_values:
                r_values[r].append(i)
            else:
                r_values[r] = [i]

        reused = {r: indices for r, indices in r_values.items() if len(indices) > 1}
        return {
            "reused_nonces": reused,
            "vulnerable_keys": self._find_vulnerable_keys(reused, signatures)
        }

    def _find_vulnerable_keys(self, reused_nonces: Dict, signatures: List[str]) -> List:
        """Calculate vulnerable private keys from reused nonces."""
        vulnerable = []
        for r, indices in reused_nonces.items():
            if len(indices) >= 2:
                sig1 = self._decode_der_signature(signatures[indices[0]])
                sig2 = self._decode_der_signature(signatures[indices[1]])
                
                # Private key recovery formula: k = (z1 - z2)/(s1 - s2) mod n
                z1 = int.from_bytes(hashlib.sha256(sig1['message']).digest(), 'big')
                z2 = int.from_bytes(hashlib.sha256(sig2['message']).digest(), 'big')
                
                s_diff = (sig1['s'] - sig2['s']) % constants.ORDER
                z_diff = (z1 - z2) % constants.ORDER
                priv_key = (z_diff * pow(s_diff, -1, constants.ORDER)) % constants.ORDER
                
                vulnerable.append(priv_key.to_bytes(32, 'big').hex())
        return vulnerable

    def _decode_der_signature(self, sig_hex: str) -> Dict:
        """Decode DER-encoded ECDSA signature."""
        der = bytes.fromhex(sig_hex[:-2])  # Exclude sighash byte
        r_len = der[3]
        r = int.from_bytes(der[4:4+r_len], 'big')
        s = int.from_bytes(der[6+r_len:6+r_len+der[5+r_len]], 'big')
        return {'r': r, 's': s, 'message': der}

    # --------------------------------
    # 3. Public Key Relationship Analysis
    # --------------------------------
    def analyze_public_keys(self, pubkeys: List[str]) -> Dict:
        """
        Detect mathematical relationships between public keys.
        Returns: { "sequential": List, "scalar_mult": List }
        """
        results = {"sequential": [], "scalar_mult": []}
        pubkey_points = [PublicKey(bytes.fromhex(pk), raw=True) for pk in pubkeys]

        # Check for sequential public keys (P2 = P1 + G)
        for i in range(len(pubkey_points)):
            for j in range(i+1, len(pubkey_points)):
                pk_candidate = pubkey_points[i].tweak_add(self.ecdsa.get_generator())
                if pk_candidate.serialize() == pubkey_points[j].serialize():
                    results["sequential"].append((i, j))

        # Check for scalar multiplication relationships
        for i in range(len(pubkey_points)):
            for j in range(i+1, len(pubkey_points)):
                if self._is_scalar_multiple(pubkey_points[i], pubkey_points[j]):
                    results["scalar_mult"].append((i, j))
        
        return results

    def _is_scalar_multiple(self, pk1: PublicKey, pk2: PublicKey) -> bool:
        """Check if pk2 = k * pk1 using Pollard's Lambda algorithm."""
        # Implementation requires advanced mathematical operations
        # Placeholder for actual implementation using Kangaroo algorithm
        return False

    # --------------------------------
    # 4. BIP44 Deterministic Wallet Analysis
    # --------------------------------
    def bip44_derivation_audit(self, mnemonic: str, address_template: str, 
                              search_depth: int = 1000) -> Optional[Dict]:
        """
        Search for target address in BIP44 derivation paths.
        Returns: { "found": bool, "path": str, "private_key": str }
        """
        wallet = Wallet(mnemonic)
        for account in range(5):  # Check first 5 accounts
            for change in [0, 1]:  # External/Internal chains
                for index in range(search_depth):
                    path = f"m/44'/0'/{account}'/{change}/{index}"
                    try:
                        address = wallet.get_address(path)
                        if address == address_template:
                            return {
                                "found": True,
                                "path": path,
                                "private_key": wallet.get_private_key(path).to_wif()
                            }
                    except:
                        continue
        return {"found": False}

    # --------------------------------
    # 5. Transaction Script Analysis
    # --------------------------------
    def analyze_sighash_flags(self, raw_tx_hex: str) -> Dict:
        """Detect SIGHASH flags and modification possibilities."""
        tx = Transaction.from_raw(raw_tx_hex)
        results = {"sighash_types": [], "modifiable_inputs": [], "modifiable_outputs": []}

        for inp in tx.inputs:
            sighash_type = inp.script_sig.sighash
            results["sighash_types"].append(sighash_type)

            if sighash_type == 0x01:  # SIGHASH_ALL
                results["modifiable_inputs"].append(False)
                results["modifiable_outputs"].append(False)
            elif sighash_type == 0x02:  # SIGHASH_NONE
                results["modifiable_outputs"].append(True)
            elif sighash_type == 0x03:  # SIGHASH_SINGLE
                results["modifiable_outputs"].append(True)

        return results

# ========================
# Example Usage
# ========================
if __name__ == "__main__":
    analyzer = BitcoinTransactionAnalyzer()

    # Example Transaction Analysis
    raw_tx_hex = "02000000000101...00000000"  # Replace with actual raw transaction
    parsed_tx = analyzer.parse_raw_transaction(raw_tx_hex)
    print("Parsed Transaction:", parsed_tx)

    # Cryptographic Checks
    signatures = [
        "304402203b5d657b5b859335b96ef4c54b3789da6dced891971ea080b2195d23709176a7022041a911e79d5e207b56b583fd83cf3b95dcc7d43e82512c4b7d99ddd1195c9d9501",
        "3044022019114a215b5218d3cdaa83be24be10d3a94972993474e8cc53d719e403ed0e77022012210b74c894ff5bca75ba3149425c57825f4fe3d1923369f9e53bb6cf7ad4d701"
    ]
    nonce_report = analyzer.detect_nonce_reuse(signatures)
    print("\nNonce Reuse Report:", nonce_report)

    # Public Key Analysis
    pubkeys = [
        "0322d014e4d848e9fcc308ae281e2b360d761116a8d961c43c867c4de268925728",
        "0236d3a2ed07adb4309076aa01c95b48001b0780fcf006916f1ecc5ac954216560"
    ]
    key_relations = analyzer.analyze_public_keys(pubkeys)
    print("\nPublic Key Relationships:", key_relations)

    # BIP44 Audit Example
    bip44_result = analyzer.bip44_derivation_audit(
        "your mnemonic seed phrase here",
        "bc1qpgf7usrugzxllvydvrnngpsw3rlewelk3qfjg4"
    )
    print("\nBIP44 Audit Result:", bip44_result)