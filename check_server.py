import urllib.request

try:
    with urllib.request.urlopen("http://127.0.0.1:5173/") as response:
        print(f"Status: {response.getcode()}")
        content = response.read().decode('utf-8')
        if "PDF Cortex" in content or "vite" in content or "src/main.tsx" in content:
             print("Content Verified: Vite is serving.")
        else:
             print("Content: Unknown")
except Exception as e:
    print(f"Error: {e}")
