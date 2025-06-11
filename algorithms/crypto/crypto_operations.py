from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives import hashes, serialization, padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.x509 import load_pem_x509_certificate
import base64
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import secrets
import zlib
from web3 import Web3
from ens import ENS
import asyncio
from eth_utils import is_address
from datetime import timedelta

class CryptoMode:
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    HYBRID = "hybrid"
    MULTI_KEY = "multi_key"
    ENS = "ens"  # New mode for ENS operations

class SecurityLevel:
    NORMAL = "normal"
    HIGH = "high"
    PARANOID = "paranoid"

class ENSOperation:
    RESOLVE = "resolve"
    REGISTER = "register"
    SET_ADDRESS = "set_address"
    SET_RESOLVER = "set_resolver"
    GET_OWNER = "get_owner"
    SET_TTL = "set_ttl"
    SET_SUBNODE = "set_subnode"
    CREATE_SUBDOMAIN = "create_subdomain"
    LIST_SUBDOMAINS = "list_subdomains"
    DELETE_SUBDOMAIN = "delete_subdomain"
    BATCH_CREATE = "batch_create"       # New operation
    BATCH_DELETE = "batch_delete"       # New operation
    TRANSFER_SUBDOMAIN = "transfer"     # New operation
    FILTER_SUBDOMAINS = "filter"        # New operation
    EXPORT_SUBDOMAINS = "export"        # New operation
    
class CryptoOperations:
    def __init__(self):
        self.initialized = False
        self.keys_dir = "crypto_keys"
        self.data_dir = "crypto_data"
        self.temp_dir = "crypto_temp"
        self.key_pairs = {}
        self.symmetric_keys = {}
        self.current_data = None
        self.operation_log = []
        self.security_level = SecurityLevel.NORMAL
        self.current_mode = CryptoMode.HYBRID
        self.salt = os.urandom(16)
        self.initialization_vector = os.urandom(16)
        
        # ENS specific initialization
        self.w3 = None
        self.ens = None
        self.eth_account = None
        
    def initialize_ens(self, provider_url: str, private_key: Optional[str] = None) -> Dict[str, Any]:
        """Initialize ENS functionality with Web3 provider"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(provider_url))
            if not self.w3.is_connected():
                return {
                    "status": "error",
                    "message": "Failed to connect to Ethereum network"
                }
            
            self.ens = ENS.from_web3(self.w3)
            
            if private_key:
                self.eth_account = self.w3.eth.account.from_key(private_key)
                self.w3.eth.default_account = self.eth_account.address
            
            self.log_operation("ens_init", {
                "status": "success",
                "network": self.w3.net.version
            })
            
            return {
                "status": "success",
                "message": "ENS system initialized",
                "network": self.w3.net.version,
                "connected": True
            }
            
        except Exception as e:
            self.log_operation("ens_init", {
                "status": "error",
                "error": str(e)
            })
            return {"status": "error", "message": str(e)}

    async def resolve_ens_name(self, ens_name: str) -> Dict[str, Any]:
        """Resolve ENS name to Ethereum address"""
        if not self.ens:
            return {"status": "error", "message": "ENS not initialized"}
        
        try:
            address = await self.ens.address(ens_name)
            if address:
                result = {
                    "status": "success",
                    "ens_name": ens_name,
                    "address": address,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "status": "error",
                    "message": f"Could not resolve {ens_name}",
                    "timestamp": datetime.now().isoformat()
                }
                
            self.log_operation("ens_resolve", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def register_ens_name(self, name: str, duration_years: int = 1) -> Dict[str, Any]:
        """Register a new ENS name"""
        if not self.ens or not self.eth_account:
            return {"status": "error", "message": "ENS not initialized or no account provided"}
            
        try:
            # Check if name is available
            owner = await self.ens.owner(name)
            if owner != "0x0000000000000000000000000000000000000000":
                return {
                    "status": "error",
                    "message": f"Name {name} is already registered"
                }
                
            # Calculate registration cost
            duration = timedelta(days=365 * duration_years)
            controller = self.ens.registrar.contract
            
            # Get registration cost
            cost = await controller.functions.rentPrice(
                name,
                duration.total_seconds()
            ).call()
            
            # Prepare transaction
            transaction = await controller.functions.register(
                name,
                self.eth_account.address,
                duration.total_seconds()
            ).build_transaction({
                'from': self.eth_account.address,
                'value': cost,
                'nonce': self.w3.eth.get_transaction_count(self.eth_account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.eth_account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            result = {
                "status": "success",
                "ens_name": name,
                "owner": self.eth_account.address,
                "duration_years": duration_years,
                "cost": self.w3.from_wei(cost, 'ether'),
                "transaction_hash": receipt['transactionHash'].hex(),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_register", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def set_ens_address(self, name: str, address: str) -> Dict[str, Any]:
        """Set the address for an ENS name"""
        if not self.ens or not self.eth_account:
            return {"status": "error", "message": "ENS not initialized or no account provided"}
            
        try:
            if not is_address(address):
                return {"status": "error", "message": "Invalid Ethereum address"}
                
            # Check ownership
            owner = await self.ens.owner(name)
            if owner.lower() != self.eth_account.address.lower():
                return {
                    "status": "error",
                    "message": f"You don't own {name}"
                }
                
            # Set address
            transaction = await self.ens.resolver.functions.setAddr(
                self.ens.namehash(name),
                address
            ).build_transaction({
                'from': self.eth_account.address,
                'nonce': self.w3.eth.get_transaction_count(self.eth_account.address)
            })
            
            signed_txn = self.eth_account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            result = {
                "status": "success",
                "ens_name": name,
                "new_address": address,
                "transaction_hash": receipt['transactionHash'].hex(),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_set_address", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_ens_owner(self, name: str) -> Dict[str, Any]:
        """Get the owner of an ENS name"""
        if not self.ens:
            return {"status": "error", "message": "ENS not initialized"}
            
        try:
            owner = await self.ens.owner(name)
            result = {
                "status": "success",
                "ens_name": name,
                "owner": owner,
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_get_owner", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def set_ens_resolver(self, name: str, resolver_address: str) -> Dict[str, Any]:
        """Set a custom resolver for an ENS name"""
        if not self.ens or not self.eth_account:
            return {"status": "error", "message": "ENS not initialized or no account provided"}
            
        try:
            if not is_address(resolver_address):
                return {"status": "error", "message": "Invalid resolver address"}
                
            # Check ownership
            owner = await self.ens.owner(name)
            if owner.lower() != self.eth_account.address.lower():
                return {
                    "status": "error",
                    "message": f"You don't own {name}"
                }
                
            # Set resolver
            transaction = await self.ens.functions.setResolver(
                self.ens.namehash(name),
                resolver_address
            ).build_transaction({
                'from': self.eth_account.address,
                'nonce': self.w3.eth.get_transaction_count(self.eth_account.address)
            })
            
            signed_txn = self.eth_account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            result = {
                "status": "success",
                "ens_name": name,
                "resolver": resolver_address,
                "transaction_hash": receipt['transactionHash'].hex(),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_set_resolver", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def set_security_level(self, level: str) -> Dict[str, Any]:
        """Set the security level for operations"""
        if level not in [SecurityLevel.NORMAL, SecurityLevel.HIGH, SecurityLevel.PARANOID]:
            return {"status": "error", "message": "Invalid security level"}
        
        self.security_level = level
        self.log_operation("security_level_change", {
            "status": "success",
            "new_level": level
        })
        return {"status": "success", "message": f"Security level set to {level}"}

    def generate_key_pair(self, key_type: str = "rsa") -> Tuple[Any, Any]:
        """Generate a new key pair based on type"""
        if key_type == "rsa":
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096 if self.security_level == SecurityLevel.PARANOID else 2048
            )
            public_key = private_key.public_key()
        elif key_type == "ec":
            private_key = ec.generate_private_key(ec.SECP384R1())
            public_key = private_key.public_key()
        else:
            raise ValueError(f"Unsupported key type: {key_type}")
        
        return private_key, public_key

    def initialize_system(self) -> Dict[str, Any]:
        """Initialize the crypto system with enhanced security"""
        # Create necessary directories
        for directory in [self.keys_dir, self.data_dir, self.temp_dir]:
            os.makedirs(directory, exist_ok=True)

        # Generate multiple key pairs for different purposes
        key_types = {
            "main": "rsa",
            "backup": "rsa",
            "signing": "ec"
        }

        for purpose, key_type in key_types.items():
            private_key, public_key = self.generate_key_pair(key_type)
            self.key_pairs[purpose] = {
                "private": private_key,
                "public": public_key,
                "type": key_type
            }

        # Generate multiple symmetric keys for layered encryption
        for i in range(3 if self.security_level == SecurityLevel.PARANOID else 1):
            key_name = f"layer_{i}" if i > 0 else "main"
            symmetric_key = Fernet.generate_key()
            self.symmetric_keys[key_name] = Fernet(symmetric_key)

        # Save public keys with proper permissions
        for purpose, keys in self.key_pairs.items():
            public_pem = keys["public"].public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            key_path = f"{self.keys_dir}/{purpose}_public_key.pem"
            with open(key_path, "wb") as f:
                f.write(public_pem)
            os.chmod(key_path, 0o600)  # Secure file permissions

        self.initialized = True
        self.log_operation("initialize", {
            "status": "success",
            "security_level": self.security_level,
            "keys_generated": list(key_types.keys())
        })

        return {
            "status": "success",
            "message": "Crypto system initialized with enhanced security",
            "security_level": self.security_level,
            "keys_generated": list(key_types.keys())
        }

    def secure_data(self, data: str, compression: bool = True) -> Dict[str, Any]:
        """Encrypt data with enhanced security features"""
        if not self.initialized:
            return {"status": "error", "message": "System not initialized"}

        try:
            # Compress data if enabled
            data_bytes = data.encode()
            if compression:
                data_bytes = zlib.compress(data_bytes)

            # Add checksum
            checksum = hashlib.sha256(data_bytes).digest()
            data_with_checksum = checksum + data_bytes

            # Multi-layer encryption based on security level
            encrypted_data = data_with_checksum
            used_keys = []

            if self.security_level == SecurityLevel.PARANOID:
                # Use all available symmetric keys in sequence
                for key_name, fernet in self.symmetric_keys.items():
                    encrypted_data = fernet.encrypt(encrypted_data)
                    used_keys.append(key_name)
            else:
                # Use main symmetric key
                encrypted_data = self.symmetric_keys["main"].encrypt(encrypted_data)
                used_keys.append("main")

            # Encrypt the final layer with asymmetric encryption
            encrypted_key = self.key_pairs["main"]["public"].encrypt(
                self.symmetric_keys["main"]._signing_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Create a digital signature
            if "signing" in self.key_pairs:
                signature = self.key_pairs["signing"]["private"].sign(
                    encrypted_data,
                    ec.ECDSA(hashes.SHA256())
                )
            else:
                signature = b""

            # Combine all components
            final_data = {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "encrypted_key": base64.b64encode(encrypted_key).decode(),
                "signature": base64.b64encode(signature).decode(),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "security_level": self.security_level,
                    "compression": compression,
                    "used_keys": used_keys
                }
            }

            # Save encrypted data
            encrypted_data_path = f"{self.data_dir}/encrypted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(encrypted_data_path, "w") as f:
                json.dump(final_data, f, indent=2)

            self.current_data = final_data

            self.log_operation("secure", {
                "status": "success",
                "file": encrypted_data_path,
                "security_level": self.security_level,
                "compression": compression
            })

            return {
                "status": "success",
                "message": "Data encrypted successfully with enhanced security",
                "file": encrypted_data_path,
                "metadata": final_data["metadata"]
            }

        except Exception as e:
            self.log_operation("secure", {
                "status": "error",
                "error": str(e)
            })
            return {"status": "error", "message": str(e)}

    def verify_data(self, data_path: Optional[str] = None) -> Dict[str, Any]:
        """Verify data integrity with enhanced checks"""
        if not self.initialized:
            return {"status": "error", "message": "System not initialized"}

        try:
            # Load data
            if data_path:
                with open(data_path, "r") as f:
                    data = json.load(f)
            elif self.current_data:
                data = self.current_data
            else:
                return {"status": "error", "message": "No data to verify"}

            # Decode components
            encrypted_data = base64.b64decode(data["encrypted_data"])
            encrypted_key = base64.b64decode(data["encrypted_key"])
            signature = base64.b64decode(data["signature"])

            # Verify signature if available
            if signature and "signing" in self.key_pairs:
                try:
                    self.key_pairs["signing"]["public"].verify(
                        signature,
                        encrypted_data,
                        ec.ECDSA(hashes.SHA256())
                    )
                    signature_valid = True
                except Exception:
                    signature_valid = False
            else:
                signature_valid = None

            # Verify key integrity
            try:
                symmetric_key = self.key_pairs["main"]["private"].decrypt(
                    encrypted_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                key_valid = symmetric_key == self.symmetric_keys["main"]._signing_key
            except Exception:
                key_valid = False

            verification_result = {
                "status": "success",
                "valid": key_valid and (signature_valid is not False),
                "details": {
                    "key_valid": key_valid,
                    "signature_valid": signature_valid,
                    "metadata": data.get("metadata", {})
                }
            }

            self.log_operation("verify", {
                "status": "success",
                "result": verification_result
            })

            return verification_result

        except Exception as e:
            self.log_operation("verify", {
                "status": "error",
                "error": str(e)
            })
            return {"status": "error", "message": str(e)}

    def process_data(self, data_path: Optional[str] = None) -> Dict[str, Any]:
        """Process (decrypt) data with enhanced features"""
        if not self.initialized:
            return {"status": "error", "message": "System not initialized"}

        try:
            # Load and verify data first
            verify_result = self.verify_data(data_path)
            if verify_result["status"] == "error" or not verify_result.get("valid", False):
                return {"status": "error", "message": "Data verification failed"}

            # Load data
            if data_path:
                with open(data_path, "r") as f:
                    data = json.load(f)
            elif self.current_data:
                data = self.current_data
            else:
                return {"status": "error", "message": "No data to process"}

            # Decode components
            encrypted_data = base64.b64decode(data["encrypted_data"])
            metadata = data.get("metadata", {})

            # Multi-layer decryption based on security level
            decrypted_data = encrypted_data
            if metadata.get("security_level") == SecurityLevel.PARANOID:
                # Decrypt all layers in reverse order
                for key_name in reversed(metadata.get("used_keys", [])):
                    decrypted_data = self.symmetric_keys[key_name].decrypt(decrypted_data)
            else:
                # Decrypt with main key
                decrypted_data = self.symmetric_keys["main"].decrypt(decrypted_data)

            # Verify checksum
            checksum = decrypted_data[:32]
            actual_data = decrypted_data[32:]
            if hashlib.sha256(actual_data).digest() != checksum:
                return {"status": "error", "message": "Checksum verification failed"}

            # Decompress if needed
            if metadata.get("compression", False):
                actual_data = zlib.decompress(actual_data)

            # Save decrypted data
            decrypted_path = f"{self.data_dir}/decrypted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(decrypted_path, "wb") as f:
                f.write(actual_data)

            self.log_operation("process", {
                "status": "success",
                "file": decrypted_path,
                "metadata": metadata
            })

            return {
                "status": "success",
                "message": "Data processed successfully",
                "decrypted_data": actual_data.decode(),
                "file": decrypted_path,
                "metadata": metadata
            }

        except Exception as e:
            self.log_operation("process", {
                "status": "error",
                "error": str(e)
            })
            return {"status": "error", "message": str(e)}

    def get_operation_log(self) -> list:
        """Get the detailed operation log"""
        return self.operation_log

    def cleanup(self):
        """Secure cleanup of sensitive data"""
        try:
            # Overwrite sensitive data in memory
            for key in self.symmetric_keys.values():
                key._signing_key = os.urandom(32)  # Overwrite with random data
            
            self.symmetric_keys.clear()
            self.key_pairs.clear()
            
            # Securely delete temporary files
            if os.path.exists(self.temp_dir):
                for file in os.listdir(self.temp_dir):
                    path = os.path.join(self.temp_dir, file)
                    with open(path, "wb") as f:
                        f.write(os.urandom(os.path.getsize(path)))
                    os.remove(path)
                
            self.initialized = False
            return {"status": "success", "message": "Cleanup completed successfully"}
        
        except Exception as e:
            return {"status": "error", "message": str(e)} 

    async def create_subdomain(self, domain: str, subdomain: str, owner_address: Optional[str] = None) -> Dict[str, Any]:
        """Create a new subdomain for an ENS name"""
        if not self.ens or not self.eth_account:
            return {"status": "error", "message": "ENS not initialized or no account provided"}
            
        try:
            # Check domain ownership
            domain_owner = await self.ens.owner(domain)
            if domain_owner.lower() != self.eth_account.address.lower():
                return {
                    "status": "error",
                    "message": f"You don't own {domain}"
                }
            
            # Generate label hash for subdomain
            label_hash = self.w3.keccak(text=subdomain)
            node_hash = self.ens.namehash(domain)
            
            # Set owner address (default to current account if not specified)
            owner = owner_address if owner_address else self.eth_account.address
            if not is_address(owner):
                return {"status": "error", "message": "Invalid owner address"}
            
            # Create subdomain transaction
            transaction = await self.ens.functions.setSubnodeOwner(
                node_hash,
                label_hash,
                owner
            ).build_transaction({
                'from': self.eth_account.address,
                'nonce': self.w3.eth.get_transaction_count(self.eth_account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.eth_account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Set up default resolver if needed
            full_name = f"{subdomain}.{domain}"
            resolver = await self.ens.resolver(full_name)
            if not resolver:
                await self.set_ens_resolver(
                    full_name, 
                    "0x4976fb03C32e5B8cfe2b6cCB31c09Ba78EBaBa41"  # ENS Public Resolver
                )
            
            result = {
                "status": "success",
                "domain": domain,
                "subdomain": subdomain,
                "full_name": full_name,
                "owner": owner,
                "transaction_hash": receipt['transactionHash'].hex(),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_create_subdomain", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def list_subdomains(self, domain: str) -> Dict[str, Any]:
        """List all subdomains for an ENS name"""
        if not self.ens:
            return {"status": "error", "message": "ENS not initialized"}
            
        try:
            # Get domain node
            node = self.ens.namehash(domain)
            
            # Query events for subdomain creation
            registry = self.ens.ens.address
            event_filter = self.w3.eth.filter({
                'fromBlock': 0,
                'toBlock': 'latest',
                'address': registry,
                'topics': [
                    self.w3.keccak(text='NewOwner(bytes32,bytes32,address)').hex(),
                    node
                ]
            })
            
            # Process events to get subdomains
            subdomains = []
            events = await event_filter.get_all_entries()
            
            for event in events:
                label_hash = event['topics'][2]
                try:
                    # Try to reverse resolve the label
                    subdomain = await self.ens.reverse(label_hash)
                    if subdomain:
                        owner = await self.ens.owner(f"{subdomain}.{domain}")
                        resolver = await self.ens.resolver(f"{subdomain}.{domain}")
                        address = await self.ens.address(f"{subdomain}.{domain}")
                        
                        subdomains.append({
                            "name": subdomain,
                            "full_name": f"{subdomain}.{domain}",
                            "owner": owner,
                            "resolver": resolver,
                            "address": address
                        })
                except Exception:
                    # If reverse resolution fails, include just the hash
                    subdomains.append({
                        "label_hash": label_hash.hex(),
                        "owner": event['args']['owner']
                    })
            
            result = {
                "status": "success",
                "domain": domain,
                "subdomains": subdomains,
                "count": len(subdomains),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_list_subdomains", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def delete_subdomain(self, domain: str, subdomain: str) -> Dict[str, Any]:
        """Delete a subdomain by setting its owner to zero address"""
        if not self.ens or not self.eth_account:
            return {"status": "error", "message": "ENS not initialized or no account provided"}
            
        try:
            # Check domain ownership
            domain_owner = await self.ens.owner(domain)
            if domain_owner.lower() != self.eth_account.address.lower():
                return {
                    "status": "error",
                    "message": f"You don't own {domain}"
                }
            
            # Generate label hash for subdomain
            label_hash = self.w3.keccak(text=subdomain)
            node_hash = self.ens.namehash(domain)
            
            # Set owner to zero address to "delete" the subdomain
            zero_address = "0x0000000000000000000000000000000000000000"
            
            transaction = await self.ens.functions.setSubnodeOwner(
                node_hash,
                label_hash,
                zero_address
            ).build_transaction({
                'from': self.eth_account.address,
                'nonce': self.w3.eth.get_transaction_count(self.eth_account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.eth_account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            result = {
                "status": "success",
                "domain": domain,
                "subdomain": subdomain,
                "full_name": f"{subdomain}.{domain}",
                "transaction_hash": receipt['transactionHash'].hex(),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_delete_subdomain", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def batch_create_subdomains(self, domain: str, subdomains: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create multiple subdomains in a single transaction batch"""
        if not self.ens or not self.eth_account:
            return {"status": "error", "message": "ENS not initialized or no account provided"}
            
        try:
            # Check domain ownership
            domain_owner = await self.ens.owner(domain)
            if domain_owner.lower() != self.eth_account.address.lower():
                return {
                    "status": "error",
                    "message": f"You don't own {domain}"
                }
            
            results = []
            nonce = self.w3.eth.get_transaction_count(self.eth_account.address)
            
            for subdomain_info in subdomains:
                subdomain = subdomain_info['name']
                owner = subdomain_info.get('owner', self.eth_account.address)
                
                # Generate label hash for subdomain
                label_hash = self.w3.keccak(text=subdomain)
                node_hash = self.ens.namehash(domain)
                
                # Create subdomain transaction
                transaction = await self.ens.functions.setSubnodeOwner(
                    node_hash,
                    label_hash,
                    owner
                ).build_transaction({
                    'from': self.eth_account.address,
                    'nonce': nonce
                })
                
                # Sign and send transaction
                signed_txn = self.eth_account.sign_transaction(transaction)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                
                results.append({
                    "subdomain": subdomain,
                    "owner": owner,
                    "transaction_hash": receipt['transactionHash'].hex()
                })
                
                nonce += 1
            
            result = {
                "status": "success",
                "domain": domain,
                "created_subdomains": results,
                "count": len(results),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_batch_create_subdomains", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def filter_subdomains(self, domain: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and search subdomains with advanced criteria"""
        try:
            # Get all subdomains first
            all_subdomains = await self.list_subdomains(domain)
            if all_subdomains["status"] != "success":
                return all_subdomains
            
            filtered_subdomains = []
            for subdomain in all_subdomains["subdomains"]:
                matches_filters = True
                
                # Apply filters
                for key, value in filters.items():
                    if key == "name_contains":
                        if value.lower() not in subdomain.get("name", "").lower():
                            matches_filters = False
                            break
                    elif key == "owner":
                        if subdomain.get("owner", "").lower() != value.lower():
                            matches_filters = False
                            break
                    elif key == "has_address":
                        if bool(subdomain.get("address")) != value:
                            matches_filters = False
                            break
                    elif key == "created_after":
                        if "creation_date" in subdomain and subdomain["creation_date"] < value:
                            matches_filters = False
                            break
                    elif key == "resolver_type":
                        resolver = subdomain.get("resolver", "")
                        if value == "public" and resolver != "0x4976fb03C32e5B8cfe2b6cCB31c09Ba78EBaBa41":
                            matches_filters = False
                            break
                
                if matches_filters:
                    filtered_subdomains.append(subdomain)
            
            result = {
                "status": "success",
                "domain": domain,
                "filtered_subdomains": filtered_subdomains,
                "total_count": len(all_subdomains["subdomains"]),
                "filtered_count": len(filtered_subdomains),
                "filters_applied": filters,
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_filter_subdomains", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def transfer_subdomain(self, domain: str, subdomain: str, new_owner: str) -> Dict[str, Any]:
        """Transfer a subdomain to a new owner"""
        if not self.ens or not self.eth_account:
            return {"status": "error", "message": "ENS not initialized or no account provided"}
            
        try:
            # Verify ownership
            full_name = f"{subdomain}.{domain}"
            current_owner = await self.ens.owner(full_name)
            if current_owner.lower() != self.eth_account.address.lower():
                return {
                    "status": "error",
                    "message": f"You don't own {full_name}"
                }
            
            if not is_address(new_owner):
                return {"status": "error", "message": "Invalid new owner address"}
            
            # Transfer ownership
            node_hash = self.ens.namehash(full_name)
            transaction = await self.ens.functions.setOwner(
                node_hash,
                new_owner
            ).build_transaction({
                'from': self.eth_account.address,
                'nonce': self.w3.eth.get_transaction_count(self.eth_account.address)
            })
            
            signed_txn = self.eth_account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            result = {
                "status": "success",
                "domain": domain,
                "subdomain": subdomain,
                "full_name": full_name,
                "previous_owner": current_owner,
                "new_owner": new_owner,
                "transaction_hash": receipt['transactionHash'].hex(),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_transfer_subdomain", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def export_subdomains(self, domain: str, format: str = "json") -> Dict[str, Any]:
        """Export subdomain information in various formats"""
        try:
            # Get all subdomains
            subdomains = await self.list_subdomains(domain)
            if subdomains["status"] != "success":
                return subdomains
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"subdomains_{domain}_{timestamp}"
            
            if format.lower() == "json":
                filename += ".json"
                with open(filename, 'w') as f:
                    json.dump(subdomains["subdomains"], f, indent=2)
            
            elif format.lower() == "csv":
                filename += ".csv"
                import csv
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    # Write header
                    if subdomains["subdomains"]:
                        writer.writerow(subdomains["subdomains"][0].keys())
                        # Write data
                        for subdomain in subdomains["subdomains"]:
                            writer.writerow(subdomain.values())
            
            elif format.lower() == "yaml":
                filename += ".yaml"
                import yaml
                with open(filename, 'w') as f:
                    yaml.dump(subdomains["subdomains"], f)
            
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported export format: {format}"
                }
            
            result = {
                "status": "success",
                "domain": domain,
                "format": format,
                "filename": filename,
                "subdomain_count": len(subdomains["subdomains"]),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_operation("ens_export_subdomains", result)
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)} 