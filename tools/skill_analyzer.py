
import os
import sys
import re
from supabase import create_client
from dotenv import load_dotenv

# Add root to path
sys.path.append(os.getcwd())

load_dotenv(".env")
load_dotenv("genesis-web/.env") 

url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
key = os.getenv("VITE_SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

# Simple Skill Dictionary (Keyword -> Category)
SKILL_MAP = {
    "python": "Language",
    "javascript": "Language",
    "typescript": "Language",
    "react": "Framework",
    "fastapi": "Framework",
    "docker": "Tool",
    "kubernetes": "Tool",
    "git": "Tool",
    "supabase": "Tool",
    "sql": "Language"
}

def analyze_history():
    print("🧠 Analyzing Neural Timeline for Skills...")
    
    # 1. Fetch recent contexts (Debates, Code Changes)
    # We fetch relevant fields.
    try:
        response = supabase.table("atomic_contexts").select("content, folder_name").order("created_at", desc=True).limit(20).execute()
    except Exception as e:
        print(f"Error fetching history: {e}")
        return

    xp_gains = {}

    for row in response.data:
        text = (row.get('content') or "") + " " + (row.get('folder_name') or "")
        text = text.lower()
        
        for skill, category in SKILL_MAP.items():
            if skill in text:
                if skill not in xp_gains: xp_gains[skill] = 0
                xp_gains[skill] += 5 # 5 XP per mention/usage context

    # 2. Update Skills in DB
    print("\n--- Skill Updates ---")
    for skill_name, xp in xp_gains.items():
        category = SKILL_MAP[skill_name]
        print(f"💪 {skill_name.title()} (+{xp} XP)")
        
        # Upsert Logic: Get current, add XP, update.
        try:
            curr = supabase.table("agent_skills").select("*").eq("name", skill_name.title()).execute()
            current_level = 0
            if curr.data:
                current_level = curr.data[0]['proficiency']
                
            new_level = min(100, current_level + xp) # Cap at 100
            
            data = {
                "name": skill_name.title(),
                "category": category,
                "proficiency": new_level
            }
            
            # Upsert using name as unique key? Table definition has unique constraint on name.
            supabase.table("agent_skills").upsert(data, on_conflict="name").execute()
            
        except Exception as e:
            print(f"Failed to update {skill_name}: {e}")

if __name__ == "__main__":
    analyze_history()
