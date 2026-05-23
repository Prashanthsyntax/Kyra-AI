# db.py
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine  = create_engine("sqlite:///kyra.db", echo=False)
Session = sessionmaker(bind=engine)
Base    = declarative_base()


class Message(Base):
    """Stores incoming WhatsApp/Telegram messages so the summariser has context."""
    __tablename__ = "messages"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    sender     = Column(String(50))
    chat_name  = Column(String(200))
    body       = Column(Text)
    timestamp  = Column(DateTime, default=datetime.utcnow)


class DigestLog(Base):
    """Keeps a record of every digest Kyra has sent."""
    __tablename__ = "digest_log"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    content    = Column(Text)
    sent_at    = Column(DateTime, default=datetime.utcnow)


class CalendarLog(Base):
    """Tracks calendar events Kyra created."""
    __tablename__ = "calendar_log"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    title      = Column(String(300))
    start_time = Column(String(50))
    end_time   = Column(String(50))
    event_id   = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationMemory(Base):
    """Short-term memory for Kyra's emotional assistant persona."""
    __tablename__ = "conversation_memory"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(String(50))
    role       = Column(String(20))   # "user" or "assistant"
    content    = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)  # auto-fills if omitted


class FactCategory(Base):
    """Single-row table that tracks which fact category is up next."""
    __tablename__ = "fact_category"
    id      = Column(Integer, primary_key=True, autoincrement=True)
    pointer = Column(Integer, default=0)


def init_db():
    """Create all tables if they don't exist. Called once on startup."""
    Base.metadata.create_all(engine)


def get_session():
    return Session()