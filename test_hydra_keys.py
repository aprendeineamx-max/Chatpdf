from llama_index.llms.gemini import Gemini
import os

# Test Keys
keys = [
    "AIzaSyDI8WM1RNCHesHEyC23aSCicWe2_sSRqlk",
    "AIzaSyARktDdbbrRjbDQDX5WxvVD4d1lbBpNMY0",
    "AIzaSyBA_J1-LPM6rsVbUozjH5nZre4spou7qNw"
]

print("--- Testing Hydra Keys ---")

for i, key in enumerate(keys):

    print(f"\nTesting Key {i+1}: {key[:5]}...")
    models_to_test = ["gemini-1.5-flash", "models/gemini-1.5-flash-001", "gemini-pro"]
    
    for m in models_to_test:
        print(f"  > Trying model: {m}")
        try:
            model = Gemini(model=m, api_key=key)
            resp = model.complete("Hello")
            print(f"  ✅ SUCCESS with {m}! Response: {resp.text[:20]}...")
            break 
        except Exception as e:
            print(f"  ❌ Failed {m}: {e}")
