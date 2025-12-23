
from pydantic_settings import BaseSettings
from typing import Optional, List, Any
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PDF Cortex"
    
    # LLM Keys
    GROQ_API_KEY: Optional[str] = None
    # Main Key
    GOOGLE_API_KEY: Optional[str] = None 
    # Hydra Keys
    GOOGLE_API_KEY_1: Optional[str] = None
    GOOGLE_API_KEY_2: Optional[str] = None
    GOOGLE_API_KEY_3: Optional[str] = None
    
    OPENROUTER_API_KEY: Optional[str] = None
    SAMBANOVA_API_KEY: Optional[str] = None
    SAMBANOVA_API_KEY_2: Optional[str] = None
    
    # Shared Providers
    BROWSER_USE_API_KEY: Optional[str] = None
    
    # Snowflake Cortex
    SNOWFLAKE_ACCOUNT: Optional[str] = None
    SNOWFLAKE_USER: Optional[str] = None
    SNOWFLAKE_PASSWORD: Optional[str] = None
    SNOWFLAKE_ROLE: Optional[str] = "ACCOUNTADMIN"
    SNOWFLAKE_WAREHOUSE: Optional[str] = "COMPUTE_WH"
    SNOWFLAKE_DATABASE: Optional[str] = None
    SNOWFLAKE_SCHEMA: Optional[str] = "PUBLIC"

    # Database Configuration Strategy
    SUPABASE_TARGET: str = "VPS" # Options: "VPS", "CLOUD"

    # VPS (Self-Hosted) Config
    VPS_SUPABASE_URL: Optional[str] = None
    VPS_SUPABASE_KEY: Optional[str] = None
    VPS_SUPABASE_DB_URL: Optional[str] = None

    # Cloud Config
    CLOUD_SUPABASE_URL: Optional[str] = None
    CLOUD_SUPABASE_KEY: Optional[str] = None
    CLOUD_SUPABASE_DB_URL: Optional[str] = None

    # Resolved Active Config (App uses these)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_DB_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # [HYBRID CORE LOGIC]
    CORE_MODE: str = "CLOUD" # Default, overridden by .env

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    def model_post_init(self, __context: Any) -> None:
        """
        Dynamically selecting the active configuration based on SUPABASE_TARGET.
        This runs after the model is initialized from env vars.
        """
        super().model_post_init(__context)
        
        # Load CORE_MODE from Env explicitly if Pydantic didn't catch it
        # (It should catch it from env_file if it matches case, but we force checking os just in case)
        if not self.CORE_MODE: 
             self.CORE_MODE = os.getenv("CORE_MODE", "CLOUD").upper()
        else:
             self.CORE_MODE = self.CORE_MODE.upper()
        
        if self.CORE_MODE == "LOCAL":
            print("⚡ HYBRID CORE: Switched to LOCAL (Pulse Mode)")
            self.SUPABASE_URL = "http://localhost:3000"
            self.SUPABASE_KEY = os.getenv("LOCAL_SUPABASE_KEY", "my-super-secret-jwt-token-with-at-least-32-chars-long")
            self.SUPABASE_DB_URL = "postgresql://postgres:postgres@localhost:54322/postgres"
            return
        
        target = self.SUPABASE_TARGET.upper()
        
        if target == "VPS":
            self.SUPABASE_URL = self.VPS_SUPABASE_URL
            self.SUPABASE_KEY = self.VPS_SUPABASE_KEY
            self.SUPABASE_DB_URL = self.VPS_SUPABASE_DB_URL
        elif target == "CLOUD":
            self.SUPABASE_URL = self.CLOUD_SUPABASE_URL
            self.SUPABASE_KEY = self.CLOUD_SUPABASE_KEY
            self.SUPABASE_DB_URL = self.CLOUD_SUPABASE_DB_URL
            
        # Fallback/Validation logging could go here if using a real logger within config logic

settings = Settings()
