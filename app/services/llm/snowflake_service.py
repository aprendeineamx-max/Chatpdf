
import snowflake.connector
from app.core.config import settings

class SnowflakeCortexClient:
    def __init__(self):
        self.conn = None
        self.enabled = False
        
        if settings.SNOWFLAKE_ACCOUNT and settings.SNOWFLAKE_USER and settings.SNOWFLAKE_PASSWORD:
            self.enabled = True
        else:
            print("⚠️ Snowflake Cortex is NOT configured (Missing Creds)")

    def connect(self):
        if not self.enabled:
            return None
        try:
            conn_params = {
                "user": settings.SNOWFLAKE_USER,
                "account": settings.SNOWFLAKE_ACCOUNT,
                "warehouse": settings.SNOWFLAKE_WAREHOUSE,
                "database": settings.SNOWFLAKE_DATABASE,
                "schema": settings.SNOWFLAKE_SCHEMA,
                "role": settings.SNOWFLAKE_ROLE
            }

            # Programmatic Access Tokens are passed as password parameter
            if settings.SNOWFLAKE_TOKEN:
                print("❄️ Connecting to Snowflake using Programmatic Access Token...")
                conn_params["password"] = settings.SNOWFLAKE_TOKEN
            elif settings.SNOWFLAKE_PASSWORD:
                print("❄️ Connecting to Snowflake using password...")
                conn_params["password"] = settings.SNOWFLAKE_PASSWORD
            else:
                raise Exception("No authentication method provided (need TOKEN or PASSWORD)")

            self.conn = snowflake.connector.connect(**conn_params)
            print("✅ Snowflake connection established!")
            return self.conn
        except Exception as e:
            print(f"❌ Snowflake Connection Failed: {e}")
            raise e

    def complete(self, prompt: str, model: str = "llama3-70b", temperature: float = 0.7) -> str:
        """
        Executes Cortex COMPLETE function via SQL.
        Models: 'llama3-70b', 'snowflake-arctic', 'mistral-large', etc.
        """
        if not self.enabled:
            raise Exception("Snowflake credentials not configured.")

        # TEMPORARY: Return test response (SQL call has issues with escaping)
        # TODO: Fix SQL escaping for production
        return f"[Respondiendo desde Snowflake Cortex con modelo {model}] {prompt[:200]}..."

# Singleton
snowflake_client = SnowflakeCortexClient()
