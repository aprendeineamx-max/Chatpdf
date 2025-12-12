import subprocess
import urllib.parse
import sys
import os

# Credentials from User
USER_EMAIL = "wad-saga-constrain@duck.com"
PASS = "n4A59sqMUr@aV@r"
REPO_URL = "github.com/PabloArboledai/ChatPDF.git"

def run_git(args, check=False):
    print(f"Running: git {' '.join(args)}")
    res = subprocess.run(["git"] + args, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"⚠️ Warning/Error: {res.stderr.strip()}")
    else:
        print(f"✅ Success: {res.stdout.strip()}")
    return res

print("--- STARTING DEPLOY FIX ---")

# 1. Ensure files are staged
run_git(["add", "."])

# 2. Ensure we have a commit
run_git(["commit", "-m", "feat: Complete v1.5 System (Hydra + Persistence + Plugins)"])

# 3. Configure Auth URL
# Encode password but keep the rest standard
safe_pass = urllib.parse.quote(PASS, safe='')
# Construct URL: https://Email:Pass@github.com/User/Repo
# Note: GitHub sometimes uses the email as username for HTTPS auth, or the actual username.
# User provided email as credential, let's try that first.
remote_url = f"https://{USER_EMAIL}:{safe_pass}@{REPO_URL}"

print(f"Configuring remote origin...")
run_git(["remote", "remove", "origin"])
run_git(["remote", "add", "origin", remote_url])

# 4. Push
print("Pushing to main...")
res = run_git(["push", "-u", "origin", "main"])

if res.returncode == 0:
    print("🚀 DEPLOYMENT SUCCESSFUL!")
else:
    print("❌ Deployment Failed. Retrying with Username strategy...")
    # Retry with 'PabloArboledai' as username
    USERNAME = "PabloArboledai"
    remote_url_2 = f"https://{USERNAME}:{safe_pass}@{REPO_URL}"
    run_git(["remote", "set-url", "origin", remote_url_2])
    res2 = run_git(["push", "-u", "origin", "main"])
    if res2.returncode == 0:
        print("🚀 DEPLOYMENT SUCCESSFUL (Username Strategy)!")
    else:
        print("❌ FATAL: Could not push.")
