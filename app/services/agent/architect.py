import uuid
import re
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, AtomicArtifact, OrchestratorTask, ChatMessage
from app.services.hive.hive_mind import HiveMind
from app.services.chat.history import history_service

class SupremeArchitect:
    def __init__(self):
        self.hive = HiveMind()
        self.debug_path = r"C:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex\debug_rag_context.txt"

    async def process_request(self, user_text: str, session_id: str, db: Session):
        """
        Main entry point for the Architect's thought process.
        Returns: The stored ChatMessage object of the assistant's reply.
        """
        self._log(f"\n\n--- NEW REQUEST: {user_text} ---\n")
        print(f"🧠 [Architect] Thinking about: {user_text}")

        # 1. Build Context
        context = self._build_context(user_text, session_id, db)
        
        # 2. Construct System Prompt
        system_prompt = f"User: {user_text}\nRole: Supreme Architect. Guide the user.\n{context}"
        self._log("FULL CONTEXT:\n" + system_prompt + "\n----------------\n")

        # 3. Consult the Hive Mind (LLM)
        try:
            response_text = await self.hive._generate_response("ARCHITECT", system_prompt)
        except Exception as e:
            self._log(f"CRITICAL LLM ERROR: {e}\n")
            response_text = "I am currently disconnected from the Hive Mind. Please check my neural pathways (API Keys/Server)."

        # 4. Save Response
        agent_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="assistant",
            content=response_text
        )
        db.add(agent_msg)
        db.commit()

        # 5. Post-Process (Task Extraction)
        self._extract_tasks(response_text, session_id, db)
        
        print("✅ [Architect] Replied.")
        return agent_msg

    def _build_context(self, user_text: str, session_id: str, db: Session) -> str:
        """Gather knowledge from RAG, Roadmap, and Session History."""
        context = ""

        # A. Repo Structure (RAG)
        artifacts = db.query(AtomicArtifact).filter(AtomicArtifact.filename == "file_structure.tree").all()
        self._log(f"Found {len(artifacts)} repo structure artifacts.\n")
        
        if artifacts:
            context += "\n\nAVAILABLE REPOSITORIES:\n"
            for art in artifacts:
                # Robust path handling
                path = art.local_path.replace("\\", "/") 
                repo_name = path.split("/")[-1]
                self._log(f"Injecting structure for {repo_name}\n")
                context += f"--- REPOSITORY: {repo_name} ---\nStructure Root:\n{art.content[:4000]}\n"

        # B. Session Roadmap
        existing_tasks = db.query(OrchestratorTask).filter(OrchestratorTask.session_id == session_id).all()
        if existing_tasks:
            task_list_str = "\n".join([f"- [{t.status}] {t.title}" for t in existing_tasks])
            context += f"\nCURRENT ROADMAP (Use this context):\n{task_list_str}\n"

        return context

    def _extract_tasks(self, text: str, session_id: str, db: Session):
        """Parse response for new tasks and add them to the Roadmap."""
        # Only extract if it looks like a plan
        triggers = ["road map", "roadmap", "plan", "to-do", "todo"]
        if not any(t in text.lower() for t in triggers):
            return

        try:
            tasks = []
            # Numbered lists: 1. Task
            matches = re.findall(r'^\d+\.\s+(.*)', text, re.MULTILINE)
            tasks.extend(matches)
            # Bullet points: - Task
            matches_bullets = re.findall(r'^-\s+(.*)', text, re.MULTILINE)
            tasks.extend(matches_bullets)
            
            count = 0
            for t_title in tasks:
                clean_title = t_title.strip("**").strip()
                if len(clean_title) > 3:
                     # Avoid duplicates? (MVP: Allow for now)
                    task = OrchestratorTask(
                        id=str(uuid.uuid4()),
                        title=clean_title,
                        status="PENDING",
                        assigned_agent="ARCHITECT",
                        session_id=session_id
                    )
                    db.add(task)
                    count += 1
            db.commit()
            if count > 0:
                print(f"✅ [Architect] Extracted {count} tasks.")
        except Exception as e:
            print(f"⚠️ Task Extraction Error: {e}")

    def _log(self, text: str):
        try:
            with open(self.debug_path, "a", encoding="utf-8") as f:
                f.write(text)
        except: pass

architect = SupremeArchitect()
