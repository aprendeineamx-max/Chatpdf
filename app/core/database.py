
import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# Ensure directory exists
DB_DIR = "data/db"
os.makedirs(DB_DIR, exist_ok=True)

SQLITE_URL = f"sqlite:///{DB_DIR}/local_core.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models matching Supabase Schema

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String, primary_key=True) # UUID string
    user_id = Column(String, nullable=True)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String) # user, assistant, system
    content = Column(Text)
    sources = Column(JSON, default=[]) 
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ChatSession", back_populates="messages")

class AtomicContext(Base):
    __tablename__ = "atomic_contexts"
    id = Column(String, primary_key=True)
    folder_name = Column(String, unique=True)
    timestamp = Column(DateTime)
    batch_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    artifacts = relationship("AtomicArtifact", back_populates="context", cascade="all, delete-orphan")

class AtomicArtifact(Base):
    __tablename__ = "atomic_artifacts"
    id = Column(String, primary_key=True)
    context_id = Column(String, ForeignKey("atomic_contexts.id"))
    filename = Column(String)
    file_type = Column(String)
    content = Column(Text)
    local_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    context = relationship("AtomicContext", back_populates="artifacts")

class OrchestratorTask(Base):
    __tablename__ = "orchestrator_tasks"
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String, default="PENDING")
    priority = Column(String, default="MEDIUM")
    assigned_agent = Column(String, default="auto")
    evidence = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    print(f"⚡ Initializing Local Core at {SQLITE_URL}...")
    Base.metadata.create_all(bind=engine)
    print("✅ Local Tables Ready.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
