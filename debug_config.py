from app.core.config import settings

print(f"Target: {settings.SUPABASE_TARGET}")
print(f"Resolved DB URL: {settings.SUPABASE_DB_URL}")
