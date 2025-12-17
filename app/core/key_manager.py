from typing import List, Dict, Optional
import itertools
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SmartKeyManager:
    def __init__(self):
        self.providers: Dict[str, List[Dict]] = {
            "google": [],
            "groq": [],
            "openrouter": []
        }
        self.max_usage = 1000 # Soft limit before rotation
        self._load_keys()

    def _load_keys(self):
        """
        Loads keys from settings and initializes their health state.
        """
        # Google
        g_keys = [k for k in [settings.GOOGLE_API_KEY, settings.GOOGLE_API_KEY_1, settings.GOOGLE_API_KEY_2, settings.GOOGLE_API_KEY_3] if k]
        self.providers["google"] = [{"key": k, "active": True, "errors": 0} for k in set(g_keys)]
        
        # Groq
        if settings.GROQ_API_KEY:
            self.providers["groq"] = [{"key": settings.GROQ_API_KEY, "active": True, "errors": 0}]
            
        # OpenRouter
        if settings.OPENROUTER_API_KEY:
            self.providers["openrouter"] = [{"key": settings.OPENROUTER_API_KEY, "active": True, "errors": 0}]

        # SambaNova
        # SambaNova
        sn_keys = [k for k in [settings.SAMBANOVA_API_KEY, settings.SAMBANOVA_API_KEY_2] if k]
        self.providers["sambanova"] = [{"key": k, "active": True, "errors": 0} for k in set(sn_keys)]
            
        logger.info(f"SmartKeyManager Loaded: {len(self.providers['google'])} Google, {len(self.providers['groq'])} Groq, {len(self.providers['openrouter'])} OpenRouter, {len(self.providers['sambanova'])} SambaNova.")

    def get_best_key(self, provider: str = "google") -> Optional[str]:
        """
        Returns an active key for the provider.
        Supports explicit selection via '_primary' or '_secondary' suffix.
        """
        # 1. Handle Explicit Selection (e.g., "sambanova_primary")
        if "_primary" in provider or "_secondary" in provider:
            base_provider = provider.split("_")[0] # "sambanova"
            pool = self.providers.get(base_provider, [])
            if not pool: return None
            
            # Primary = Index 0, Secondary = Index 1
            index = 0 if "_primary" in provider else 1
            
            if index < len(pool):
                # Return specifically requested key if legitimate
                return pool[index]["key"]
            else:
                logger.warning(f"Requested {provider} (Index {index}) but only {len(pool)} keys available.")
                return None

        # 2. Standard Rotation Logic
        pool = self.providers.get(provider, [])
        if not pool: return None
        
        # Simple Strategy: Return first active. Real world: Use iterator for round-robin.
        # Let's rotate the list to simulate round-robin on next call
        active_keys = [k for k in pool if k["active"]]
        if not active_keys:
            logger.error(f"FATAL: All keys for {provider} are dead.")
            return None
            
        # Select first, then rotate list
        selected_meta = active_keys[0]
        
        # Rotate logic: remove from front, add to back in main pool
        pool.remove(selected_meta)
        pool.append(selected_meta)
        
        return selected_meta["key"]

    def report_failure(self, key: str, provider: str = "google"):
        """
        Marks a key as invalid/dead.
        """
        pool = self.providers.get(provider, [])
        for meta in pool:
            if meta["key"] == key:
                meta["errors"] += 1
                if meta["errors"] >= 1: # Strict 1-strike policy for 403s
                    meta["active"] = False
                    logger.warning(f"Key {key[:4]}... marked DEAD for {provider}.")
                return

    def get_failover_order(self) -> List[str]:
        """
        Returns preferred provider order.
        """
        return ["google", "groq", "sambanova", "openrouter"]

key_manager = SmartKeyManager()
