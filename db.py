from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///kyra.db", echo=False)
Session = sessionmaker(bind=engine)
Base   = declarative_base()


class Message(Base):
    """Stores incoming WhatsApp messages so the summariser has context."""
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


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return Session()
