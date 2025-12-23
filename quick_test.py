import requests
import json

response = requests.post(
    "http://127.0.0.1:8000/api/v1/query",
    json={
        "query_text": "test",
        "provider": "snowflake",
        "model": "llama3-70b",
        "pdf_id": "all",
        "rag_mode": "injection",
        "persona": "architect"
    },
    timeout=40
)

data = response.json()
metadata = data.get('metadata', {})
answer = data.get('answer', '')[:500]

print(f"Provider in metadata: {metadata.get('provider')}")
print(f"Answer contains SNOWFLAKE TEST: {'SNOWFLAKE' in answer}")
print(f"Answer preview: {answer}")
