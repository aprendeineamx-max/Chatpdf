
import asyncio
import uuid
import time
import logging
from typing import List, Dict, Any
from pydantic import BaseModel
import google.generativeai as genai
from supabase import create_client, Client
from app.core.config import settings
from app.core.key_manager import key_manager

logger = logging.getLogger(__name__)

class AgentPersona(BaseModel):
    name: str
    role: str
    color: str
    system_prompt: str

class HiveMessage(BaseModel):
    id: str
    agent_name: str
    content: str
    timestamp: float

class HiveMind:
    def __init__(self):
        # 1. Define Personas
        self.personas = {
            "ARCHITECT": AgentPersona(
                name="Architect",
                role="System Design",
                color="blue",
                system_prompt="You are the Architect. You design scalable, robust system architectures. You think in big pictures, modules, and data flows. Be concise but authoritative."
            ),
            "CODER": AgentPersona(
                name="Coder",
                role="Implementation",
                color="green",
                system_prompt="You are the Coder. You care about clean code, libraries, and implementation details. You speak in technical terms (Python, React, Asyncio). Be practical."
            ),
            "QA": AgentPersona(
                name="QA",
                role="Quality Assurance",
                color="red",
                system_prompt="You are QA. You are paranoid about bugs, security deficiencies, and edge cases. You critique plans and point out flaws. Be sharp and critical."
            )
        }
        self.sessions: Dict[str, List[HiveMessage]] = {}
        
        # 2. Init Supabase (Liquid Memory)
        self.supabase: Client = None
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                logger.info("HiveMind connected to Liquid Memory (Supabase).")
            except Exception as e:
                logger.error(f"HiveMind Memory Error: {e}")

    async def start_council(self, topic: str) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        
        # Initial User Topic
        self._add_message(session_id, "USER", topic)
        
        # Log start in local memory
        logger.info(f"Council Summoned for Session {session_id}")
        return session_id

    async def process_turn(self, session_id: str) -> List[HiveMessage]:
        if session_id not in self.sessions:
            return []

        history = self.sessions[session_id]
        if not history: return []
        
        last_msg = history[-1]
        new_messages = []
        
        # Logic: If USER spoke, trigger the Chain of Thought
        if last_msg.agent_name == "USER":
            # 1. Architect Analysis
            architect_ctx = f"User Request: '{last_msg.content}'"
            arch_resp = await self._generate_response("ARCHITECT", architect_ctx)
            new_messages.append(self._add_message(session_id, "Architect", arch_resp))
            
            # 2. Coder Implementation Plan (Simulated delay for realism)
            coder_ctx = f"Request: '{last_msg.content}'.\nArchitect Plan: '{arch_resp}'"
            coder_resp = await self._generate_response("CODER", coder_ctx)
            new_messages.append(self._add_message(session_id, "Coder", coder_resp))

            # 3. QA Review
            qa_ctx = f"Plan: '{coder_resp}'.\nCritique this for security and bugs."
            qa_resp = await self._generate_response("QA", qa_ctx)
            new_messages.append(self._add_message(session_id, "QA", qa_resp))
            
            # 4. Persist to Timeline (Synergy)
            await self._persist_session(session_id, last_msg.content)
            
        return new_messages

    async def _generate_response(self, persona_key: str, context: str, provider_override: str = None) -> str:
        persona = self.personas.get(persona_key)
        if not persona: return "Error: Unknown Persona"

        # Logic: If Override exists, use ONLY that provider. Else use failover order.
        if provider_override and provider_override != "auto":
            providers = [provider_override]
        else:
            providers = key_manager.get_failover_order()
        
        for provider in providers:
            retries = 3 # Try 3 keys per provider
            while retries > 0:
                api_key = key_manager.get_best_key(provider)
                if not api_key: 
                    logger.warning(f"No active keys for {provider}. Switching...")
                    break # Next provider
                
                try:
                    prompt = f"{persona.system_prompt}\n\nCONTEXT:\n{context}\n\nRESPONSE:"
                    
                    if provider == "google":
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('models/gemini-flash-latest')
                        response = await asyncio.to_thread(model.generate_content, prompt)
                        return response.text.strip()
                    
                    elif provider == "groq":
                         from groq import Groq
                         client = Groq(api_key=api_key)
                         
                         completion = await asyncio.to_thread(
                             lambda: client.chat.completions.create(
                                 model="llama-3.3-70b-versatile",
                                 messages=[
                                     {"role": "system", "content": persona.system_prompt},
                                     {"role": "user", "content": f"CONTEXT:\n{context}"}
                                 ],
                                 temperature=0.7,
                                 max_tokens=1024
                             )
                         )
                         return completion.choices[0].message.content.strip()

                    elif "sambanova" in provider: # Handles 'sambanova', 'sambanova_primary', 'sambanova_secondary'
                         from openai import OpenAI
                         client = OpenAI(
                             base_url="https://api.sambanova.ai/v1",
                             api_key=api_key,
                         )
                         
                         completion = await asyncio.to_thread(
                             lambda: client.chat.completions.create(
                                 model="Meta-Llama-3.3-70B-Instruct",
                                 messages=[
                                     {"role": "system", "content": persona.system_prompt},
                                     {"role": "user", "content": f"CONTEXT:\n{context}"}
                                 ],
                                 temperature=0.7,
                                 max_tokens=1024
                             )
                         )
                         return completion.choices[0].message.content.strip()

                    elif provider == "openrouter":
                         from openai import OpenAI
                         client = OpenAI(
                             base_url="https://openrouter.ai/api/v1",
                             api_key=api_key,
                         )
                         
                         completion = await asyncio.to_thread(
                             lambda: client.chat.completions.create(
                                 model="anthropic/claude-3.5-sonnet",
                                 headers={
                                     "HTTP-Referer": "https://genesis-architect.com", # Required by OpenRouter
                                     "X-Title": "Genesis Architect"
                                 },
                                 messages=[
                                     {"role": "system", "content": persona.system_prompt},
                                     {"role": "user", "content": f"CONTEXT:\n{context}"}
                                 ]
                             )
                         )
                         return completion.choices[0].message.content.strip()

                except Exception as e:
                    logger.error(f"Provider {provider} failed with key {api_key[:4]}...: {e}")
                    key_manager.report_failure(api_key, provider)
                    retries -= 1
        
        return f"[{persona.name} is offline: System Exhaustion]"

    def _add_message(self, session_id: str, agent: str, content: str) -> HiveMessage:
        msg = HiveMessage(
            id=str(uuid.uuid4()),
            agent_name=agent,
            content=content,
            timestamp=time.time()
        )
        self.sessions[session_id].append(msg)
        return msg

    async def _persist_session(self, session_id: str, title: str):
        """
        Saves the debate to 'atomic_contexts' (Folder) and 'atomic_artifacts' (File).
        Supports both Cloud (Supabase) and Local (SQLite).
        """
        timestamp_str = time.strftime('%Y-%m-%d_%H-%M-%S')
        created_at_fmt = time.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Transcript compilation
        history = self.sessions.get(session_id, [])
        transcript = f"# Council Debate: {title}\n\n"
        for msg in history:
            transcript += f"### **{msg.agent_name}**\n{msg.content}\n\n---\n"

        if settings.CORE_MODE == "LOCAL":
            # --- LOCAL MODE (SQLite) ---
            try:
                from app.core.database import SessionLocal, AtomicContext, AtomicArtifact
                db = SessionLocal()
                
                # 1. Create Context
                ctx = AtomicContext(
                    id=session_id,
                    folder_name=f"Council Debate: {title[:40]}...",
                    timestamp=datetime.now(),
                    batch_id="HIVE"
                )
                db.add(ctx)
                
                # 2. Create Artifact
                art = AtomicArtifact(
                    id=str(uuid.uuid4()),
                    context_id=session_id,
                    filename="transcript.md",
                    file_type="GENERATED",
                    content=transcript,
                    local_path="HIVE_MEMORY"
                )
                db.add(art)
                
                db.commit()
                db.close()
                logger.info(f"✅ [Local] Session {session_id} persisted to SQLite.")
            except Exception as e:
                logger.error(f"❌ [Local] Persistence Failed: {e}")

        else:
            # --- CLOUD MODE (Supabase) ---
            if not self.supabase: return
            
            try:
                # 1. Create Context (The Folder)
                ctx_data = {
                    "id": session_id,
                    "folder_name": f"Council Debate: {title[:40]}...", 
                    "timestamp": timestamp_str,
                    "batch_id": "HIVE",
                    "created_at": created_at_fmt
                }
                
                await asyncio.to_thread(lambda: self.supabase.table("atomic_contexts").insert(ctx_data).execute())
                
                # 2. Create Artifact (The File)
                art_data = {
                    "id": str(uuid.uuid4()),
                    "context_id": session_id,
                    "filename": "transcript.md",
                    "file_type": "GENERATED",
                    "content": transcript,
                    "local_path": "HIVE_MEMORY",
                    "created_at": created_at_fmt
                }
                
                await asyncio.to_thread(lambda: self.supabase.table("atomic_artifacts").insert(art_data).execute())
                logger.info(f"Session {session_id} persisted as Context+Artifact.")
                
            except Exception as e:
                logger.error(f"Persistence Failed: {e}")

hive_mind = HiveMind()
