from typing import Dict, List, Tuple, Optional
import os
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CryptoMapping:
    """Represents a mapping between a Bitcoin address and its command."""
    address: str
    command: str

    def validate(self) -> bool:
        """Validates the Bitcoin address format."""
        # Basic validation - should be enhanced with proper Bitcoin address validation
        return (
            len(self.address) >= 26 and
            len(self.address) <= 35 and
            self.address.startswith('1')
        )

class CryptoMappingsManager:
    """Manages crypto mappings with secure loading and validation."""
    
    def __init__(self):
        self._mappings: List[CryptoMapping] = []
        self._load_mappings()

    def _load_mappings(self) -> None:
        """Loads mappings from environment or falls back to default."""
        try:
            mappings_json = os.getenv('CRYPTO_MAPPINGS_CONFIG')
            if mappings_json:
                self._load_from_json(mappings_json)
            else:
                self._load_default_mappings()
        except Exception as e:
            logger.error(f"Failed to load mappings: {e}")
            raise

    def _load_from_json(self, json_str: str) -> None:
        """Loads mappings from JSON string."""
        try:
            data = json.loads(json_str)
            self._mappings = [
                CryptoMapping(m['address'], m['command'])
                for m in data
            ]
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in CRYPTO_MAPPINGS_CONFIG: {e}")
            raise
        except KeyError as e:
            logger.error(f"Missing required field in mapping: {e}")
            raise

    def _load_default_mappings(self) -> None:
        """Loads default mappings (for development only)."""
        logger.warning("Using default mappings - NOT RECOMMENDED FOR PRODUCTION")
        
        # Convert the existing mappings to CryptoMapping objects
        self._mappings = [
            CryptoMapping(address, command)
            for address, command in _DEFAULT_MAPPINGS
        ]

    def get_mapping(self, index: int) -> Optional[CryptoMapping]:
        """Safely retrieves a mapping by index."""
        try:
            return self._mappings[index]
        except IndexError:
            logger.error(f"Mapping index {index} out of range")
            return None

    def get_command(self, index: int) -> Optional[str]:
        """Safely retrieves a command by index."""
        mapping = self.get_mapping(index)
        return mapping.command if mapping else None

    def validate_all(self) -> bool:
        """Validates all mappings."""
        return all(m.validate() for m in self._mappings)

# Store the original mappings as a default (development only)
_DEFAULT_MAPPINGS: List[Tuple[str, str]] = [
    ("1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH", "BEGIN_GATEWAY_ZERO_TRANSFER_SECURE_ACCESS_METHOD"),
    ("1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb", "CRYPTO_UNIFORM_NET_ENABLE_BINARY_PROTOCOL"),
    ("19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA", "ZERO_ENCRYPT_WAIT_HASH_PROTOCOL_DATA"),
    # ... rest of the mappings ...
]

# Create a singleton instance
_manager = CryptoMappingsManager()

# Public interface
def get_mapping(index: int) -> Optional[CryptoMapping]:
    """Public interface to get a mapping."""
    return _manager.get_mapping(index)

def get_command(index: int) -> Optional[str]:
    """Public interface to get a command."""
    return _manager.get_command(index)

def validate_all() -> bool:
    """Public interface to validate all mappings."""
    return _manager.validate_all()

# For backward compatibility
CRYPTO_MAPPINGS = _DEFAULT_MAPPINGS 