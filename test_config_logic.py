from app.core.config import Settings
import os

def test_config_switching():
    print("Testing VPS Mode...")
    # Mock Env for VPS
    os.environ["SUPABASE_TARGET"] = "VPS"
    os.environ["VPS_SUPABASE_URL"] = "http://vps-url"
    os.environ["CLOUD_SUPABASE_URL"] = "http://cloud-url"
    
    s = Settings()
    # Note: Pydantic Settings reads from cached env or file, re-instantiation usually reads os.environ if Config allows it. 
    # But Settings() might have already loaded .env file which takes precedence or not depending on config.
    # To test logic pure, we can instantiate passing values if arguments allowed, but BaseSettings is mostly env based.
    # Let's check logic:
    
    if s.SUPABASE_URL == "http://vps-url":
        print("✅ VPS Mode Correct")
    else:
        print(f"❌ VPS Mode Failed. Got: {s.SUPABASE_URL}")

    print("Testing CLOUD Mode...")
    os.environ["SUPABASE_TARGET"] = "CLOUD"
    s2 = Settings()
    
    if s2.SUPABASE_URL == "http://cloud-url":
         print("✅ CLOUD Mode Correct")
    else:
         print(f"❌ CLOUD Mode Failed. Got: {s2.SUPABASE_URL}")

if __name__ == "__main__":
    test_config_switching()
