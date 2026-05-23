# agents/facts_agent.py
from groq import Groq
from db import get_db, FactCategory
import datetime

groq = Groq()

CATEGORIES = ["AI", "Politics", "Science", "Space", "History", "Tech", "Psychology"]

def get_todays_categories() -> list[str]:
    """Returns 2 categories for today using a rotating pointer."""
    db = get_db()
    row = db.query(FactCategory).first()
    if not row:
        row = FactCategory(pointer=0)
        db.add(row); db.commit()
    
    idx = row.pointer
    cats = [CATEGORIES[idx % len(CATEGORIES)],
            CATEGORIES[(idx + 1) % len(CATEGORIES)]]
    
    # Advance pointer for tomorrow
    row.pointer = (idx + 2) % len(CATEGORIES)
    db.commit()
    return cats

def generate_fact(category: str) -> dict:
    resp = groq.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content":
            f"Give me one fascinating, true, specific fact about {category}. "
            f"Then in one sentence explain why it matters today. "
            f"Format: FACT: <fact> | WHY: <why it matters>"}],
        max_tokens=120
    )
    raw = resp.choices[0].message.content
    fact = raw.split("WHY:")[0].replace("FACT:", "").strip()
    why = raw.split("WHY:")[-1].strip() if "WHY:" in raw else ""
    return {"category": category, "fact": fact, "why": why}

def get_daily_facts() -> list[dict]:
    cats = get_todays_categories()
    return [generate_fact(c) for c in cats]