from llama_index.llms.gemini import Gemini
import os

key = "AIzaSyDI8WM1RNCHesHEyC23aSCicWe2_sSRqlk"

print("--- Testing LlamaIndex Gemini Wrapper ---")

# Test 1: Full path
print("\nTest 1: models/gemini-2.0-flash")
try:
    llm = Gemini(model="models/gemini-2.0-flash", api_key=key)
    resp = llm.complete("Hello")
    print(f"SUCCESS: {resp}")
except Exception as e:
    print(f"FAILED: {e}")

# Test 2: Short path
print("\nTest 2: gemini-2.0-flash")
try:
    llm = Gemini(model="gemini-2.0-flash", api_key=key)
    resp = llm.complete("Hello")
    print(f"SUCCESS: {resp}")
except Exception as e:
    print(f"FAILED: {e}")

# Test 3: Fallback 1.5
print("\nTest 3: models/gemini-1.5-flash")
try:
    llm = Gemini(model="models/gemini-1.5-flash", api_key=key)
    resp = llm.complete("Hello")
    print(f"SUCCESS: {resp}")
except Exception as e:
    print(f"FAILED: {e}")
