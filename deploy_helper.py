import subprocess
import urllib.parse
import sys

# Creds
USER_EMAIL = "wad-saga-constrain@duck.com"
USER_NAME = "PabloArboledai"
PASS = "n4A59sqMUr@aV@r"
REPO = "github.com/PabloArboledai/ChatPDF.git"

def try_push(username, password):
    safe_user = urllib.parse.quote(username, safe='')
    safe_pass = urllib.parse.quote(password, safe='')
    
    url = f"https://{safe_user}:{safe_pass}@{REPO}"
    print(f"Attempting push with user: {username}...")
    
    # 1. Set Remote
    subprocess.run(["git", "remote", "set-url", "origin", url], check=False)
    
    # 2. Push
    result = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ SUCCESS: Pushed to GitHub!")
        return True
    else:
        print(f"❌ FAILED: {result.stderr}")
        return False

print("--- DEPLOYMENT HELPER ---")

# Try 1: Username
if try_push(USER_NAME, PASS):
    sys.exit(0)

# Try 2: Email
if try_push(USER_EMAIL, PASS):
    sys.exit(0)

print("All attempts failed.")
sys.exit(1)
