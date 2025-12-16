
import os
from dotenv import load_dotenv

load_dotenv()

print(f"GOOGLE_KEY_0: {os.getenv('GOOGLE_API_KEY')[:10]}...")
print(f"GOOGLE_KEY_1: {os.getenv('GOOGLE_API_KEY_1')[:10]}...")
print(f"GOOGLE_KEY_2: {os.getenv('GOOGLE_API_KEY_2')}")
