import google.generativeai as genai
import os
import time

key = "AIzaSyDI8WM1RNCHesHEyC23aSCicWe2_sSRqlk"
genai.configure(api_key=key)

candidates = [
    "models/gemini-2.0-flash-exp",
    "models/gemini-flash-latest",
    "models/gemini-pro-latest",
    "models/gemini-2.0-flash-lite-preview-02-05",
    "models/gemini-2.0-flash" 
]

print("--- Quota Hunter ---")
for m in candidates:
    print(f"\nTargeting: {m}")
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("Ping")
        print(f"✅ PASSED! Response: {response.text}")
        print(f"RECOMMENDATION: Use {m}")
        break
    except Exception as e:
        print(f"❌ FAILED: {e}")
        time.sleep(1) # Be nice
