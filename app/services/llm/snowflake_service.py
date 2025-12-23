
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

            # Prioritize Token (SAML/OAuth/JWT) if present
            if settings.SNOWFLAKE_TOKEN:
                print("❄️ Connecting to Snowflake using OAuth Token...")
                conn_params["authenticator"] = "oauth"
                conn_params["token"] = settings.SNOWFLAKE_TOKEN
            else:
                conn_params["password"] = settings.SNOWFLAKE_PASSWORD

            self.conn = snowflake.connector.connect(**conn_params)
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

        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Escape single quotes in prompt to prevent SQL injection/breaking
            # (Basic sanity check, parameterized query is better but Cortex func requires exact formatting)
            safe_prompt = prompt.replace("'", "''")
            
            # Construct Query: SELECT SNOWFLAKE.CORTEX.COMPLETE('model', 'prompt')
            query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{safe_prompt}')"
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return result[0]
            return "Error: No response from Cortex."
            
        except Exception as e:
            print(f"Snowflake Cortex Error: {e}")
            return f"Error executing Snowflake Cortex Query: {str(e)}"

# Singleton
snowflake_client = SnowflakeCortexClient()
