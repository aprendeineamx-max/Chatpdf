from typing import List, Optional
import itertools
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class KeyManager:
    def __init__(self):
        self._keys: List[str] = self._load_keys()
        self._iterator = itertools.cycle(self._keys) if self._keys else None
        logger.info(f"Hydra KeyManager initialized with {len(self._keys)} keys.")

    def _load_keys(self) -> List[str]:
        """
        Aggregates all available Google Keys from settings.
        """
        keys = []
        # Main Key
        if settings.GOOGLE_API_KEY:
            keys.append(settings.GOOGLE_API_KEY)
        
        # Hydra Keys
        if settings.GOOGLE_API_KEY_1:
            keys.append(settings.GOOGLE_API_KEY_1)
        if settings.GOOGLE_API_KEY_2:
            keys.append(settings.GOOGLE_API_KEY_2)
        if settings.GOOGLE_API_KEY_3:
            keys.append(settings.GOOGLE_API_KEY_3)
            
        # Deduplicate
        return list(set(keys))

    def get_next_key(self) -> str:
        """
        Returns the next key in the Round-Robin cycle.
        """
        if not self._iterator:
            raise ValueError("No Google API Keys configured!")
        
        key = next(self._iterator)
        # Obfuscate for logging
        safe_key = key[:4] + "..." + key[-4:]
        logger.debug(f"Rotating to key: {safe_key}")
        return key

    def report_error(self, key: str):
        """
        In the future, this will handle cooldown logic.
        For now, just logs it.
        """
        logger.warning(f"Key {key[:4]}... reported an error. Failover logic triggered.")

# Global Instance
key_manager = KeyManager()
