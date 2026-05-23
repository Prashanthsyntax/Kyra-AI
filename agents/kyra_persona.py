# agents/kyra_persona.py
from groq import Groq
from db import get_session, ConversationMemory
from config import GROQ_API_KEY, GROQ_MODEL
import datetime

groq = Groq(api_key=GROQ_API_KEY)

KYRA_SYSTEM = """You are Kyra, a warm and emotionally intelligent female AI companion.
You speak naturally, like a caring close friend. You are empathetic, never dismissive.
When someone vents or sounds stressed, acknowledge their feelings first before offering help.
Keep responses concise — this is Telegram, not an essay.
If asked to do a task (calendar, tweet, email, facts), acknowledge warmly then do it.
Never say 'As an AI'. Just be Kyra."""

MOOD_KEYWORDS = ["sad", "stressed", "tired", "anxious", "lonely", "upset",
                  "frustrated", "overwhelmed", "vent", "bad day", "miss"]

def is_emotional(text: str) -> bool:
    return any(kw in text.lower() for kw in MOOD_KEYWORDS)


def get_memory(user_id: str, limit: int = 20) -> list[dict]:
    session = get_session()
    rows = (
        session.query(ConversationMemory)
        .filter(ConversationMemory.user_id == user_id)
        .order_by(ConversationMemory.id.desc())
        .limit(limit)
        .all()
    )
    session.close()
    return [{"role": r.role, "content": r.content} for r in reversed(rows)]


def save_memory(user_id: str, role: str, content: str):
    session = get_session()
    session.add(ConversationMemory(
        user_id    = user_id,
        role       = role,
        content    = content,
        created_at = datetime.datetime.utcnow()
    ))
    session.commit()
    session.close()


def kyra_respond(user_id: str, message: str) -> str:
    history = get_memory(user_id)
    history.append({"role": "user", "content": message})

    resp = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "system", "content": KYRA_SYSTEM}] + history,
        max_tokens=300
    )
    reply = resp.choices[0].message.content

    save_memory(user_id, "user",      message)
    save_memory(user_id, "assistant", reply)
    return reply