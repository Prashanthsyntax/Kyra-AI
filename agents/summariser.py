# agents/summariser.py
from groq import Groq
from datetime import datetime, timedelta
from db import get_session, Message, DigestLog
from connectors.twitter_connector import get_home_timeline
from connectors.news_connector import get_top_news
from config import GROQ_API_KEY, GROQ_MODEL
from connectors.telegram_connector import send_message
from agents.email_agent import fetch_important_emails

groq = Groq(api_key=GROQ_API_KEY)


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _get_recent_whatsapp_messages(hours: int = 2) -> str:
    """Pull messages stored in the last N hours from SQLite."""
    session = get_session()
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    msgs = (
        session.query(Message)
        .filter(Message.timestamp >= cutoff)
        .order_by(Message.timestamp.asc())
        .all()
    )
    session.close()
    if not msgs:
        return "No new WhatsApp messages in the last 2 hours."
    lines = [f"• [{m.chat_name}] {m.sender}: {m.body[:120]}" for m in msgs]
    return "\n".join(lines)


def _format_emails() -> str:
    """Fetch and format important emails."""
    try:
        emails = fetch_important_emails(max_results=20)
        if not emails:
            return "No important emails."
        lines = []
        for e in emails:
            icon   = "🔴" if e["priority"] == "urgent" else "📧"
            sender = e["from"].split("<")[0].strip() or e["from"]
            lines.append(f"• {icon} {sender}: {e['subject']}")
        return "\n".join(lines)
    except Exception as ex:
        print(f"[Kyra] Email fetch failed: {ex}")
        return "Email summary unavailable."


def _summarise_with_groq(wa: str, tweets: str, news: str, emails: str) -> str:
    prompt = f"""
You are Kyra, a smart personal AI assistant.
Summarise the following information clearly and concisely for the user.
Use bullet points. Be friendly. Keep it under 500 words.
Add relevant emojis for readability.

=== WhatsApp messages (last 2 hrs) ===
{wa}

=== Twitter / X timeline ===
{tweets}

=== Top news ===
{news}

=== Important emails ===
{emails}

Start your reply with: "Hi! Here's your Kyra digest 🤖"
Sections order: WhatsApp → Twitter → News → Email
    """.strip()

    response = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


# ──────────────────────────────────────────────────────────────
# Send helper
# ──────────────────────────────────────────────────────────────

async def send_whatsapp_message(text: str):
    """Send message via Telegram to Kyra's dedicated chat."""
    try:
        await send_message(text)
        print("[Kyra] Telegram message sent.")
    except Exception as e:
        print(f"[Kyra] Failed to send Telegram message: {e}")


# ──────────────────────────────────────────────────────────────
# Entry points called by scheduler.py
# ──────────────────────────────────────────────────────────────

async def run_digest():
    """Main entry point called by the scheduler every 2 hours."""
    print(f"[Kyra] Running digest at {datetime.now().strftime('%H:%M %d-%m-%Y')}")

    wa     = _get_recent_whatsapp_messages()
    tweets = get_home_timeline()
    news   = get_top_news()
    emails = _format_emails()              # ← collected here, inside the function

    summary = _summarise_with_groq(wa, tweets, news, emails)

    # Save to DB
    session = get_session()
    session.add(DigestLog(content=summary))
    session.commit()
    session.close()

    await send_whatsapp_message(summary)
    print("[Kyra] Digest sent.")