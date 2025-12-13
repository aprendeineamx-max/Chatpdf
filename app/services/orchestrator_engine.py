
import os
import sys
import time
import asyncio
from supabase import create_client
from dotenv import load_dotenv

# Add root to path
sys.path.append(os.getcwd())

from app.services.hive.hive_mind import HiveMind
from app.core.config import settings

load_dotenv(".env")
load_dotenv("genesis-web/.env")

# Init Supabase
url = settings.SUPABASE_URL or os.getenv("VITE_SUPABASE_URL")
key = settings.SUPABASE_KEY or os.getenv("VITE_SUPABASE_KEY")

if not url or not key:
    print("❌ Critical: Supabase URLs missing.")
    exit(1)

supabase = create_client(url, key)
hive_mind = HiveMind()

async def process_message(msg):
    print(f"🧠 Processing: {msg['content']}")
    
    # 1. Ask the Neural Council (Architect Persona)
    # logic: User input -> Architect System Prompt -> Response + Potential Tasks
    
    context = f"The user is asking: '{msg['content']}'. You are the Supreme Architect of the Genesis System. Guide them or generate tasks."
    response_text = await hive_mind._generate_response("ARCHITECT", context)
    
    # 2. Reply to User
    reply_data = {
        "session_id": msg.get('session_id'),
        "role": "assistant",
        "content": response_text
    }
    
    try:
        supabase.table("chat_messages").insert(reply_data).execute()
        print("✅ Replied to User.")
    except Exception as e:
        print(f"❌ Failed to reply: {e}")

    # 3. Task Extraction (Simple Heuristic for now)
    # If the response contains "[TASK]", we parse it. 
    # For now, let's keep it conversational.

def watch_chat():
    print("👁️ Orchestrator Engine Online. Waiting for orders...")
    
    # Simple Polling for new USER messages without a reply?
    # Or rely on a "processing" flag? 
    # For simplicity: Subscribe to Postgres Changes via Realtime (using Python client is tricky for realtime)
    # fallback: Poll 'chat_messages' where role='user' and created_at > last_check
    
    last_check = time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    while True:
        try:
            # Get latest user message created AFTER last check
            response = supabase.table("chat_messages")\
                .select("*")\
                .eq("role", "user")\
                .gt("created_at", last_check)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
                
            if response.data:
                msg = response.data[0]
                last_check = msg['created_at'] # Update cursor
                
                # Check if this ID has already been replied to? 
                # (Simple dedupe logic via timestamp cursor should work for sequential chat)
                
                asyncio.run(process_message(msg))
                
        except Exception as e:
            print(f"Loop Error: {e}")
            
        time.sleep(2)

if __name__ == "__main__":
    watch_chat()
