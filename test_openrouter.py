import os
import requests
import json

OPENROUTER_API_KEY = "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"

def test_openrouter():
    print("Testing OpenRouter...")
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000", 
        },
        data=json.dumps({
            "model": "google/gemini-2.0-flash-exp:free", # Free model to test
            "messages": [
                {"role": "user", "content": "What is 1+1?"}
            ]
        })
    )
    
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")

if __name__ == "__main__":
    test_openrouter()
