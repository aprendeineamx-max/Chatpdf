import redis
import sys

try:
    r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=2)
    r.ping()
    print("✅ Redis is ONLINE!")
except Exception as e:
    print(f"❌ Redis is OFFLINE: {e}")
    # sys.exit(1) # Don't exit error code, just print
