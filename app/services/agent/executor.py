import os
import re

class AgentExecutorService:
    def __init__(self, base_repos_path: str = "data/shared_repos"):
        self.base_repos_path = base_repos_path

    def execute_actions(self, response_data: dict | str, target_repo: str) -> str:
        """
        Parses the LLM response for *** WRITE_FILE *** blocks and executes them.
        Returns a log string of actions taken (to be appended to the AI response).
        """
        
        # Normalize Response (Handle Dict vs Str)
        response_text = response_data
        if isinstance(response_data, dict):
            response_text = response_data.get("answer", "")
            
        if not isinstance(response_text, str) or "*** WRITE_FILE:" not in response_text:
            return ""

        if not target_repo:
             print("⚠️ AGENT WARNING: Agent tried to write file but no TARGET REPO identified. Write skipped.")
             return "\n\n⚠️ AGENT WARNING: I tried to edit a file, but I don't know which Repository to use. Please specify a repo context."

        action_log = ""
        try:
            # Flexible Regex handles: "*** WRITE_FILE: path ***", "***WRITE_FILE: path***", newline, content, "*** END_WRITE ***"
            action_blocks = re.findall(r"\*\*\*\s*WRITE_FILE:\s*(.*?)\s*\*\*\*\n(.*?)\s*(\*\*\*\s*END_WRITE\s*\*\*\*|$)", response_text, re.DOTALL)
            
            writes_log = []
            repo_root = os.path.join(self.base_repos_path, target_repo)
            
            for path_raw, content_raw, _ in action_blocks:
                rel_path = path_raw.strip()
                file_content = content_raw.strip()
                
                # [FIX] Redundant Path Handling
                # If agent writes 'repo_name/file.txt', strip 'repo_name/'
                if target_repo and rel_path.startswith(f"{target_repo}/"):
                    rel_path = rel_path[len(target_repo)+1:]
                    print(f"⚠️ FIXED STRING: Stripped repo name from path -> {rel_path}")

                # Security Check: Prevent traversal
                if ".." in rel_path or rel_path.startswith("/") or "\\" in rel_path:
                    print(f"⚠️ Security blocked write to: {rel_path}")
                    writes_log.append(f"Blocked (Security): {rel_path}")
                    continue
                    
                full_path = os.path.join(repo_root, rel_path)
                
                # Ensure dir exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, "w", encoding="utf-8") as f_write:
                    f_write.write(file_content)
                print(f"✅ AGENT WROTE TO: {full_path}")
                writes_log.append(f"Edited: {rel_path}")
            
            if writes_log:
                action_log = "\n\n⚡ AGENT ACTIONS EXECUTED:\n- " + "\n- ".join(writes_log)
                
        except Exception as e_action:
            print(f"Agent Action Failed: {e_action}")
            action_log = f"\n\n❌ AGENT ERROR: Failed to execute write. {str(e_action)}"

        return action_log

agent_executor = AgentExecutorService()
