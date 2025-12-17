import os
import shutil

class RealtimeKnowledgeService:
    def __init__(self, base_repos_path: str = "data/shared_repos"):
        self.base_repos_path = base_repos_path

    def get_file_context(self, query_text: str, explicit_repo_context: str = None) -> tuple[str, str]:
        """
        Scans the file system to find relevant code based on the query or explicit context.
        Returns:
            - knowledge_context (str): The formatted context string.
            - target_repo (str): The name of the identified repository (or None).
        """
        knowledge_context = ""
        target_repo = None
        
        if not os.path.exists(self.base_repos_path):
            return "", None

        repos = [d for d in os.listdir(self.base_repos_path) if os.path.isdir(os.path.join(self.base_repos_path, d))]
        
        # Strategy 0: Explicit Context from UI (Highest Priority)
        if explicit_repo_context:
            clean_ctx = explicit_repo_context.replace("REPO: ", "")
            if clean_ctx in repos:
                target_repo = clean_ctx
                print(f"DEBUG AGENT: Target Repo set to {target_repo} via Context")

        # Strategy A: Explicit Mention in Query
        if not target_repo:
            for r in repos:
                repo_parts = r.lower().replace("-", " ").split()
                # Check strict name match or fuzzy part match (len > 3)
                if r.lower() in query_text.lower() or any(p in query_text.lower() for p in repo_parts if len(p)>3):
                    target_repo = r
                    print(f"DEBUG AGENT: Target Repo set to {target_repo} via Query Heuristic")
                    break
        
        # Strategy B: Implicit Context (Single Repo)
        if not target_repo and len(repos) == 1:
            target_repo = repos[0]

        # Strategy C: File Hunting (Look for specific files mentioned)
        if not target_repo:
            words = query_text.split()
            potential_files = [w for w in words if "." in w and len(w) > 3] 
            for r in repos:
                repo_root_check = os.path.join(self.base_repos_path, r)
                # MVP: If specific file mentioned, just defaults to first repo or 'Strategy D' logic?
                # For now let's keep the logic simple: if we find a potential file, we assume it *might* be here.
                # Actually, main.py original logic wasn't fully implemented for hunting. 
                pass

        # Strategy D: Default Fallback
        if not target_repo and len(repos) > 0:
             print(f"DEBUG AGENT: Defaulting to first repo {repos[0]} as fallback")
             target_repo = repos[0]
        
        # 2. Walk and Read
        if target_repo:
            repo_root = os.path.join(self.base_repos_path, target_repo)
            knowledge_context += f"\n\n--- 🔴 LIVE FILE SYSTEM ACCESS: {target_repo} ---\n"
            knowledge_context += "The user has granted you READ access to the following files. ANSWER ONLY BASED ON THIS CODE. DO NOT HALLUCINATE OR GIVE GENERIC DEFINITIONS.\n"
            
            file_count = 0
            total_chars = 0
            MAX_CHARS = 65000 # Increased for larger reads
            
            for root, dirs, files in os.walk(repo_root):
                # Exclude noise
                if ".git" in root or "node_modules" in root or "__pycache__" in root or ".next" in root: continue
                
                for f in files:
                    if f in ["package-lock.json", ".DS_Store", "yarn.lock", "pnpm-lock.yaml"]: continue
                    if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".ico"): continue
                    
                    file_path = os.path.join(root, f)
                    rel_path = os.path.relpath(file_path, repo_root)
                    
                    # Prioritize the requested file if mentioned
                    is_priority = f.lower() in query_text.lower()
                    
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as file_obj:
                            content = file_obj.read()
                            
                            # Size limiter per file?
                            if len(content) > 20000:
                                content = content[:20000] + "\n... (File truncated due to size) ..."

                            # If this is the specific file requested, ensure it gets in!
                            if is_priority:
                                knowledge_context = f"\n[PRIORITY FILE: {rel_path}]\n```\n{content}\n```\n" + knowledge_context
                                total_chars += len(content)
                                file_count += 1
                                continue

                            if total_chars + len(content) > MAX_CHARS:
                                knowledge_context += f"\n[FILE: {rel_path}] (Truncated context)\n"
                                continue
                                
                            knowledge_context += f"\n[FILE: {rel_path}]\n```\n{content}\n```\n"
                            total_chars += len(content)
                            file_count += 1
                    except Exception as e_read:
                         print(f"Error reading {rel_path}: {e_read}")
            
            print(f"✅ [Live Read] Injected {file_count} files ({total_chars} chars) from {target_repo}")

        return knowledge_context, target_repo

realtime_knowledge = RealtimeKnowledgeService()
