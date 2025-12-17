
import os
import shutil
import subprocess
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List

from app.core.database import SessionLocal, AtomicContext, AtomicArtifact

SHARED_REPOS_DIR = "data/shared_repos"

class RepoIngestor:

    def __init__(self):
        os.makedirs(SHARED_REPOS_DIR, exist_ok=True)
        # Simple in-memory job tracking: {job_id: {status: str, repo: str, error: str, start_time: str}}
        self.JOBS: Dict[str, Dict[str, Any]] = {}

    def ingest_repo(self, repo_url: str, job_id: str, scope: str = "global", session_id: str = None) -> Dict[str, Any]:
        """
        Clones a repo and generates a knowledge artifact.
        Returns the ID of the created AtomicContext.
        """
        self.JOBS[job_id] = {
            "status": "CLONING",
            "repo": repo_url,
            "start_time": datetime.utcnow().isoformat()
        }

        repo_name = repo_url.split("/")[-1].replace(".git", "")
        # Handle query params or slight variations in URL
        if "?" in repo_name: repo_name = repo_name.split("?")[0]
        
        target_dir = os.path.join(SHARED_REPOS_DIR, repo_name)
        
        try:
            # 1. Clean previous if exists
            if os.path.exists(target_dir):
                self.JOBS[job_id]["status"] = "CLEANING"
                try:
                    # Handle windows read-only files (git)
                    def on_rm_error(func, path, exc_info):
                        os.chmod(path, 0o777)
                        func(path)
                    shutil.rmtree(target_dir, onerror=on_rm_error)
                except Exception as e:
                    print(f"⚠️ Could not fully clean {target_dir}: {e}")

            # 2. Clone
            print(f"⬇️ Cloning {repo_url}...")
            self.JOBS[job_id]["status"] = "CLONING_GIT"
            try:
                # Disable interactive prompts for credentials
                env = os.environ.copy()
                env["GIT_TERMINAL_PROMPT"] = "0"
                subprocess.run(["git", "clone", "--depth", "1", repo_url, target_dir], check=True, capture_output=True, env=env)
            except subprocess.CalledProcessError as e:
                err_msg = e.stderr.decode()
                # Check for common auth errors
                if "Authentication failed" in err_msg or "could not read Username" in err_msg:
                    raise Exception("Public access denied. Repo might be private.")
                raise Exception(f"Git Clone Failed: {err_msg}")

            # 3. Analyze Structure
            print(f"🔍 Analyzing {repo_name}...")
            self.JOBS[job_id]["status"] = "ANALYZING"
            structure = self._generate_tree(target_dir)
            summary = self._read_key_files(target_dir)
            
            # 4. Create Context in DB
            self.JOBS[job_id]["status"] = "SAVING"
            context_id = str(uuid.uuid4())
            db = SessionLocal()
            try:
                # Main Context Entry
                ctx = AtomicContext(
                    id=context_id,
                    folder_name=f"REPO: {repo_name}",
                    timestamp=datetime.utcnow(),
                    batch_id="REPO_INGESTION",
                    scope=scope,
                    session_id=session_id
                )
                db.add(ctx)
                
                # Artifact 1: Structure
                art_struct = AtomicArtifact(
                    id=str(uuid.uuid4()),
                    context_id=context_id,
                    filename="file_structure.tree",
                    file_type="tree",
                    content=structure,
                    local_path=target_dir
                )
                db.add(art_struct)
                
                # Artifact 2: Key Content Summary
                art_summary = AtomicArtifact(
                    id=str(uuid.uuid4()),
                    context_id=context_id,
                    filename="repo_summary.md",
                    file_type="markdown",
                    content=summary,
                    local_path=target_dir
                )
                db.add(art_summary)
                
                db.commit()
                print(f"✅ Ingested {repo_name} into Local Core.")
                self.JOBS[job_id]["status"] = "COMPLETED"
                return {
                    "status": "success",
                    "repo_name": repo_name,
                    "context_id": context_id,
                    "structure_preview": structure[:500] + "..."
                }
                
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Ingestion Failed: {e}")
            self.JOBS[job_id]["status"] = "FAILED"
            self.JOBS[job_id]["error"] = str(e)
            raise e

    def get_active_jobs(self):
        # Clean up old completed jobs (keep them for 1 minute for UI to see)
        # For simplicity, we just return everything for now, can optimize later if needed
        return self.JOBS

    def _generate_tree(self, startpath: str) -> str:
        """Generates a visual tree structure"""
        tree_str = ""
        prefix = "|-- "
        
        for root, dirs, files in os.walk(startpath):
            if ".git" in root: continue
            
            level = root.replace(startpath, '').count(os.sep)
            indent = '    ' * level
            tree_str += f"{indent}{os.path.basename(root)}/\n"
            subindent = '    ' * (level + 1)
            for f in files:
                tree_str += f"{subindent}{prefix}{f}\n"
                
        return tree_str

    def _read_key_files(self, startpath: str) -> str:
        """Reads README, package.json, requirements.txt, etc."""
        content = "# Repo Summary\n\n"
        
        priority_files = ["README.md", "README.txt", "package.json", "requirements.txt", "docker-compose.yml"]
        
        for root, dirs, files in os.walk(startpath):
            if ".git" in root: continue
            
            for f in files:
                if f in priority_files:
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as file:
                            data = file.read()
                            # Limit file size to avoid blowing up context immediately
                            if len(data) > 10000: data = data[:10000] + "\n...[TRUNCATED]"
                            
                            rel_path = os.path.relpath(path, startpath)
                            content += f"## {rel_path}\n```\n{data}\n```\n\n"
                    except:
                        pass
        return content

repo_ingestor = RepoIngestor()
