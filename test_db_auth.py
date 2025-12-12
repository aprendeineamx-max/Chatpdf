import psycopg2
import sys

# Credentials
HOST_POOLER = "aws-0-us-west-1.pooler.supabase.com"
HOST_DIRECT = "db.jrjsxjmjfsjltgutssib.supabase.co"
PORT = 5432 # Testing Session Mode
USER = "postgres"
REF = "jrjsxjmjfsjltgutssib"
PASS = "SuperSegura2024!"
DB = "postgres"

def try_connect(host, user, password, desc):
    print(f"Testing {desc}...")
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            port=PORT,
            dbname=DB,
            connect_timeout=5
        )
        print(f"✅ SUCCESS: Connected via {desc}!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ FAILED {desc}: {e}")
        return False

print("--- Starting Auth Diagnostic ---")

# 1. Pooler Host, Standard User
if try_connect(HOST_POOLER, USER, PASS, "Pooler Host + Standard User"):
    sys.exit(0)

# 2. Pooler Host, Project User
if try_connect(HOST_POOLER, f"{USER}.{REF}", PASS, "Pooler Host + Tenant User"):
    sys.exit(0)

# 3. Direct Host, Standard User
if try_connect(HOST_DIRECT, USER, PASS, "Direct Host + Standard User"):
    sys.exit(0)

# 4. Pooler Host, Port 6543
print("Testing Port 6543 (Transaction Mode)...")
try:
    conn = psycopg2.connect(
        host=HOST_POOLER,
        user=f"{USER}.{REF}", # Pooler on 6543 usually requires tenant ref
        password=PASS,
        port=6543,
        dbname=DB,
        connect_timeout=5
    )
    print("✅ SUCCESS: Connected via Pooler 6543!")
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f"❌ FAILED Pooler 6543: {e}")

