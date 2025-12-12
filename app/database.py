from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func
import uuid
from app.core.config import settings

Base = declarative_base()

# -----------------
# Models
# -----------------
class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('chat_sessions.id'))
    role = Column(String, nullable=False) # user, assistant
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    session = relationship("ChatSession", back_populates="messages")

# -----------------
# Engine
# -----------------
# Fallback to local SQLite if Supabase not properly configured, or if explicit Local mode
if settings.SUPABASE_TARGET == "LOCAL" or not settings.SUPABASE_DB_URL:
    # Use SQLite
    import os
    os.makedirs("data/db", exist_ok=True)
    DATABASE_URL = "sqlite:///./data/db/chat_history.db"
    print("⚠️ Using Local SQLite Database for Chat History")
else:
    # Use Supabase/Postgres
    DATABASE_URL = settings.SUPABASE_DB_URL

# Handle connect_args for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
