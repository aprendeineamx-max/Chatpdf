
import asyncio
import uuid
from typing import List, Dict, Any
from pydantic import BaseModel

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
        self.personas = {
            "ARCHITECT": AgentPersona(
                name="Architect",
                role="System Design",
                color="blue",
                system_prompt="You are the Architect. Design high-level structures."
            ),
            "CODER": AgentPersona(
                name="Coder",
                role="Implementation",
                color="green",
                system_prompt="You are the Coder. Write efficient, clean Python/React code."
            ),
            "QA": AgentPersona(
                name="QA",
                role="Quality Assurance",
                color="red",
                system_prompt="You are QA. Find bugs, security flaws, and edge cases."
            )
        }
        self.sessions: Dict[str, List[HiveMessage]] = {}

    async def start_council(self, topic: str) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        
        # Initial Topic
        self._add_message(session_id, "USER", topic)
        
        return session_id

    async def process_turn(self, session_id: str) -> List[HiveMessage]:
        if session_id not in self.sessions:
            return []

        # Mock Simulation for MVP (real implementation would call LLMs)
        history = self.sessions[session_id]
        last_msg = history[-1]
        
        new_messages = []
        
        if last_msg.agent_name == "USER":
            # Architect responds first
            msg = self._add_message(session_id, "Architect", f"Analyzing request: '{last_msg.content}'.\nI propose a 3-layer architecture...")
            new_messages.append(msg)
            await asyncio.sleep(1) 
            
            # Coder responds
            msg = self._add_message(session_id, "Coder", "Agreed. I will implement the Service layer first using FastAPI.")
            new_messages.append(msg)
            await asyncio.sleep(1)

            # QA responds
            msg = self._add_message(session_id, "QA", "Caution: Ensure input validation on the API endpoints.")
            new_messages.append(msg)
            
        return new_messages

    def _add_message(self, session_id: str, agent: str, content: str) -> HiveMessage:
        import time
        msg = HiveMessage(
            id=str(uuid.uuid4()),
            agent_name=agent,
            content=content,
            timestamp=time.time()
        )
        self.sessions[session_id].append(msg)
        return msg

hive_mind = HiveMind()
